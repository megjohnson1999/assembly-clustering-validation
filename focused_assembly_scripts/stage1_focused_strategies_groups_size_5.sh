#!/bin/bash
#SBATCH --job-name=stage1_focused_strategies_groups_size_5
#SBATCH --time=8:00:00
#SBATCH --mem=64G
#SBATCH --cpus-per-task=12
#SBATCH --output=logs/stage1_focused_strategies_groups_size_5_%j.out
#SBATCH --error=logs/stage1_focused_strategies_groups_size_5_%j.err
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=megan.j@wustl.edu

# Load conda environment
source /ref/sahlab/software/miniforge3/bin/activate
conda activate coassembly_env

# Create output directories
mkdir -p logs

echo "Starting stage1 for strategy: focused_strategies_groups_size_5"
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURM_NODELIST"
echo "Start time: $(date)"


# Group: group_groups_size_5_group_1 (5 samples)

# Step 1: Concatenate 5 R1 files
echo 'Running: concat_r1_group_groups_size_5_group_1'
cat samples/subset_50/sample_067_rrna_removed_R1.fastq samples/subset_50/sample_188_rrna_removed_R1.fastq samples/subset_50/sample_102_rrna_removed_R1.fastq samples/subset_50/sample_194_rrna_removed_R1.fastq samples/subset_50/sample_112_rrna_removed_R1.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_1/concatenated_R1.fastq
echo 'Completed: concat_r1_group_groups_size_5_group_1'


# Step 2: Concatenate 5 R2 files
echo 'Running: concat_r2_group_groups_size_5_group_1'
cat samples/subset_50/sample_067_rrna_removed_R2.fastq samples/subset_50/sample_188_rrna_removed_R2.fastq samples/subset_50/sample_102_rrna_removed_R2.fastq samples/subset_50/sample_194_rrna_removed_R2.fastq samples/subset_50/sample_112_rrna_removed_R2.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_1/concatenated_R2.fastq
echo 'Completed: concat_r2_group_groups_size_5_group_1'


# Step 3: MEGAHIT assembly of concatenated reads (5 samples)
echo 'Running: megahit_group_groups_size_5_group_1'
megahit \
    -1 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_1/concatenated_R1.fastq \
    -2 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_1/concatenated_R2.fastq \
    -o results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_1/megahit_assembly \
    --min-contig-len 500 \
    --k-list 45,65,85,105,125,145,165,185,205,225 \
    --min-count 2 \
    -t 18 \
    --memory 161061273600
echo 'Completed: megahit_group_groups_size_5_group_1'


# Group: group_groups_size_5_group_2 (5 samples)

# Step 1: Concatenate 5 R1 files
echo 'Running: concat_r1_group_groups_size_5_group_2'
cat samples/subset_50/sample_122_rrna_removed_R1.fastq samples/subset_50/sample_014_rrna_removed_R1.fastq samples/subset_50/sample_003_rrna_removed_R1.fastq samples/subset_50/sample_065_rrna_removed_R1.fastq samples/subset_50/sample_045_rrna_removed_R1.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_2/concatenated_R1.fastq
echo 'Completed: concat_r1_group_groups_size_5_group_2'


# Step 2: Concatenate 5 R2 files
echo 'Running: concat_r2_group_groups_size_5_group_2'
cat samples/subset_50/sample_122_rrna_removed_R2.fastq samples/subset_50/sample_014_rrna_removed_R2.fastq samples/subset_50/sample_003_rrna_removed_R2.fastq samples/subset_50/sample_065_rrna_removed_R2.fastq samples/subset_50/sample_045_rrna_removed_R2.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_2/concatenated_R2.fastq
echo 'Completed: concat_r2_group_groups_size_5_group_2'


# Step 3: MEGAHIT assembly of concatenated reads (5 samples)
echo 'Running: megahit_group_groups_size_5_group_2'
megahit \
    -1 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_2/concatenated_R1.fastq \
    -2 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_2/concatenated_R2.fastq \
    -o results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_2/megahit_assembly \
    --min-contig-len 500 \
    --k-list 45,65,85,105,125,145,165,185,205,225 \
    --min-count 2 \
    -t 18 \
    --memory 161061273600
echo 'Completed: megahit_group_groups_size_5_group_2'


# Group: group_groups_size_5_group_3 (5 samples)

# Step 1: Concatenate 5 R1 files
echo 'Running: concat_r1_group_groups_size_5_group_3'
cat samples/subset_50/sample_137_rrna_removed_R1.fastq samples/subset_50/sample_171_rrna_removed_R1.fastq samples/subset_50/sample_129_rrna_removed_R1.fastq samples/subset_50/sample_077_rrna_removed_R1.fastq samples/subset_50/sample_159_rrna_removed_R1.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_3/concatenated_R1.fastq
echo 'Completed: concat_r1_group_groups_size_5_group_3'


# Step 2: Concatenate 5 R2 files
echo 'Running: concat_r2_group_groups_size_5_group_3'
cat samples/subset_50/sample_137_rrna_removed_R2.fastq samples/subset_50/sample_171_rrna_removed_R2.fastq samples/subset_50/sample_129_rrna_removed_R2.fastq samples/subset_50/sample_077_rrna_removed_R2.fastq samples/subset_50/sample_159_rrna_removed_R2.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_3/concatenated_R2.fastq
echo 'Completed: concat_r2_group_groups_size_5_group_3'


# Step 3: MEGAHIT assembly of concatenated reads (5 samples)
echo 'Running: megahit_group_groups_size_5_group_3'
megahit \
    -1 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_3/concatenated_R1.fastq \
    -2 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_3/concatenated_R2.fastq \
    -o results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_3/megahit_assembly \
    --min-contig-len 500 \
    --k-list 45,65,85,105,125,145,165,185,205,225 \
    --min-count 2 \
    -t 18 \
    --memory 161061273600
echo 'Completed: megahit_group_groups_size_5_group_3'


# Group: group_groups_size_5_group_4 (5 samples)

# Step 1: Concatenate 5 R1 files
echo 'Running: concat_r1_group_groups_size_5_group_4'
cat samples/subset_50/sample_168_rrna_removed_R1.fastq samples/subset_50/sample_046_rrna_removed_R1.fastq samples/subset_50/sample_131_rrna_removed_R1.fastq samples/subset_50/sample_031_rrna_removed_R1.fastq samples/subset_50/sample_004_rrna_removed_R1.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_4/concatenated_R1.fastq
echo 'Completed: concat_r1_group_groups_size_5_group_4'


# Step 2: Concatenate 5 R2 files
echo 'Running: concat_r2_group_groups_size_5_group_4'
cat samples/subset_50/sample_168_rrna_removed_R2.fastq samples/subset_50/sample_046_rrna_removed_R2.fastq samples/subset_50/sample_131_rrna_removed_R2.fastq samples/subset_50/sample_031_rrna_removed_R2.fastq samples/subset_50/sample_004_rrna_removed_R2.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_4/concatenated_R2.fastq
echo 'Completed: concat_r2_group_groups_size_5_group_4'


# Step 3: MEGAHIT assembly of concatenated reads (5 samples)
echo 'Running: megahit_group_groups_size_5_group_4'
megahit \
    -1 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_4/concatenated_R1.fastq \
    -2 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_4/concatenated_R2.fastq \
    -o results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_4/megahit_assembly \
    --min-contig-len 500 \
    --k-list 45,65,85,105,125,145,165,185,205,225 \
    --min-count 2 \
    -t 18 \
    --memory 161061273600
echo 'Completed: megahit_group_groups_size_5_group_4'


# Group: group_groups_size_5_group_5 (5 samples)

# Step 1: Concatenate 5 R1 files
echo 'Running: concat_r1_group_groups_size_5_group_5'
cat samples/subset_50/sample_160_rrna_removed_R1.fastq samples/subset_50/sample_016_rrna_removed_R1.fastq samples/subset_50/sample_043_rrna_removed_R1.fastq samples/subset_50/sample_127_rrna_removed_R1.fastq samples/subset_50/sample_187_rrna_removed_R1.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_5/concatenated_R1.fastq
echo 'Completed: concat_r1_group_groups_size_5_group_5'


# Step 2: Concatenate 5 R2 files
echo 'Running: concat_r2_group_groups_size_5_group_5'
cat samples/subset_50/sample_160_rrna_removed_R2.fastq samples/subset_50/sample_016_rrna_removed_R2.fastq samples/subset_50/sample_043_rrna_removed_R2.fastq samples/subset_50/sample_127_rrna_removed_R2.fastq samples/subset_50/sample_187_rrna_removed_R2.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_5/concatenated_R2.fastq
echo 'Completed: concat_r2_group_groups_size_5_group_5'


# Step 3: MEGAHIT assembly of concatenated reads (5 samples)
echo 'Running: megahit_group_groups_size_5_group_5'
megahit \
    -1 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_5/concatenated_R1.fastq \
    -2 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_5/concatenated_R2.fastq \
    -o results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_5/megahit_assembly \
    --min-contig-len 500 \
    --k-list 45,65,85,105,125,145,165,185,205,225 \
    --min-count 2 \
    -t 18 \
    --memory 161061273600
echo 'Completed: megahit_group_groups_size_5_group_5'


# Group: group_groups_size_5_group_6 (5 samples)

# Step 1: Concatenate 5 R1 files
echo 'Running: concat_r1_group_groups_size_5_group_6'
cat samples/subset_50/sample_163_rrna_removed_R1.fastq samples/subset_50/sample_048_rrna_removed_R1.fastq samples/subset_50/sample_111_rrna_removed_R1.fastq samples/subset_50/sample_006_rrna_removed_R1.fastq samples/subset_50/sample_195_rrna_removed_R1.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_6/concatenated_R1.fastq
echo 'Completed: concat_r1_group_groups_size_5_group_6'


# Step 2: Concatenate 5 R2 files
echo 'Running: concat_r2_group_groups_size_5_group_6'
cat samples/subset_50/sample_163_rrna_removed_R2.fastq samples/subset_50/sample_048_rrna_removed_R2.fastq samples/subset_50/sample_111_rrna_removed_R2.fastq samples/subset_50/sample_006_rrna_removed_R2.fastq samples/subset_50/sample_195_rrna_removed_R2.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_6/concatenated_R2.fastq
echo 'Completed: concat_r2_group_groups_size_5_group_6'


# Step 3: MEGAHIT assembly of concatenated reads (5 samples)
echo 'Running: megahit_group_groups_size_5_group_6'
megahit \
    -1 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_6/concatenated_R1.fastq \
    -2 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_6/concatenated_R2.fastq \
    -o results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_6/megahit_assembly \
    --min-contig-len 500 \
    --k-list 45,65,85,105,125,145,165,185,205,225 \
    --min-count 2 \
    -t 18 \
    --memory 161061273600
echo 'Completed: megahit_group_groups_size_5_group_6'


# Group: group_groups_size_5_group_7 (5 samples)

# Step 1: Concatenate 5 R1 files
echo 'Running: concat_r1_group_groups_size_5_group_7'
cat samples/subset_50/sample_038_rrna_removed_R1.fastq samples/subset_50/sample_123_rrna_removed_R1.fastq samples/subset_50/sample_013_rrna_removed_R1.fastq samples/subset_50/sample_037_rrna_removed_R1.fastq samples/subset_50/sample_154_rrna_removed_R1.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_7/concatenated_R1.fastq
echo 'Completed: concat_r1_group_groups_size_5_group_7'


# Step 2: Concatenate 5 R2 files
echo 'Running: concat_r2_group_groups_size_5_group_7'
cat samples/subset_50/sample_038_rrna_removed_R2.fastq samples/subset_50/sample_123_rrna_removed_R2.fastq samples/subset_50/sample_013_rrna_removed_R2.fastq samples/subset_50/sample_037_rrna_removed_R2.fastq samples/subset_50/sample_154_rrna_removed_R2.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_7/concatenated_R2.fastq
echo 'Completed: concat_r2_group_groups_size_5_group_7'


# Step 3: MEGAHIT assembly of concatenated reads (5 samples)
echo 'Running: megahit_group_groups_size_5_group_7'
megahit \
    -1 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_7/concatenated_R1.fastq \
    -2 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_7/concatenated_R2.fastq \
    -o results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_7/megahit_assembly \
    --min-contig-len 500 \
    --k-list 45,65,85,105,125,145,165,185,205,225 \
    --min-count 2 \
    -t 18 \
    --memory 161061273600
echo 'Completed: megahit_group_groups_size_5_group_7'


# Group: group_groups_size_5_group_8 (5 samples)

# Step 1: Concatenate 5 R1 files
echo 'Running: concat_r1_group_groups_size_5_group_8'
cat samples/subset_50/sample_070_rrna_removed_R1.fastq samples/subset_50/sample_062_rrna_removed_R1.fastq samples/subset_50/sample_196_rrna_removed_R1.fastq samples/subset_50/sample_033_rrna_removed_R1.fastq samples/subset_50/sample_173_rrna_removed_R1.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_8/concatenated_R1.fastq
echo 'Completed: concat_r1_group_groups_size_5_group_8'


# Step 2: Concatenate 5 R2 files
echo 'Running: concat_r2_group_groups_size_5_group_8'
cat samples/subset_50/sample_070_rrna_removed_R2.fastq samples/subset_50/sample_062_rrna_removed_R2.fastq samples/subset_50/sample_196_rrna_removed_R2.fastq samples/subset_50/sample_033_rrna_removed_R2.fastq samples/subset_50/sample_173_rrna_removed_R2.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_8/concatenated_R2.fastq
echo 'Completed: concat_r2_group_groups_size_5_group_8'


# Step 3: MEGAHIT assembly of concatenated reads (5 samples)
echo 'Running: megahit_group_groups_size_5_group_8'
megahit \
    -1 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_8/concatenated_R1.fastq \
    -2 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_8/concatenated_R2.fastq \
    -o results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_8/megahit_assembly \
    --min-contig-len 500 \
    --k-list 45,65,85,105,125,145,165,185,205,225 \
    --min-count 2 \
    -t 18 \
    --memory 161061273600
echo 'Completed: megahit_group_groups_size_5_group_8'


# Group: group_groups_size_5_group_9 (5 samples)

# Step 1: Concatenate 5 R1 files
echo 'Running: concat_r1_group_groups_size_5_group_9'
cat samples/subset_50/sample_172_rrna_removed_R1.fastq samples/subset_50/sample_061_rrna_removed_R1.fastq samples/subset_50/sample_011_rrna_removed_R1.fastq samples/subset_50/sample_145_rrna_removed_R1.fastq samples/subset_50/sample_161_rrna_removed_R1.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_9/concatenated_R1.fastq
echo 'Completed: concat_r1_group_groups_size_5_group_9'


# Step 2: Concatenate 5 R2 files
echo 'Running: concat_r2_group_groups_size_5_group_9'
cat samples/subset_50/sample_172_rrna_removed_R2.fastq samples/subset_50/sample_061_rrna_removed_R2.fastq samples/subset_50/sample_011_rrna_removed_R2.fastq samples/subset_50/sample_145_rrna_removed_R2.fastq samples/subset_50/sample_161_rrna_removed_R2.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_9/concatenated_R2.fastq
echo 'Completed: concat_r2_group_groups_size_5_group_9'


# Step 3: MEGAHIT assembly of concatenated reads (5 samples)
echo 'Running: megahit_group_groups_size_5_group_9'
megahit \
    -1 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_9/concatenated_R1.fastq \
    -2 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_9/concatenated_R2.fastq \
    -o results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_9/megahit_assembly \
    --min-contig-len 500 \
    --k-list 45,65,85,105,125,145,165,185,205,225 \
    --min-count 2 \
    -t 18 \
    --memory 161061273600
echo 'Completed: megahit_group_groups_size_5_group_9'


# Group: group_groups_size_5_group_10 (5 samples)

# Step 1: Concatenate 5 R1 files
echo 'Running: concat_r1_group_groups_size_5_group_10'
cat samples/subset_50/sample_053_rrna_removed_R1.fastq samples/subset_50/sample_126_rrna_removed_R1.fastq samples/subset_50/sample_107_rrna_removed_R1.fastq samples/subset_50/sample_074_rrna_removed_R1.fastq samples/subset_50/sample_114_rrna_removed_R1.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_10/concatenated_R1.fastq
echo 'Completed: concat_r1_group_groups_size_5_group_10'


# Step 2: Concatenate 5 R2 files
echo 'Running: concat_r2_group_groups_size_5_group_10'
cat samples/subset_50/sample_053_rrna_removed_R2.fastq samples/subset_50/sample_126_rrna_removed_R2.fastq samples/subset_50/sample_107_rrna_removed_R2.fastq samples/subset_50/sample_074_rrna_removed_R2.fastq samples/subset_50/sample_114_rrna_removed_R2.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_10/concatenated_R2.fastq
echo 'Completed: concat_r2_group_groups_size_5_group_10'


# Step 3: MEGAHIT assembly of concatenated reads (5 samples)
echo 'Running: megahit_group_groups_size_5_group_10'
megahit \
    -1 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_10/concatenated_R1.fastq \
    -2 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_10/concatenated_R2.fastq \
    -o results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_10/megahit_assembly \
    --min-contig-len 500 \
    --k-list 45,65,85,105,125,145,165,185,205,225 \
    --min-count 2 \
    -t 18 \
    --memory 161061273600
echo 'Completed: megahit_group_groups_size_5_group_10'


# Group: group_groups_size_5_group_11 (5 samples)

# Step 1: Concatenate 5 R1 files
echo 'Running: concat_r1_group_groups_size_5_group_11'
cat samples/subset_50/sample_106_rrna_removed_R1.fastq samples/subset_50/sample_096_rrna_removed_R1.fastq samples/subset_50/sample_104_rrna_removed_R1.fastq samples/subset_50/sample_146_rrna_removed_R1.fastq samples/subset_50/sample_044_rrna_removed_R1.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_11/concatenated_R1.fastq
echo 'Completed: concat_r1_group_groups_size_5_group_11'


# Step 2: Concatenate 5 R2 files
echo 'Running: concat_r2_group_groups_size_5_group_11'
cat samples/subset_50/sample_106_rrna_removed_R2.fastq samples/subset_50/sample_096_rrna_removed_R2.fastq samples/subset_50/sample_104_rrna_removed_R2.fastq samples/subset_50/sample_146_rrna_removed_R2.fastq samples/subset_50/sample_044_rrna_removed_R2.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_11/concatenated_R2.fastq
echo 'Completed: concat_r2_group_groups_size_5_group_11'


# Step 3: MEGAHIT assembly of concatenated reads (5 samples)
echo 'Running: megahit_group_groups_size_5_group_11'
megahit \
    -1 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_11/concatenated_R1.fastq \
    -2 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_11/concatenated_R2.fastq \
    -o results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_11/megahit_assembly \
    --min-contig-len 500 \
    --k-list 45,65,85,105,125,145,165,185,205,225 \
    --min-count 2 \
    -t 18 \
    --memory 161061273600
echo 'Completed: megahit_group_groups_size_5_group_11'


# Group: group_groups_size_5_group_12 (5 samples)

# Step 1: Concatenate 5 R1 files
echo 'Running: concat_r1_group_groups_size_5_group_12'
cat samples/subset_50/sample_001_rrna_removed_R1.fastq samples/subset_50/sample_162_rrna_removed_R1.fastq samples/subset_50/sample_193_rrna_removed_R1.fastq samples/subset_50/sample_017_rrna_removed_R1.fastq samples/subset_50/sample_081_rrna_removed_R1.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_12/concatenated_R1.fastq
echo 'Completed: concat_r1_group_groups_size_5_group_12'


# Step 2: Concatenate 5 R2 files
echo 'Running: concat_r2_group_groups_size_5_group_12'
cat samples/subset_50/sample_001_rrna_removed_R2.fastq samples/subset_50/sample_162_rrna_removed_R2.fastq samples/subset_50/sample_193_rrna_removed_R2.fastq samples/subset_50/sample_017_rrna_removed_R2.fastq samples/subset_50/sample_081_rrna_removed_R2.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_12/concatenated_R2.fastq
echo 'Completed: concat_r2_group_groups_size_5_group_12'


# Step 3: MEGAHIT assembly of concatenated reads (5 samples)
echo 'Running: megahit_group_groups_size_5_group_12'
megahit \
    -1 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_12/concatenated_R1.fastq \
    -2 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_12/concatenated_R2.fastq \
    -o results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_12/megahit_assembly \
    --min-contig-len 500 \
    --k-list 45,65,85,105,125,145,165,185,205,225 \
    --min-count 2 \
    -t 18 \
    --memory 161061273600
echo 'Completed: megahit_group_groups_size_5_group_12'


# Group: group_groups_size_5_group_13 (5 samples)

# Step 1: Concatenate 5 R1 files
echo 'Running: concat_r1_group_groups_size_5_group_13'
cat samples/subset_50/sample_103_rrna_removed_R1.fastq samples/subset_50/sample_039_rrna_removed_R1.fastq samples/subset_50/sample_157_rrna_removed_R1.fastq samples/subset_50/sample_177_rrna_removed_R1.fastq samples/subset_50/sample_136_rrna_removed_R1.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_13/concatenated_R1.fastq
echo 'Completed: concat_r1_group_groups_size_5_group_13'


# Step 2: Concatenate 5 R2 files
echo 'Running: concat_r2_group_groups_size_5_group_13'
cat samples/subset_50/sample_103_rrna_removed_R2.fastq samples/subset_50/sample_039_rrna_removed_R2.fastq samples/subset_50/sample_157_rrna_removed_R2.fastq samples/subset_50/sample_177_rrna_removed_R2.fastq samples/subset_50/sample_136_rrna_removed_R2.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_13/concatenated_R2.fastq
echo 'Completed: concat_r2_group_groups_size_5_group_13'


# Step 3: MEGAHIT assembly of concatenated reads (5 samples)
echo 'Running: megahit_group_groups_size_5_group_13'
megahit \
    -1 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_13/concatenated_R1.fastq \
    -2 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_13/concatenated_R2.fastq \
    -o results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_13/megahit_assembly \
    --min-contig-len 500 \
    --k-list 45,65,85,105,125,145,165,185,205,225 \
    --min-count 2 \
    -t 18 \
    --memory 161061273600
echo 'Completed: megahit_group_groups_size_5_group_13'


# Group: group_groups_size_5_group_14 (5 samples)

# Step 1: Concatenate 5 R1 files
echo 'Running: concat_r1_group_groups_size_5_group_14'
cat samples/subset_50/sample_079_rrna_removed_R1.fastq samples/subset_50/sample_116_rrna_removed_R1.fastq samples/subset_50/sample_020_rrna_removed_R1.fastq samples/subset_50/sample_015_rrna_removed_R1.fastq samples/subset_50/sample_178_rrna_removed_R1.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_14/concatenated_R1.fastq
echo 'Completed: concat_r1_group_groups_size_5_group_14'


# Step 2: Concatenate 5 R2 files
echo 'Running: concat_r2_group_groups_size_5_group_14'
cat samples/subset_50/sample_079_rrna_removed_R2.fastq samples/subset_50/sample_116_rrna_removed_R2.fastq samples/subset_50/sample_020_rrna_removed_R2.fastq samples/subset_50/sample_015_rrna_removed_R2.fastq samples/subset_50/sample_178_rrna_removed_R2.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_14/concatenated_R2.fastq
echo 'Completed: concat_r2_group_groups_size_5_group_14'


# Step 3: MEGAHIT assembly of concatenated reads (5 samples)
echo 'Running: megahit_group_groups_size_5_group_14'
megahit \
    -1 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_14/concatenated_R1.fastq \
    -2 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_14/concatenated_R2.fastq \
    -o results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_14/megahit_assembly \
    --min-contig-len 500 \
    --k-list 45,65,85,105,125,145,165,185,205,225 \
    --min-count 2 \
    -t 18 \
    --memory 161061273600
echo 'Completed: megahit_group_groups_size_5_group_14'


# Group: group_groups_size_5_group_15 (5 samples)

# Step 1: Concatenate 5 R1 files
echo 'Running: concat_r1_group_groups_size_5_group_15'
cat samples/subset_50/sample_147_rrna_removed_R1.fastq samples/subset_50/sample_180_rrna_removed_R1.fastq samples/subset_50/sample_066_rrna_removed_R1.fastq samples/subset_50/sample_085_rrna_removed_R1.fastq samples/subset_50/sample_166_rrna_removed_R1.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_15/concatenated_R1.fastq
echo 'Completed: concat_r1_group_groups_size_5_group_15'


# Step 2: Concatenate 5 R2 files
echo 'Running: concat_r2_group_groups_size_5_group_15'
cat samples/subset_50/sample_147_rrna_removed_R2.fastq samples/subset_50/sample_180_rrna_removed_R2.fastq samples/subset_50/sample_066_rrna_removed_R2.fastq samples/subset_50/sample_085_rrna_removed_R2.fastq samples/subset_50/sample_166_rrna_removed_R2.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_15/concatenated_R2.fastq
echo 'Completed: concat_r2_group_groups_size_5_group_15'


# Step 3: MEGAHIT assembly of concatenated reads (5 samples)
echo 'Running: megahit_group_groups_size_5_group_15'
megahit \
    -1 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_15/concatenated_R1.fastq \
    -2 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_15/concatenated_R2.fastq \
    -o results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_15/megahit_assembly \
    --min-contig-len 500 \
    --k-list 45,65,85,105,125,145,165,185,205,225 \
    --min-count 2 \
    -t 18 \
    --memory 161061273600
echo 'Completed: megahit_group_groups_size_5_group_15'


# Group: group_groups_size_5_group_16 (5 samples)

# Step 1: Concatenate 5 R1 files
echo 'Running: concat_r1_group_groups_size_5_group_16'
cat samples/subset_50/sample_047_rrna_removed_R1.fastq samples/subset_50/sample_105_rrna_removed_R1.fastq samples/subset_50/sample_080_rrna_removed_R1.fastq samples/subset_50/sample_055_rrna_removed_R1.fastq samples/subset_50/sample_197_rrna_removed_R1.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_16/concatenated_R1.fastq
echo 'Completed: concat_r1_group_groups_size_5_group_16'


# Step 2: Concatenate 5 R2 files
echo 'Running: concat_r2_group_groups_size_5_group_16'
cat samples/subset_50/sample_047_rrna_removed_R2.fastq samples/subset_50/sample_105_rrna_removed_R2.fastq samples/subset_50/sample_080_rrna_removed_R2.fastq samples/subset_50/sample_055_rrna_removed_R2.fastq samples/subset_50/sample_197_rrna_removed_R2.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_16/concatenated_R2.fastq
echo 'Completed: concat_r2_group_groups_size_5_group_16'


# Step 3: MEGAHIT assembly of concatenated reads (5 samples)
echo 'Running: megahit_group_groups_size_5_group_16'
megahit \
    -1 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_16/concatenated_R1.fastq \
    -2 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_16/concatenated_R2.fastq \
    -o results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_16/megahit_assembly \
    --min-contig-len 500 \
    --k-list 45,65,85,105,125,145,165,185,205,225 \
    --min-count 2 \
    -t 18 \
    --memory 161061273600
echo 'Completed: megahit_group_groups_size_5_group_16'


# Group: group_groups_size_5_group_17 (5 samples)

# Step 1: Concatenate 5 R1 files
echo 'Running: concat_r1_group_groups_size_5_group_17'
cat samples/subset_50/sample_086_rrna_removed_R1.fastq samples/subset_50/sample_119_rrna_removed_R1.fastq samples/subset_50/sample_110_rrna_removed_R1.fastq samples/subset_50/sample_134_rrna_removed_R1.fastq samples/subset_50/sample_143_rrna_removed_R1.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_17/concatenated_R1.fastq
echo 'Completed: concat_r1_group_groups_size_5_group_17'


# Step 2: Concatenate 5 R2 files
echo 'Running: concat_r2_group_groups_size_5_group_17'
cat samples/subset_50/sample_086_rrna_removed_R2.fastq samples/subset_50/sample_119_rrna_removed_R2.fastq samples/subset_50/sample_110_rrna_removed_R2.fastq samples/subset_50/sample_134_rrna_removed_R2.fastq samples/subset_50/sample_143_rrna_removed_R2.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_17/concatenated_R2.fastq
echo 'Completed: concat_r2_group_groups_size_5_group_17'


# Step 3: MEGAHIT assembly of concatenated reads (5 samples)
echo 'Running: megahit_group_groups_size_5_group_17'
megahit \
    -1 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_17/concatenated_R1.fastq \
    -2 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_17/concatenated_R2.fastq \
    -o results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_17/megahit_assembly \
    --min-contig-len 500 \
    --k-list 45,65,85,105,125,145,165,185,205,225 \
    --min-count 2 \
    -t 18 \
    --memory 161061273600
echo 'Completed: megahit_group_groups_size_5_group_17'


# Group: group_groups_size_5_group_18 (5 samples)

# Step 1: Concatenate 5 R1 files
echo 'Running: concat_r1_group_groups_size_5_group_18'
cat samples/subset_50/sample_034_rrna_removed_R1.fastq samples/subset_50/sample_019_rrna_removed_R1.fastq samples/subset_50/sample_141_rrna_removed_R1.fastq samples/subset_50/sample_124_rrna_removed_R1.fastq samples/subset_50/sample_176_rrna_removed_R1.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_18/concatenated_R1.fastq
echo 'Completed: concat_r1_group_groups_size_5_group_18'


# Step 2: Concatenate 5 R2 files
echo 'Running: concat_r2_group_groups_size_5_group_18'
cat samples/subset_50/sample_034_rrna_removed_R2.fastq samples/subset_50/sample_019_rrna_removed_R2.fastq samples/subset_50/sample_141_rrna_removed_R2.fastq samples/subset_50/sample_124_rrna_removed_R2.fastq samples/subset_50/sample_176_rrna_removed_R2.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_18/concatenated_R2.fastq
echo 'Completed: concat_r2_group_groups_size_5_group_18'


# Step 3: MEGAHIT assembly of concatenated reads (5 samples)
echo 'Running: megahit_group_groups_size_5_group_18'
megahit \
    -1 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_18/concatenated_R1.fastq \
    -2 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_18/concatenated_R2.fastq \
    -o results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_18/megahit_assembly \
    --min-contig-len 500 \
    --k-list 45,65,85,105,125,145,165,185,205,225 \
    --min-count 2 \
    -t 18 \
    --memory 161061273600
echo 'Completed: megahit_group_groups_size_5_group_18'


# Group: group_groups_size_5_group_19 (5 samples)

# Step 1: Concatenate 5 R1 files
echo 'Running: concat_r1_group_groups_size_5_group_19'
cat samples/subset_50/sample_064_rrna_removed_R1.fastq samples/subset_50/sample_084_rrna_removed_R1.fastq samples/subset_50/sample_149_rrna_removed_R1.fastq samples/subset_50/sample_101_rrna_removed_R1.fastq samples/subset_50/sample_156_rrna_removed_R1.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_19/concatenated_R1.fastq
echo 'Completed: concat_r1_group_groups_size_5_group_19'


# Step 2: Concatenate 5 R2 files
echo 'Running: concat_r2_group_groups_size_5_group_19'
cat samples/subset_50/sample_064_rrna_removed_R2.fastq samples/subset_50/sample_084_rrna_removed_R2.fastq samples/subset_50/sample_149_rrna_removed_R2.fastq samples/subset_50/sample_101_rrna_removed_R2.fastq samples/subset_50/sample_156_rrna_removed_R2.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_19/concatenated_R2.fastq
echo 'Completed: concat_r2_group_groups_size_5_group_19'


# Step 3: MEGAHIT assembly of concatenated reads (5 samples)
echo 'Running: megahit_group_groups_size_5_group_19'
megahit \
    -1 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_19/concatenated_R1.fastq \
    -2 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_19/concatenated_R2.fastq \
    -o results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_19/megahit_assembly \
    --min-contig-len 500 \
    --k-list 45,65,85,105,125,145,165,185,205,225 \
    --min-count 2 \
    -t 18 \
    --memory 161061273600
echo 'Completed: megahit_group_groups_size_5_group_19'


# Group: group_groups_size_5_group_20 (5 samples)

# Step 1: Concatenate 5 R1 files
echo 'Running: concat_r1_group_groups_size_5_group_20'
cat samples/subset_50/sample_073_rrna_removed_R1.fastq samples/subset_50/sample_028_rrna_removed_R1.fastq samples/subset_50/sample_185_rrna_removed_R1.fastq samples/subset_50/sample_113_rrna_removed_R1.fastq samples/subset_50/sample_052_rrna_removed_R1.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_20/concatenated_R1.fastq
echo 'Completed: concat_r1_group_groups_size_5_group_20'


# Step 2: Concatenate 5 R2 files
echo 'Running: concat_r2_group_groups_size_5_group_20'
cat samples/subset_50/sample_073_rrna_removed_R2.fastq samples/subset_50/sample_028_rrna_removed_R2.fastq samples/subset_50/sample_185_rrna_removed_R2.fastq samples/subset_50/sample_113_rrna_removed_R2.fastq samples/subset_50/sample_052_rrna_removed_R2.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_20/concatenated_R2.fastq
echo 'Completed: concat_r2_group_groups_size_5_group_20'


# Step 3: MEGAHIT assembly of concatenated reads (5 samples)
echo 'Running: megahit_group_groups_size_5_group_20'
megahit \
    -1 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_20/concatenated_R1.fastq \
    -2 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_20/concatenated_R2.fastq \
    -o results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_20/megahit_assembly \
    --min-contig-len 500 \
    --k-list 45,65,85,105,125,145,165,185,205,225 \
    --min-count 2 \
    -t 18 \
    --memory 161061273600
echo 'Completed: megahit_group_groups_size_5_group_20'


# Group: group_groups_size_5_group_21 (5 samples)

# Step 1: Concatenate 5 R1 files
echo 'Running: concat_r1_group_groups_size_5_group_21'
cat samples/subset_50/sample_175_rrna_removed_R1.fastq samples/subset_50/sample_005_rrna_removed_R1.fastq samples/subset_50/sample_030_rrna_removed_R1.fastq samples/subset_50/sample_184_rrna_removed_R1.fastq samples/subset_50/sample_100_rrna_removed_R1.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_21/concatenated_R1.fastq
echo 'Completed: concat_r1_group_groups_size_5_group_21'


# Step 2: Concatenate 5 R2 files
echo 'Running: concat_r2_group_groups_size_5_group_21'
cat samples/subset_50/sample_175_rrna_removed_R2.fastq samples/subset_50/sample_005_rrna_removed_R2.fastq samples/subset_50/sample_030_rrna_removed_R2.fastq samples/subset_50/sample_184_rrna_removed_R2.fastq samples/subset_50/sample_100_rrna_removed_R2.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_21/concatenated_R2.fastq
echo 'Completed: concat_r2_group_groups_size_5_group_21'


# Step 3: MEGAHIT assembly of concatenated reads (5 samples)
echo 'Running: megahit_group_groups_size_5_group_21'
megahit \
    -1 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_21/concatenated_R1.fastq \
    -2 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_21/concatenated_R2.fastq \
    -o results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_21/megahit_assembly \
    --min-contig-len 500 \
    --k-list 45,65,85,105,125,145,165,185,205,225 \
    --min-count 2 \
    -t 18 \
    --memory 161061273600
echo 'Completed: megahit_group_groups_size_5_group_21'


# Group: group_groups_size_5_group_22 (5 samples)

# Step 1: Concatenate 5 R1 files
echo 'Running: concat_r1_group_groups_size_5_group_22'
cat samples/subset_50/sample_099_rrna_removed_R1.fastq samples/subset_50/sample_132_rrna_removed_R1.fastq samples/subset_50/sample_125_rrna_removed_R1.fastq samples/subset_50/sample_199_rrna_removed_R1.fastq samples/subset_50/sample_135_rrna_removed_R1.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_22/concatenated_R1.fastq
echo 'Completed: concat_r1_group_groups_size_5_group_22'


# Step 2: Concatenate 5 R2 files
echo 'Running: concat_r2_group_groups_size_5_group_22'
cat samples/subset_50/sample_099_rrna_removed_R2.fastq samples/subset_50/sample_132_rrna_removed_R2.fastq samples/subset_50/sample_125_rrna_removed_R2.fastq samples/subset_50/sample_199_rrna_removed_R2.fastq samples/subset_50/sample_135_rrna_removed_R2.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_22/concatenated_R2.fastq
echo 'Completed: concat_r2_group_groups_size_5_group_22'


# Step 3: MEGAHIT assembly of concatenated reads (5 samples)
echo 'Running: megahit_group_groups_size_5_group_22'
megahit \
    -1 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_22/concatenated_R1.fastq \
    -2 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_22/concatenated_R2.fastq \
    -o results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_22/megahit_assembly \
    --min-contig-len 500 \
    --k-list 45,65,85,105,125,145,165,185,205,225 \
    --min-count 2 \
    -t 18 \
    --memory 161061273600
echo 'Completed: megahit_group_groups_size_5_group_22'


# Group: group_groups_size_5_group_23 (5 samples)

# Step 1: Concatenate 5 R1 files
echo 'Running: concat_r1_group_groups_size_5_group_23'
cat samples/subset_50/sample_179_rrna_removed_R1.fastq samples/subset_50/sample_121_rrna_removed_R1.fastq samples/subset_50/sample_035_rrna_removed_R1.fastq samples/subset_50/sample_049_rrna_removed_R1.fastq samples/subset_50/sample_170_rrna_removed_R1.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_23/concatenated_R1.fastq
echo 'Completed: concat_r1_group_groups_size_5_group_23'


# Step 2: Concatenate 5 R2 files
echo 'Running: concat_r2_group_groups_size_5_group_23'
cat samples/subset_50/sample_179_rrna_removed_R2.fastq samples/subset_50/sample_121_rrna_removed_R2.fastq samples/subset_50/sample_035_rrna_removed_R2.fastq samples/subset_50/sample_049_rrna_removed_R2.fastq samples/subset_50/sample_170_rrna_removed_R2.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_23/concatenated_R2.fastq
echo 'Completed: concat_r2_group_groups_size_5_group_23'


# Step 3: MEGAHIT assembly of concatenated reads (5 samples)
echo 'Running: megahit_group_groups_size_5_group_23'
megahit \
    -1 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_23/concatenated_R1.fastq \
    -2 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_23/concatenated_R2.fastq \
    -o results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_23/megahit_assembly \
    --min-contig-len 500 \
    --k-list 45,65,85,105,125,145,165,185,205,225 \
    --min-count 2 \
    -t 18 \
    --memory 161061273600
echo 'Completed: megahit_group_groups_size_5_group_23'


# Group: group_groups_size_5_group_24 (5 samples)

# Step 1: Concatenate 5 R1 files
echo 'Running: concat_r1_group_groups_size_5_group_24'
cat samples/subset_50/sample_139_rrna_removed_R1.fastq samples/subset_50/sample_150_rrna_removed_R1.fastq samples/subset_50/sample_133_rrna_removed_R1.fastq samples/subset_50/sample_128_rrna_removed_R1.fastq samples/subset_50/sample_022_rrna_removed_R1.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_24/concatenated_R1.fastq
echo 'Completed: concat_r1_group_groups_size_5_group_24'


# Step 2: Concatenate 5 R2 files
echo 'Running: concat_r2_group_groups_size_5_group_24'
cat samples/subset_50/sample_139_rrna_removed_R2.fastq samples/subset_50/sample_150_rrna_removed_R2.fastq samples/subset_50/sample_133_rrna_removed_R2.fastq samples/subset_50/sample_128_rrna_removed_R2.fastq samples/subset_50/sample_022_rrna_removed_R2.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_24/concatenated_R2.fastq
echo 'Completed: concat_r2_group_groups_size_5_group_24'


# Step 3: MEGAHIT assembly of concatenated reads (5 samples)
echo 'Running: megahit_group_groups_size_5_group_24'
megahit \
    -1 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_24/concatenated_R1.fastq \
    -2 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_24/concatenated_R2.fastq \
    -o results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_24/megahit_assembly \
    --min-contig-len 500 \
    --k-list 45,65,85,105,125,145,165,185,205,225 \
    --min-count 2 \
    -t 18 \
    --memory 161061273600
echo 'Completed: megahit_group_groups_size_5_group_24'


# Group: group_groups_size_5_group_25 (5 samples)

# Step 1: Concatenate 5 R1 files
echo 'Running: concat_r1_group_groups_size_5_group_25'
cat samples/subset_50/sample_082_rrna_removed_R1.fastq samples/subset_50/sample_078_rrna_removed_R1.fastq samples/subset_50/sample_010_rrna_removed_R1.fastq samples/subset_50/sample_083_rrna_removed_R1.fastq samples/subset_50/sample_165_rrna_removed_R1.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_25/concatenated_R1.fastq
echo 'Completed: concat_r1_group_groups_size_5_group_25'


# Step 2: Concatenate 5 R2 files
echo 'Running: concat_r2_group_groups_size_5_group_25'
cat samples/subset_50/sample_082_rrna_removed_R2.fastq samples/subset_50/sample_078_rrna_removed_R2.fastq samples/subset_50/sample_010_rrna_removed_R2.fastq samples/subset_50/sample_083_rrna_removed_R2.fastq samples/subset_50/sample_165_rrna_removed_R2.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_25/concatenated_R2.fastq
echo 'Completed: concat_r2_group_groups_size_5_group_25'


# Step 3: MEGAHIT assembly of concatenated reads (5 samples)
echo 'Running: megahit_group_groups_size_5_group_25'
megahit \
    -1 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_25/concatenated_R1.fastq \
    -2 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_25/concatenated_R2.fastq \
    -o results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_25/megahit_assembly \
    --min-contig-len 500 \
    --k-list 45,65,85,105,125,145,165,185,205,225 \
    --min-count 2 \
    -t 18 \
    --memory 161061273600
echo 'Completed: megahit_group_groups_size_5_group_25'


# Group: group_groups_size_5_group_26 (5 samples)

# Step 1: Concatenate 5 R1 files
echo 'Running: concat_r1_group_groups_size_5_group_26'
cat samples/subset_50/sample_120_rrna_removed_R1.fastq samples/subset_50/sample_090_rrna_removed_R1.fastq samples/subset_50/sample_069_rrna_removed_R1.fastq samples/subset_50/sample_054_rrna_removed_R1.fastq samples/subset_50/sample_091_rrna_removed_R1.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_26/concatenated_R1.fastq
echo 'Completed: concat_r1_group_groups_size_5_group_26'


# Step 2: Concatenate 5 R2 files
echo 'Running: concat_r2_group_groups_size_5_group_26'
cat samples/subset_50/sample_120_rrna_removed_R2.fastq samples/subset_50/sample_090_rrna_removed_R2.fastq samples/subset_50/sample_069_rrna_removed_R2.fastq samples/subset_50/sample_054_rrna_removed_R2.fastq samples/subset_50/sample_091_rrna_removed_R2.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_26/concatenated_R2.fastq
echo 'Completed: concat_r2_group_groups_size_5_group_26'


# Step 3: MEGAHIT assembly of concatenated reads (5 samples)
echo 'Running: megahit_group_groups_size_5_group_26'
megahit \
    -1 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_26/concatenated_R1.fastq \
    -2 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_26/concatenated_R2.fastq \
    -o results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_26/megahit_assembly \
    --min-contig-len 500 \
    --k-list 45,65,85,105,125,145,165,185,205,225 \
    --min-count 2 \
    -t 18 \
    --memory 161061273600
echo 'Completed: megahit_group_groups_size_5_group_26'


# Group: group_groups_size_5_group_27 (5 samples)

# Step 1: Concatenate 5 R1 files
echo 'Running: concat_r1_group_groups_size_5_group_27'
cat samples/subset_50/sample_095_rrna_removed_R1.fastq samples/subset_50/sample_042_rrna_removed_R1.fastq samples/subset_50/sample_094_rrna_removed_R1.fastq samples/subset_50/sample_117_rrna_removed_R1.fastq samples/subset_50/sample_200_rrna_removed_R1.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_27/concatenated_R1.fastq
echo 'Completed: concat_r1_group_groups_size_5_group_27'


# Step 2: Concatenate 5 R2 files
echo 'Running: concat_r2_group_groups_size_5_group_27'
cat samples/subset_50/sample_095_rrna_removed_R2.fastq samples/subset_50/sample_042_rrna_removed_R2.fastq samples/subset_50/sample_094_rrna_removed_R2.fastq samples/subset_50/sample_117_rrna_removed_R2.fastq samples/subset_50/sample_200_rrna_removed_R2.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_27/concatenated_R2.fastq
echo 'Completed: concat_r2_group_groups_size_5_group_27'


# Step 3: MEGAHIT assembly of concatenated reads (5 samples)
echo 'Running: megahit_group_groups_size_5_group_27'
megahit \
    -1 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_27/concatenated_R1.fastq \
    -2 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_27/concatenated_R2.fastq \
    -o results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_27/megahit_assembly \
    --min-contig-len 500 \
    --k-list 45,65,85,105,125,145,165,185,205,225 \
    --min-count 2 \
    -t 18 \
    --memory 161061273600
echo 'Completed: megahit_group_groups_size_5_group_27'


# Group: group_groups_size_5_group_28 (5 samples)

# Step 1: Concatenate 5 R1 files
echo 'Running: concat_r1_group_groups_size_5_group_28'
cat samples/subset_50/sample_158_rrna_removed_R1.fastq samples/subset_50/sample_026_rrna_removed_R1.fastq samples/subset_50/sample_181_rrna_removed_R1.fastq samples/subset_50/sample_148_rrna_removed_R1.fastq samples/subset_50/sample_075_rrna_removed_R1.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_28/concatenated_R1.fastq
echo 'Completed: concat_r1_group_groups_size_5_group_28'


# Step 2: Concatenate 5 R2 files
echo 'Running: concat_r2_group_groups_size_5_group_28'
cat samples/subset_50/sample_158_rrna_removed_R2.fastq samples/subset_50/sample_026_rrna_removed_R2.fastq samples/subset_50/sample_181_rrna_removed_R2.fastq samples/subset_50/sample_148_rrna_removed_R2.fastq samples/subset_50/sample_075_rrna_removed_R2.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_28/concatenated_R2.fastq
echo 'Completed: concat_r2_group_groups_size_5_group_28'


# Step 3: MEGAHIT assembly of concatenated reads (5 samples)
echo 'Running: megahit_group_groups_size_5_group_28'
megahit \
    -1 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_28/concatenated_R1.fastq \
    -2 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_28/concatenated_R2.fastq \
    -o results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_28/megahit_assembly \
    --min-contig-len 500 \
    --k-list 45,65,85,105,125,145,165,185,205,225 \
    --min-count 2 \
    -t 18 \
    --memory 161061273600
echo 'Completed: megahit_group_groups_size_5_group_28'


# Group: group_groups_size_5_group_29 (5 samples)

# Step 1: Concatenate 5 R1 files
echo 'Running: concat_r1_group_groups_size_5_group_29'
cat samples/subset_50/sample_059_rrna_removed_R1.fastq samples/subset_50/sample_153_rrna_removed_R1.fastq samples/subset_50/sample_018_rrna_removed_R1.fastq samples/subset_50/sample_050_rrna_removed_R1.fastq samples/subset_50/sample_093_rrna_removed_R1.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_29/concatenated_R1.fastq
echo 'Completed: concat_r1_group_groups_size_5_group_29'


# Step 2: Concatenate 5 R2 files
echo 'Running: concat_r2_group_groups_size_5_group_29'
cat samples/subset_50/sample_059_rrna_removed_R2.fastq samples/subset_50/sample_153_rrna_removed_R2.fastq samples/subset_50/sample_018_rrna_removed_R2.fastq samples/subset_50/sample_050_rrna_removed_R2.fastq samples/subset_50/sample_093_rrna_removed_R2.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_29/concatenated_R2.fastq
echo 'Completed: concat_r2_group_groups_size_5_group_29'


# Step 3: MEGAHIT assembly of concatenated reads (5 samples)
echo 'Running: megahit_group_groups_size_5_group_29'
megahit \
    -1 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_29/concatenated_R1.fastq \
    -2 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_29/concatenated_R2.fastq \
    -o results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_29/megahit_assembly \
    --min-contig-len 500 \
    --k-list 45,65,85,105,125,145,165,185,205,225 \
    --min-count 2 \
    -t 18 \
    --memory 161061273600
echo 'Completed: megahit_group_groups_size_5_group_29'


# Group: group_groups_size_5_group_30 (5 samples)

# Step 1: Concatenate 5 R1 files
echo 'Running: concat_r1_group_groups_size_5_group_30'
cat samples/subset_50/sample_076_rrna_removed_R1.fastq samples/subset_50/sample_142_rrna_removed_R1.fastq samples/subset_50/sample_021_rrna_removed_R1.fastq samples/subset_50/sample_097_rrna_removed_R1.fastq samples/subset_50/sample_032_rrna_removed_R1.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_30/concatenated_R1.fastq
echo 'Completed: concat_r1_group_groups_size_5_group_30'


# Step 2: Concatenate 5 R2 files
echo 'Running: concat_r2_group_groups_size_5_group_30'
cat samples/subset_50/sample_076_rrna_removed_R2.fastq samples/subset_50/sample_142_rrna_removed_R2.fastq samples/subset_50/sample_021_rrna_removed_R2.fastq samples/subset_50/sample_097_rrna_removed_R2.fastq samples/subset_50/sample_032_rrna_removed_R2.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_30/concatenated_R2.fastq
echo 'Completed: concat_r2_group_groups_size_5_group_30'


# Step 3: MEGAHIT assembly of concatenated reads (5 samples)
echo 'Running: megahit_group_groups_size_5_group_30'
megahit \
    -1 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_30/concatenated_R1.fastq \
    -2 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_30/concatenated_R2.fastq \
    -o results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_30/megahit_assembly \
    --min-contig-len 500 \
    --k-list 45,65,85,105,125,145,165,185,205,225 \
    --min-count 2 \
    -t 18 \
    --memory 161061273600
echo 'Completed: megahit_group_groups_size_5_group_30'


# Group: group_groups_size_5_group_31 (5 samples)

# Step 1: Concatenate 5 R1 files
echo 'Running: concat_r1_group_groups_size_5_group_31'
cat samples/subset_50/sample_138_rrna_removed_R1.fastq samples/subset_50/sample_118_rrna_removed_R1.fastq samples/subset_50/sample_012_rrna_removed_R1.fastq samples/subset_50/sample_068_rrna_removed_R1.fastq samples/subset_50/sample_089_rrna_removed_R1.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_31/concatenated_R1.fastq
echo 'Completed: concat_r1_group_groups_size_5_group_31'


# Step 2: Concatenate 5 R2 files
echo 'Running: concat_r2_group_groups_size_5_group_31'
cat samples/subset_50/sample_138_rrna_removed_R2.fastq samples/subset_50/sample_118_rrna_removed_R2.fastq samples/subset_50/sample_012_rrna_removed_R2.fastq samples/subset_50/sample_068_rrna_removed_R2.fastq samples/subset_50/sample_089_rrna_removed_R2.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_31/concatenated_R2.fastq
echo 'Completed: concat_r2_group_groups_size_5_group_31'


# Step 3: MEGAHIT assembly of concatenated reads (5 samples)
echo 'Running: megahit_group_groups_size_5_group_31'
megahit \
    -1 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_31/concatenated_R1.fastq \
    -2 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_31/concatenated_R2.fastq \
    -o results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_31/megahit_assembly \
    --min-contig-len 500 \
    --k-list 45,65,85,105,125,145,165,185,205,225 \
    --min-count 2 \
    -t 18 \
    --memory 161061273600
echo 'Completed: megahit_group_groups_size_5_group_31'


# Group: group_groups_size_5_group_32 (5 samples)

# Step 1: Concatenate 5 R1 files
echo 'Running: concat_r1_group_groups_size_5_group_32'
cat samples/subset_50/sample_092_rrna_removed_R1.fastq samples/subset_50/sample_025_rrna_removed_R1.fastq samples/subset_50/sample_098_rrna_removed_R1.fastq samples/subset_50/sample_183_rrna_removed_R1.fastq samples/subset_50/sample_191_rrna_removed_R1.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_32/concatenated_R1.fastq
echo 'Completed: concat_r1_group_groups_size_5_group_32'


# Step 2: Concatenate 5 R2 files
echo 'Running: concat_r2_group_groups_size_5_group_32'
cat samples/subset_50/sample_092_rrna_removed_R2.fastq samples/subset_50/sample_025_rrna_removed_R2.fastq samples/subset_50/sample_098_rrna_removed_R2.fastq samples/subset_50/sample_183_rrna_removed_R2.fastq samples/subset_50/sample_191_rrna_removed_R2.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_32/concatenated_R2.fastq
echo 'Completed: concat_r2_group_groups_size_5_group_32'


# Step 3: MEGAHIT assembly of concatenated reads (5 samples)
echo 'Running: megahit_group_groups_size_5_group_32'
megahit \
    -1 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_32/concatenated_R1.fastq \
    -2 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_32/concatenated_R2.fastq \
    -o results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_32/megahit_assembly \
    --min-contig-len 500 \
    --k-list 45,65,85,105,125,145,165,185,205,225 \
    --min-count 2 \
    -t 18 \
    --memory 161061273600
echo 'Completed: megahit_group_groups_size_5_group_32'


# Group: group_groups_size_5_group_33 (5 samples)

# Step 1: Concatenate 5 R1 files
echo 'Running: concat_r1_group_groups_size_5_group_33'
cat samples/subset_50/sample_087_rrna_removed_R1.fastq samples/subset_50/sample_182_rrna_removed_R1.fastq samples/subset_50/sample_040_rrna_removed_R1.fastq samples/subset_50/sample_169_rrna_removed_R1.fastq samples/subset_50/sample_088_rrna_removed_R1.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_33/concatenated_R1.fastq
echo 'Completed: concat_r1_group_groups_size_5_group_33'


# Step 2: Concatenate 5 R2 files
echo 'Running: concat_r2_group_groups_size_5_group_33'
cat samples/subset_50/sample_087_rrna_removed_R2.fastq samples/subset_50/sample_182_rrna_removed_R2.fastq samples/subset_50/sample_040_rrna_removed_R2.fastq samples/subset_50/sample_169_rrna_removed_R2.fastq samples/subset_50/sample_088_rrna_removed_R2.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_33/concatenated_R2.fastq
echo 'Completed: concat_r2_group_groups_size_5_group_33'


# Step 3: MEGAHIT assembly of concatenated reads (5 samples)
echo 'Running: megahit_group_groups_size_5_group_33'
megahit \
    -1 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_33/concatenated_R1.fastq \
    -2 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_33/concatenated_R2.fastq \
    -o results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_33/megahit_assembly \
    --min-contig-len 500 \
    --k-list 45,65,85,105,125,145,165,185,205,225 \
    --min-count 2 \
    -t 18 \
    --memory 161061273600
echo 'Completed: megahit_group_groups_size_5_group_33'


# Group: group_groups_size_5_group_34 (5 samples)

# Step 1: Concatenate 5 R1 files
echo 'Running: concat_r1_group_groups_size_5_group_34'
cat samples/subset_50/sample_186_rrna_removed_R1.fastq samples/subset_50/sample_041_rrna_removed_R1.fastq samples/subset_50/sample_002_rrna_removed_R1.fastq samples/subset_50/sample_072_rrna_removed_R1.fastq samples/subset_50/sample_151_rrna_removed_R1.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_34/concatenated_R1.fastq
echo 'Completed: concat_r1_group_groups_size_5_group_34'


# Step 2: Concatenate 5 R2 files
echo 'Running: concat_r2_group_groups_size_5_group_34'
cat samples/subset_50/sample_186_rrna_removed_R2.fastq samples/subset_50/sample_041_rrna_removed_R2.fastq samples/subset_50/sample_002_rrna_removed_R2.fastq samples/subset_50/sample_072_rrna_removed_R2.fastq samples/subset_50/sample_151_rrna_removed_R2.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_34/concatenated_R2.fastq
echo 'Completed: concat_r2_group_groups_size_5_group_34'


# Step 3: MEGAHIT assembly of concatenated reads (5 samples)
echo 'Running: megahit_group_groups_size_5_group_34'
megahit \
    -1 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_34/concatenated_R1.fastq \
    -2 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_34/concatenated_R2.fastq \
    -o results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_34/megahit_assembly \
    --min-contig-len 500 \
    --k-list 45,65,85,105,125,145,165,185,205,225 \
    --min-count 2 \
    -t 18 \
    --memory 161061273600
echo 'Completed: megahit_group_groups_size_5_group_34'


# Group: group_groups_size_5_group_35 (5 samples)

# Step 1: Concatenate 5 R1 files
echo 'Running: concat_r1_group_groups_size_5_group_35'
cat samples/subset_50/sample_115_rrna_removed_R1.fastq samples/subset_50/sample_057_rrna_removed_R1.fastq samples/subset_50/sample_108_rrna_removed_R1.fastq samples/subset_50/sample_192_rrna_removed_R1.fastq samples/subset_50/sample_167_rrna_removed_R1.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_35/concatenated_R1.fastq
echo 'Completed: concat_r1_group_groups_size_5_group_35'


# Step 2: Concatenate 5 R2 files
echo 'Running: concat_r2_group_groups_size_5_group_35'
cat samples/subset_50/sample_115_rrna_removed_R2.fastq samples/subset_50/sample_057_rrna_removed_R2.fastq samples/subset_50/sample_108_rrna_removed_R2.fastq samples/subset_50/sample_192_rrna_removed_R2.fastq samples/subset_50/sample_167_rrna_removed_R2.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_35/concatenated_R2.fastq
echo 'Completed: concat_r2_group_groups_size_5_group_35'


# Step 3: MEGAHIT assembly of concatenated reads (5 samples)
echo 'Running: megahit_group_groups_size_5_group_35'
megahit \
    -1 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_35/concatenated_R1.fastq \
    -2 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_35/concatenated_R2.fastq \
    -o results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_35/megahit_assembly \
    --min-contig-len 500 \
    --k-list 45,65,85,105,125,145,165,185,205,225 \
    --min-count 2 \
    -t 18 \
    --memory 161061273600
echo 'Completed: megahit_group_groups_size_5_group_35'


# Group: group_groups_size_5_group_36 (5 samples)

# Step 1: Concatenate 5 R1 files
echo 'Running: concat_r1_group_groups_size_5_group_36'
cat samples/subset_50/sample_051_rrna_removed_R1.fastq samples/subset_50/sample_144_rrna_removed_R1.fastq samples/subset_50/sample_198_rrna_removed_R1.fastq samples/subset_50/sample_155_rrna_removed_R1.fastq samples/subset_50/sample_130_rrna_removed_R1.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_36/concatenated_R1.fastq
echo 'Completed: concat_r1_group_groups_size_5_group_36'


# Step 2: Concatenate 5 R2 files
echo 'Running: concat_r2_group_groups_size_5_group_36'
cat samples/subset_50/sample_051_rrna_removed_R2.fastq samples/subset_50/sample_144_rrna_removed_R2.fastq samples/subset_50/sample_198_rrna_removed_R2.fastq samples/subset_50/sample_155_rrna_removed_R2.fastq samples/subset_50/sample_130_rrna_removed_R2.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_36/concatenated_R2.fastq
echo 'Completed: concat_r2_group_groups_size_5_group_36'


# Step 3: MEGAHIT assembly of concatenated reads (5 samples)
echo 'Running: megahit_group_groups_size_5_group_36'
megahit \
    -1 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_36/concatenated_R1.fastq \
    -2 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_36/concatenated_R2.fastq \
    -o results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_36/megahit_assembly \
    --min-contig-len 500 \
    --k-list 45,65,85,105,125,145,165,185,205,225 \
    --min-count 2 \
    -t 18 \
    --memory 161061273600
echo 'Completed: megahit_group_groups_size_5_group_36'


# Group: group_groups_size_5_group_37 (5 samples)

# Step 1: Concatenate 5 R1 files
echo 'Running: concat_r1_group_groups_size_5_group_37'
cat samples/subset_50/sample_060_rrna_removed_R1.fastq samples/subset_50/sample_056_rrna_removed_R1.fastq samples/subset_50/sample_024_rrna_removed_R1.fastq samples/subset_50/sample_008_rrna_removed_R1.fastq samples/subset_50/sample_009_rrna_removed_R1.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_37/concatenated_R1.fastq
echo 'Completed: concat_r1_group_groups_size_5_group_37'


# Step 2: Concatenate 5 R2 files
echo 'Running: concat_r2_group_groups_size_5_group_37'
cat samples/subset_50/sample_060_rrna_removed_R2.fastq samples/subset_50/sample_056_rrna_removed_R2.fastq samples/subset_50/sample_024_rrna_removed_R2.fastq samples/subset_50/sample_008_rrna_removed_R2.fastq samples/subset_50/sample_009_rrna_removed_R2.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_37/concatenated_R2.fastq
echo 'Completed: concat_r2_group_groups_size_5_group_37'


# Step 3: MEGAHIT assembly of concatenated reads (5 samples)
echo 'Running: megahit_group_groups_size_5_group_37'
megahit \
    -1 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_37/concatenated_R1.fastq \
    -2 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_37/concatenated_R2.fastq \
    -o results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_37/megahit_assembly \
    --min-contig-len 500 \
    --k-list 45,65,85,105,125,145,165,185,205,225 \
    --min-count 2 \
    -t 18 \
    --memory 161061273600
echo 'Completed: megahit_group_groups_size_5_group_37'


# Group: group_groups_size_5_group_38 (5 samples)

# Step 1: Concatenate 5 R1 files
echo 'Running: concat_r1_group_groups_size_5_group_38'
cat samples/subset_50/sample_109_rrna_removed_R1.fastq samples/subset_50/sample_152_rrna_removed_R1.fastq samples/subset_50/sample_023_rrna_removed_R1.fastq samples/subset_50/sample_140_rrna_removed_R1.fastq samples/subset_50/sample_174_rrna_removed_R1.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_38/concatenated_R1.fastq
echo 'Completed: concat_r1_group_groups_size_5_group_38'


# Step 2: Concatenate 5 R2 files
echo 'Running: concat_r2_group_groups_size_5_group_38'
cat samples/subset_50/sample_109_rrna_removed_R2.fastq samples/subset_50/sample_152_rrna_removed_R2.fastq samples/subset_50/sample_023_rrna_removed_R2.fastq samples/subset_50/sample_140_rrna_removed_R2.fastq samples/subset_50/sample_174_rrna_removed_R2.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_38/concatenated_R2.fastq
echo 'Completed: concat_r2_group_groups_size_5_group_38'


# Step 3: MEGAHIT assembly of concatenated reads (5 samples)
echo 'Running: megahit_group_groups_size_5_group_38'
megahit \
    -1 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_38/concatenated_R1.fastq \
    -2 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_38/concatenated_R2.fastq \
    -o results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_38/megahit_assembly \
    --min-contig-len 500 \
    --k-list 45,65,85,105,125,145,165,185,205,225 \
    --min-count 2 \
    -t 18 \
    --memory 161061273600
echo 'Completed: megahit_group_groups_size_5_group_38'


# Group: group_groups_size_5_group_39 (5 samples)

# Step 1: Concatenate 5 R1 files
echo 'Running: concat_r1_group_groups_size_5_group_39'
cat samples/subset_50/sample_027_rrna_removed_R1.fastq samples/subset_50/sample_189_rrna_removed_R1.fastq samples/subset_50/sample_036_rrna_removed_R1.fastq samples/subset_50/sample_058_rrna_removed_R1.fastq samples/subset_50/sample_063_rrna_removed_R1.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_39/concatenated_R1.fastq
echo 'Completed: concat_r1_group_groups_size_5_group_39'


# Step 2: Concatenate 5 R2 files
echo 'Running: concat_r2_group_groups_size_5_group_39'
cat samples/subset_50/sample_027_rrna_removed_R2.fastq samples/subset_50/sample_189_rrna_removed_R2.fastq samples/subset_50/sample_036_rrna_removed_R2.fastq samples/subset_50/sample_058_rrna_removed_R2.fastq samples/subset_50/sample_063_rrna_removed_R2.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_39/concatenated_R2.fastq
echo 'Completed: concat_r2_group_groups_size_5_group_39'


# Step 3: MEGAHIT assembly of concatenated reads (5 samples)
echo 'Running: megahit_group_groups_size_5_group_39'
megahit \
    -1 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_39/concatenated_R1.fastq \
    -2 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_39/concatenated_R2.fastq \
    -o results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_39/megahit_assembly \
    --min-contig-len 500 \
    --k-list 45,65,85,105,125,145,165,185,205,225 \
    --min-count 2 \
    -t 18 \
    --memory 161061273600
echo 'Completed: megahit_group_groups_size_5_group_39'


# Group: group_groups_size_5_group_40 (5 samples)

# Step 1: Concatenate 5 R1 files
echo 'Running: concat_r1_group_groups_size_5_group_40'
cat samples/subset_50/sample_071_rrna_removed_R1.fastq samples/subset_50/sample_190_rrna_removed_R1.fastq samples/subset_50/sample_007_rrna_removed_R1.fastq samples/subset_50/sample_029_rrna_removed_R1.fastq samples/subset_50/sample_164_rrna_removed_R1.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_40/concatenated_R1.fastq
echo 'Completed: concat_r1_group_groups_size_5_group_40'


# Step 2: Concatenate 5 R2 files
echo 'Running: concat_r2_group_groups_size_5_group_40'
cat samples/subset_50/sample_071_rrna_removed_R2.fastq samples/subset_50/sample_190_rrna_removed_R2.fastq samples/subset_50/sample_007_rrna_removed_R2.fastq samples/subset_50/sample_029_rrna_removed_R2.fastq samples/subset_50/sample_164_rrna_removed_R2.fastq > results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_40/concatenated_R2.fastq
echo 'Completed: concat_r2_group_groups_size_5_group_40'


# Step 3: MEGAHIT assembly of concatenated reads (5 samples)
echo 'Running: megahit_group_groups_size_5_group_40'
megahit \
    -1 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_40/concatenated_R1.fastq \
    -2 results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_40/concatenated_R2.fastq \
    -o results/focused_assemblies/stage1_megahit/focused_strategies_groups_size_5/group_groups_size_5_group_40/megahit_assembly \
    --min-contig-len 500 \
    --k-list 45,65,85,105,125,145,165,185,205,225 \
    --min-count 2 \
    -t 18 \
    --memory 161061273600
echo 'Completed: megahit_group_groups_size_5_group_40'


echo "End time: $(date)"
echo "stage1 completed for strategy: focused_strategies_groups_size_5"
