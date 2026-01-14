#!/bin/bash

# Staged MetaGrouper validation experiment
# Follows hecatomb workflow to generate 8 final meta-assemblies:
# 1. Individual meta-assembly (MEGAHIT → concat → Flye)
# 2. Random meta-assemblies × 5 (MEGAHIT → concat → Flye each)
# 3. K-mer meta-assembly (MEGAHIT → concat → Flye)
# 4. Global assembly (MEGAHIT only)

set -e  # Exit on any error

# Configuration
SAMPLES_DIR="/lts/sahlab/data4/megan/RC2_rrna_removed_reads"
N_SAMPLES=50  # Start with 50 samples
SEEDS=(42 43 44 45 46)  # 5 random seeds for robust comparison

# Experiment directory structure
BASE_DIR="metagrouper_validation"
RESULTS_DIR="$BASE_DIR/results"
SCRIPTS_DIR="$BASE_DIR/scripts"
LOGS_DIR="$BASE_DIR/logs"

echo "================================================================"
echo "Assembly Clustering Validation: Staged Experiment"
echo "================================================================"
echo "Start time: $(date)"
echo "Samples directory: $SAMPLES_DIR"
echo "Number of samples: $N_SAMPLES"
echo "Random seeds: ${SEEDS[@]}"
echo ""
echo "Final outputs: 8 meta-assemblies"
echo "  1 × Individual meta-assembly"
echo "  5 × Random meta-assemblies"
echo "  1 × K-mer meta-assembly"
echo "  1 × Global assembly"
echo ""

# Function to check job status and wait for completion
check_job_status() {
    local job_id=$1
    local job_name=$2

    if [ -z "$job_id" ]; then
        echo "Error: No job ID provided for $job_name"
        return 1
    fi

    echo "Submitted $job_name (Job ID: $job_id)"

    # Extract main job ID for array jobs
    main_job_id=${job_id%_*}

    while squeue -j $main_job_id > /dev/null 2>&1; do
        # Show progress for array jobs
        if squeue -j $main_job_id | grep -q "\\["; then
            running=$(squeue -j $main_job_id -t RUNNING | wc -l)
            pending=$(squeue -j $main_job_id -t PENDING | wc -l)
            echo "  Array job status: $((running-1)) running, $((pending-1)) pending"
        fi
        sleep 60
    done

    # Check if jobs completed successfully
    failed_jobs=$(sacct -j $main_job_id --format=State --noheader --parsable2 | grep -v "COMPLETED\\|RUNNING\\|PENDING" | wc -l)
    completed_jobs=$(sacct -j $main_job_id --format=State --noheader --parsable2 | grep -c "COMPLETED" || echo "0")

    if [ "$failed_jobs" -gt 0 ]; then
        echo "✗ $job_name: $failed_jobs jobs failed"
        echo "Check logs in: $LOGS_DIR/"
        return 1
    else
        echo "✓ $job_name completed successfully ($completed_jobs jobs)"
        return 0
    fi
}

# Create timestamp for monitoring
touch /tmp/experiment_start_time

# Setup experiment directory
echo "Setting up experiment directory..."
mkdir -p $BASE_DIR/{results,scripts,logs,samples}
mkdir -p $RESULTS_DIR/{kmer_groups,random_groups,assemblies,final_analysis}

# Copy scripts
echo "Copying experiment scripts..."
cp scripts/assembly/*.py $SCRIPTS_DIR/
cp scripts/analysis/*.py $SCRIPTS_DIR/
cp scripts/utils/*.py $SCRIPTS_DIR/
chmod +x $SCRIPTS_DIR/*.py

cd $BASE_DIR

# Check MetaGrouper setup
echo ""
echo "Checking MetaGrouper setup..."
if [ ! -d "setup/metaGrouper" ]; then
    echo "ERROR: MetaGrouper not found at setup/metaGrouper/"
    echo "Please copy MetaGrouper to this location:"
    echo "  scp -r /path/to/metaGrouper setup/"
    exit 1
else
    echo "✓ MetaGrouper found"
fi

# Load environment
source /ref/sahlab/software/miniforge3/bin/activate
conda activate coassembly_env

# Verify tools are available
echo "Checking assembly tools..."
megahit --version > /dev/null 2>&1 && echo "✓ MEGAHIT available" || { echo "✗ MEGAHIT not found"; exit 1; }
flye --version > /dev/null 2>&1 && echo "✓ Flye available" || { echo "✗ Flye not found"; exit 1; }

# Step 1: Select samples (same as before)
echo ""
echo "Step 1: Selecting $N_SAMPLES random samples..."

python scripts/select_samples.py \
    --input $SAMPLES_DIR \
    --output samples/subset_50 \
    --n-samples $N_SAMPLES \
    --seed 42

echo "✓ Sample selection complete"

# Step 2: Run MetaGrouper for k-mer clustering (same as before)
echo ""
echo "Step 2: Running MetaGrouper k-mer analysis..."

METAGROUPER_JOB=$(sbatch --parsable scripts/assembly/run_metagrouper.sh)
check_job_status $METAGROUPER_JOB "MetaGrouper k-mer analysis" || exit 1

# Step 3: Generate multiple random groupings (same as before)
echo ""
echo "Step 3: Generating ${#SEEDS[@]} random groupings..."

python scripts/create_random_groups.py \
    --kmer-results results/kmer_groups/assembly_recommendations.json \
    --output results/random_groups \
    --seeds ${SEEDS[@]}

echo "✓ Random groupings generated"

# Step 4: Generate staged assembly commands
echo ""
echo "Step 4: Generating staged assembly commands..."

python scripts/generate_staged_assembly_commands.py \
    --samples-dir samples/subset_50 \
    --kmer-groups results/kmer_groups/assembly_recommendations.json \
    --random-groups-dir results/random_groups \
    --output-dir results/assemblies \
    --scripts-dir scripts

echo "✓ Staged assembly scripts generated"

# Step 5: Run MEGAHIT assemblies (Stage 1)
echo ""
echo "Step 5: Running MEGAHIT assemblies (Stage 1)..."
echo "This stage runs all MEGAHIT jobs in parallel..."

# Submit all MEGAHIT jobs simultaneously
INDIVIDUAL_JOB=$(sbatch --parsable scripts/run_megahit_individual.sh 2>/dev/null || echo "")
GROUPED_JOB=$(sbatch --parsable scripts/run_megahit_grouped.sh 2>/dev/null || echo "")
GLOBAL_JOB=$(sbatch --parsable scripts/run_megahit_global.sh 2>/dev/null || echo "")

echo "MEGAHIT jobs submitted:"
[ -n "$INDIVIDUAL_JOB" ] && echo "  Individual: $INDIVIDUAL_JOB"
[ -n "$GROUPED_JOB" ] && echo "  Grouped (k-mer + random): $GROUPED_JOB"
[ -n "$GLOBAL_JOB" ] && echo "  Global: $GLOBAL_JOB"

# Wait for all MEGAHIT jobs to complete
echo ""
echo "Waiting for all MEGAHIT assemblies to complete..."

megahit_success=true
[ -n "$INDIVIDUAL_JOB" ] && { check_job_status $INDIVIDUAL_JOB "Individual MEGAHIT assemblies" || megahit_success=false; }
[ -n "$GROUPED_JOB" ] && { check_job_status $GROUPED_JOB "Grouped MEGAHIT assemblies" || megahit_success=false; }
[ -n "$GLOBAL_JOB" ] && { check_job_status $GLOBAL_JOB "Global MEGAHIT assembly" || megahit_success=false; }

if [ "$megahit_success" = false ]; then
    echo "ERROR: Some MEGAHIT assemblies failed. Check logs before proceeding."
    exit 1
fi

echo "✓ All MEGAHIT assemblies completed successfully"

# Step 6: Run concatenation (Stage 2)
echo ""
echo "Step 6: Concatenating assemblies by condition (Stage 2)..."

if [ -f "scripts/run_concatenate.sh" ]; then
    CONCAT_JOB=$(sbatch --parsable scripts/run_concatenate.sh)
    check_job_status $CONCAT_JOB "Assembly concatenation" || exit 1
    echo "✓ Assembly concatenation completed"
else
    echo "Warning: Concatenation script not found, skipping..."
fi

# Step 7: Run Flye meta-assembly (Stage 3)
echo ""
echo "Step 7: Running Flye meta-assemblies (Stage 3)..."

if [ -f "scripts/run_flye_meta.sh" ]; then
    FLYE_JOB=$(sbatch --parsable scripts/run_flye_meta.sh)
    check_job_status $FLYE_JOB "Flye meta-assembly" || exit 1
    echo "✓ Flye meta-assemblies completed"
else
    echo "Warning: Flye meta-assembly script not found, skipping..."
fi

# Copy global assembly to final location
if [ -f "results/assemblies/megahit_global/global_all_samples/global_assembly.contigs.fa" ]; then
    mkdir -p results/assemblies/final_assemblies
    cp results/assemblies/megahit_global/global_all_samples/global_assembly.contigs.fa \
       results/assemblies/final_assemblies/global_assembly.fasta
    echo "✓ Global assembly copied to final location"
fi

# Step 8: Final assembly quality assessment
echo ""
echo "Step 8: Assessing final assembly quality..."

python scripts/assess_final_assemblies.py \
    --assemblies-dir results/assemblies/final_assemblies \
    --output-dir results/final_analysis

echo ""
echo "================================================================"
echo "STAGED ASSEMBLY EXPERIMENT COMPLETE!"
echo "================================================================"
echo "End time: $(date)"
echo ""

# Show final assemblies
echo "Final assemblies generated:"
if [ -d "results/assemblies/final_assemblies" ]; then
    ls -lh results/assemblies/final_assemblies/ | grep -v "^total" | while read line; do
        echo "  $line"
    done
else
    echo "  ERROR: Final assemblies directory not found!"
fi

echo ""

# Display key results
if [ -f "results/final_analysis/final_assembly_comparison_report.txt" ]; then
    echo "KEY FINDINGS:"
    echo "============"

    # Extract the main recommendation
    grep -A 5 "RECOMMENDATION:" results/final_analysis/final_assembly_comparison_report.txt || echo "Report parsing failed"

    echo ""
    echo "QUICK SUMMARY:"
    grep -A 2 "QUICK SUMMARY:" results/final_analysis/final_assembly_comparison_report.txt || echo "Summary not found"

else
    echo "ERROR: Analysis report not found!"
    echo "Check for errors in the quality assessment step."
fi

echo ""
echo "FULL RESULTS AVAILABLE IN:"
echo "=========================="
echo "📋 Main report: results/final_analysis/final_assembly_comparison_report.txt"
echo "📊 Detailed data: results/final_analysis/final_assembly_statistics.csv"
echo "📁 Final assemblies: results/assemblies/final_assemblies/"
echo "📜 All logs: logs/"

echo ""
echo "WHAT THIS TELLS YOU:"
echo "==================="
echo "This experiment definitively answers whether k-mer clustering"
echo "produces better final meta-assemblies than random grouping."
echo ""
echo "The 8 final assemblies represent:"
echo "• Individual approach: All samples assembled separately, then meta-assembled"
echo "• Random approaches: 5 different random groupings, each meta-assembled"
echo "• K-mer approach: MetaGrouper grouping, then meta-assembled"
echo "• Global approach: All samples co-assembled together"
echo ""

# Decision guidance
if grep -q "STRONGLY PROMISING\\|PROMISING" results/final_analysis/final_assembly_comparison_report.txt 2>/dev/null; then
    echo "🎉 RESULT: K-mer clustering shows promise for meta-assembly!"
    echo "   Consider scaling up and testing different parameters."
elif grep -q "MIXED" results/final_analysis/final_assembly_comparison_report.txt 2>/dev/null; then
    echo "⚠️  RESULT: Mixed results - some promise but needs refinement."
    echo "   Consider parameter optimization before major investment."
else
    echo "❌ RESULT: K-mer clustering doesn't beat random grouping."
    echo "   Consider alternative approaches for metagenomic assembly."
fi

echo ""
echo "Total experiment time: $(date)"
echo "Workspace: $(pwd)"
echo "================================================================"