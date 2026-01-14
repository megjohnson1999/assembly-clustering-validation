#!/bin/bash

# Setup script for MetaGrouper validation experiment
# Configured for Megan's cluster environment

export SAMPLES_PATH="/lts/sahlab/data4/megan/RC2_rrna_removed_reads"
export WORKSPACE="$PWD/metagrouper_validation"

echo "Setting up MetaGrouper validation experiment..."
echo "Samples path: $SAMPLES_PATH"
echo "Workspace: $WORKSPACE"

# Create directory structure
mkdir -p $WORKSPACE/{setup,samples,results,scripts,logs}
mkdir -p $WORKSPACE/results/{kmer_groups,random_groups,assemblies,metrics}
mkdir -p $WORKSPACE/samples/{subset_50,subset_200}
mkdir -p $WORKSPACE/results/assemblies/{kmer,random}

# Clone MetaGrouper (you'll need to update the URL)
echo "Cloning MetaGrouper..."
cd $WORKSPACE/setup

# Clone from your current local copy - you'll need to push to a repo first
echo "NOTE: You'll need to push your local metaGrouper to a git repository"
echo "Then update the git clone command below with the correct URL"

# git clone https://github.com/yourusername/metaGrouper.git

echo "For now, manually copy your metaGrouper directory here:"
echo "cp -r /path/to/your/local/metaGrouper ./metaGrouper"

# Test conda environment
echo "Testing conda environment..."
source /ref/sahlab/software/miniforge3/bin/activate
conda activate metagrouper_env

# Test installation
python -c "import pandas, numpy, sklearn; print('✓ Dependencies available in metagrouper_env')"

# Copy scripts to workspace
echo "Copying scripts..."
cp ../../*.py $WORKSPACE/scripts/
cp ../../*.sh $WORKSPACE/scripts/
chmod +x $WORKSPACE/scripts/*.sh

cd $WORKSPACE

echo "✓ Setup complete!"
echo ""
echo "Directory structure:"
tree -L 3 . 2>/dev/null || find . -type d | head -20

echo ""
echo "Next steps:"
echo "1. Copy/clone MetaGrouper to setup/metaGrouper/"
echo "2. Run the complete experiment: bash scripts/run_full_experiment.sh"
echo "   OR run steps individually:"
echo "   - python scripts/select_samples.py"
echo "   - sbatch scripts/run_metagrouper.sh"
echo "   - etc."