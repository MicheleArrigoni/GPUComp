// GPU Computing (Heidelberg University) - Exercise 2.3: PCIe Data Movements
// Compare synchronous cudaMemcpy on pageable (malloc) and pinned (cudaMallocHost)
// host memory, for host-to-device and device-to-host directions.
// Measurements include CUDA API/launch overhead and CUDA synchronization;
// malloc, cudaMalloc, cudaMallocHost, and initialization are NOT timed.

#include <cuda_runtime.h>

#include <algorithm>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <exception>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

constexpr std::size_t kKiB = 1024;
constexpr std::size_t kMiB = 1024 * kKiB;
constexpr std::size_t kGiB = 1024 * kMiB;

void checkCuda(cudaError_t status, const char *operation, int line) {
    if (status != cudaSuccess) {
        throw std::runtime_error(std::string(operation) + " failed at line " +
                                 std::to_string(line) + ": " + cudaGetErrorString(status));
    }
}
#define CUDA_CHECK(expr) checkCuda((expr), #expr, __LINE__)

int repetitions(std::size_t bytes) {
    if (bytes <= 64 * kKiB) return 1000;
    if (bytes <= kMiB) return 200;
    if (bytes <= 16 * kMiB) return 30;
    if (bytes <= 256 * kMiB) return 8;
    return 4;
}

// Measures the average elapsed host wall-clock time per synchronous cudaMemcpy.
// Synchronization at each end ensures the batch of transfers has finished.
double measureAverageSeconds(void *device, void *host, std::size_t bytes,
                             cudaMemcpyKind direction, int n) {
    void *destination = (direction == cudaMemcpyHostToDevice) ? device : host;
    const void *source = (direction == cudaMemcpyHostToDevice) ? host : device;

    for (int warmup = 0; warmup < 3; ++warmup) {
        CUDA_CHECK(cudaMemcpy(destination, source, bytes, direction));
    }
    CUDA_CHECK(cudaDeviceSynchronize());

    const auto start = std::chrono::steady_clock::now();
    for (int i = 0; i < n; ++i) {
        CUDA_CHECK(cudaMemcpy(destination, source, bytes, direction));
    }
    CUDA_CHECK(cudaDeviceSynchronize());
    const auto stop = std::chrono::steady_clock::now();

    const double total = std::chrono::duration<double>(stop - start).count();
    return total / static_cast<double>(n);
}

std::size_t parseMaxBytes(int argc, char **argv) {
    if (argc == 1) return kGiB;
    if (argc != 3 || std::string(argv[1]) != "--max-mib") {
        throw std::runtime_error("Usage: ./bin/pcie_benchmark [--max-mib 16]\n"
                                 "  Default: full experiment, up to 1024 MiB (1 GiB).\n"
                                 "  --max-mib 16: quick test only, NOT the complete experiment.");
    }
    const std::string arg(argv[2]);
    std::size_t pos = 0;
    const auto value = std::stoull(arg, &pos);
    if (pos != arg.size() || value < 1 || value > 1024) {
        throw std::runtime_error("--max-mib must be an integer from 1 to 1024.");
    }
    return static_cast<std::size_t>(value) * kMiB;
}

}  // namespace

int main(int argc, char **argv) {
    void *pageable = nullptr;
    void *pinned = nullptr;
    void *device = nullptr;

    try {
        const std::size_t maxBytes = parseMaxBytes(argc, argv);
        int deviceId = 0;
        CUDA_CHECK(cudaGetDevice(&deviceId));
        cudaDeviceProp deviceInfo{};
        CUDA_CHECK(cudaGetDeviceProperties(&deviceInfo, deviceId));
        std::cout << "GPU: " << deviceInfo.name << '\n';
        std::cout << "Maximum transfer size: " << (maxBytes / kMiB) << " MiB\n";
        if (maxBytes != kGiB) {
            std::cout << "QUICK TEST ONLY - run without --max-mib for full exercise.\n";
        }

        pageable = std::malloc(maxBytes);
        if (!pageable) {
            throw std::runtime_error("malloc failed: not enough host memory.");
        }
        CUDA_CHECK(cudaMallocHost(&pinned, maxBytes));
        CUDA_CHECK(cudaMalloc(&device, maxBytes));
        std::memset(pageable, 0xA5, maxBytes);
        std::memset(pinned, 0xA5, maxBytes);
        CUDA_CHECK(cudaMemset(device, 0x5A, maxBytes));
        CUDA_CHECK(cudaDeviceSynchronize());

        std::ofstream csv("pcie_results.csv");
        if (!csv) throw std::runtime_error("Cannot create pcie_results.csv.");
        csv << "bytes,memory,direction,time_ms,gbps,repetitions\n";
        csv << std::fixed << std::setprecision(7);

        int pointCount = 0;
        for (std::size_t bytes = kKiB; bytes <= maxBytes; bytes *= 4) {
            ++pointCount;
            for (int memoryType = 0; memoryType < 2; ++memoryType) {
                void *host = memoryType == 0 ? pageable : pinned;
                const char *memoryName = memoryType == 0 ? "pageable" : "pinned";
                for (int direction = 0; direction < 2; ++direction) {
                    const auto kind = direction == 0 ? cudaMemcpyHostToDevice : cudaMemcpyDeviceToHost;
                    const char *dirName = direction == 0 ? "H2D" : "D2H";
                    const int n = repetitions(bytes);
                    const double seconds = measureAverageSeconds(device, host, bytes, kind, n);
                    const double ms = seconds * 1e3;
                    const double gbps = (static_cast<double>(bytes) / seconds) / 1e9;
                    csv << bytes << ',' << memoryName << ',' << dirName << ','
                        << ms << ',' << gbps << ',' << n << '\n';
                    std::cout << std::setw(10) << bytes << " B  " << std::setw(8)
                              << memoryName << "  " << dirName << "  " << std::setw(10)
                              << std::setprecision(4) << gbps << " GB/s\n";
                }
            }
        }
        csv.close();
        std::cout << "\nFinished " << pointCount << " data sizes, 4 conditions each.\n";
        std::cout << "Saved: pcie_results.csv\n";

        CUDA_CHECK(cudaFree(device));
        device = nullptr;
        CUDA_CHECK(cudaFreeHost(pinned));
        pinned = nullptr;
        std::free(pageable);
        pageable = nullptr;
        return EXIT_SUCCESS;
    } catch (const std::exception &error) {
        std::cerr << "ERROR: " << error.what() << '\n';
        if (device) cudaFree(device);
        if (pinned) cudaFreeHost(pinned);
        std::free(pageable);
        return EXIT_FAILURE;
    }
}
