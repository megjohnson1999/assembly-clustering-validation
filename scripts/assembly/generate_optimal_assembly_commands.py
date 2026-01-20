#!/usr/bin/env python3
"""
Generate assembly commands for optimal grouping strategies.

This script reads the optimal grouping JSON files and generates a 3-stage
assembly pipeline for each strategy:
1. Stage 1: MEGAHIT assemblies (individual/grouped)
2. Stage 2: Concatenate assemblies by strategy
3. Stage 3: Flye meta-assembly per strategy

Result: 17 final assemblies for comparison (individual, global, + 15 grouped strategies)
"""
import json
from pathlib import Path
import argparse
import math


def find_sample_files(sample_id, samples_dir):
    """Find R1 and R2 files for a sample ID."""
    samples_path = Path(samples_dir)

    r1_file = samples_path / f"{sample_id}_rrna_removed_R1.fastq"
    r2_file = samples_path / f"{sample_id}_rrna_removed_R2.fastq"

    if not r1_file.exists() or not r2_file.exists():
        print(f"Warning: Missing files for {sample_id}")
        return None, None

    return str(r1_file), str(r2_file)


def load_strategy_file(strategy_file):
    """Load a strategy JSON file."""
    try:
        with open(strategy_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {strategy_file}: {e}")
        return None


def find_all_strategies(groupings_dir):
    """Find all strategy JSON files in the optimal groupings directory."""
    groupings_path = Path(groupings_dir)
    strategy_files = []

    # Find all assembly_recommendations.json files
    for json_file in groupings_path.rglob("assembly_recommendations.json"):
        strategy_files.append(json_file)

    return sorted(strategy_files)


def generate_concatenation_and_megahit_commands(sample_pairs, output_dir, job_name, threads=8, memory_gb=32):
    """Generate concatenation commands followed by MEGAHIT command for a group of samples."""
    if not sample_pairs:
        return []

    commands = []

    # For multiple samples, first concatenate the reads
    if len(sample_pairs) > 1:
        # Collect all R1 and R2 files
        r1_files = []
        r2_files = []

        for r1, r2 in sample_pairs:
            r1_files.append(r1)
            r2_files.append(r2)

        # Create concatenated file paths
        concat_r1 = output_dir / "concatenated_R1.fastq"
        concat_r2 = output_dir / "concatenated_R2.fastq"

        # Concatenation commands
        concat_r1_cmd = f"cat {' '.join(r1_files)} > {concat_r1}"
        concat_r2_cmd = f"cat {' '.join(r2_files)} > {concat_r2}"

        commands.append({
            'name': f"concat_r1_{job_name}",
            'command': concat_r1_cmd,
            'description': f"Concatenate {len(r1_files)} R1 files"
        })

        commands.append({
            'name': f"concat_r2_{job_name}",
            'command': concat_r2_cmd,
            'description': f"Concatenate {len(r2_files)} R2 files"
        })

        # MEGAHIT command on concatenated files
        megahit_cmd = f"""megahit \\
    -1 {concat_r1} \\
    -2 {concat_r2} \\
    -o {output_dir}/megahit_assembly \\
    --min-contig-len 500 \\
    --k-list 45,65,85,105,125,145,165,185,205,225 \\
    --min-count 2 \\
    -t {threads} \\
    --memory {memory_gb * 1073741824}"""

        commands.append({
            'name': f"megahit_{job_name}",
            'command': megahit_cmd,
            'description': f"MEGAHIT assembly of concatenated reads ({len(sample_pairs)} samples)",
            'output': output_dir / "megahit_assembly" / "final.contigs.fa"
        })

    else:
        # Single sample - no concatenation needed
        r1, r2 = sample_pairs[0]
        megahit_cmd = f"""megahit \\
    -1 {r1} \\
    -2 {r2} \\
    -o {output_dir}/megahit_assembly \\
    --min-contig-len 500 \\
    --k-list 45,65,85,105,125,145,165,185,205,225 \\
    --min-count 2 \\
    -t {threads} \\
    --memory {memory_gb * 1073741824}"""

        commands.append({
            'name': f"megahit_{job_name}",
            'command': megahit_cmd,
            'description': f"MEGAHIT assembly of single sample",
            'output': output_dir / "megahit_assembly" / "final.contigs.fa"
        })

    return commands


def generate_stage1_commands(strategy, samples_dir, base_output_dir, strategy_name):
    """Generate Stage 1 MEGAHIT commands for a strategy."""
    commands = []
    stage1_dir = Path(base_output_dir) / "stage1_megahit" / strategy_name

    if strategy["strategy"] == "individual":
        # Individual assemblies: use SLURM array for parallel execution
        print(f"  Stage 1: {len(strategy['individual_samples'])} individual assemblies (SLURM array)")

        # Create sample list file for the array job to read
        sample_list_file = stage1_dir / "sample_list.txt"
        stage1_dir.mkdir(parents=True, exist_ok=True)

        valid_samples = []
        with open(sample_list_file, 'w') as f:
            for sample_id in strategy["individual_samples"]:
                r1, r2 = find_sample_files(sample_id, samples_dir)
                if r1 and r2:
                    f.write(f"{sample_id}\t{r1}\t{r2}\n")
                    valid_samples.append(sample_id)

        if valid_samples:
            # Return array job info instead of individual commands
            commands.append({
                'type': 'array',
                'array_size': len(valid_samples),
                'sample_list_file': sample_list_file,
                'samples_dir': samples_dir,
                'output_dir': stage1_dir,
                'threads': 8,
                'memory_gb': 32
            })

    elif strategy["groups"]:
        # Grouped assemblies: concatenate then MEGAHIT per group
        print(f"  Stage 1: {len(strategy['groups'])} group assemblies (concatenation approach)")

        for group in strategy["groups"]:
            group_id = group["group_id"]
            sample_pairs = []

            for sample_id in group["samples"]:
                r1, r2 = find_sample_files(sample_id, samples_dir)
                if r1 and r2:
                    sample_pairs.append((r1, r2))

            if sample_pairs:
                group_output = stage1_dir / f"group_{group_id}"
                group_output.mkdir(parents=True, exist_ok=True)

                # Determine resources based on group size
                group_size = len(sample_pairs)
                if group_size <= 4:
                    threads, memory_gb = 16, 120
                elif group_size <= 16:
                    threads, memory_gb = 18, 150
                else:
                    threads, memory_gb = 20, 200

                # Generate concatenation + MEGAHIT commands
                group_commands = generate_concatenation_and_megahit_commands(
                    sample_pairs, group_output, f"group_{group_id}",
                    threads=threads, memory_gb=memory_gb
                )

                if group_commands:
                    # Find the MEGAHIT command to get the output path
                    megahit_command = None
                    for cmd in group_commands:
                        if 'megahit_' in cmd['name']:
                            megahit_command = cmd
                            break

                    commands.append({
                        'name': f"group_{group_id}",
                        'commands': group_commands,  # List of commands (concat R1, concat R2, megahit)
                        'output': megahit_command['output'] if megahit_command else group_output / "megahit_assembly" / "final.contigs.fa",
                        'threads': threads,
                        'memory_gb': memory_gb,
                        'samples_count': len(sample_pairs)
                    })

    return commands


def generate_stage2_commands(stage1_commands, base_output_dir, strategy_name, strategy=None):
    """Generate Stage 2 concatenation commands."""
    if not stage1_commands:
        return None

    stage2_dir = Path(base_output_dir) / "stage2_concat" / strategy_name
    stage2_dir.mkdir(parents=True, exist_ok=True)

    # Handle array jobs vs regular commands differently
    if len(stage1_commands) == 1 and stage1_commands[0].get('type') == 'array':
        # Array job: collect outputs from individual sample directories
        array_info = stage1_commands[0]
        input_files = []

        if strategy and strategy.get('individual_samples'):
            for sample_id in strategy['individual_samples']:
                sample_output = array_info['output_dir'] / f"individual_{sample_id}" / "final.contigs.fa"
                input_files.append(str(sample_output))
    else:
        # Regular commands: collect from command outputs
        input_files = []
        for cmd_info in stage1_commands:
            if isinstance(cmd_info, dict) and 'output' in cmd_info:
                input_files.append(str(cmd_info['output']))

    if not input_files:
        return None

    output_file = stage2_dir / "concatenated_contigs.fa"

    # Simple concatenation command
    concat_cmd = f"cat {' '.join(input_files)} > {output_file}"

    return {
        'name': f"concat_{strategy_name}",
        'command': concat_cmd,
        'output': output_file,
        'depends_on': ['stage1_array'] if len(stage1_commands) == 1 and stage1_commands[0].get('type') == 'array'
                      else [cmd.get('name', f'stage1_{i}') for i, cmd in enumerate(stage1_commands)]
    }


def generate_stage3_commands(stage2_command, base_output_dir, strategy_name):
    """Generate Stage 3 Flye meta-assembly commands."""
    if not stage2_command:
        return None

    stage3_dir = Path(base_output_dir) / "stage3_flye" / strategy_name
    stage3_dir.mkdir(parents=True, exist_ok=True)

    input_file = stage2_command['output']
    output_dir = stage3_dir / "flye_assembly"

    # Flye meta-assembly command (matching Hecatomb parameters)
    flye_cmd = f"""flye \\
    --subassemblies {input_file} \\
    --plasmids \\
    -g 1g \\
    -t 20 \\
    -o {output_dir}"""

    return {
        'name': f"flye_{strategy_name}",
        'command': flye_cmd,
        'output': output_dir / "assembly.fasta",
        'depends_on': [stage2_command['name']],
        'threads': 20,
        'memory_gb': 200
    }


def write_slurm_script(commands, script_file, stage_name, strategy_name, time_limit=None, memory_gb=None, cpus=None):
    """Write a SLURM batch script for a set of commands."""
    script_path = Path(script_file)
    script_path.parent.mkdir(parents=True, exist_ok=True)

    # Set defaults if not provided
    if time_limit is None:
        time_limit = "8:00:00"  # 8 hours default
    if memory_gb is None:
        memory_gb = 32  # 32GB default
    if cpus is None:
        cpus = 8  # 8 CPUs default

    # Check if this is an array job
    is_array_job = len(commands) == 1 and isinstance(commands[0], dict) and commands[0].get('type') == 'array'

    with open(script_path, 'w') as f:
        # SLURM headers
        f.write(f"""#!/bin/bash
#SBATCH --job-name={stage_name}_{strategy_name}
#SBATCH --time={time_limit}
#SBATCH --mem={memory_gb}G
#SBATCH --cpus-per-task={cpus}""")

        # Add array directive if this is an array job
        if is_array_job:
            array_size = commands[0]['array_size']
            f.write(f"""
#SBATCH --array=1-{array_size}""")

        f.write(f"""
#SBATCH --output=logs/{stage_name}_{strategy_name}_%j.out
#SBATCH --error=logs/{stage_name}_{strategy_name}_%j.err
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=megan.j@wustl.edu

# Load conda environment
source /ref/sahlab/software/miniforge3/bin/activate
conda activate coassembly_env

# Create output directories
mkdir -p logs

echo "Starting {stage_name} for strategy: {strategy_name}"
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURM_NODELIST"
echo "Start time: $(date)"

""")

        if is_array_job:
            # Array job: process one sample per task
            array_info = commands[0]
            sample_list_file = array_info['sample_list_file']
            output_dir = array_info['output_dir']

            f.write(f"""
# Array job: process sample based on SLURM_ARRAY_TASK_ID
echo "Processing array task: $SLURM_ARRAY_TASK_ID"

# Read sample info from list file (using absolute path)
SAMPLE_INFO=$(sed -n "${{SLURM_ARRAY_TASK_ID}}p" {str(sample_list_file.absolute())})
SAMPLE_ID=$(echo "$SAMPLE_INFO" | cut -f1)
R1_FILE=$(echo "$SAMPLE_INFO" | cut -f2)
R2_FILE=$(echo "$SAMPLE_INFO" | cut -f3)

echo "Sample: $SAMPLE_ID"
echo "R1: $R1_FILE"
echo "R2: $R2_FILE"

# Create sample-specific output directory path (MEGAHIT will create it)
SAMPLE_OUTPUT="{str(output_dir.absolute())}/individual_${{SAMPLE_ID}}"

# Run MEGAHIT for this sample
echo "Running MEGAHIT for sample: $SAMPLE_ID"
megahit \\
    -1 "$R1_FILE" \\
    -2 "$R2_FILE" \\
    -o "$SAMPLE_OUTPUT" \\
    --min-contig-len 500 \\
    --k-list 45,65,85,105,125,145,165,185,205,225 \\
    --min-count 2 \\
    -t {cpus} \\
    --memory {memory_gb * 1073741824}

echo "MEGAHIT completed for sample: $SAMPLE_ID"
""")
        else:
            # Regular commands (for grouped assemblies with concatenation)
            for i, cmd_info in enumerate(commands):
                if isinstance(cmd_info, dict):
                    if 'commands' in cmd_info:
                        # Multiple commands for this group (concatenation approach)
                        f.write(f"\n# Group: {cmd_info['name']} ({cmd_info.get('samples_count', '?')} samples)\n")
                        for j, subcmd in enumerate(cmd_info['commands']):
                            f.write(f"\n# Step {j+1}: {subcmd.get('description', subcmd['name'])}\n")
                            f.write(f"echo 'Running: {subcmd['name']}'\n")
                            f.write(f"{subcmd['command']}\n")
                            f.write(f"echo 'Completed: {subcmd['name']}'\n\n")
                    else:
                        # Single command
                        f.write(f"\n# Command {i+1}: {cmd_info['name']}\n")
                        f.write(f"echo 'Running: {cmd_info['name']}'\n")
                        f.write(f"{cmd_info['command']}\n")
                        f.write(f"echo 'Completed: {cmd_info['name']}'\n\n")
                else:
                    f.write(f"\n# Command {i+1}\n")
                    f.write(f"{cmd_info}\n\n")

        f.write(f"""
echo "End time: $(date)"
echo "{stage_name} completed for strategy: {strategy_name}"
""")

    return script_path


def process_strategy(strategy_file, samples_dir, base_output_dir, scripts_dir):
    """Process a single strategy and generate all assembly commands."""
    strategy = load_strategy_file(strategy_file)
    if not strategy:
        return None

    # Create a clean strategy name from the file path
    rel_path = Path(strategy_file).relative_to(Path(strategy_file).parents[2])
    strategy_name = str(rel_path.parent).replace('/', '_')
    if strategy_name == '.':
        strategy_name = strategy["strategy"]

    print(f"\n=== Processing Strategy: {strategy_name} ===")
    print(f"  Type: {strategy['strategy']}")
    print(f"  Groups: {len(strategy.get('groups', []))}")
    print(f"  Individual samples: {len(strategy.get('individual_samples', []))}")

    # Generate Stage 1 commands
    stage1_commands = generate_stage1_commands(strategy, samples_dir, base_output_dir, strategy_name)
    print(f"  Stage 1: Generated {len(stage1_commands)} MEGAHIT commands")

    # Generate Stage 2 command
    stage2_command = generate_stage2_commands(stage1_commands, base_output_dir, strategy_name, strategy)
    print(f"  Stage 2: Generated concatenation command")

    # Generate Stage 3 command
    stage3_command = generate_stage3_commands(stage2_command, base_output_dir, strategy_name)
    print(f"  Stage 3: Generated Flye meta-assembly command")

    # Write SLURM scripts with appropriate resource allocation
    scripts_path = Path(scripts_dir)

    if stage1_commands:
        # Determine Stage 1 resources based on strategy type
        if strategy["strategy"] == "individual":
            # Individual assemblies: moderate resources, short time
            time_limit = "4:00:00"  # 4 hours
            memory_gb = 32
            cpus = 8
        elif strategy["strategy"] == "global":
            # Global assembly: massive resources, long time
            time_limit = "3-00:00:00"  # 3 days
            memory_gb = 200
            cpus = 20
        else:
            # Group assemblies: scale by group size based on focused strategies
            # Determine group size from strategy name or actual group sizes
            if "groups_size_5" in strategy.get("strategy", ""):
                # Small groups (5 samples each): 40 groups
                time_limit = "8:00:00"  # 8 hours
                memory_gb = 64
                cpus = 12
            elif "groups_size_12" in strategy.get("strategy", ""):
                # Small-medium groups (12 samples each): ~17 groups
                time_limit = "12:00:00"  # 12 hours
                memory_gb = 96
                cpus = 16
            elif "groups_size_25" in strategy.get("strategy", ""):
                # Medium groups (25 samples each): 8 groups
                time_limit = "1-06:00:00"  # 30 hours
                memory_gb = 128
                cpus = 18
            else:
                # Default for any other grouped strategy
                time_limit = "16:00:00"  # 16 hours
                memory_gb = 120
                cpus = 16

        stage1_script = write_slurm_script(
            stage1_commands,
            scripts_path / f"stage1_{strategy_name}.sh",
            "stage1", strategy_name,
            time_limit=time_limit, memory_gb=memory_gb, cpus=cpus
        )

    if stage2_command:
        # Stage 2: Concatenation - light resources, short time
        stage2_script = write_slurm_script(
            [stage2_command],
            scripts_path / f"stage2_{strategy_name}.sh",
            "stage2", strategy_name,
            time_limit="0:30:00", memory_gb=8, cpus=2
        )

    if stage3_command:
        # Stage 3: Flye meta-assembly - heavy resources, medium time
        stage3_script = write_slurm_script(
            [stage3_command],
            scripts_path / f"stage3_{strategy_name}.sh",
            "stage3", strategy_name,
            time_limit="1-00:00:00", memory_gb=200, cpus=20
        )

    return {
        'strategy_name': strategy_name,
        'stage1_commands': len(stage1_commands),
        'final_assembly': stage3_command['output'] if stage3_command else None
    }


def main():
    parser = argparse.ArgumentParser(description="Generate assembly commands for focused assembly strategies")
    parser.add_argument("--groupings-dir", default="results/focused_strategies",
                       help="Directory containing strategy JSON files")
    parser.add_argument("--samples-dir", default="samples/subset_200",
                       help="Directory containing FASTQ files")
    parser.add_argument("--output-dir", default="results/focused_assemblies",
                       help="Base output directory for assemblies")
    parser.add_argument("--scripts-dir", default="focused_assembly_scripts",
                       help="Directory to write SLURM scripts")

    args = parser.parse_args()

    print("🧬 Focused Assembly Command Generator")
    print("=" * 60)
    print("Generating 3-stage assembly pipeline for literature-informed strategies")
    print()

    # Create output directories
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    Path(args.scripts_dir).mkdir(parents=True, exist_ok=True)
    Path("logs").mkdir(exist_ok=True)

    # Find all strategy files
    strategy_files = find_all_strategies(args.groupings_dir)
    print(f"Found {len(strategy_files)} strategy files:")
    for sf in strategy_files:
        print(f"  • {sf}")
    print()

    results = []
    total_stage1_commands = 0

    # Process each strategy
    for strategy_file in strategy_files:
        result = process_strategy(strategy_file, args.samples_dir, args.output_dir, args.scripts_dir)
        if result:
            results.append(result)
            total_stage1_commands += result['stage1_commands']

    # Summary
    print("\n" + "=" * 60)
    print("🎉 Focused assembly command generation completed!")
    print(f"📊 Summary:")
    print(f"  • Literature-informed strategies: {len(results)}")
    print(f"  • Total Stage 1 MEGAHIT jobs: {total_stage1_commands}")
    print(f"  • Final assemblies expected: {len(results)}")
    print(f"  • SLURM scripts written to: {args.scripts_dir}/")
    print()

    print("📁 Final assemblies will be at:")
    for result in results:
        if result['final_assembly']:
            print(f"  • {result['strategy_name']}: {result['final_assembly']}")

    print()
    print("🚀 Next steps:")
    print("1. Review generated SLURM scripts")
    print("2. Submit Stage 1 jobs: sbatch focused_assembly_scripts/stage1_*.sh")
    print("3. Monitor completion, then submit Stage 2 jobs")
    print("4. Monitor completion, then submit Stage 3 jobs")
    print("5. Run CheckV analysis for viral genome completeness")
    print("6. Compare strain diversity vs low-abundance recovery")


if __name__ == "__main__":
    main()