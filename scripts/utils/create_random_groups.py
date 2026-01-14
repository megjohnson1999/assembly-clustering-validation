#!/usr/bin/env python3
"""
Generate random groupings with the same structure as MetaGrouper's k-mer clustering.
This creates the null hypothesis for comparison.
"""
import json
import random
from pathlib import Path
import argparse

def create_random_groups(kmer_results_file, output_base_dir, seeds=[42, 43, 44, 45, 46]):
    """Create multiple random groupings matching k-mer group structure."""

    # Read MetaGrouper results
    with open(kmer_results_file) as f:
        kmer_results = json.load(f)

    print(f"Reading k-mer results from: {kmer_results_file}")

    # Extract all samples and group structure
    all_samples = []
    group_sizes = []

    groups = kmer_results.get('groups', [])
    if not groups:
        print("ERROR: No groups found in MetaGrouper results")
        return None

    for group in groups:
        samples = group.get('samples', [])
        all_samples.extend(samples)
        group_sizes.append(len(samples))

    print(f"Found {len(all_samples)} samples in {len(group_sizes)} groups")
    print(f"K-mer group sizes: {group_sizes}")

    # Create output base directory
    output_base_path = Path(output_base_dir)
    output_base_path.mkdir(parents=True, exist_ok=True)

    created_groupings = []

    # Create multiple random groupings with different seeds
    for seed_num in seeds:
        print(f"\nGenerating random grouping with seed {seed_num}...")

        random.seed(seed_num)

        # Shuffle samples randomly
        shuffled_samples = all_samples.copy()
        random.shuffle(shuffled_samples)

        # Create random groups with same size structure
        random_groups = []
        sample_idx = 0

        for i, size in enumerate(group_sizes):
            group_samples = shuffled_samples[sample_idx:sample_idx + size]

            random_groups.append({
                "group_id": f"random_seed{seed_num}_group_{i+1}",
                "samples": group_samples,
                "strategy": "grouped",
                "size": size,
                "similarity_threshold": 0.5,  # Neutral for random
                "confidence": 0.5  # Neutral confidence
            })
            sample_idx += size

        # Create output structure matching MetaGrouper format
        random_results = {
            "strategy": "random_grouped",
            "total_samples": len(all_samples),
            "total_groups": len(random_groups),
            "groups": random_groups,
            "confidence": 0.5,  # Neutral confidence for random
            "similarity_threshold": 0.5,
            "method": "random_clustering",
            "seed": seed_num,
            "created_by": "random_grouping_script",
            "based_on": str(kmer_results_file)
        }

        # Create seed-specific directory
        seed_dir = output_base_path / f"random_seed_{seed_num}"
        seed_dir.mkdir(parents=True, exist_ok=True)

        # Save random results
        output_file = seed_dir / "assembly_recommendations.json"
        with open(output_file, 'w') as f:
            json.dump(random_results, f, indent=2)

        created_groupings.append({
            'seed': seed_num,
            'file': output_file,
            'groups': len(random_groups)
        })

        print(f"  ✓ Seed {seed_num}: {len(random_groups)} groups → {output_file}")

    # Create overall summary
    summary_file = output_base_path / "random_groupings_summary.txt"
    with open(summary_file, 'w') as f:
        f.write("Multiple Random Groupings Summary\n")
        f.write("=" * 40 + "\n\n")
        f.write(f"Total samples: {len(all_samples)}\n")
        f.write(f"K-mer group structure: {group_sizes}\n")
        f.write(f"Number of random groupings: {len(seeds)}\n")
        f.write(f"Seeds used: {seeds}\n\n")

        f.write("Random groupings created:\n")
        for grouping in created_groupings:
            f.write(f"  Seed {grouping['seed']}: {grouping['groups']} groups\n")

    print(f"\n✓ Created {len(created_groupings)} random groupings")
    print(f"✓ Summary: {summary_file}")

    return created_groupings

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create random groupings matching k-mer structure")
    parser.add_argument("--kmer-results",
                       default="results/kmer_groups/assembly_recommendations.json",
                       help="MetaGrouper k-mer results file")
    parser.add_argument("--output",
                       default="results/random_groups",
                       help="Base output directory for random groups")
    parser.add_argument("--seeds", nargs="+", type=int, default=[42, 43, 44, 45, 46],
                       help="Random seeds for multiple groupings")

    args = parser.parse_args()

    print("Multiple Random Grouping Generator")
    print("=" * 40)
    print(f"K-mer results: {args.kmer_results}")
    print(f"Output directory: {args.output}")
    print(f"Random seeds: {args.seeds}")
    print()

    # Check input file exists
    if not Path(args.kmer_results).exists():
        print(f"ERROR: K-mer results file not found: {args.kmer_results}")
        print("Run MetaGrouper first (sbatch run_metagrouper.sh)")
        exit(1)

    results = create_random_groups(args.kmer_results, args.output, args.seeds)

    if results:
        print(f"\n✓ Successfully created {len(results)} random groupings")
        print("\nNext step: Generate assembly commands for all conditions")
        print("python scripts/generate_assembly_commands.py")
    else:
        print("ERROR: Failed to create random groups")
        exit(1)