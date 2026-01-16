#!/bin/bash

# Setup script for MetaGrouper validation experiment
# Updated for current repository structure

export SAMPLES_PATH="/lts/sahlab/data4/megan/RC2_rrna_removed_reads"
export WORKSPACE="$PWD/metagrouper_validation"

echo "Setting up MetaGrouper validation experiment..."
echo "Samples path: $SAMPLES_PATH"
echo "Workspace: $WORKSPACE"

# Create directory structure
mkdir -p $WORKSPACE/{setup,samples,results,scripts,logs}
mkdir -p $WORKSPACE/results/{kmer_groups,random_groups,assemblies,final_analysis}
mkdir -p $WORKSPACE/samples/{subset_50,subset_200}
mkdir -p $WORKSPACE/results/assemblies/{megahit_individual,megahit_global,concatenated,flye_meta,final_assemblies}

# Check if MetaGrouper is already available
if [ -d "setup/metaGrouper" ]; then
    echo "✓ MetaGrouper found in setup/metaGrouper/"
    # Copy MetaGrouper to workspace
    echo "Copying MetaGrouper to workspace..."
    cp -r setup/metaGrouper $WORKSPACE/setup/
else
    echo "Warning: MetaGrouper not found in setup/metaGrouper/"
    echo "Please ensure MetaGrouper is in setup/metaGrouper/ before running experiments"
fi

# Test conda environment
echo "Testing conda environment..."
source /ref/sahlab/software/miniforge3/bin/activate
conda activate coassembly_env

# Test dependencies
python -c "import pandas, numpy, sklearn; print('✓ Dependencies available in coassembly_env')"

# Copy scripts to workspace from current repository structure
echo "Copying experiment scripts..."
mkdir -p $WORKSPACE/scripts/{setup,assembly,analysis,utils}

# Copy scripts from the organized structure
cp scripts/setup/*.sh $WORKSPACE/scripts/setup/ 2>/dev/null || echo "No setup scripts to copy"
cp scripts/assembly/*.py $WORKSPACE/scripts/assembly/ 2>/dev/null || echo "No assembly python scripts to copy"
cp scripts/assembly/*.sh $WORKSPACE/scripts/assembly/ 2>/dev/null || echo "No assembly shell scripts to copy"
cp scripts/analysis/*.py $WORKSPACE/scripts/analysis/ 2>/dev/null || echo "No analysis scripts to copy"
cp scripts/utils/*.py $WORKSPACE/scripts/utils/ 2>/dev/null || echo "No utility scripts to copy"

# Also copy any scripts from the main scripts directory
cp scripts/*.py $WORKSPACE/scripts/ 2>/dev/null || echo "No main scripts to copy"
cp scripts/*.sh $WORKSPACE/scripts/ 2>/dev/null || echo "No main shell scripts to copy"

# Make scripts executable
find $WORKSPACE/scripts -name "*.sh" -exec chmod +x {} \; 2>/dev/null
find $WORKSPACE/scripts -name "*.py" -exec chmod +x {} \; 2>/dev/null

cd $WORKSPACE

echo "✓ Setup complete!"
echo ""
echo "Directory structure:"
tree -L 3 . 2>/dev/null || find . -type d | head -20

echo ""
echo "Next steps:"
echo "1. ✓ MetaGrouper already configured"
echo "2. Run the staged experiment:"
echo "   bash scripts/setup/run_staged_experiment.sh"
echo ""
echo "OR run steps individually:"
echo "   python scripts/utils/select_samples.py"
echo "   sbatch scripts/assembly/run_metagrouper.sh"
echo "   python scripts/utils/create_random_groups.py"
echo "   python scripts/assembly/generate_staged_assembly_commands.py"
echo "   # Submit generated SLURM scripts"
echo "   python scripts/analysis/assess_final_assemblies.py"