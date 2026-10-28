#!/bin/bash
#SBATCH --job-name=ex2-3
#SBATCH --partition=exercise-gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=00:20:00
#SBATCH --output=ex2-3-%j.out

set -euo pipefail
cd "$SLURM_SUBMIT_DIR"

echo "Job ID: ${SLURM_JOB_ID}"
echo "Node: $(hostname)"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader

template_dir="$PWD"
results_dir="$template_dir/results/es2.3/${SLURM_JOB_ID}"
mkdir -p "$results_dir"
cd "$results_dir"

"$template_dir/bin/pcie_benchmark" > pcie_output.txt
python3 "$template_dir/src/es2.3/plot_pcie.py" pcie_results.csv

echo "Results saved in $results_dir"
