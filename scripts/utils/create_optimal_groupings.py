#!/usr/bin/env python3
"""
Generate multiple random grouping strategies to test optimal assembly group sizes.

Since no k-mer clusters exist in viral metagenomic data, this tests different
random grouping sizes to find the optimal assembly strategy.
"""
import json
import random
from pathlib import Path
import argparse
import math

def get_sample_list(sample_dir):
    """Get list of sample names from directory."""
    sample_path = Path(sample_dir)

    # Find all R1 files and extract sample names
    r1_files = list(sample_path.glob("*_rrna_removed_R1.fastq"))
    sample_names = []

    for r1_file in r1_files:
        sample_id = r1_file.stem.replace("_rrna_removed_R1", "")
        r2_file = sample_path / f"{sample_id}_rrna_removed_R2.fastq"

        if r2_file.exists():
            sample_names.append(sample_id)
        else:
            print(f"Warning: Missing R2 for {sample_id}, skipping")

    sample_names.sort()  # Consistent ordering
    return sample_names

def create_grouping_strategy(samples, group_size, strategy_name, output_dir, seeds=[42, 43, 44, 45, 46]):
    """Create multiple random groupings for a given group size strategy."""

    n_samples = len(samples)
    n_groups = math.ceil(n_samples / group_size)

    print(f"\n=== {strategy_name.upper()} STRATEGY ===")
    print(f"  Samples: {n_samples}")
    print(f"  Group size: {group_size}")
    print(f"  Expected groups: {n_groups}")

    strategy_results = []

    for seed in seeds:
        print(f"  Generating grouping with seed {seed}...")

        random.seed(seed)
        shuffled_samples = samples.copy()
        random.shuffle(shuffled_samples)

        # Create groups of specified size
        groups = []
        for i in range(0, n_samples, group_size):
            group_samples = shuffled_samples[i:i + group_size]

            if len(group_samples) >= 2:  # Only groups with at least 2 samples
                groups.append({
                    "group_id": f"{strategy_name}_seed{seed}_group_{len(groups)+1}",
                    "samples": group_samples,
                    "size": len(group_samples),
                    "assembly_strategy": "grouped"
                })

        # Handle any remaining individual samples
        individual_samples = []
        total_grouped = sum(len(group["samples"]) for group in groups)
        if total_grouped < n_samples:
            individual_samples = shuffled_samples[total_grouped:]

        # Create output structure
        grouping_result = {
            "strategy": f"random_groups_size_{group_size}",
            "tool": "random_grouping",
            "confidence": 0.5,  # Neutral for random
            "groups": groups,
            "individual_samples": individual_samples,
            "summary": {
                "total_samples": n_samples,
                "grouped_samples": total_grouped,
                "individual_samples": len(individual_samples),
                "total_groups": len(groups),
                "target_group_size": group_size,
                "actual_group_sizes": [len(g["samples"]) for g in groups]
            },
            "parameters": {
                "group_size": group_size,
                "seed": seed,
                "strategy_name": strategy_name
            }
        }

        # Save this seed's grouping
        seed_dir = output_dir / strategy_name / f"seed_{seed}"
        seed_dir.mkdir(parents=True, exist_ok=True)

        output_file = seed_dir / "assembly_recommendations.json"
        with open(output_file, 'w') as f:
            json.dump(grouping_result, f, indent=2)

        strategy_results.append({
            'seed': seed,
            'file': output_file,
            'groups': len(groups),
            'grouped_samples': total_grouped,
            'individual_samples': len(individual_samples)
        })

        print(f"    → {len(groups)} groups, {total_grouped} grouped, {len(individual_samples)} individual")

    return strategy_results

def create_individual_strategy(samples, output_dir):
    """Create individual assembly strategy (each sample assembled separately)."""

    print(f"\n=== INDIVIDUAL STRATEGY ===")
    print(f"  Samples: {len(samples)}")
    print(f"  Strategy: Each sample assembled individually")

    individual_result = {
        "strategy": "individual",
        "tool": "individual_assembly",
        "confidence": 1.0,  # High confidence in individual approach
        "groups": [],  # No groups - all individual
        "individual_samples": samples,
        "summary": {
            "total_samples": len(samples),
            "grouped_samples": 0,
            "individual_samples": len(samples),
            "total_groups": 0
        },
        "parameters": {
            "strategy_name": "individual"
        }
    }

    # Save individual strategy
    individual_dir = output_dir / "individual"
    individual_dir.mkdir(parents=True, exist_ok=True)

    output_file = individual_dir / "assembly_recommendations.json"
    with open(output_file, 'w') as f:
        json.dump(individual_result, f, indent=2)

    print(f"    → All {len(samples)} samples as individuals")

    return {
        'strategy': 'individual',
        'file': output_file,
        'samples': len(samples)
    }

def create_global_strategy(samples, output_dir):
    """Create global assembly strategy (all samples together)."""

    print(f"\n=== GLOBAL STRATEGY ===")
    print(f"  Samples: {len(samples)}")
    print(f"  Strategy: All samples co-assembled together")

    global_result = {
        "strategy": "global",
        "tool": "global_assembly",
        "confidence": 0.7,  # Moderate confidence in global approach
        "groups": [{
            "group_id": "global_all_samples",
            "samples": samples,
            "size": len(samples),
            "assembly_strategy": "grouped"
        }],
        "individual_samples": [],
        "summary": {
            "total_samples": len(samples),
            "grouped_samples": len(samples),
            "individual_samples": 0,
            "total_groups": 1
        },
        "parameters": {
            "strategy_name": "global"
        }
    }

    # Save global strategy
    global_dir = output_dir / "global"
    global_dir.mkdir(parents=True, exist_ok=True)

    output_file = global_dir / "assembly_recommendations.json"
    with open(output_file, 'w') as f:
        json.dump(global_result, f, indent=2)

    print(f"    → 1 group with all {len(samples)} samples")

    return {
        'strategy': 'global',
        'file': output_file,
        'samples': len(samples)
    }

def main():
    parser = argparse.ArgumentParser(description="Generate optimal random grouping strategies")
    parser.add_argument("sample_dir", help="Directory containing FASTQ files")
    parser.add_argument("-o", "--output", default="results/optimal_groupings",
                       help="Output directory")
    parser.add_argument("--group-sizes", nargs="+", type=int, default=[4, 8, 16],
                       help="Group sizes to test (default: 4 8 16)")
    parser.add_argument("--seeds", nargs="+", type=int, default=[42, 43, 44, 45, 46],
                       help="Random seeds for robustness")

    args = parser.parse_args()

    print("🧬 Optimal Assembly Strategy Generator")
    print("=" * 60)
    print("Testing multiple assembly strategies for viral metagenomic data")
    print("(Since no k-mer clusters exist)")
    print()

    # Get sample list
    samples = get_sample_list(args.sample_dir)
    print(f"Found {len(samples)} samples")

    if len(samples) == 0:
        print("ERROR: No samples found")
        return False

    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)

    all_results = {}

    try:
        # Strategy 1: Individual assembly
        individual_result = create_individual_strategy(samples, output_path)
        all_results['individual'] = individual_result

        # Strategy 2: Random groups of different sizes
        for group_size in args.group_sizes:
            strategy_name = f"groups_size_{group_size}"
            group_results = create_grouping_strategy(
                samples, group_size, strategy_name, output_path, args.seeds
            )
            all_results[strategy_name] = group_results

        # Strategy 3: Global assembly
        global_result = create_global_strategy(samples, output_path)
        all_results['global'] = global_result

        # Create overall summary
        summary_file = output_path / "assembly_strategies_summary.txt"
        with open(summary_file, 'w') as f:
            f.write("Assembly Strategy Comparison Experiment\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Research Question: What's the optimal assembly strategy when no k-mer clusters exist?\n\n")
            f.write(f"Total samples: {len(samples)}\n")
            f.write(f"Random seeds: {args.seeds}\n")
            f.write(f"Group sizes tested: {args.group_sizes}\n\n")

            f.write("Strategies Created:\n\n")

            f.write("1. Individual Assembly\n")
            f.write(f"   - {len(samples)} separate assemblies\n")
            f.write(f"   - File: {individual_result['file']}\n\n")

            for group_size in args.group_sizes:
                strategy_name = f"groups_size_{group_size}"
                f.write(f"2. Random Groups (Size {group_size})\n")
                for result in all_results[strategy_name]:
                    f.write(f"   - Seed {result['seed']}: {result['groups']} groups, {result['grouped_samples']} grouped\n")
                f.write("\n")

            f.write("3. Global Assembly\n")
            f.write(f"   - All {len(samples)} samples together\n")
            f.write(f"   - File: {global_result['file']}\n\n")

            f.write("Next Steps:\n")
            f.write("1. Generate assembly commands for all strategies\n")
            f.write("2. Run MEGAHIT → Flye pipeline for each\n")
            f.write("3. Compare assembly quality metrics\n")
            f.write("4. Determine optimal group size for viral metagenomes\n")

        print("\n" + "=" * 60)
        print("🎉 All assembly strategies generated successfully!")
        print(f"📁 Results saved to: {args.output}")
        print(f"📋 Summary: {summary_file}")
        print()
        print("Strategies created:")
        print(f"  • Individual: {len(samples)} separate assemblies")
        for group_size in args.group_sizes:
            n_groups = math.ceil(len(samples) / group_size)
            print(f"  • Groups of {group_size}: ~{n_groups} groups × {len(args.seeds)} seeds")
        print(f"  • Global: All {len(samples)} samples together")
        print()
        print("🚀 Ready for assembly pipeline comparison!")

        return True

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)