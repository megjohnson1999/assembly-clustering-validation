#!/bin/bash
#SBATCH --job-name=sourmash_clustering
#SBATCH --time=1:00:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=4
#SBATCH --output=logs/sourmash_%j.out
#SBATCH --error=logs/sourmash_%j.err
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=megan.j@wustl.edu

echo "Starting Sourmash K-mer Clustering: $(date)"
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURM_NODELIST"

# Load conda environment
source /ref/sahlab/software/miniforge3/bin/activate
conda activate metagrouper_env

# Verify environment
echo "Python version: $(python --version)"
echo "Working directory: $(pwd)"

# Verify sourmash is available
echo "Sourmash version: $(sourmash --version)"

# Check if samples exist
if [ ! -d "samples/subset_50" ] || [ -z "$(ls -A samples/subset_50)" ]; then
    echo "ERROR: No samples found in samples/subset_50. Run select_samples.py first."
    exit 1
fi

# Count samples
n_samples=$(ls samples/subset_50/*_R1.fastq 2>/dev/null | wc -l)
echo "Processing $n_samples samples with Sourmash"

if [ "$n_samples" -eq 0 ]; then
    echo "ERROR: No R1 fastq files found in samples/subset_50/"
    exit 1
fi

# Create output directory
mkdir -p results/kmer_groups

# Run Sourmash clustering
echo ""
echo "🧬 Starting SOURMASH k-mer clustering..."
echo "  Tool: Sourmash (optimized MinHash implementation)"
echo "  K-mer size: 21"
echo "  Scaled: 1000 (sketch compression)"
echo "  Expected runtime: ~15-30 minutes"
echo "  Memory usage: Low (sketches only)"
echo ""

python scripts/utils/sourmash_clustering.py \
    samples/subset_50 \
    --output results/kmer_groups \
    --similarity-threshold 0.3 \
    --min-group-size 2 \
    --max-group-size 5 \
    --ksize 21 \
    --scaled 1000

echo "Sourmash clustering completed: $(date)"

# Check outputs
if [ -f "results/kmer_groups/assembly_recommendations.json" ]; then
    echo "✅ K-mer groupings generated successfully with SOURMASH"

    # Show summary
    echo ""
    echo "=== SOURMASH CLUSTERING RESULTS ==="
    if [ -f "results/kmer_groups/clustering_summary.txt" ]; then
        cat results/kmer_groups/clustering_summary.txt
    fi

    echo ""
    echo "Group summary from assembly recommendations:"
    python -c "
import json
with open('results/kmer_groups/assembly_recommendations.json') as f:
    data = json.load(f)
    print(f\"  Tool: {data.get('tool', 'unknown')}\")
    print(f\"  Strategy: {data.get('strategy', 'unknown')}\")
    print(f\"  Total samples: {data['summary']['total_samples']}\")
    print(f\"  Valid groups: {data['summary']['total_groups']}\")
    print(f\"  Grouped samples: {data['summary']['grouped_samples']}\")
    print(f\"  Individual samples: {data['summary']['individual_samples']}\")
"

    echo ""
    echo "✅ SUCCESS: Sourmash clustering completed in ~$(printf '%02d:%02d' $((SECONDS/60)) $((SECONDS%60)))!"
    echo "🚀 MASSIVE SPEEDUP: Minutes instead of hours!"
    echo ""
    echo "Next step: Generate random groupings"
    echo "python scripts/utils/create_random_groups.py --kmer-results results/kmer_groups/assembly_recommendations.json"

else
    echo "❌ ERROR: Sourmash clustering failed - no output file found"
    echo ""
    echo "Checking for common issues..."

    # Check for dependency issues
    echo "Sourmash version: $(sourmash --version 2>/dev/null || echo 'NOT FOUND')"

    # Check for input issues
    if [ ! -f "scripts/utils/sourmash_clustering.py" ]; then
        echo "SCRIPT ERROR: sourmash_clustering.py not found"
        echo "Ensure scripts are copied to workspace"
    fi

    echo "Check logs for details: logs/sourmash_*.err"
    exit 1
fi