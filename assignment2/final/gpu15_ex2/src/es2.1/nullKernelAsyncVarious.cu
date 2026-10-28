/*
 *
 * nullKernelAsyncVarious.cu
 *
 * Microbenchmark for asynchronous and synchronous kernel launch times.
 *
 * Build with: nvcc -O2 -I ../../data/template/inc nullKernelAsyncVarious.cu
 * Requires: No minimum SM requirement.
 *
 * Copyright (c) 2011-2012, Archaea Software, LLC.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions 
 * are met: 
 *
 * 1. Redistributions of source code must retain the above copyright 
 *    notice, this list of conditions and the following disclaimer. 
 * 2. Redistributions in binary form must reproduce the above copyright 
 *    notice, this list of conditions and the following disclaimer in 
 *    the documentation and/or other materials provided with the 
 *    distribution. 
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS 
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT 
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS 
 * FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE 
 * COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, 
 * INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, 
 * BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER 
 * CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT 
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN 
 * ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
 * POSSIBILITY OF SUCH DAMAGE.
 *
 */

#include <stdio.h>

#include "chTimer.h"

__global__
void
NullKernel()
{
    // Empty kernel used to measure the overhead of launching a CUDA kernel.
}

int
main()
{
    const int iterations = 1000;

    const int blockValues[] = {
        1, 2, 4, 8, 16, 32, 64, 128,
        256, 512, 1024, 2048, 4096, 8192, 16384
    };
    const int threadValues[] = {
        1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024
    };

    // Determine based on the size of the arrays and the number
    // of elements in each array. 
    const int nBlocks = sizeof(blockValues) / sizeof(blockValues[0]);
    const int nThreads = sizeof(threadValues) / sizeof(threadValues[0]);
    
    for (int i = 0; i < nBlocks; ++i)
    {
        for (int j = 0; j < nThreads; ++j)
        {
            const int blocks = blockValues[i];
            const int threads = threadValues[j];

            // Warm up CUDA before measuring this configuration.
            NullKernel<<<blocks, threads>>>();
            cudaError_t error = cudaDeviceSynchronize();
            if (error != cudaSuccess) {
                fprintf(stderr, "CUDA error for %d blocks and %d threads: %s\n",
                        blocks, threads, cudaGetErrorString(error));
                return 1;
            }

            chTimerTimestamp start, stop;

            // Measure asynchronous launches with one final synchronization.
            chTimerGetTime(&start);

            for (int k = 0; k < iterations; ++k)
            {
                NullKernel<<<blocks, threads>>>();
            }

            error = cudaDeviceSynchronize();
            chTimerGetTime(&stop);

            if (error != cudaSuccess) {
                fprintf(stderr, "CUDA async error for %d blocks and %d threads: %s\n",
                        blocks, threads, cudaGetErrorString(error));
                return 1;
            }

            // Compute average time per kernel launch in seconds.
            const double asyncTime = chTimerElapsedTime(&start, &stop) / iterations;

            // Measure synchronous launches by waiting after every kernel.
            chTimerGetTime(&start);

            for (int k = 0; k < iterations; ++k)
            {
                NullKernel<<<blocks, threads>>>();
                error = cudaDeviceSynchronize();
                if (error != cudaSuccess) {
                    fprintf(stderr, "CUDA sync error for %d blocks and %d threads: %s\n",
                            blocks, threads, cudaGetErrorString(error));
                    return 1;
                }
            }

            chTimerGetTime(&stop);
            const double syncTime = chTimerElapsedTime(&start, &stop) / iterations;

            // Print blocks, threads, average async seconds, average sync seconds.
            printf("%d %d %.9f %.9f\n", blocks, threads, asyncTime, syncTime);
        }
    }

    return 0;
}
