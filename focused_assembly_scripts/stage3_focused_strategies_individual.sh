#!/bin/bash
#SBATCH --job-name=stage3_focused_strategies_individual
#SBATCH --time=1-00:00:00
#SBATCH --mem=200G
#SBATCH --cpus-per-task=20
#SBATCH --output=logs/stage3_focused_strategies_individual_%j.out
#SBATCH --error=logs/stage3_focused_strategies_individual_%j.err
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=megan.j@wustl.edu

# Load conda environment
source /ref/sahlab/software/miniforge3/bin/activate
conda activate coassembly_env

# Create output directories
mkdir -p logs

echo "Starting stage3 for strategy: focused_strategies_individual"
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURM_NODELIST"
echo "Start time: $(date)"


# Command 1: flye_focused_strategies_individual
echo 'Running: flye_focused_strategies_individual'
flye \
    --meta \
    --asm-coverage 50 \
    --genome-size 100m \
    --out-dir results/focused_assemblies/stage3_flye/focused_strategies_individual/flye_assembly \
    --threads 20 \
    --iterations 3 \
    --contigs results/focused_assemblies/stage2_concat/focused_strategies_individual/concatenated_contigs.fa
echo 'Completed: flye_focused_strategies_individual'


echo "End time: $(date)"
echo "stage3 completed for strategy: focused_strategies_individual"
