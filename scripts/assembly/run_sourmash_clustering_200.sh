#!/bin/bash
#SBATCH --job-name=sourmash_200samples
#SBATCH --time=2:00:00
#SBATCH --mem=32G
#SBATCH --cpus-per-task=8
#SBATCH --output=logs/sourmash_200_%j.out
#SBATCH --error=logs/sourmash_200_%j.err
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=megan.j@wustl.edu

echo "Starting Sourmash K-mer Clustering (200 samples): $(date)"
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURM_NODELIST"

# Load conda environment
source /ref/sahlab/software/miniforge3/bin/activate
conda activate metagrouper_env

# Verify environment
echo "Python version: $(python --version)"
echo "Working directory: $(pwd)"
echo "Sourmash version: $(sourmash --version)"

# Check if samples exist
if [ ! -d "samples/subset_200" ] || [ -z "$(ls -A samples/subset_200)" ]; then
    echo "ERROR: No samples found in samples/subset_200. Run select_samples.py first."
    exit 1
fi

# Count samples
n_samples=$(ls samples/subset_200/*_rrna_removed_R1.fastq 2>/dev/null | wc -l)
echo "Processing $n_samples samples with Sourmash"

if [ "$n_samples" -eq 0 ]; then
    echo "ERROR: No _rrna_removed_R1.fastq files found in samples/subset_200/"
    echo "Expected naming pattern: {sample_id}_rrna_removed_R{1,2}.fastq"
    exit 1
fi

if [ "$n_samples" -lt 180 ]; then
    echo "WARNING: Expected ~200 samples, found $n_samples"
    echo "Proceeding anyway..."
fi

# Create output directory
mkdir -p results/kmer_groups_200

# Run Sourmash clustering
echo ""
echo "🧬 Starting SOURMASH k-mer clustering (200 samples)..."
echo "  Tool: Sourmash (optimized MinHash implementation)"
echo "  Sample count: $n_samples"
echo "  K-mer size: 21"
echo "  Scaled: 1000 (sketch compression)"
echo "  Similarity threshold: 0.1 (permissive)"
echo "  Expected runtime: ~45-60 minutes"
echo "  Memory usage: Moderate (200 sketches + similarity matrix)"
echo ""

python scripts/utils/sourmash_clustering.py \
    samples/subset_200 \
    --output results/kmer_groups_200 \
    --similarity-threshold 0.1 \
    --min-group-size 2 \
    --max-group-size 8 \
    --ksize 21 \
    --scaled 1000

echo "Sourmash clustering completed: $(date)"

# Check outputs
if [ -f "results/kmer_groups_200/assembly_recommendations.json" ]; then
    echo "✅ K-mer groupings generated successfully with SOURMASH (200 samples)"

    # Show summary
    echo ""
    echo "=== SOURMASH CLUSTERING RESULTS (200 SAMPLES) ==="
    if [ -f "results/kmer_groups_200/clustering_summary.txt" ]; then
        cat results/kmer_groups_200/clustering_summary.txt
    fi

    echo ""
    echo "Group summary from assembly recommendations:"
    python -c "
import json
with open('results/kmer_groups_200/assembly_recommendations.json') as f:
    data = json.load(f)
    print(f\"  Tool: {data.get('tool', 'unknown')}\")
    print(f\"  Strategy: {data.get('strategy', 'unknown')}\")
    print(f\"  Total samples: {data['summary']['total_samples']}\")
    print(f\"  Valid groups: {data['summary']['total_groups']}\")
    print(f\"  Grouped samples: {data['summary']['grouped_samples']}\")
    print(f\"  Individual samples: {data['summary']['individual_samples']}\")

    if data['summary']['total_groups'] > 0:
        print(f\"  SUCCESS: Found clusters for validation experiment!\")
    else:
        print(f\"  No clusters found even with 200 samples - genuinely diverse dataset\")
"

    echo ""
    echo "✅ SUCCESS: 200-sample clustering completed!"
    echo "Runtime: ~$(printf '%02d:%02d' $((SECONDS/60)) $((SECONDS%60)))"
    echo ""

    if [ -f "results/kmer_groups_200/assembly_recommendations.json" ]; then
        groups=$(python -c "import json; data=json.load(open('results/kmer_groups_200/assembly_recommendations.json')); print(data['summary']['total_groups'])")
        if [ "$groups" -gt 0 ]; then
            echo "🎉 CLUSTERS FOUND! Ready for validation experiment:"
            echo "   python scripts/utils/create_random_groups.py --kmer-results results/kmer_groups_200/assembly_recommendations.json --output results/random_groups_200"
        else
            echo "📊 NO CLUSTERS: Strong evidence that viral samples are too diverse for k-mer clustering"
            echo "   This is still valuable scientific data!"
        fi
    fi

else
    echo "❌ ERROR: Sourmash clustering failed - no output file found"
    echo ""
    echo "Checking for common issues..."
    echo "Sourmash version: $(sourmash --version 2>/dev/null || echo 'NOT FOUND')"
    echo "Check logs for details: logs/sourmash_200_*.err"
    exit 1
fi