#!/bin/bash
#SBATCH --job-name=checkv_analysis
#SBATCH --time=4:00:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=8
#SBATCH --array=1-5
#SBATCH --output=logs/checkv_%A_%a.out
#SBATCH --error=logs/checkv_%A_%a.err
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=megan.j@wustl.edu

# Load conda environment with CheckV
source /ref/sahlab/software/anaconda3/bin/activate
conda activate checkV

# Create output directories
mkdir -p logs

echo "Running CheckV analysis"
echo "Job ID: $SLURM_JOB_ID"
echo "Array Task ID: $SLURM_ARRAY_TASK_ID"
echo "Start time: $(date)"

# Define base directories (using absolute paths)
BASE_DIR="/scratch/sahlab/Megan/assembly-clustering-validation/metagrouper_validation"
CHECKV_DB="/ref/sahlab/data/viral_analysis_DBs/checkV_DB/checkv-db-v1.5"
OUTPUT_BASE="${BASE_DIR}/results/analysis/checkv"

# Map task ID to strategy name and assembly path
case $SLURM_ARRAY_TASK_ID in
    1)
        STRATEGY="individual"
        ;;
    2)
        STRATEGY="groups_size_5"
        ;;
    3)
        STRATEGY="groups_size_12"
        ;;
    4)
        STRATEGY="groups_size_25"
        ;;
    5)
        STRATEGY="global"
        ;;
esac

ASSEMBLY="${BASE_DIR}/results/focused_assemblies/stage3_flye/focused_strategies_${STRATEGY}/flye_assembly/assembly.fasta"
OUTPUT_DIR="${OUTPUT_BASE}/${STRATEGY}"

echo "Strategy: $STRATEGY"
echo "Input assembly: $ASSEMBLY"
echo "Output directory: $OUTPUT_DIR"

# Check if input file exists
if [ ! -f "$ASSEMBLY" ]; then
    echo "ERROR: Assembly file not found: $ASSEMBLY"
    echo "Skipping this strategy - assembly may not be complete yet"
    exit 0
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Run CheckV
echo "Running CheckV..."
checkv end_to_end "$ASSEMBLY" "$OUTPUT_DIR" -t 8 -d "$CHECKV_DB"

echo ""
echo "CheckV completed for strategy: $STRATEGY"
echo "Results in: $OUTPUT_DIR"
echo ""

# Show summary of results
if [ -f "${OUTPUT_DIR}/quality_summary.tsv" ]; then
    echo "Quality summary preview:"
    head -20 "${OUTPUT_DIR}/quality_summary.tsv"
fi

echo ""
echo "End time: $(date)"
