#!/bin/bash
#SBATCH --job-name=ex2-1
#SBATCH --partition=exercise-gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=00:20:00
#SBATCH --output=ex2-1-%j.out

set -euo pipefail
cd "$SLURM_SUBMIT_DIR"

echo "Job ID: ${SLURM_JOB_ID}"
echo "Node: $(hostname)"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader

template_dir="$PWD"
results_dir="$template_dir/results/es2.1/${SLURM_JOB_ID}"
mkdir -p "$results_dir"
cd "$results_dir"

# Save the configuration sweep before running the longer baseline comparison.
"$template_dir/bin/nullKernelAsyncVarious" > results.txt
"$template_dir/bin/nullKernelAsync" > baseline.txt

echo "Results saved in $results_dir"
