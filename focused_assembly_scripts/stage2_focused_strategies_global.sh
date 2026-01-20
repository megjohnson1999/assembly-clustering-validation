#!/bin/bash
#SBATCH --job-name=stage2_focused_strategies_global
#SBATCH --time=0:30:00
#SBATCH --mem=8G
#SBATCH --cpus-per-task=2
#SBATCH --output=logs/stage2_focused_strategies_global_%j.out
#SBATCH --error=logs/stage2_focused_strategies_global_%j.err
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=megan.j@wustl.edu

# Load conda environment
source /ref/sahlab/software/miniforge3/bin/activate
conda activate coassembly_env

# Create output directories
mkdir -p logs

echo "Starting stage2 for strategy: focused_strategies_global"
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURM_NODELIST"
echo "Start time: $(date)"


# Command 1: concat_focused_strategies_global
echo 'Running: concat_focused_strategies_global'
cat results/focused_assemblies/stage1_megahit/focused_strategies_global/group_global_all_samples/megahit_assembly/final.contigs.fa > results/focused_assemblies/stage2_concat/focused_strategies_global/concatenated_contigs.fa
echo 'Completed: concat_focused_strategies_global'


echo "End time: $(date)"
echo "stage2 completed for strategy: focused_strategies_global"
