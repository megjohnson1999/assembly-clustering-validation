#!/bin/bash

# Comprehensive MetaGrouper validation experiment
# Tests k-mer clustering against random grouping across 4 experimental conditions:
# 1. Individual assemblies (50 separate assemblies)
# 2. Random groupings (5 different seeds)
# 3. K-mer grouping (MetaGrouper clustering)
# 4. Global assembly (all 50 samples together)

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
echo "MetaGrouper Comprehensive Validation Experiment"
echo "================================================================"
echo "Start time: $(date)"
echo "Samples directory: $SAMPLES_DIR"
echo "Number of samples: $N_SAMPLES"
echo "Random seeds: ${SEEDS[@]}"
echo ""
echo "Experimental conditions:"
echo "  1. Individual assemblies (${N_SAMPLES} separate assemblies)"
echo "  2. Random groupings (${#SEEDS[@]} different seeds)"
echo "  3. K-mer clustering (1 MetaGrouper result)"
echo "  4. Global assembly (1 assembly with all samples)"
echo ""

# Function to check job status
check_job_status() {
    local job_id=$1
    local job_name=$2

    if [ -z "$job_id" ]; then
        echo "Error: No job ID provided for $job_name"
        return 1
    fi

    echo "Submitted $job_name (Job ID: $job_id)"

    # For array jobs, extract just the main job ID
    main_job_id=${job_id%_*}

    echo "Monitoring job $main_job_id..."

    while squeue -j $main_job_id > /dev/null 2>&1; do
        # Show progress for array jobs
        if [[ "$job_id" == *"["* ]]; then
            running=$(squeue -j $main_job_id | grep -c "RUNNING" || echo "0")
            pending=$(squeue -j $main_job_id | grep -c "PENDING" || echo "0")
            echo "  Array job status: $running running, $pending pending"
        fi
        sleep 60
    done

    # Check if job completed successfully
    if sacct -j $main_job_id --format=State --noheader --parsable2 | grep -q "COMPLETED"; then
        echo "✓ $job_name completed successfully"
        return 0
    else
        echo "✗ $job_name failed or was cancelled"
        echo "Check logs in: $LOGS_DIR/"

        # Show recent error logs
        echo "Recent error messages:"
        find $LOGS_DIR -name "*${main_job_id}*.err" -newer /tmp/job_start_time 2>/dev/null | head -3 | while read logfile; do
            echo "  From $logfile:"
            tail -5 "$logfile" 2>/dev/null | sed 's/^/    /'
        done

        return 1
    fi
}

# Create timestamp for log monitoring
touch /tmp/job_start_time

# Setup experiment directory
echo "Setting up experiment directory..."
mkdir -p $BASE_DIR/{results,scripts,logs,samples}
mkdir -p $RESULTS_DIR/{kmer_groups,random_groups,assemblies/{individual,kmer,random,global},comprehensive_analysis}

# Copy scripts
echo "Copying experiment scripts..."
cp *.py $SCRIPTS_DIR/
cp *.sh $SCRIPTS_DIR/
chmod +x $SCRIPTS_DIR/*.sh

cd $BASE_DIR

# Check MetaGrouper setup
echo ""
echo "Checking MetaGrouper setup..."
if [ ! -d "setup/metaGrouper" ]; then
    echo "ERROR: MetaGrouper not found. Please run setup first:"
    echo "1. bash ../setup_experiment.sh"
    echo "2. Copy/clone MetaGrouper to setup/metaGrouper/"
    exit 1
else
    echo "✓ MetaGrouper found"
fi

# Load environment
source /ref/sahlab/software/miniforge3/bin/activate
conda activate metagrouper_env

# Step 1: Select samples
echo ""
echo "Step 1: Selecting $N_SAMPLES random samples..."

python scripts/select_samples.py \
    --input $SAMPLES_DIR \
    --output samples/subset_50 \
    --n-samples $N_SAMPLES \
    --seed 42

echo "✓ Sample selection complete"

# Step 2: Run MetaGrouper for k-mer clustering
echo ""
echo "Step 2: Running MetaGrouper k-mer analysis..."

METAGROUPER_JOB=$(sbatch --parsable scripts/run_metagrouper.sh)
check_job_status $METAGROUPER_JOB "MetaGrouper k-mer analysis" || exit 1

# Step 3: Generate multiple random groupings
echo ""
echo "Step 3: Generating ${#SEEDS[@]} random groupings with different seeds..."

python scripts/create_random_groups.py \
    --kmer-results results/kmer_groups/assembly_recommendations.json \
    --output results/random_groups \
    --seeds ${SEEDS[@]}

echo "✓ Random groupings generated"

# Step 4: Generate assembly commands for all conditions
echo ""
echo "Step 4: Generating assembly commands for all experimental conditions..."

python scripts/generate_all_assembly_commands.py \
    --samples-dir samples/subset_50 \
    --kmer-groups results/kmer_groups/assembly_recommendations.json \
    --random-groups-dir results/random_groups \
    --output-dir results/assemblies \
    --scripts-dir scripts

echo "✓ Assembly scripts generated for all conditions"

# Step 5: Submit assembly jobs
echo ""
echo "Step 5: Submitting assembly jobs..."

# Submit all assembly jobs
INDIVIDUAL_JOB=$(sbatch --parsable scripts/run_individual_assemblies.sh)
KMER_JOB=$(sbatch --parsable scripts/run_kmer_assemblies.sh)
RANDOM_JOB=$(sbatch --parsable scripts/run_random_assemblies.sh)
GLOBAL_JOB=$(sbatch --parsable scripts/run_global_assemblies.sh)

echo "Assembly jobs submitted:"
echo "  Individual: $INDIVIDUAL_JOB"
echo "  K-mer: $KMER_JOB"
echo "  Random: $RANDOM_JOB"
echo "  Global: $GLOBAL_JOB"

# Wait for all assembly jobs to complete
echo ""
echo "Waiting for all assembly jobs to complete..."
echo "This may take 1-2 days depending on cluster load..."

check_job_status $INDIVIDUAL_JOB "Individual assemblies" || echo "Warning: Individual assemblies failed"
check_job_status $KMER_JOB "K-mer assemblies" || echo "Warning: K-mer assemblies failed"
check_job_status $RANDOM_JOB "Random assemblies" || echo "Warning: Random assemblies failed"
check_job_status $GLOBAL_JOB "Global assembly" || echo "Warning: Global assembly failed"

# Step 6: Comprehensive quality assessment
echo ""
echo "Step 6: Running comprehensive assembly quality assessment..."

python scripts/assess_all_conditions.py \
    --assemblies-dir results/assemblies \
    --output-dir results/comprehensive_analysis

echo ""
echo "================================================================"
echo "COMPREHENSIVE EXPERIMENT COMPLETE!"
echo "================================================================"
echo "End time: $(date)"
echo ""

# Display key results
if [ -f "results/comprehensive_analysis/comprehensive_analysis_report.txt" ]; then
    echo "KEY FINDINGS:"
    echo "============"

    # Extract the main recommendation
    grep -A 5 "RECOMMENDATION:" results/comprehensive_analysis/comprehensive_analysis_report.txt || echo "Report parsing failed"

    echo ""
    echo "EXPERIMENTAL SUMMARY:"
    grep -E "(Individual assemblies|Random assemblies|K-mer assemblies|Global assemblies)" results/comprehensive_analysis/comprehensive_analysis_report.txt || echo "Summary not found"

else
    echo "ERROR: Analysis report not found!"
    echo "Check for errors in the quality assessment step."
fi

echo ""
echo "FULL RESULTS AVAILABLE IN:"
echo "=========================="
echo "📋 Main report: results/comprehensive_analysis/comprehensive_analysis_report.txt"
echo "📊 Detailed data: results/comprehensive_analysis/detailed_assembly_statistics.csv"
echo "📁 All assemblies: results/assemblies/"
echo "📜 All logs: logs/"

echo ""
echo "WHAT THIS TELLS YOU:"
echo "==================="
echo "This experiment definitively answers whether MetaGrouper's k-mer clustering"
echo "approach is fundamentally sound by comparing it against:"
echo "• Random chance (5 different random groupings)"
echo "• Individual assembly baseline"
echo "• Maximum cooperation (global assembly)"
echo ""

# Decision guidance
if grep -q "STRONGLY PROMISING\\|PROMISING" results/comprehensive_analysis/comprehensive_analysis_report.txt 2>/dev/null; then
    echo "🎉 NEXT STEPS: Results look promising!"
    echo "   Consider scaling to 200+ samples and testing different parameters"
elif grep -q "MIXED" results/comprehensive_analysis/comprehensive_analysis_report.txt 2>/dev/null; then
    echo "⚠️  NEXT STEPS: Mixed results"
    echo "   Consider larger sample size or method refinements before major investment"
else
    echo "❌ NEXT STEPS: Results suggest k-mer clustering is not effective"
    echo "   Consider alternative approaches rather than investing more in this method"
fi

echo ""
echo "Total experiment time: $(date)"
echo "Workspace: $(pwd)"
echo "================================================================"