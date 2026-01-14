#!/usr/bin/env python3
"""
Generate MEGAHIT assembly commands for all experimental conditions:
1. Individual assemblies (50 separate assemblies)
2. Random groupings (5 different seeds)
3. K-mer grouping (1 grouping from MetaGrouper)
4. Global assembly (all 50 samples together)
"""
import json
from pathlib import Path
import argparse
import glob

def find_sample_files(sample_id, samples_dir):
    """Find R1 and R2 files for a sample ID."""
    samples_path = Path(samples_dir)

    r1_file = samples_path / f"{sample_id}_rrna_removed_R1.fastq"
    r2_file = samples_path / f"{sample_id}_rrna_removed_R2.fastq"

    if not r1_file.exists():
        return None, None

    if not r2_file.exists():
        return None, None

    return str(r1_file), str(r2_file)

def get_all_samples(samples_dir):
    """Get list of all sample IDs from directory."""
    samples_path = Path(samples_dir)
    r1_files = list(samples_path.glob("*_rrna_removed_R1.fastq"))

    sample_ids = []
    for r1_file in r1_files:
        sample_id = r1_file.name.replace("_rrna_removed_R1.fastq", "")
        sample_ids.append(sample_id)

    return sorted(sample_ids)

def generate_individual_commands(samples_dir, output_dir):
    """Generate commands for individual sample assemblies."""
    sample_ids = get_all_samples(samples_dir)
    commands = []

    print(f"Generating individual assembly commands for {len(sample_ids)} samples...")

    for sample_id in sample_ids:
        r1_file, r2_file = find_sample_files(sample_id, samples_dir)

        if r1_file and r2_file:
            sample_output = Path(output_dir) / f"individual_{sample_id}"

            cmd = (f"megahit -1 {r1_file} -2 {r2_file} "
                   f"-o {sample_output} "
                   f"--out-prefix {sample_id} "
                   f"--min-contig-len 500 "
                   f"--k-list 21,29,39,59,79,99 "
                   f"--num-cpu-threads 8")  # Smaller threads for individual assemblies

            commands.append({
                'command': cmd,
                'condition': 'individual',
                'group_id': f"individual_{sample_id}",
                'n_samples': 1,
                'output_dir': str(sample_output),
                'samples': [sample_id]
            })
        else:
            print(f"  Warning: Files not found for {sample_id}")

    print(f"  Generated {len(commands)} individual assembly commands")
    return commands

def generate_global_command(samples_dir, output_dir):
    """Generate command for global assembly (all samples together)."""
    sample_ids = get_all_samples(samples_dir)

    r1_files = []
    r2_files = []
    valid_samples = []

    for sample_id in sample_ids:
        r1_file, r2_file = find_sample_files(sample_id, samples_dir)
        if r1_file and r2_file:
            r1_files.append(r1_file)
            r2_files.append(r2_file)
            valid_samples.append(sample_id)

    if not r1_files:
        print("ERROR: No valid sample files found for global assembly")
        return []

    print(f"Generating global assembly command for {len(valid_samples)} samples...")

    r1_list = ",".join(r1_files)
    r2_list = ",".join(r2_files)
    global_output = Path(output_dir) / "global_all_samples"

    cmd = (f"megahit -1 {r1_list} -2 {r2_list} "
           f"-o {global_output} "
           f"--out-prefix global_assembly "
           f"--min-contig-len 500 "
           f"--k-list 21,29,39,59,79,99 "
           f"--num-cpu-threads 20")  # More threads for large assembly

    command = [{
        'command': cmd,
        'condition': 'global',
        'group_id': 'global_all_samples',
        'n_samples': len(valid_samples),
        'output_dir': str(global_output),
        'samples': valid_samples
    }]

    print(f"  Generated global assembly command")
    return command

def generate_grouped_commands(groups_file, samples_dir, output_dir, condition_name):
    """Generate commands for grouped assemblies (k-mer or random)."""
    with open(groups_file) as f:
        results = json.load(f)

    commands = []
    groups = results.get('groups', [])

    print(f"Generating {condition_name} assembly commands for {len(groups)} groups...")

    for group in groups:
        group_id = group['group_id']
        samples = group['samples']

        r1_files = []
        r2_files = []
        valid_samples = []

        for sample in samples:
            r1_file, r2_file = find_sample_files(sample, samples_dir)
            if r1_file and r2_file:
                r1_files.append(r1_file)
                r2_files.append(r2_file)
                valid_samples.append(sample)

        if len(r1_files) == 0:
            print(f"  Warning: No valid files found for {group_id}")
            continue

        r1_list = ",".join(r1_files)
        r2_list = ",".join(r2_files)
        group_output = Path(output_dir) / f"{condition_name}_{group_id}"

        cmd = (f"megahit -1 {r1_list} -2 {r2_list} "
               f"-o {group_output} "
               f"--out-prefix {group_id} "
               f"--min-contig-len 500 "
               f"--k-list 21,29,39,59,79,99 "
               f"--num-cpu-threads 16")

        commands.append({
            'command': cmd,
            'condition': condition_name,
            'group_id': f"{condition_name}_{group_id}",
            'n_samples': len(valid_samples),
            'output_dir': str(group_output),
            'samples': valid_samples
        })

    print(f"  Generated {len(commands)} {condition_name} assembly commands")
    return commands

def write_assembly_scripts(all_commands, base_output_dir):
    """Write separate SLURM scripts for each condition."""

    # Group commands by condition
    conditions = {}
    for cmd_info in all_commands:
        condition = cmd_info['condition']
        if condition not in conditions:
            conditions[condition] = []
        conditions[condition].append(cmd_info)

    script_files = []

    for condition, commands in conditions.items():
        print(f"\\nWriting {condition} assembly script ({len(commands)} jobs)...")

        # Determine resource requirements based on condition
        if condition == 'individual':
            time_limit = "8:00:00"
            memory = "32G"
            threads = 8
        elif condition == 'global':
            time_limit = "48:00:00"
            memory = "200G"
            threads = 20
        else:  # grouped conditions
            time_limit = "24:00:00"
            memory = "120G"
            threads = 16

        script_file = f"run_{condition}_assemblies.sh"

        script_content = f"""#!/bin/bash
#SBATCH --job-name={condition}_assembly
#SBATCH --time={time_limit}
#SBATCH --mem={memory}
#SBATCH --cpus-per-task={threads}
#SBATCH --array=1-{len(commands)}
#SBATCH --output=logs/{condition}_assembly_%A_%a.out
#SBATCH --error=logs/{condition}_assembly_%A_%a.err
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=megan.j@your-institution.edu

echo "Starting {condition} assembly job: $(date)"
echo "Job ID: $SLURM_JOB_ID"
echo "Array task ID: $SLURM_ARRAY_TASK_ID"
echo "Node: $SLURM_NODELIST"

# Load conda environment
source /ref/sahlab/software/miniforge3/bin/activate
conda activate metagrouper_env

# Check if megahit is available
if ! command -v megahit &> /dev/null; then
    echo "ERROR: megahit not found in PATH"
    exit 1
fi

echo "MEGAHIT version: $(megahit --version)"

# Array of commands
declare -a COMMANDS=(
"""

        for cmd_info in commands:
            cmd = cmd_info['command'].replace('"', '\\"')
            script_content += f'    "{cmd}"\n'

        script_content += f"""
)

# Array of output directories
declare -a OUTPUT_DIRS=(
"""

        for cmd_info in commands:
            script_content += f'    "{cmd_info["output_dir"]}"\n'

        script_content += f"""
)

# Array of sample info for logging
declare -a SAMPLE_INFO=(
"""

        for cmd_info in commands:
            sample_count = cmd_info['n_samples']
            group_id = cmd_info['group_id']
            script_content += f'    "{group_id} ({sample_count} samples)"\n'

        script_content += f"""
)

# Get command for this array task
TASK_ID=$((SLURM_ARRAY_TASK_ID - 1))
COMMAND="${{COMMANDS[$TASK_ID]}}"
OUTPUT_DIR="${{OUTPUT_DIRS[$TASK_ID]}}"
SAMPLE_INFO="${{SAMPLE_INFO[$TASK_ID]}}"

echo "Processing: $SAMPLE_INFO"
echo "Command: $COMMAND"
echo "Output directory: $OUTPUT_DIR"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Run assembly
echo "Starting MEGAHIT: $(date)"
eval $COMMAND

# Check results
if [ -f "$OUTPUT_DIR/final.contigs.fa" ]; then
    echo "✓ Assembly completed successfully: $(date)"

    # Basic stats
    n_contigs=$(grep -c ">" "$OUTPUT_DIR/final.contigs.fa" || echo "0")
    total_len=$(awk '!/^>/' "$OUTPUT_DIR/final.contigs.fa" | tr -d '\\n' | wc -c || echo "0")

    echo "  Contigs: $n_contigs"
    echo "  Total length: $total_len bp"
else
    echo "ERROR: Assembly failed - no final.contigs.fa found"
    echo "Output directory contents:"
    ls -la "$OUTPUT_DIR" 2>/dev/null || echo "Directory not found"
    exit 1
fi

echo "{condition} assembly task completed: $(date)"
"""

        # Write script
        script_path = Path(base_output_dir) / script_file
        with open(script_path, 'w') as f:
            f.write(script_content)

        script_path.chmod(0o755)
        script_files.append(str(script_path))

        print(f"  Written: {script_path}")

    return script_files

def main():
    parser = argparse.ArgumentParser(description="Generate assembly commands for all experimental conditions")
    parser.add_argument("--samples-dir", default="samples/subset_50",
                       help="Directory with FASTQ files")
    parser.add_argument("--kmer-groups",
                       default="results/kmer_groups/assembly_recommendations.json",
                       help="K-mer grouping file")
    parser.add_argument("--random-groups-dir",
                       default="results/random_groups",
                       help="Directory containing random grouping files")
    parser.add_argument("--output-dir", default="results/assemblies",
                       help="Base output directory for assemblies")
    parser.add_argument("--scripts-dir", default="scripts",
                       help="Directory to write SLURM scripts")

    args = parser.parse_args()

    print("Multi-Condition Assembly Command Generator")
    print("=" * 50)
    print(f"Samples directory: {args.samples_dir}")
    print(f"K-mer groups: {args.kmer_groups}")
    print(f"Random groups dir: {args.random_groups_dir}")
    print(f"Output directory: {args.output_dir}")
    print()

    # Check inputs exist
    if not Path(args.samples_dir).exists():
        print(f"ERROR: Samples directory not found: {args.samples_dir}")
        exit(1)

    if not Path(args.kmer_groups).exists():
        print(f"ERROR: K-mer groups file not found: {args.kmer_groups}")
        exit(1)

    if not Path(args.random_groups_dir).exists():
        print(f"ERROR: Random groups directory not found: {args.random_groups_dir}")
        exit(1)

    # Create output directories
    output_path = Path(args.output_dir)
    for condition in ['individual', 'kmer', 'random', 'global']:
        (output_path / condition).mkdir(parents=True, exist_ok=True)

    all_commands = []

    # 1. Individual assemblies
    print("\\n" + "="*50)
    individual_commands = generate_individual_commands(
        args.samples_dir, output_path / "individual"
    )
    all_commands.extend(individual_commands)

    # 2. K-mer grouping
    print("\\n" + "="*50)
    kmer_commands = generate_grouped_commands(
        args.kmer_groups, args.samples_dir, output_path / "kmer", "kmer"
    )
    all_commands.extend(kmer_commands)

    # 3. Random groupings
    print("\\n" + "="*50)
    random_files = list(Path(args.random_groups_dir).glob("*/assembly_recommendations.json"))

    for random_file in sorted(random_files):
        seed_dir = random_file.parent.name  # e.g., "random_seed_42"
        condition_name = f"random_{seed_dir.split('_')[-1]}"  # e.g., "random_42"

        random_commands = generate_grouped_commands(
            random_file, args.samples_dir, output_path / "random", condition_name
        )
        all_commands.extend(random_commands)

    # 4. Global assembly
    print("\\n" + "="*50)
    global_commands = generate_global_command(
        args.samples_dir, output_path / "global"
    )
    all_commands.extend(global_commands)

    # Write SLURM scripts
    print("\\n" + "="*50)
    print("Writing SLURM scripts...")

    script_files = write_assembly_scripts(all_commands, args.scripts_dir)

    # Summary
    print("\\n" + "="*50)
    print("ASSEMBLY COMMAND GENERATION COMPLETE")
    print("="*50)

    conditions = {}
    for cmd in all_commands:
        condition = cmd['condition']
        conditions[condition] = conditions.get(condition, 0) + 1

    print("\\nGenerated commands:")
    total_jobs = 0
    for condition, count in sorted(conditions.items()):
        print(f"  {condition}: {count} jobs")
        total_jobs += count

    print(f"\\nTotal assembly jobs: {total_jobs}")

    print("\\nSLURM scripts created:")
    for script in sorted(script_files):
        print(f"  {script}")

    print("\\nTo submit all jobs:")
    for script in sorted(script_files):
        script_name = Path(script).name
        print(f"  sbatch scripts/{script_name}")

    print("\\nEstimated runtime:")
    print("  Individual: ~8 hours")
    print("  Random/K-mer: ~24 hours")
    print("  Global: ~48 hours")
    print("\\nNext step: Submit jobs and run quality assessment when complete")

if __name__ == "__main__":
    main()