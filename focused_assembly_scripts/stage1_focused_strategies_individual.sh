#!/bin/bash
#SBATCH --job-name=stage1_focused_strategies_individual
#SBATCH --time=4:00:00
#SBATCH --mem=32G
#SBATCH --cpus-per-task=8
#SBATCH --array=1-200
#SBATCH --output=logs/stage1_focused_strategies_individual_%j.out
#SBATCH --error=logs/stage1_focused_strategies_individual_%j.err
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=megan.j@wustl.edu

# Load conda environment
source /ref/sahlab/software/miniforge3/bin/activate
conda activate coassembly_env

# Create output directories
mkdir -p logs

echo "Starting stage1 for strategy: focused_strategies_individual"
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURM_NODELIST"
echo "Start time: $(date)"


# Array job: process sample based on SLURM_ARRAY_TASK_ID
echo "Processing array task: $SLURM_ARRAY_TASK_ID"

# Read sample info from list file (using absolute path)
SAMPLE_INFO=$(sed -n "${SLURM_ARRAY_TASK_ID}p" /Users/Megan Johnson/Projects/metaGrouper/assembly-clustering-validation/results/focused_assemblies/stage1_megahit/focused_strategies_individual/sample_list.txt)
SAMPLE_ID=$(echo "$SAMPLE_INFO" | cut -f1)
R1_FILE=$(echo "$SAMPLE_INFO" | cut -f2)
R2_FILE=$(echo "$SAMPLE_INFO" | cut -f3)

echo "Sample: $SAMPLE_ID"
echo "R1: $R1_FILE"
echo "R2: $R2_FILE"

# Create sample-specific output directory (using absolute path)
SAMPLE_OUTPUT="/Users/Megan Johnson/Projects/metaGrouper/assembly-clustering-validation/results/focused_assemblies/stage1_megahit/focused_strategies_individual/individual_${SAMPLE_ID}"
mkdir -p "$SAMPLE_OUTPUT"

# Run MEGAHIT for this sample
echo "Running MEGAHIT for sample: $SAMPLE_ID"
megahit \
    -1 "$R1_FILE" \
    -2 "$R2_FILE" \
    -o "$SAMPLE_OUTPUT" \
    --min-contig-len 500 \
    --k-list 45,65,85,105,125,145,165,185,205,225 \
    --min-count 2 \
    -t 8 \
    --memory 34359738368

echo "MEGAHIT completed for sample: $SAMPLE_ID"

echo "End time: $(date)"
echo "stage1 completed for strategy: focused_strategies_individual"
