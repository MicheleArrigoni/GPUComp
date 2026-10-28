# GPU Computing - Exercise 2 - Group 15

Authors: Michele Arrigoni, Francesco Foresti, Kasra Ghasemipoo, Karol Bonat.
The group is willing to present Exercises 2.1, 2.2 and 2.3.

## Contents

- `report.pdf`: the single report for all exercises, compiled from LaTeX.
- `report.tex`: the LaTeX source of the report.
- `src/`, `inc/`, `Makefile`: CUDA sources, timer dependency and build recipe.
- `ex2_1.sh`, `ex2_2.sh`, `ex2_3.sh`: Slurm job scripts.
- `results/`: original execution logs, including the Slurm completion summaries.
- `waitKernel_results.txt`: all 76 break-even measurements; comma-separated columns `clocks,time_us,baseline_us,threshold_us`.
- `pcie_results.csv`: all 44 PCIe measurements with transfer times, bandwidths and repetitions.
- `figures/`: PNG and SVG graphs generated from the submitted data.

## Compile on the cluster

Load the course CUDA environment, then run from this directory:

```bash
make
```

Individual build targets: `make es2.1`, `make es2.2`, `make es2.3`.
Executables are created in `bin/`. `make clean` removes only these executables.
A CUDA toolkit supporting the GPU, a compatible host C++ compiler and GNU Make are required.
The compiler version used for the recorded jobs was not saved in the logs.

## Run with Slurm

Submit from this directory after compiling; do not run the GPU benchmarks directly on the head node:

```bash
sbatch ex2_1.sh
sbatch ex2_2.sh
sbatch ex2_3.sh
```

The scripts request the `exercise-gpu` partition, one GPU, two CPU cores, 8 GiB RAM and 20 minutes.
Each new job saves its output in `results/es2.X/<job-id>/`; Slurm logs are written in this directory.
The supplied measurements below were obtained using separate `srun` executions and are preserved at their original paths.

## Reproduce the submitted figures

Python 3 and Matplotlib are needed for plotting (`python3 -m pip install matplotlib` if not already available).
From this directory:

```bash
python3 src/es2.1/plotter.py results/es2.1/nullKernelAsyncVarious.txt figures
python3 src/es2.2/plotter.py waitKernel_results.txt figures
python3 src/es2.3/plot_pcie.py pcie_results.csv figures
```

For a newly submitted job, pass its data file as the first argument and the desired output directory as the second.
Plotting does not require a GPU. The PCIe Slurm script also generates a graph after the benchmark and needs Matplotlib available in its Python environment.

## Measurement provenance and units

| Data | Job | Description |
|---|---|---|
| `results/es2.1/nullKernelAsync.txt` | 279658 | Baseline comparison, 100000 launches per mode; printed means in us |
| `results/es2.1/nullKernelAsyncVarious.txt` | 279659 | 165 configurations; blocks, threads, async seconds, sync seconds |
| `results/es2.2/waitKernel.txt` and `waitKernel_results.txt` | 279660 | Debug log and 76 measured points; 100000 launches per point |
| `results/es2.3/pcie_benchmark.txt` and `pcie_results.csv` | 279661 | 44 PCIe measurements; CSV uses ms and decimal GB/s |

The PCIe program reports an NVIDIA GeForce RTX 2080 Ti. Per-job compiler versions and compute-node names are not included in these submitted logs.
The baseline program has no explicit initial warm-up; the configuration sweep and break-even search do warm up CUDA.
All figures and reported numerical conclusions use the files listed here, rather than older runs.

## Rebuild the report

The PDF is compiled from `report.tex`. From the submission directory, run:

```bash
tectonic report.tex
```

Alternatively, run `pdflatex report.tex` twice. Keep the `figures/` directory next to the source. No bibliography tool is required.
