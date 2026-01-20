#!/bin/bash
#SBATCH --job-name=seqkit_stats
#SBATCH --time=0:30:00
#SBATCH --mem=4G
#SBATCH --cpus-per-task=1
#SBATCH --output=logs/seqkit_stats_%j.out
#SBATCH --error=logs/seqkit_stats_%j.err
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=megan.j@wustl.edu

# Load conda environment with seqkit
source /ref/sahlab/software/miniforge3/bin/activate
conda activate snakemake_tutorial

# Create output directories
mkdir -p logs
mkdir -p results/analysis

echo "Running seqkit stats on all 5 assemblies"
echo "Job ID: $SLURM_JOB_ID"
echo "Start time: $(date)"

# Define assembly paths (using absolute paths)
BASE_DIR="/ref/sahlab/megan.j/metagrouper_validation"
ASSEMBLIES=(
    "${BASE_DIR}/results/focused_assemblies/stage3_flye/focused_strategies_individual/flye_assembly/assembly.fasta"
    "${BASE_DIR}/results/focused_assemblies/stage3_flye/focused_strategies_groups_size_5/flye_assembly/assembly.fasta"
    "${BASE_DIR}/results/focused_assemblies/stage3_flye/focused_strategies_groups_size_12/flye_assembly/assembly.fasta"
    "${BASE_DIR}/results/focused_assemblies/stage3_flye/focused_strategies_groups_size_25/flye_assembly/assembly.fasta"
    "${BASE_DIR}/results/focused_assemblies/stage3_flye/focused_strategies_global/flye_assembly/assembly.fasta"
)

# Output file
OUTPUT="${BASE_DIR}/results/analysis/basic_metrics.tsv"

# Run seqkit stats with header on all assemblies
echo "Running seqkit stats..."
seqkit stats -a -T "${ASSEMBLIES[@]}" > "$OUTPUT"

echo "Results written to: $OUTPUT"
echo ""
echo "Preview of results:"
cat "$OUTPUT"

echo ""
echo "End time: $(date)"
echo "seqkit stats completed"
