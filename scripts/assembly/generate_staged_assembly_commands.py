#!/usr/bin/env python3
"""
Generate staged assembly commands following hecatomb workflow:
Stage 1: MEGAHIT assemblies (individual/grouped)
Stage 2: Concatenate assemblies by condition
Stage 3: Flye meta-assembly per condition
Final result: 8 assemblies for comparison

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

    if not r1_file.exists() or not r2_file.exists():
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

def generate_megahit_commands_individual(samples_dir, output_dir):
    """Generate MEGAHIT commands for individual sample assemblies."""
    sample_ids = get_all_samples(samples_dir)
    commands = []

    print(f"Generating individual MEGAHIT commands for {len(sample_ids)} samples...")

    for sample_id in sample_ids:
        r1_file, r2_file = find_sample_files(sample_id, samples_dir)

        if r1_file and r2_file:
            sample_output = Path(output_dir) / "megahit_individual" / sample_id

            cmd = (f"megahit -1 {r1_file} -2 {r2_file} "
                   f"-o {sample_output} "
                   f"--out-prefix {sample_id} "
                   f"--min-contig-len 500 "
                   f"--k-min 45 --k-max 225 --k-step 26 --min-count 2 "
                   f"-t 8")

            commands.append({
                'command': cmd,
                'condition': 'individual',
                'stage': 'megahit',
                'group_id': sample_id,
                'n_samples': 1,
                'output_dir': str(sample_output),
                'samples': [sample_id],
                'contigs_file': str(sample_output / f"{sample_id}.contigs.fa")
            })
        else:
            print(f"  Warning: Files not found for {sample_id}")

    print(f"  Generated {len(commands)} individual MEGAHIT commands")
    return commands

def generate_megahit_commands_grouped(groups_file, samples_dir, output_dir, condition_name):
    """Generate MEGAHIT commands for grouped assemblies (k-mer or random)."""
    with open(groups_file) as f:
        results = json.load(f)

    commands = []
    groups = results.get('groups', [])

    print(f"Generating {condition_name} MEGAHIT commands for {len(groups)} groups...")

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
        group_output = Path(output_dir) / f"megahit_{condition_name}" / group_id

        cmd = (f"megahit -1 {r1_list} -2 {r2_list} "
               f"-o {group_output} "
               f"--out-prefix {group_id} "
               f"--min-contig-len 500 "
               f"--k-min 45 --k-max 225 --k-step 26 --min-count 2 "
               f"-t 16")

        commands.append({
            'command': cmd,
            'condition': condition_name,
            'stage': 'megahit',
            'group_id': group_id,
            'n_samples': len(valid_samples),
            'output_dir': str(group_output),
            'samples': valid_samples,
            'contigs_file': str(group_output / f"{group_id}.contigs.fa")
        })

    print(f"  Generated {len(commands)} {condition_name} MEGAHIT commands")
    return commands

def generate_megahit_command_global(samples_dir, output_dir):
    """Generate MEGAHIT command for global assembly (all samples together)."""
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

    print(f"Generating global MEGAHIT command for {len(valid_samples)} samples...")

    r1_list = ",".join(r1_files)
    r2_list = ",".join(r2_files)
    global_output = Path(output_dir) / "megahit_global" / "global_all_samples"

    cmd = (f"megahit -1 {r1_list} -2 {r2_list} "
           f"-o {global_output} "
           f"--out-prefix global_assembly "
           f"--min-contig-len 500 "
           f"--k-min 45 --k-max 225 --k-step 26 --min-count 2 "
           f"-t 20")

    command = [{
        'command': cmd,
        'condition': 'global',
        'stage': 'megahit',
        'group_id': 'global_all_samples',
        'n_samples': len(valid_samples),
        'output_dir': str(global_output),
        'samples': valid_samples,
        'contigs_file': str(global_output / "global_assembly.contigs.fa")
    }]

    print(f"  Generated global MEGAHIT command")
    return command

def generate_concatenation_commands(megahit_commands, output_dir):
    """Generate commands to concatenate MEGAHIT assemblies by condition."""

    # Group MEGAHIT commands by condition
    by_condition = {}
    for cmd_info in megahit_commands:
        condition = cmd_info['condition']
        if condition not in by_condition:
            by_condition[condition] = []
        by_condition[condition].append(cmd_info)

    concat_commands = []

    for condition, commands in by_condition.items():
        if condition == 'global':
            # Global assembly doesn't need concatenation
            continue

        # Input files are the contigs from MEGAHIT
        input_files = [cmd['contigs_file'] for cmd in commands]

        # Output concatenated file
        concat_output = Path(output_dir) / "concatenated" / f"{condition}_all_contigs.fasta"
        concat_output.parent.mkdir(parents=True, exist_ok=True)

        # Create concatenation command
        cmd = f"cat {' '.join(input_files)} > {concat_output}"

        concat_commands.append({
            'command': cmd,
            'condition': condition,
            'stage': 'concatenate',
            'input_files': input_files,
            'output_file': str(concat_output),
            'n_input_assemblies': len(input_files)
        })

        print(f"  Generated concatenation command for {condition} ({len(input_files)} assemblies)")

    return concat_commands

def generate_flye_commands(concat_commands, megahit_commands, output_dir):
    """Generate Flye meta-assembly commands."""

    flye_commands = []

    # Flye commands for concatenated conditions (individual, random seeds, kmer)
    for concat_cmd in concat_commands:
        condition = concat_cmd['condition']
        input_file = concat_cmd['output_file']

        flye_output_dir = Path(output_dir) / "flye_meta" / condition
        assembly_output = flye_output_dir / "assembly.fasta"
        final_output = Path(output_dir) / "final_assemblies" / f"{condition}_meta_assembly.fasta"

        cmd = (f"flye --subassemblies {input_file} "
               f"-t 16 --plasmids -o {flye_output_dir} -g 1g")

        flye_commands.append({
            'command': cmd,
            'condition': condition,
            'stage': 'flye_meta',
            'input_file': input_file,
            'output_dir': str(flye_output_dir),
            'assembly_file': str(assembly_output),
            'final_file': str(final_output),
            'copy_command': f"cp {assembly_output} {final_output}"
        })

    # Handle global assembly (just copy, no Flye needed)
    global_commands = [cmd for cmd in megahit_commands if cmd['condition'] == 'global']
    if global_commands:
        global_cmd = global_commands[0]
        global_contigs = global_cmd['contigs_file']
        final_global = Path(output_dir) / "final_assemblies" / "global_assembly.fasta"

        flye_commands.append({
            'command': f"cp {global_contigs} {final_global}",
            'condition': 'global',
            'stage': 'copy_global',
            'input_file': global_contigs,
            'final_file': str(final_global),
            'copy_command': f"cp {global_contigs} {final_global}"
        })

    print(f"Generated {len(flye_commands)} Flye/copy commands")
    return flye_commands

def write_staged_scripts(all_commands, scripts_dir):
    """Write separate SLURM scripts for each stage."""

    # Group commands by stage
    by_stage = {}
    for cmd_info in all_commands:
        stage = cmd_info['stage']
        if stage not in by_stage:
            by_stage[stage] = []
        by_stage[stage].append(cmd_info)

    script_files = []

    for stage, commands in by_stage.items():
        print(f"\\nWriting {stage} script ({len(commands)} jobs)...")

        # Resource allocation by stage
        if stage == 'megahit':
            # Determine resources by condition
            individual_cmds = [c for c in commands if c['condition'] == 'individual']
            grouped_cmds = [c for c in commands if c['condition'] in ['random_42', 'random_43', 'random_44', 'random_45', 'random_46', 'kmer']]
            global_cmds = [c for c in commands if c['condition'] == 'global']

            # Write separate scripts for different resource needs
            if individual_cmds:
                script_files.append(write_megahit_script(individual_cmds, "individual", scripts_dir, 8, "32G", "12:00:00"))
            if grouped_cmds:
                script_files.append(write_megahit_script(grouped_cmds, "grouped", scripts_dir, 16, "64G", "24:00:00"))
            if global_cmds:
                script_files.append(write_megahit_script(global_cmds, "global", scripts_dir, 20, "128G", "36:00:00"))

        elif stage == 'concatenate':
            script_files.append(write_simple_script(commands, f"run_{stage}.sh", scripts_dir, 2, "8G", "2:00:00"))

        elif stage == 'flye_meta':
            script_files.append(write_simple_script(commands, f"run_{stage}.sh", scripts_dir, 16, "64G", "24:00:00"))

        elif stage == 'copy_global':
            script_files.append(write_simple_script(commands, f"run_{stage}.sh", scripts_dir, 1, "4G", "1:00:00"))

    return script_files

def write_megahit_script(commands, suffix, scripts_dir, threads, memory, time_limit):
    """Write MEGAHIT-specific script with cleanup."""

    script_file = f"run_megahit_{suffix}.sh"
    script_path = Path(scripts_dir) / script_file

    script_content = f"""#!/bin/bash
#SBATCH --job-name=megahit_{suffix}
#SBATCH --time={time_limit}
#SBATCH --mem={memory}
#SBATCH --cpus-per-task={threads}
#SBATCH --array=1-{len(commands)}
#SBATCH --output=logs/megahit_{suffix}_%A_%a.out
#SBATCH --error=logs/megahit_{suffix}_%A_%a.err
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=megan.j@wustl.edu

echo "Starting MEGAHIT {suffix} assembly: $(date)"
echo "Job ID: $SLURM_JOB_ID"
echo "Array task ID: $SLURM_ARRAY_TASK_ID"

# Load environment
source /ref/sahlab/software/miniforge3/bin/activate
conda activate coassembly_env

# Check MEGAHIT availability
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

# Array of output directories and cleanup info
declare -a OUTPUT_DIRS=(
"""

    for cmd_info in commands:
        script_content += f'    "{cmd_info["output_dir"]}"\n'

    script_content += f"""
)

declare -a SAMPLE_INFO=(
"""

    for cmd_info in commands:
        script_content += f'    "{cmd_info["group_id"]} ({cmd_info["n_samples"]} samples)"\n'

    script_content += f"""
)

# Get command for this array task
TASK_ID=$((SLURM_ARRAY_TASK_ID - 1))
COMMAND="${{COMMANDS[$TASK_ID]}}"
OUTPUT_DIR="${{OUTPUT_DIRS[$TASK_ID]}}"
SAMPLE_INFO="${{SAMPLE_INFO[$TASK_ID]}}"

echo "Processing: $SAMPLE_INFO"
echo "Output directory: $OUTPUT_DIR"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Run MEGAHIT
echo "Starting MEGAHIT: $(date)"
eval $COMMAND

# Check results and rename contigs file appropriately
if [ -f "$OUTPUT_DIR"/*.contigs.fa ]; then
    # Find the contigs file (might have different prefix)
    CONTIGS_FILE=$(find "$OUTPUT_DIR" -name "*.contigs.fa" | head -1)

    if [ -n "$CONTIGS_FILE" ]; then
        echo "✓ MEGAHIT completed successfully: $(date)"

        # Basic stats
        n_contigs=$(grep -c ">" "$CONTIGS_FILE" || echo "0")
        total_len=$(awk '!/^>/' "$CONTIGS_FILE" | tr -d '\\n' | wc -c || echo "0")

        echo "  Contigs: $n_contigs"
        echo "  Total length: $total_len bp"

        # Cleanup intermediate files but keep contigs
        find "$OUTPUT_DIR" -type f -name "*.tmp.*" -delete 2>/dev/null || true
        find "$OUTPUT_DIR" -type f -name "*.edges.*" -delete 2>/dev/null || true

    else
        echo "ERROR: No contigs file found in $OUTPUT_DIR"
        exit 1
    fi
else
    echo "ERROR: MEGAHIT failed - no contigs found in $OUTPUT_DIR"
    ls -la "$OUTPUT_DIR" || echo "Output directory not found"
    exit 1
fi

echo "MEGAHIT {suffix} task completed: $(date)"
"""

    with open(script_path, 'w') as f:
        f.write(script_content)

    script_path.chmod(0o755)
    return str(script_path)

def write_simple_script(commands, script_name, scripts_dir, threads, memory, time_limit):
    """Write simple script for concatenation/flye stages."""

    script_path = Path(scripts_dir) / script_name

    script_content = f"""#!/bin/bash
#SBATCH --job-name={script_name.replace('.sh', '')}
#SBATCH --time={time_limit}
#SBATCH --mem={memory}
#SBATCH --cpus-per-task={threads}
#SBATCH --array=1-{len(commands)}
#SBATCH --output=logs/{script_name.replace('.sh', '')}_%A_%a.out
#SBATCH --error=logs/{script_name.replace('.sh', '')}_%A_%a.err
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=megan.j@wustl.edu

echo "Starting {script_name.replace('.sh', '')} job: $(date)"
echo "Job ID: $SLURM_JOB_ID"
echo "Array task ID: $SLURM_ARRAY_TASK_ID"

# Load environment
source /ref/sahlab/software/miniforge3/bin/activate
conda activate coassembly_env

# Array of commands
declare -a COMMANDS=(
"""

    for cmd_info in commands:
        # For Flye commands, we need both the main command and copy command
        if 'copy_command' in cmd_info:
            full_cmd = cmd_info['command'] + " && " + cmd_info['copy_command']
        else:
            full_cmd = cmd_info['command']

        full_cmd = full_cmd.replace('"', '\\"')
        script_content += f'    "{full_cmd}"\n'

    script_content += f"""
)

# Get command for this array task
TASK_ID=$((SLURM_ARRAY_TASK_ID - 1))
COMMAND="${{COMMANDS[$TASK_ID]}}"

echo "Command: $COMMAND"

# Create output directories
mkdir -p results/concatenated results/flye_meta results/final_assemblies

# Execute command
echo "Starting execution: $(date)"
eval $COMMAND

echo "Task completed: $(date)"
"""

    with open(script_path, 'w') as f:
        f.write(script_content)

    script_path.chmod(0o755)
    return str(script_path)

def main():
    parser = argparse.ArgumentParser(description="Generate staged assembly commands for hecatomb-style workflow")
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

    print("Staged Assembly Command Generator (Hecatomb-style)")
    print("=" * 60)
    print(f"Samples directory: {args.samples_dir}")
    print(f"K-mer groups: {args.kmer_groups}")
    print(f"Random groups dir: {args.random_groups_dir}")
    print(f"Output directory: {args.output_dir}")
    print()

    # Create output directories
    output_path = Path(args.output_dir)
    for subdir in ['megahit_individual', 'megahit_global', 'concatenated', 'flye_meta', 'final_assemblies']:
        (output_path / subdir).mkdir(parents=True, exist_ok=True)

    all_commands = []

    # Stage 1: Generate MEGAHIT commands
    print("\\n" + "="*60)
    print("STAGE 1: MEGAHIT ASSEMBLIES")
    print("="*60)

    # Individual assemblies
    individual_commands = generate_megahit_commands_individual(
        args.samples_dir, args.output_dir
    )
    all_commands.extend(individual_commands)

    # K-mer grouping assemblies
    kmer_commands = generate_megahit_commands_grouped(
        args.kmer_groups, args.samples_dir, args.output_dir, "kmer"
    )
    all_commands.extend(kmer_commands)

    # Random grouping assemblies
    random_files = list(Path(args.random_groups_dir).glob("*/assembly_recommendations.json"))
    for random_file in sorted(random_files):
        seed_dir = random_file.parent.name  # e.g., "random_seed_42"
        seed_num = seed_dir.split('_')[-1]  # e.g., "42"
        condition_name = f"random_{seed_num}"

        random_commands = generate_megahit_commands_grouped(
            random_file, args.samples_dir, args.output_dir, condition_name
        )
        all_commands.extend(random_commands)

    # Global assembly
    global_commands = generate_megahit_command_global(
        args.samples_dir, args.output_dir
    )
    all_commands.extend(global_commands)

    # Stage 2: Generate concatenation commands
    print("\\n" + "="*60)
    print("STAGE 2: CONCATENATION")
    print("="*60)

    megahit_commands = [cmd for cmd in all_commands if cmd['stage'] == 'megahit']
    concat_commands = generate_concatenation_commands(megahit_commands, args.output_dir)
    all_commands.extend(concat_commands)

    # Stage 3: Generate Flye commands
    print("\\n" + "="*60)
    print("STAGE 3: FLYE META-ASSEMBLY")
    print("="*60)

    flye_commands = generate_flye_commands(concat_commands, megahit_commands, args.output_dir)
    all_commands.extend(flye_commands)

    # Write SLURM scripts
    print("\\n" + "="*60)
    print("WRITING SLURM SCRIPTS")
    print("="*60)

    script_files = write_staged_scripts(all_commands, args.scripts_dir)

    # Summary
    print("\\n" + "="*60)
    print("STAGED ASSEMBLY GENERATION COMPLETE")
    print("="*60)

    # Count by stage and condition
    by_stage = {}
    by_condition = {}
    for cmd in all_commands:
        stage = cmd['stage']
        condition = cmd.get('condition', 'unknown')

        by_stage[stage] = by_stage.get(stage, 0) + 1
        by_condition[condition] = by_condition.get(condition, 0) + 1

    print("\\nCommands by stage:")
    for stage, count in sorted(by_stage.items()):
        print(f"  {stage}: {count} jobs")

    print("\\nMEGAHIT assemblies by condition:")
    megahit_by_condition = {}
    for cmd in all_commands:
        if cmd['stage'] == 'megahit':
            condition = cmd['condition']
            megahit_by_condition[condition] = megahit_by_condition.get(condition, 0) + 1

    for condition, count in sorted(megahit_by_condition.items()):
        print(f"  {condition}: {count} assemblies")

    print(f"\\nSLURM scripts created:")
    for script in sorted(script_files):
        print(f"  {script}")

    print(f"\\nFinal result: 8 assemblies in {args.output_dir}/final_assemblies/")
    print("  - individual_meta_assembly.fasta")
    print("  - random_42_meta_assembly.fasta")
    print("  - random_43_meta_assembly.fasta")
    print("  - random_44_meta_assembly.fasta")
    print("  - random_45_meta_assembly.fasta")
    print("  - random_46_meta_assembly.fasta")
    print("  - kmer_meta_assembly.fasta")
    print("  - global_assembly.fasta")

    print("\\nNext step: Submit SLURM scripts in order:")
    print("1. Submit all MEGAHIT scripts (can run in parallel)")
    print("2. Wait for completion, then submit concatenation")
    print("3. Wait for completion, then submit Flye meta-assembly")

if __name__ == "__main__":
    main()