#include <stdio.h>
#

#include "chTimer.h"

__device__ clock_t clock_difference;

__global__
void
WaitKernel(int num_clocks, bool write_clock)
{
    clock_t start = clock();
    while ( clock() - start < num_clocks ) {
        // do nothing   
    }

    // Conditionally store the elapsed cycles to prevent compiler optimizations.
    if (write_clock) {
        clock_t stop = clock();
        clock_difference = stop - start;
    }
}

int
main()
{
    const int max_iterations = 100000;

    // Save every measurement for plotting.
    FILE *results = fopen("waitKernel_results.txt", "w");
    if (results == NULL) {
        perror("Cannot open waitKernel_results.txt");
        return 1;
    }
    fprintf(results, "clocks,time_us,baseline_us,threshold_us\n");

    // initialize time variables
    chTimerTimestamp start, stop;
    fprintf(stderr, "[DEBUG] Avvio: %d lanci per prova, passo di 100 cicli.\n",
           max_iterations);
    // Warm up CUDA before measuring the baseline.
    for (int j = 0; j < max_iterations; j++) {
        WaitKernel<<<1,1>>>(0, true);
    }
    cudaDeviceSynchronize();

    fprintf(stderr, "[DEBUG] Inizio misura base.\n");

    // acquire start time
    chTimerGetTime(&start);
    for (int j = 0; j < max_iterations; j ++)
        {
            WaitKernel<<<1,1>>>(0, true);
        }
    cudaDeviceSynchronize();
    chTimerGetTime(&stop);

    double base_measure = chTimerElapsedTime(&start, &stop) / max_iterations;   
    double treshold = base_measure * 2;
    fprintf(results, "0,%.9f,%.9f,%.9f\n",
            base_measure * 1e6, base_measure * 1e6, treshold * 1e6);
    if (fflush(results) != 0 || ferror(results)) {
        perror("Cannot write waitKernel_results.txt");
        fclose(results);
        return 1;
    }
    fprintf(stderr, "[DEBUG] Base: totale=%.3f ms, media=%.3f us, soglia=%.3f us\n",
           chTimerElapsedTime(&start, &stop) * 1e3,
           base_measure * 1e6, treshold * 1e6);
    fprintf(stderr, "[DEBUG] Ricerca avviata: stampa le prime 10 prove, poi una ogni 100.\n");
    double last_measure = 0;
    int i = 0;

    while (last_measure < treshold)
    {
        i++;
        chTimerGetTime(&start);
        for (int j = 0; j < max_iterations; j ++)
        {
            WaitKernel<<<1,1>>>(i*100, true);
        }
        cudaDeviceSynchronize();
        chTimerGetTime(&stop);
        last_measure = chTimerElapsedTime(&start, &stop) / max_iterations;

        // File output is excluded from the measured time.
        fprintf(results, "%d,%.9f,%.9f,%.9f\n",
                i * 100, last_measure * 1e6, base_measure * 1e6, treshold * 1e6);
        if (fflush(results) != 0 || ferror(results)) {
            perror("Cannot write waitKernel_results.txt");
            fclose(results);
            return 1;
        }

        if (i <= 10 || i % 100 == 0 || last_measure >= treshold) {
            fprintf(stderr, "[DEBUG] Prova=%d, cicli=%d, media=%.3f us, soglia=%.3f us\n",
                    i, i * 100, last_measure * 1e6, treshold * 1e6);
        }
        
    }

    if (fclose(results) != 0) {
        perror("Cannot close waitKernel_results.txt");
        return 1;
    }

    printf("num clock -> %d\n", i*100);
    printf("Dati salvati in waitKernel_results.txt\n");

    return 0;
}
