#!/usr/bin/env python3
"""
Generate MEGAHIT assembly commands for both k-mer and random groupings.
Handles the specific naming convention: {sample_id}_rrna_removed_R{1,2}.fastq
"""
import json
from pathlib import Path
import argparse

def find_sample_files(sample_id, samples_dir):
    """Find R1 and R2 files for a sample ID."""
    samples_path = Path(samples_dir)

    r1_file = samples_path / f"{sample_id}_rrna_removed_R1.fastq"
    r2_file = samples_path / f"{sample_id}_rrna_removed_R2.fastq"

    if not r1_file.exists():
        print(f"Warning: R1 file not found for {sample_id}: {r1_file}")
        return None, None

    if not r2_file.exists():
        print(f"Warning: R2 file not found for {sample_id}: {r2_file}")
        return None, None

    return str(r1_file), str(r2_file)

def generate_megahit_commands(groups_file, samples_dir, output_dir, prefix):
    """Generate MEGAHIT assembly commands from groupings."""

    with open(groups_file) as f:
        results = json.load(f)

    samples_path = Path(samples_dir)
    output_path = Path(output_dir)
    commands = []
    failed_groups = []

    print(f"Generating assembly commands for {len(results.get('groups', []))} groups...")

    for group in results.get('groups', []):
        group_id = group['group_id']
        samples = group['samples']

        print(f"Processing {group_id}: {len(samples)} samples")

        # Build file lists for paired-end
        r1_files = []
        r2_files = []
        missing_files = []

        for sample in samples:
            r1_file, r2_file = find_sample_files(sample, samples_dir)

            if r1_file and r2_file:
                r1_files.append(r1_file)
                r2_files.append(r2_file)
            else:
                missing_files.append(sample)

        if missing_files:
            print(f"  Warning: {len(missing_files)} samples missing files: {missing_files}")

        if len(r1_files) == 0:
            print(f"  Error: No valid files found for {group_id}")
            failed_groups.append(group_id)
            continue

        # Create MEGAHIT command
        r1_list = ",".join(r1_files)
        r2_list = ",".join(r2_files)

        # Output directory for this group
        group_output = output_path / f"{prefix}_{group_id}"

        cmd = (f"megahit -1 {r1_list} -2 {r2_list} "
               f"-o {group_output} "
               f"--out-prefix {prefix}_{group_id} "
               f"--min-contig-len 500 "
               f"--k-list 21,29,39,59,79,99 "
               f"--num-cpu-threads 16")

        commands.append({
            'command': cmd,
            'group_id': group_id,
            'n_samples': len(samples),
            'n_files': len(r1_files),
            'output_dir': str(group_output)
        })

    if failed_groups:
        print(f"Warning: {len(failed_groups)} groups failed: {failed_groups}")

    print(f"Generated {len(commands)} assembly commands")
    return commands

def write_assembly_script(commands, script_file, job_name, output_dir):
    """Write commands to executable SLURM array job script."""

    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    script_content = f"""#!/bin/bash
#SBATCH --job-name={job_name}
#SBATCH --time=24:00:00
#SBATCH --mem=120G
#SBATCH --cpus-per-task=16
#SBATCH --array=1-{len(commands)}
#SBATCH --output=logs/{job_name}_%A_%a.out
#SBATCH --error=logs/{job_name}_%A_%a.err
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=megan.j@your-institution.edu  # Edit this email

echo "Starting assembly job: $(date)"
echo "Job ID: $SLURM_JOB_ID"
echo "Array task ID: $SLURM_ARRAY_TASK_ID"
echo "Node: $SLURM_NODELIST"

# Load conda environment
source /ref/sahlab/software/miniforge3/bin/activate
conda activate metagrouper_env

# Check if megahit is available
if ! command -v megahit &> /dev/null; then
    echo "ERROR: megahit not found in PATH"
    echo "Available assemblers:"
    which -a megahit || echo "  megahit: not found"
    exit 1
fi

echo "MEGAHIT version: $(megahit --version)"

# Array of commands
declare -a COMMANDS=(
"""

    for cmd_info in commands:
        # Escape quotes in command
        cmd = cmd_info['command'].replace('"', '\\"')
        script_content += f'    "{cmd}"\n'

    script_content += f"""
)

# Array of output directories (for cleanup)
declare -a OUTPUT_DIRS=(
"""

    for cmd_info in commands:
        script_content += f'    "{cmd_info["output_dir"]}"\n'

    script_content += f"""
)

# Get command for this array task
TASK_ID=$((SLURM_ARRAY_TASK_ID - 1))
COMMAND="${{COMMANDS[$TASK_ID]}}"
OUTPUT_DIR="${{OUTPUT_DIRS[$TASK_ID]}}"

echo "Command: $COMMAND"
echo "Output directory: $OUTPUT_DIR"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Run assembly
echo "Starting MEGAHIT: $(date)"
eval $COMMAND

# Check if assembly succeeded
if [ -f "$OUTPUT_DIR/final.contigs.fa" ]; then
    echo "✓ Assembly completed successfully: $(date)"

    # Basic stats
    n_contigs=$(grep -c ">" "$OUTPUT_DIR/final.contigs.fa")
    echo "Number of contigs: $n_contigs"

    # Total length
    total_len=$(awk '!/^>/' "$OUTPUT_DIR/final.contigs.fa" | tr -d '\\n' | wc -c)
    echo "Total assembly length: $total_len bp"

else
    echo "ERROR: Assembly failed - no final.contigs.fa found"
    echo "Checking intermediate files..."
    ls -la "$OUTPUT_DIR" || echo "Output directory not found"
    exit 1
fi

echo "Assembly task completed: $(date)"
"""

    # Write script
    with open(script_file, 'w') as f:
        f.write(script_content)

    # Make executable
    Path(script_file).chmod(0o755)

    print(f"Assembly script written to: {script_file}")
    print(f"Submit with: sbatch {script_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate assembly commands")
    parser.add_argument("groups_file", help="JSON file with group definitions")
    parser.add_argument("--samples-dir", default="samples/subset_50",
                       help="Directory with FASTQ files")
    parser.add_argument("--output-dir", required=True,
                       help="Assembly output directory")
    parser.add_argument("--script-name", required=True,
                       help="Output script filename")
    parser.add_argument("--prefix", required=True,
                       help="Assembly directory prefix (kmer/random)")
    parser.add_argument("--job-name", help="SLURM job name (auto-generated if not provided)")

    args = parser.parse_args()

    # Auto-generate job name if not provided
    if not args.job_name:
        args.job_name = f"assembly_{args.prefix}"

    print("Assembly Command Generator")
    print("=" * 40)
    print(f"Groups file: {args.groups_file}")
    print(f"Samples directory: {args.samples_dir}")
    print(f"Output directory: {args.output_dir}")
    print(f"Script name: {args.script_name}")
    print(f"Prefix: {args.prefix}")
    print(f"Job name: {args.job_name}")
    print()

    # Check input file exists
    if not Path(args.groups_file).exists():
        print(f"ERROR: Groups file not found: {args.groups_file}")
        exit(1)

    # Check samples directory exists
    if not Path(args.samples_dir).exists():
        print(f"ERROR: Samples directory not found: {args.samples_dir}")
        exit(1)

    # Generate commands
    commands = generate_megahit_commands(
        args.groups_file, args.samples_dir, args.output_dir, args.prefix
    )

    if not commands:
        print("ERROR: No valid assembly commands generated")
        exit(1)

    # Write script
    write_assembly_script(commands, args.script_name, args.job_name, args.output_dir)

    print(f"\\n✓ Generated {len(commands)} assembly commands")
    print(f"✓ Script ready: {args.script_name}")
    print(f"\\nNext step: sbatch {args.script_name}")