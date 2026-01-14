#!/bin/bash

# Complete MetaGrouper validation experiment workflow
# Tests whether k-mer clustering beats random grouping for co-assembly

set -e  # Exit on any error

# Configuration
SAMPLES_DIR="/lts/sahlab/data4/megan/RC2_rrna_removed_reads"
N_SAMPLES=50  # Start with 50 samples
SEED=42

# Experiment directory structure
BASE_DIR="metagrouper_validation"
RESULTS_DIR="$BASE_DIR/results"
SCRIPTS_DIR="$BASE_DIR/scripts"
LOGS_DIR="$BASE_DIR/logs"

echo "================================================================"
echo "MetaGrouper vs Random Grouping Validation Experiment"
echo "================================================================"
echo "Start time: $(date)"
echo "Samples directory: $SAMPLES_DIR"
echo "Number of samples: $N_SAMPLES"
echo "Random seed: $SEED"
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
    echo "Waiting for $job_name to complete..."

    while squeue -j $job_id > /dev/null 2>&1; do
        sleep 30
    done

    # Check if job completed successfully
    if sacct -j $job_id --format=State --noheader --parsable2 | grep -q "COMPLETED"; then
        echo "✓ $job_name completed successfully"
        return 0
    else
        echo "✗ $job_name failed"
        echo "Check logs in: $LOGS_DIR/"
        return 1
    fi
}

# Setup experiment directory
echo "Setting up experiment directory..."
mkdir -p $BASE_DIR/{results,scripts,logs,samples}
mkdir -p $RESULTS_DIR/{kmer_groups,random_groups,assemblies/{kmer,random},metrics}

# Copy scripts
echo "Copying experiment scripts..."
cp *.py $SCRIPTS_DIR/
cp *.sh $SCRIPTS_DIR/
chmod +x $SCRIPTS_DIR/*.sh

cd $BASE_DIR

# Step 1: Setup MetaGrouper
echo ""
echo "Step 1: Setting up MetaGrouper..."
if [ ! -d "setup/metaGrouper" ]; then
    mkdir -p setup
    cd setup
    echo "Cloning MetaGrouper repository..."
    # You'll need to update this URL to the actual repository
    git clone https://github.com/yourusername/metaGrouper.git
    cd ..
else
    echo "✓ MetaGrouper already cloned"
fi

# Step 2: Select samples
echo ""
echo "Step 2: Selecting $N_SAMPLES random samples..."
source /ref/sahlab/software/miniforge3/bin/activate
conda activate metagrouper_env

python scripts/select_samples.py \
    --input $SAMPLES_DIR \
    --output samples/subset_50 \
    --n-samples $N_SAMPLES \
    --seed $SEED

echo "✓ Sample selection complete"

# Step 3: Run MetaGrouper for k-mer clustering
echo ""
echo "Step 3: Running MetaGrouper k-mer analysis..."

# Submit MetaGrouper job
METAGROUPER_JOB=$(sbatch --parsable scripts/run_metagrouper.sh)
check_job_status $METAGROUPER_JOB "MetaGrouper k-mer analysis" || exit 1

# Step 4: Generate random groupings
echo ""
echo "Step 4: Generating random groupings with same structure..."

python scripts/create_random_groups.py \
    --kmer-results results/kmer_groups/assembly_recommendations.json \
    --output results/random_groups \
    --seed $SEED

echo "✓ Random groupings generated"

# Step 5: Generate assembly commands
echo ""
echo "Step 5: Generating assembly commands..."

# K-mer grouping assemblies
python scripts/generate_assembly_commands.py \
    results/kmer_groups/assembly_recommendations.json \
    --samples-dir samples/subset_50 \
    --output-dir results/assemblies/kmer \
    --script-name scripts/run_kmer_assemblies.sh \
    --prefix kmer \
    --job-name kmer_assembly

# Random grouping assemblies
python scripts/generate_assembly_commands.py \
    results/random_groups/assembly_recommendations.json \
    --samples-dir samples/subset_50 \
    --output-dir results/assemblies/random \
    --script-name scripts/run_random_assemblies.sh \
    --prefix random \
    --job-name random_assembly

echo "✓ Assembly scripts generated"

# Step 6: Run assemblies
echo ""
echo "Step 6: Running assemblies..."

# Submit both assembly jobs
KMER_ASSEMBLY_JOB=$(sbatch --parsable scripts/run_kmer_assemblies.sh)
RANDOM_ASSEMBLY_JOB=$(sbatch --parsable scripts/run_random_assemblies.sh)

# Wait for both to complete
check_job_status $KMER_ASSEMBLY_JOB "K-mer assemblies" || exit 1
check_job_status $RANDOM_ASSEMBLY_JOB "Random assemblies" || exit 1

# Step 7: Quality assessment
echo ""
echo "Step 7: Comparing assembly quality..."

python scripts/assess_quality.py \
    --kmer-dir results/assemblies/kmer \
    --random-dir results/assemblies/random \
    --output-dir results/metrics

echo ""
echo "================================================================"
echo "EXPERIMENT COMPLETE!"
echo "================================================================"
echo "End time: $(date)"
echo ""

# Display results
echo "QUICK RESULTS:"
if [ -f "results/metrics/comparison_summary.txt" ]; then
    echo ""
    tail -20 results/metrics/comparison_summary.txt
else
    echo "Error: Results file not found"
fi

echo ""
echo "NEXT STEPS:"
echo "1. Review full results: cat results/metrics/comparison_summary.txt"
echo "2. Check detailed stats: results/metrics/detailed_assembly_stats.csv"
echo ""

# Recommend scaling decision
if grep -q "PROMISING" results/metrics/comparison_summary.txt 2>/dev/null; then
    echo "🎉 K-mer clustering shows promise! Consider scaling to 200+ samples."
elif grep -q "MIXED" results/metrics/comparison_summary.txt 2>/dev/null; then
    echo "⚠️  Mixed results. Consider testing with more samples or refining approach."
else
    echo "❌ K-mer clustering doesn't beat random. Consider alternative approaches."
fi

echo ""
echo "Experiment workspace: $(pwd)"
echo "================================================================"