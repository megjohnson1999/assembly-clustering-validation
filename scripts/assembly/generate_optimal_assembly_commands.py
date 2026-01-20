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


def generate_megahit_command(sample_pairs, output_dir, job_name, threads=8, memory_gb=32):
    """Generate a MEGAHIT command for a list of sample pairs."""
    if not sample_pairs:
        return None

    # Collect all R1 and R2 files
    r1_files = []
    r2_files = []

    for r1, r2 in sample_pairs:
        r1_files.append(r1)
        r2_files.append(r2)

    r1_list = ",".join(r1_files)
    r2_list = ",".join(r2_files)

    # MEGAHIT command with optimized parameters
    command = f"""megahit \\
    -1 {r1_list} \\
    -2 {r2_list} \\
    -o {output_dir} \\
    --min-contig-len 500 \\
    --k-list 45,65,85,105,125,145,165,185,205,225 \\
    --min-count 2 \\
    -t {threads} \\
    --memory {memory_gb * 1073741824}"""  # Convert GB to bytes

    return command


def generate_stage1_commands(strategy, samples_dir, base_output_dir, strategy_name):
    """Generate Stage 1 MEGAHIT commands for a strategy."""
    commands = []
    stage1_dir = Path(base_output_dir) / "stage1_megahit" / strategy_name

    if strategy["strategy"] == "individual":
        # Individual assemblies: one MEGAHIT per sample
        print(f"  Stage 1: {len(strategy['individual_samples'])} individual assemblies")

        for sample_id in strategy["individual_samples"]:
            r1, r2 = find_sample_files(sample_id, samples_dir)
            if r1 and r2:
                sample_output = stage1_dir / f"individual_{sample_id}"
                sample_pairs = [(r1, r2)]

                cmd = generate_megahit_command(
                    sample_pairs, sample_output, f"megahit_{sample_id}",
                    threads=8, memory_gb=32
                )

                if cmd:
                    commands.append({
                        'name': f"individual_{sample_id}",
                        'command': cmd,
                        'output': sample_output / "final.contigs.fa",
                        'threads': 8,
                        'memory_gb': 32
                    })

    elif strategy["groups"]:
        # Grouped assemblies: one MEGAHIT per group
        print(f"  Stage 1: {len(strategy['groups'])} group assemblies")

        for group in strategy["groups"]:
            group_id = group["group_id"]
            sample_pairs = []

            for sample_id in group["samples"]:
                r1, r2 = find_sample_files(sample_id, samples_dir)
                if r1 and r2:
                    sample_pairs.append((r1, r2))

            if sample_pairs:
                group_output = stage1_dir / f"group_{group_id}"

                # Determine resources based on group size
                group_size = len(sample_pairs)
                if group_size <= 4:
                    threads, memory_gb = 16, 120
                elif group_size <= 16:
                    threads, memory_gb = 18, 150
                else:
                    threads, memory_gb = 20, 200

                cmd = generate_megahit_command(
                    sample_pairs, group_output, f"megahit_{group_id}",
                    threads=threads, memory_gb=memory_gb
                )

                if cmd:
                    commands.append({
                        'name': f"group_{group_id}",
                        'command': cmd,
                        'output': group_output / "final.contigs.fa",
                        'threads': threads,
                        'memory_gb': memory_gb
                    })

    return commands


def generate_stage2_commands(stage1_commands, base_output_dir, strategy_name):
    """Generate Stage 2 concatenation commands."""
    if not stage1_commands:
        return None

    stage2_dir = Path(base_output_dir) / "stage2_concat" / strategy_name
    stage2_dir.mkdir(parents=True, exist_ok=True)

    # Collect all stage 1 output files
    input_files = []
    for cmd_info in stage1_commands:
        input_files.append(str(cmd_info['output']))

    output_file = stage2_dir / "concatenated_contigs.fa"

    # Simple concatenation command
    concat_cmd = f"cat {' '.join(input_files)} > {output_file}"

    return {
        'name': f"concat_{strategy_name}",
        'command': concat_cmd,
        'output': output_file,
        'depends_on': [cmd['name'] for cmd in stage1_commands]
    }


def generate_stage3_commands(stage2_command, base_output_dir, strategy_name):
    """Generate Stage 3 Flye meta-assembly commands."""
    if not stage2_command:
        return None

    stage3_dir = Path(base_output_dir) / "stage3_flye" / strategy_name
    stage3_dir.mkdir(parents=True, exist_ok=True)

    input_file = stage2_command['output']
    output_dir = stage3_dir / "flye_assembly"

    # Flye meta-assembly command
    flye_cmd = f"""flye \\
    --meta \\
    --asm-coverage 50 \\
    --genome-size 100m \\
    --out-dir {output_dir} \\
    --threads 20 \\
    --iterations 3 \\
    --contigs {input_file}"""

    return {
        'name': f"flye_{strategy_name}",
        'command': flye_cmd,
        'output': output_dir / "assembly.fasta",
        'depends_on': [stage2_command['name']],
        'threads': 20,
        'memory_gb': 200
    }


def write_slurm_script(commands, script_file, stage_name, strategy_name):
    """Write a SLURM batch script for a set of commands."""
    script_path = Path(script_file)
    script_path.parent.mkdir(parents=True, exist_ok=True)

    with open(script_path, 'w') as f:
        f.write(f"""#!/bin/bash
#SBATCH --job-name={stage_name}_{strategy_name}
#SBATCH --partition=sahlab
#SBATCH --time=2-00:00:00
#SBATCH --nodes=1
#SBATCH --output=logs/{stage_name}_{strategy_name}_%j.out
#SBATCH --error=logs/{stage_name}_{strategy_name}_%j.err
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=megan.johnson@wustl.edu

# Load environments
source /ref/sahlab/software/miniforge3/etc/profile.d/conda.sh
conda activate coassembly_env

# Create output directories
mkdir -p logs

echo "Starting {stage_name} for strategy: {strategy_name}"
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURM_NODELIST"
echo "Start time: $(date)"

""")

        for i, cmd_info in enumerate(commands):
            if isinstance(cmd_info, dict):
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
    stage2_command = generate_stage2_commands(stage1_commands, base_output_dir, strategy_name)
    print(f"  Stage 2: Generated concatenation command")

    # Generate Stage 3 command
    stage3_command = generate_stage3_commands(stage2_command, base_output_dir, strategy_name)
    print(f"  Stage 3: Generated Flye meta-assembly command")

    # Write SLURM scripts
    scripts_path = Path(scripts_dir)

    if stage1_commands:
        stage1_script = write_slurm_script(
            stage1_commands,
            scripts_path / f"stage1_{strategy_name}.sh",
            "stage1", strategy_name
        )

    if stage2_command:
        stage2_script = write_slurm_script(
            [stage2_command],
            scripts_path / f"stage2_{strategy_name}.sh",
            "stage2", strategy_name
        )

    if stage3_command:
        stage3_script = write_slurm_script(
            [stage3_command],
            scripts_path / f"stage3_{strategy_name}.sh",
            "stage3", strategy_name
        )

    return {
        'strategy_name': strategy_name,
        'stage1_commands': len(stage1_commands),
        'final_assembly': stage3_command['output'] if stage3_command else None
    }


def main():
    parser = argparse.ArgumentParser(description="Generate assembly commands for optimal grouping strategies")
    parser.add_argument("--groupings-dir", default="results/optimal_groupings",
                       help="Directory containing strategy JSON files")
    parser.add_argument("--samples-dir", default="samples/subset_200",
                       help="Directory containing FASTQ files")
    parser.add_argument("--output-dir", default="results/assemblies",
                       help="Base output directory for assemblies")
    parser.add_argument("--scripts-dir", default="assembly_scripts",
                       help="Directory to write SLURM scripts")

    args = parser.parse_args()

    print("🧬 Optimal Assembly Command Generator")
    print("=" * 60)
    print("Generating 3-stage assembly pipeline for all strategies")
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
    print("🎉 Assembly command generation completed!")
    print(f"📊 Summary:")
    print(f"  • Strategies processed: {len(results)}")
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
    print("2. Submit Stage 1 jobs: sbatch assembly_scripts/stage1_*.sh")
    print("3. Monitor completion, then submit Stage 2 jobs")
    print("4. Monitor completion, then submit Stage 3 jobs")
    print("5. Run assembly quality analysis on final results")


if __name__ == "__main__":
    main()