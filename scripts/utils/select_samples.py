#!/usr/bin/env python3
"""
Select random paired-end samples for MetaGrouper validation experiment.
Handles the specific naming convention: {sample_id}_rrna_removed_R{1,2}.fastq
"""
import os
import random
import shutil
from pathlib import Path
import argparse

def find_sample_pairs(input_dir):
    """Find all valid R1/R2 pairs in the directory."""
    input_path = Path(input_dir)

    # Find all R1 files
    r1_files = list(input_path.glob("*_rrna_removed_R1.fastq"))
    print(f"Found {len(r1_files)} R1 files")

    # Check for corresponding R2 files
    valid_pairs = []
    missing_r2 = []

    for r1_file in r1_files:
        # Extract sample ID by removing the suffix
        sample_id = r1_file.name.replace("_rrna_removed_R1.fastq", "")
        r2_file = input_path / f"{sample_id}_rrna_removed_R2.fastq"

        if r2_file.exists():
            valid_pairs.append((sample_id, r1_file, r2_file))
        else:
            missing_r2.append(sample_id)

    if missing_r2:
        print(f"Warning: {len(missing_r2)} samples missing R2 files")
        if len(missing_r2) <= 10:
            print("Missing R2 for:", missing_r2)

    print(f"Found {len(valid_pairs)} valid paired samples")
    return valid_pairs

def select_samples(input_dir, output_dir, n_samples=50, seed=42):
    """Select random samples and create symlinks."""

    random.seed(seed)

    # Find all valid pairs
    valid_pairs = find_sample_pairs(input_dir)

    if len(valid_pairs) < n_samples:
        print(f"Warning: Only {len(valid_pairs)} samples available, selecting all")
        selected_pairs = valid_pairs
    else:
        selected_pairs = random.sample(valid_pairs, n_samples)

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Create symlinks
    print(f"Creating symlinks for {len(selected_pairs)} samples...")
    for sample_id, r1_file, r2_file in selected_pairs:
        r1_link = output_path / r1_file.name
        r2_link = output_path / r2_file.name

        # Remove existing symlinks if they exist
        if r1_link.exists():
            r1_link.unlink()
        if r2_link.exists():
            r2_link.unlink()

        # Create new symlinks
        r1_link.symlink_to(r1_file.absolute())
        r2_link.symlink_to(r2_file.absolute())

    # Save sample list for reference
    sample_list_file = output_path / "selected_samples.txt"
    with open(sample_list_file, "w") as f:
        f.write("# Selected samples for MetaGrouper validation\n")
        f.write(f"# Total: {len(selected_pairs)} samples\n")
        f.write(f"# Seed: {seed}\n\n")
        for sample_id, _, _ in selected_pairs:
            f.write(f"{sample_id}\n")

    print(f"✓ Selected {len(selected_pairs)} samples")
    print(f"✓ Symlinks created in: {output_path}")
    print(f"✓ Sample list saved to: {sample_list_file}")

    return len(selected_pairs)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Select samples for MetaGrouper validation")
    parser.add_argument("--input",
                       default="/lts/sahlab/data4/megan/RC2_rrna_removed_reads",
                       help="Input directory with samples")
    parser.add_argument("--output",
                       default="samples/subset_50",
                       help="Output directory for selected samples")
    parser.add_argument("--n-samples", type=int, default=50,
                       help="Number of samples to select")
    parser.add_argument("--seed", type=int, default=42,
                       help="Random seed for reproducible selection")

    args = parser.parse_args()

    print("MetaGrouper Sample Selection")
    print("=" * 40)
    print(f"Input directory: {args.input}")
    print(f"Output directory: {args.output}")
    print(f"Number of samples: {args.n_samples}")
    print(f"Random seed: {args.seed}")
    print()

    n_selected = select_samples(args.input, args.output, args.n_samples, args.seed)

    print("\nNext step: Run MetaGrouper on selected samples")
    print(f"sbatch run_metagrouper.sh")