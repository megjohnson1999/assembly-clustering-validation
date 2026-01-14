#!/bin/bash

# Resume experiment from failure point
# Usage: bash scripts/setup/resume_experiment.sh

set -e

echo "=================================================="
echo "Experiment Recovery Tool"
echo "=================================================="
echo "Checking experiment status..."

# Check current working directory
if [ ! -d "metagrouper_validation" ]; then
    echo "ERROR: Run from project root directory"
    exit 1
fi

cd metagrouper_validation

# Function to check if stage completed
check_stage() {
    local stage=$1
    local check_path=$2

    if [ -e "$check_path" ]; then
        echo "✅ Stage $stage: Complete ($check_path found)"
        return 0
    else
        echo "❌ Stage $stage: Incomplete ($check_path missing)"
        return 1
    fi
}

echo ""
echo "Checking pipeline status:"

# Check each stage
check_stage "1. Sample Selection" "samples/subset_50/selected_samples.txt" && SAMPLES_OK=1 || SAMPLES_OK=0
check_stage "2. MetaGrouper" "results/kmer_groups/assembly_recommendations.json" && METAGROUPER_OK=1 || METAGROUPER_OK=0
check_stage "3. Random Groups" "results/random_groups/random_groups_42.json" && RANDOM_OK=1 || RANDOM_OK=0
check_stage "4. Script Generation" "scripts/run_megahit_individual.sh" && SCRIPTS_OK=1 || SCRIPTS_OK=0

# Check MEGAHIT completion (more complex)
if [ -d "results/assemblies/megahit_individual" ] && [ "$(ls results/assemblies/megahit_individual/ | wc -l)" -gt 40 ]; then
    echo "✅ Stage 5a. MEGAHIT Individual: Complete (~$(ls results/assemblies/megahit_individual/ | wc -l) assemblies)"
    MEGAHIT_INDIVIDUAL_OK=1
else
    echo "❌ Stage 5a. MEGAHIT Individual: Incomplete"
    MEGAHIT_INDIVIDUAL_OK=0
fi

if [ -d "results/assemblies/megahit_grouped" ] && [ "$(ls results/assemblies/megahit_grouped/ 2>/dev/null | wc -l)" -gt 5 ]; then
    echo "✅ Stage 5b. MEGAHIT Grouped: Complete (~$(ls results/assemblies/megahit_grouped/ | wc -l) assemblies)"
    MEGAHIT_GROUPED_OK=1
else
    echo "❌ Stage 5b. MEGAHIT Grouped: Incomplete"
    MEGAHIT_GROUPED_OK=0
fi

check_stage "5c. MEGAHIT Global" "results/assemblies/megahit_global/global_all_samples" && MEGAHIT_GLOBAL_OK=1 || MEGAHIT_GLOBAL_OK=0
check_stage "6. Concatenation" "results/assemblies/concatenated" && CONCAT_OK=1 || CONCAT_OK=0
check_stage "7. Flye Meta-assembly" "results/assemblies/final_assemblies" && FLYE_OK=1 || FLYE_OK=0
check_stage "8. Final Analysis" "results/final_analysis/final_assembly_comparison_report.txt" && ANALYSIS_OK=1 || ANALYSIS_OK=0

echo ""
echo "Recovery recommendations:"

# Determine restart point
if [ $ANALYSIS_OK -eq 1 ]; then
    echo "🎉 EXPERIMENT COMPLETE! Check results/final_analysis/"
elif [ $FLYE_OK -eq 0 ] && [ $CONCAT_OK -eq 1 ]; then
    echo "▶️  Restart from Step 7: sbatch scripts/run_flye_meta.sh"
elif [ $CONCAT_OK -eq 0 ] && [ $MEGAHIT_INDIVIDUAL_OK -eq 1 ] && [ $MEGAHIT_GROUPED_OK -eq 1 ] && [ $MEGAHIT_GLOBAL_OK -eq 1 ]; then
    echo "▶️  Restart from Step 6: sbatch scripts/run_concatenate.sh"
elif [ $MEGAHIT_INDIVIDUAL_OK -eq 0 ] || [ $MEGAHIT_GROUPED_OK -eq 0 ] || [ $MEGAHIT_GLOBAL_OK -eq 0 ]; then
    echo "⚠️  MEGAHIT stage partially failed. Options:"
    echo "   1. Restart failed MEGAHIT jobs:"
    [ $MEGAHIT_INDIVIDUAL_OK -eq 0 ] && echo "      sbatch scripts/run_megahit_individual.sh"
    [ $MEGAHIT_GROUPED_OK -eq 0 ] && echo "      sbatch scripts/run_megahit_grouped.sh"
    [ $MEGAHIT_GLOBAL_OK -eq 0 ] && echo "      sbatch scripts/run_megahit_global.sh"
    echo "   2. Check logs: ls logs/megahit_*"
    echo "   3. Fix resource issues, then resubmit"
elif [ $SCRIPTS_OK -eq 0 ]; then
    echo "▶️  Restart from Step 4: python scripts/generate_staged_assembly_commands.py ..."
elif [ $RANDOM_OK -eq 0 ]; then
    echo "▶️  Restart from Step 3: python scripts/create_random_groups.py ..."
elif [ $METAGROUPER_OK -eq 0 ]; then
    echo "▶️  Restart from Step 2: sbatch scripts/run_metagrouper.sh"
else
    echo "▶️  Restart from Step 1: bash ../scripts/setup/run_staged_experiment.sh"
fi

echo ""
echo "Quick status check commands:"
echo "  Current jobs: squeue -u megan.j"
echo "  Recent jobs: sacct -u megan.j --starttime=today --format=JobID,JobName,State,ExitCode -X"
echo "  Disk usage: du -sh results/"
echo "  Logs: ls -lt logs/ | head -10"