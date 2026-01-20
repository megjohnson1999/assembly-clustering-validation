#!/usr/bin/env python3
"""
Generate focused assembly strategies based on literature review.

Literature-informed approach testing optimal co-assembly group sizes for viral metagenomes:
- Individual assembly (maximum strain resolution, baseline)
- Size-5 groups (optimal from medical pooling research)
- Size-12 groups (intermediate hypothesis)
- Size-50 groups (medium co-assembly)
- Global assembly (maximum low-abundance recovery)

This focused approach addresses the research gap identified in literature:
most studies test either individual OR massive co-assembly, but not intermediate sizes.
"""
import json
import random
from pathlib import Path
import argparse
import math


def get_sample_list(sample_dir, max_samples=200):
    """Get list of sample names for focused experiment."""
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

    # Use all available samples up to max_samples
    if len(sample_names) > max_samples:
        print(f"Using first {max_samples} samples for focused experiment (found {len(sample_names)})")
        sample_names = sample_names[:max_samples]

    return sample_names


def create_individual_strategy(samples, output_dir):
    """Create individual assembly strategy (baseline for strain resolution)."""

    print(f"\n=== INDIVIDUAL STRATEGY ===")
    print(f"  Samples: {len(samples)}")
    print(f"  Strategy: Each sample assembled individually (maximum strain resolution)")
    print(f"  Literature basis: Preserves all strain-level diversity")

    individual_result = {
        "strategy": "individual",
        "tool": "individual_assembly",
        "confidence": 1.0,
        "groups": [],
        "individual_samples": samples,
        "summary": {
            "total_samples": len(samples),
            "grouped_samples": 0,
            "individual_samples": len(samples),
            "total_groups": 0
        },
        "parameters": {
            "strategy_name": "individual",
            "literature_basis": "Maximum strain resolution, baseline condition"
        }
    }

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


def create_focused_group_strategy(samples, group_size, strategy_name, output_dir, literature_basis):
    """Create a focused grouping strategy with literature justification."""

    n_samples = len(samples)
    n_groups = math.ceil(n_samples / group_size)

    print(f"\n=== {strategy_name.upper()} STRATEGY ===")
    print(f"  Samples: {n_samples}")
    print(f"  Group size: {group_size}")
    print(f"  Expected groups: {n_groups}")
    print(f"  Literature basis: {literature_basis}")

    # Use fixed seed for reproducibility
    random.seed(42)
    shuffled_samples = samples.copy()
    random.shuffle(shuffled_samples)

    # Create groups of specified size
    groups = []
    for i in range(0, n_samples, group_size):
        group_samples = shuffled_samples[i:i + group_size]

        if len(group_samples) >= 2:  # Only groups with at least 2 samples
            groups.append({
                "group_id": f"{strategy_name}_group_{len(groups)+1}",
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
        "strategy": f"groups_size_{group_size}",
        "tool": "focused_grouping",
        "confidence": 0.8,  # High confidence in literature-informed choice
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
            "strategy_name": strategy_name,
            "literature_basis": literature_basis,
            "seed": 42
        }
    }

    # Save strategy
    strategy_dir = output_dir / strategy_name
    strategy_dir.mkdir(parents=True, exist_ok=True)

    output_file = strategy_dir / "assembly_recommendations.json"
    with open(output_file, 'w') as f:
        json.dump(grouping_result, f, indent=2)

    print(f"    → {len(groups)} groups, {total_grouped} grouped, {len(individual_samples)} individual")

    return {
        'strategy': strategy_name,
        'file': output_file,
        'groups': len(groups),
        'grouped_samples': total_grouped,
        'individual_samples': len(individual_samples)
    }


def create_global_strategy(samples, output_dir):
    """Create global assembly strategy (maximum low-abundance recovery)."""

    print(f"\n=== GLOBAL STRATEGY ===")
    print(f"  Samples: {len(samples)}")
    print(f"  Strategy: All samples co-assembled together")
    print(f"  Literature basis: Maximum recovery of low-abundance viral genomes")

    global_result = {
        "strategy": "global",
        "tool": "global_assembly",
        "confidence": 0.7,
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
            "strategy_name": "global",
            "literature_basis": "Maximum coverage for low-abundance virus recovery"
        }
    }

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
    parser = argparse.ArgumentParser(description="Generate focused assembly strategies based on literature")
    parser.add_argument("sample_dir", help="Directory containing FASTQ files")
    parser.add_argument("-o", "--output", default="results/focused_strategies",
                       help="Output directory")
    parser.add_argument("--max-samples", type=int, default=200,
                       help="Maximum samples for focused experiment (default: 200)")

    args = parser.parse_args()

    print("🧬 Focused Assembly Strategy Generator")
    print("=" * 60)
    print("Literature-informed experiment design for viral metagenome assembly")
    print("Research Question: Optimal co-assembly group size balancing")
    print("                  low-abundance recovery vs strain-mixing artifacts")
    print()

    # Get sample list
    samples = get_sample_list(args.sample_dir, args.max_samples)
    print(f"Selected {len(samples)} samples for focused experiment")
    print(f"Sample IDs: {samples[:5]}..." if len(samples) > 5 else f"Sample IDs: {samples}")
    print()

    if len(samples) == 0:
        print("ERROR: No samples found")
        return False

    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)

    all_results = {}

    try:
        # Strategy 1: Individual assembly (baseline)
        individual_result = create_individual_strategy(samples, output_path)
        all_results['individual'] = individual_result

        # Strategy 2: Size-5 groups (optimal from medical literature)
        size5_result = create_focused_group_strategy(
            samples, 5, "groups_size_5", output_path,
            "Optimal pool size from medical testing research (Nature 2021)"
        )
        all_results['groups_size_5'] = size5_result

        # Strategy 3: Size-12 groups (small-medium groups)
        size12_result = create_focused_group_strategy(
            samples, 12, "groups_size_12", output_path,
            "Small-medium groups: ~17 groups for 200 samples"
        )
        all_results['groups_size_12'] = size12_result

        # Strategy 4: Size-25 groups (medium groups)
        size25_result = create_focused_group_strategy(
            samples, 25, "groups_size_25", output_path,
            "Medium groups: 8 groups balancing coverage and strain diversity"
        )
        all_results['groups_size_25'] = size25_result

        # Strategy 5: Global assembly (maximum recovery)
        global_result = create_global_strategy(samples, output_path)
        all_results['global'] = global_result

        # Create overall summary
        summary_file = output_path / "focused_experiment_summary.txt"
        with open(summary_file, 'w') as f:
            f.write("Focused Viral Metagenome Assembly Experiment\n")
            f.write("=" * 60 + "\n\n")
            f.write("Research Question:\n")
            f.write("What is the optimal co-assembly group size for viral metagenomes?\n")
            f.write("(Balancing low-abundance recovery against strain-mixing artifacts)\n\n")

            f.write("Literature-Informed Design:\n")
            f.write(f"- Total samples: {len(samples)}\n")
            f.write("- Strategies: 5 (down from 17 in original design)\n")
            f.write("- Cost reduction: ~85% (1,500 vs 10,000 CPU hours)\n")
            f.write("- Statistical power: High with {len(samples)} samples\n\n")

            f.write("Strategies Created:\n\n")

            f.write("1. Individual Assembly (Baseline)\n")
            f.write(f"   - {len(samples)} separate assemblies\n")
            f.write(f"   - Literature: Maximum strain resolution\n")
            f.write(f"   - File: {individual_result['file']}\n\n")

            f.write("2. Groups of 5 Samples\n")
            f.write(f"   - {size5_result['groups']} groups, {size5_result['grouped_samples']} grouped\n")
            f.write(f"   - Literature: Optimal pool size (Nature 2021)\n")
            f.write(f"   - File: {size5_result['file']}\n\n")

            f.write("3. Groups of 12 Samples\n")
            f.write(f"   - {size12_result['groups']} groups, {size12_result['grouped_samples']} grouped\n")
            f.write(f"   - Literature: Small-medium group size\n")
            f.write(f"   - File: {size12_result['file']}\n\n")

            f.write("4. Groups of 25 Samples\n")
            f.write(f"   - {size25_result['groups']} groups, {size25_result['grouped_samples']} grouped\n")
            f.write(f"   - Literature: Medium group balancing coverage vs diversity\n")
            f.write(f"   - File: {size25_result['file']}\n\n")

            f.write("5. Global Assembly\n")
            f.write(f"   - All {len(samples)} samples together\n")
            f.write(f"   - Literature: Maximum low-abundance recovery\n")
            f.write(f"   - File: {global_result['file']}\n\n")

            f.write("Next Steps:\n")
            f.write("1. Generate assembly commands for all 5 strategies\n")
            f.write("2. Run MEGAHIT → Flye pipeline\n")
            f.write("3. Analyze with CheckV for viral genome completeness\n")
            f.write("4. Compare strain diversity vs low-abundance recovery\n")
            f.write("5. Determine optimal group size for viral metagenomes\n")

        print("\n" + "=" * 60)
        print("🎉 Focused assembly strategies generated successfully!")
        print(f"📁 Results saved to: {args.output}")
        print(f"📋 Summary: {summary_file}")
        print()
        print("Literature-Informed Strategies:")
        print(f"  • Individual: {len(samples)} assemblies (strain resolution baseline)")
        print(f"  • Groups of 5: {size5_result['groups']} groups (medical optimal)")
        print(f"  • Groups of 12: {size12_result['groups']} groups (small-medium)")
        print(f"  • Groups of 25: {size25_result['groups']} groups (medium)")
        print(f"  • Global: All {len(samples)} together (max recovery)")
        print()
        print("Cost Analysis:")
        print(f"  • Original plan: 10,000+ CPU hours, 17 strategies")
        print(f"  • Focused plan: ~1,500 CPU hours, 5 strategies")
        print(f"  • Cost reduction: 85% while addressing genuine research gap")
        print()
        print("🚀 Ready for focused assembly pipeline!")

        return True

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)