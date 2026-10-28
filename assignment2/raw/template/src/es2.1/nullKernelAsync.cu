/*
 *
 * nullKernelAsync.cu
 *
 * Microbenchmark for throughput of asynchronous kernel launch.
 *
 * Build with: nvcc -I ../chLib <options> nullKernelAsync.cu
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
    // Launch the empty kernel many times to obtain a stable average.
    const int cIterations = 100000;
    printf( "Measuring asynchronous launch time... " ); fflush( stdout );

    chTimerTimestamp start, stop;

    // Start timing immediately before the sequence of asynchronous launches.
    chTimerGetTime( &start );
    for ( int i = 0; i < cIterations; i++ ) {
        NullKernel<<<1,1>>>();
    }

    // Wait for all launches to finish before stopping the timer.
    cudaDeviceSynchronize();
    chTimerGetTime( &stop );

    {
        // Convert the total elapsed time to microseconds and compute the
        // average time required for a single kernel launch.
        double microseconds = 1e6*chTimerElapsedTime( &start, &stop );
        double usPerLaunch = microseconds / (float) cIterations;

        printf( "%.2f us\n", usPerLaunch );
    }

    printf("Measuring synchronous launch time... " ); fflush( stdout );

    chTimerGetTime(&start);

    for ( int i = 0; i < cIterations; i++ ) {
        NullKernel<<<1,1>>>();
        cudaDeviceSynchronize();
    }

    chTimerGetTime(&stop);

    double synchronousMicroseconds = 1e6*chTimerElapsedTime( &start, &stop );
    double synchronousUsPerLaunch = synchronousMicroseconds / (float) cIterations;

    printf( "%.2f us\n", synchronousUsPerLaunch );

    return 0;
}
