#!/usr/bin/env python3
"""
Sourmash-based k-mer clustering for MetaGrouper validation.

Replaces MetaGrouper's custom sketching with optimized sourmash approach
while maintaining same clustering logic and output format.
"""

import os
import json
import argparse
import subprocess
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.cluster import AgglomerativeClustering
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, fcluster
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_sourmash_sketches(sample_dir, output_dir, ksize=21, scaled=1000):
    """Create sourmash sketches for all samples."""

    output_path = Path(output_dir)
    sketches_dir = output_path / "sketches"
    sketches_dir.mkdir(parents=True, exist_ok=True)

    # Find all R1 files (paired-end samples)
    sample_files = list(Path(sample_dir).glob("*_R1.fastq"))

    logging.info(f"Creating sourmash sketches for {len(sample_files)} samples...")

    sketch_files = []

    for r1_file in sample_files:
        sample_id = r1_file.stem.replace("_R1", "")
        r2_file = r1_file.parent / f"{sample_id}_R2.fastq"

        if not r2_file.exists():
            logging.warning(f"Missing R2 file for {sample_id}, skipping")
            continue

        sketch_file = sketches_dir / f"{sample_id}.sig"
        sketch_files.append(sketch_file)

        if sketch_file.exists():
            logging.info(f"Sketch exists for {sample_id}, skipping")
            continue

        # Create sketch for paired-end sample
        cmd = [
            'sourmash', 'sketch', 'dna',
            str(r1_file), str(r2_file),
            '-o', str(sketch_file),
            '--name', sample_id,
            '--ksize', str(ksize),
            '--scaled', str(scaled)
        ]

        logging.info(f"Creating sketch for {sample_id}...")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            logging.error(f"Failed to create sketch for {sample_id}: {result.stderr}")
            continue

    logging.info(f"✅ Created {len(sketch_files)} sketches")
    return sketch_files

def compute_sourmash_distances(sketch_files, output_dir):
    """Compute pairwise distances using sourmash compare."""

    output_path = Path(output_dir)
    compare_matrix_file = output_path / "sourmash_compare.csv"

    if compare_matrix_file.exists():
        logging.info("Similarity matrix exists, loading...")
        similarity_df = pd.read_csv(compare_matrix_file, index_col=0)
        return 1 - similarity_df.values, similarity_df.index.tolist()

    logging.info("Computing pairwise similarities...")

    cmd = [
        'sourmash', 'compare',
        '--csv', str(compare_matrix_file)
    ] + [str(f) for f in sketch_files]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"Sourmash compare failed: {result.stderr}")

    # Load similarity matrix and convert to distance
    similarity_df = pd.read_csv(compare_matrix_file, index_col=0)
    distance_matrix = 1 - similarity_df.values
    sample_names = similarity_df.index.tolist()

    logging.info(f"✅ Computed {len(sample_names)}x{len(sample_names)} distance matrix")
    return distance_matrix, sample_names

def cluster_samples(distance_matrix, sample_names,
                   similarity_threshold=0.3, min_group_size=2, max_group_size=5):
    """Apply hierarchical clustering to group samples."""

    logging.info(f"Clustering samples (threshold={similarity_threshold})...")

    # Convert distance matrix to condensed form for linkage
    condensed_distances = pdist(distance_matrix)

    # Perform hierarchical clustering
    linkage_matrix = linkage(condensed_distances, method='average')

    # Cut tree at similarity threshold (convert to distance threshold)
    distance_threshold = 1 - similarity_threshold
    cluster_labels = fcluster(linkage_matrix, distance_threshold, criterion='distance')

    # Group samples by cluster
    groups = {}
    for sample, cluster_id in zip(sample_names, cluster_labels):
        if cluster_id not in groups:
            groups[cluster_id] = []
        groups[cluster_id].append(sample)

    # Filter groups by size constraints
    valid_groups = []
    individual_samples = []

    for group_samples in groups.values():
        if min_group_size <= len(group_samples) <= max_group_size:
            valid_groups.append(group_samples)
        else:
            # Add samples that don't fit criteria as individual samples
            individual_samples.extend(group_samples)

    logging.info(f"✅ Created {len(valid_groups)} valid groups, {len(individual_samples)} individual samples")

    return valid_groups, individual_samples

def create_metagrouper_output(groups, individual_samples, output_dir, sample_names):
    """Create MetaGrouper-compatible output format."""

    output_path = Path(output_dir)

    # Create assembly recommendations in MetaGrouper format
    recommendations = {
        "strategy": "kmer_grouped",
        "tool": "sourmash",
        "confidence": 0.85,  # High confidence for sourmash approach
        "groups": [],
        "individual_samples": individual_samples,
        "summary": {
            "total_samples": len(sample_names),
            "grouped_samples": sum(len(group) for group in groups),
            "individual_samples": len(individual_samples),
            "total_groups": len(groups)
        }
    }

    # Add group information
    for i, group_samples in enumerate(groups):
        group_info = {
            "group_id": f"group_{i+1}",
            "samples": group_samples,
            "size": len(group_samples),
            "assembly_strategy": "grouped"
        }
        recommendations["groups"].append(group_info)

    # Save recommendations
    recommendations_file = output_path / "assembly_recommendations.json"
    with open(recommendations_file, 'w') as f:
        json.dump(recommendations, f, indent=2)

    logging.info(f"✅ Saved assembly recommendations to {recommendations_file}")

    # Create summary report
    summary_file = output_path / "clustering_summary.txt"
    with open(summary_file, 'w') as f:
        f.write("Sourmash K-mer Clustering Summary\n")
        f.write("=" * 40 + "\n\n")
        f.write(f"Total samples processed: {len(sample_names)}\n")
        f.write(f"Valid groups created: {len(groups)}\n")
        f.write(f"Samples in groups: {sum(len(group) for group in groups)}\n")
        f.write(f"Individual samples: {len(individual_samples)}\n\n")

        f.write("Group Details:\n")
        for i, group in enumerate(groups):
            f.write(f"  Group {i+1}: {len(group)} samples - {', '.join(group)}\n")

        if individual_samples:
            f.write(f"\nIndividual samples: {', '.join(individual_samples)}\n")

    logging.info(f"✅ Saved summary report to {summary_file}")

    return recommendations

def main():
    parser = argparse.ArgumentParser(description="Sourmash-based clustering for MetaGrouper validation")
    parser.add_argument("sample_dir", help="Directory containing FASTQ files")
    parser.add_argument("-o", "--output", default="results/kmer_groups",
                       help="Output directory")
    parser.add_argument("--similarity-threshold", type=float, default=0.3,
                       help="Similarity threshold for grouping (default: 0.3)")
    parser.add_argument("--min-group-size", type=int, default=2,
                       help="Minimum group size (default: 2)")
    parser.add_argument("--max-group-size", type=int, default=5,
                       help="Maximum group size (default: 5)")
    parser.add_argument("--ksize", type=int, default=21,
                       help="K-mer size (default: 21)")
    parser.add_argument("--scaled", type=int, default=1000,
                       help="Sourmash scaled parameter (default: 1000)")

    args = parser.parse_args()

    logging.info("🧬 Sourmash K-mer Clustering for MetaGrouper Validation")
    logging.info("=" * 60)

    # Create output directory
    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)

    try:
        # Step 1: Create sourmash sketches
        sketch_files = create_sourmash_sketches(
            args.sample_dir, args.output,
            ksize=args.ksize, scaled=args.scaled
        )

        if not sketch_files:
            raise RuntimeError("No sketches created - check input directory and file format")

        # Step 2: Compute distance matrix
        distance_matrix, sample_names = compute_sourmash_distances(sketch_files, args.output)

        # Step 3: Cluster samples
        groups, individual_samples = cluster_samples(
            distance_matrix, sample_names,
            similarity_threshold=args.similarity_threshold,
            min_group_size=args.min_group_size,
            max_group_size=args.max_group_size
        )

        # Step 4: Create MetaGrouper-compatible output
        recommendations = create_metagrouper_output(
            groups, individual_samples, args.output, sample_names
        )

        # Success summary
        logging.info("\n" + "=" * 60)
        logging.info("🎉 Sourmash clustering completed successfully!")
        logging.info(f"📁 Results saved to: {args.output}")
        logging.info(f"📊 Created {len(groups)} groups from {len(sample_names)} samples")
        logging.info(f"⏱️  Next step: Generate random groupings")

        return True

    except Exception as e:
        logging.error(f"❌ Clustering failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)