#!/bin/bash
#SBATCH --job-name=metagrouper_kmer
#SBATCH --time=6:00:00
#SBATCH --mem=64G
#SBATCH --cpus-per-task=16
#SBATCH --output=logs/metagrouper_%j.out
#SBATCH --error=logs/metagrouper_%j.err
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=megan.j@wustl.edu

echo "Starting MetaGrouper analysis: $(date)"
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURM_NODELIST"

# Load conda environment
source /ref/sahlab/software/miniforge3/bin/activate
conda activate metagrouper_env

# Verify environment
echo "Python version: $(python --version)"
echo "Working directory: $(pwd)"

# Check if MetaGrouper is available, if not copy from parent directory
if [ ! -d "setup/metaGrouper" ]; then
    echo "MetaGrouper not found in setup/, copying from parent directory..."
    mkdir -p setup
    cp -r ../metagrouper_package setup/metaGrouper
    cp ../metagrouper.py setup/metaGrouper/
    chmod +x setup/metaGrouper/metagrouper.py
    echo "✓ MetaGrouper copied successfully"
fi

# Check if samples exist
if [ ! -d "samples/subset_50" ] || [ -z "$(ls -A samples/subset_50)" ]; then
    echo "ERROR: No samples found in samples/subset_50. Run select_samples.py first."
    exit 1
fi

# Count samples
n_samples=$(ls samples/subset_50/*_R1.fastq | wc -l)
echo "Processing $n_samples samples"

# Run MetaGrouper with memory-efficient sketching
echo "Starting MetaGrouper k-mer analysis (SCIENTIFICALLY VALID)..."
echo "  Using sketching: YES (99% memory reduction)"
echo "  Sketch size: 1000 (most frequent k-mers per sample)"
echo "  Sampling method: frequency (MetaGrouper's intended approach)"
echo "  Processing: Full samples (maintains biological signal)"
echo "  Expected runtime: ~4 hours for 25 samples"
cd setup/metaGrouper

python metagrouper.py \
    ../../samples/subset_50 \
    --output ../../results/kmer_groups \
    --assembly-tools megahit \
    --similarity-threshold 0.3 \
    --min-group-size 2 \
    --max-group-size 5 \
    --processes 16 \
    --use-sketching \
    --sketch-size 1000 \
    --sampling-method frequency \
    --verbose

echo "MetaGrouper completed: $(date)"

# Check outputs
cd ../../results/kmer_groups
if [ -f "assembly_recommendations.json" ]; then
    echo "✓ K-mer groupings generated successfully"

    # Show summary
    echo "Group summary:"
    python -c "
import json
with open('assembly_recommendations.json') as f:
    data = json.load(f)
    groups = data.get('groups', [])
    print(f'  Total groups: {len(groups)}')
    sizes = [len(g.get('samples', [])) for g in groups]
    if sizes:
        print(f'  Group sizes: {sizes}')
        print(f'  Average group size: {sum(sizes)/len(sizes):.1f}')
"

    echo ""
    echo "Next step: Generate random groupings"
    echo "python scripts/create_random_groups.py"
else
    echo "ERROR: MetaGrouper failed - no output file found"
    exit 1
fi