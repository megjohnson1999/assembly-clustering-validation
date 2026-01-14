#!/usr/bin/env python3
"""
Assess and compare assembly quality between k-mer and random groupings.
This is the critical script that determines if k-mer clustering beats random.
"""
import os
import pandas as pd
from pathlib import Path
import numpy as np
import argparse
from collections import defaultdict

def parse_fasta_stats(fasta_file):
    """Calculate detailed assembly statistics from FASTA file."""
    if not Path(fasta_file).exists():
        return None

    contigs = []
    current_seq = ""

    try:
        with open(fasta_file) as f:
            for line in f:
                line = line.strip()
                if line.startswith(">"):
                    if current_seq:
                        contigs.append(len(current_seq))
                    current_seq = ""
                else:
                    current_seq += line
            # Don't forget the last contig
            if current_seq:
                contigs.append(len(current_seq))

    except Exception as e:
        print(f"Error reading {fasta_file}: {e}")
        return None

    if not contigs:
        return None

    # Sort contigs by length (descending)
    contigs.sort(reverse=True)

    # Basic stats
    total_length = sum(contigs)
    n_contigs = len(contigs)
    max_contig = max(contigs)
    min_contig = min(contigs)
    mean_contig = np.mean(contigs)
    median_contig = np.median(contigs)

    # Calculate N50
    cumsum = 0
    n50 = 0
    for length in contigs:
        cumsum += length
        if cumsum >= total_length / 2:
            n50 = length
            break

    # Calculate N90
    cumsum = 0
    n90 = 0
    for length in contigs:
        cumsum += length
        if cumsum >= total_length * 0.9:
            n90 = length
            break

    # Additional metrics
    contigs_1kb = sum(1 for c in contigs if c >= 1000)
    contigs_10kb = sum(1 for c in contigs if c >= 10000)

    return {
        'total_length': total_length,
        'n_contigs': n_contigs,
        'n50': n50,
        'n90': n90,
        'max_contig': max_contig,
        'min_contig': min_contig,
        'mean_contig': mean_contig,
        'median_contig': median_contig,
        'contigs_1kb+': contigs_1kb,
        'contigs_10kb+': contigs_10kb,
        'assembly_file': str(fasta_file)
    }

def get_assembly_stats(assembly_dir, method_name):
    """Get stats for all assemblies in a directory."""
    stats = []
    assembly_path = Path(assembly_dir)

    if not assembly_path.exists():
        print(f"Warning: Assembly directory not found: {assembly_dir}")
        return pd.DataFrame()

    # Look for MEGAHIT output files
    pattern_files = [
        "*/final.contigs.fa",  # Standard MEGAHIT output
        "*/*.contigs.fa",      # Alternative naming
        "*/*.fa"               # Fallback
    ]

    found_files = []
    for pattern in pattern_files:
        found_files.extend(assembly_path.glob(pattern))

    if not found_files:
        print(f"Warning: No assembly files found in {assembly_dir}")
        return pd.DataFrame()

    print(f"Found {len(found_files)} assembly files in {assembly_dir}")

    for assembly_file in found_files:
        # Extract group name from path
        group_name = assembly_file.parent.name

        print(f"  Processing {group_name}...")

        stats_dict = parse_fasta_stats(assembly_file)
        if stats_dict:
            stats_dict['group'] = group_name
            stats_dict['method'] = method_name
            stats.append(stats_dict)
        else:
            print(f"    Warning: Failed to parse {assembly_file}")

    return pd.DataFrame(stats)

def calculate_summary_stats(df, method_name):
    """Calculate summary statistics for a method."""
    if df.empty:
        return {}

    numeric_cols = ['total_length', 'n_contigs', 'n50', 'n90', 'max_contig',
                   'mean_contig', 'contigs_1kb+', 'contigs_10kb+']

    summary = {}
    for col in numeric_cols:
        if col in df.columns:
            summary[f'{col}_mean'] = df[col].mean()
            summary[f'{col}_std'] = df[col].std()
            summary[f'{col}_median'] = df[col].median()

    summary['n_assemblies'] = len(df)
    summary['method'] = method_name

    return summary

def compare_assemblies(kmer_dir, random_dir, output_dir):
    """Main comparison function."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print("Assembly Quality Assessment")
    print("=" * 50)

    # Get assembly stats
    print("\\nAnalyzing k-mer clustering assemblies...")
    kmer_stats = get_assembly_stats(kmer_dir, 'kmer')

    print("\\nAnalyzing random grouping assemblies...")
    random_stats = get_assembly_stats(random_dir, 'random')

    if kmer_stats.empty and random_stats.empty:
        print("ERROR: No assembly stats found for either method")
        return

    if kmer_stats.empty:
        print("ERROR: No k-mer assembly stats found")
        return

    if random_stats.empty:
        print("ERROR: No random assembly stats found")
        return

    # Combine all stats
    all_stats = pd.concat([kmer_stats, random_stats], ignore_index=True)

    # Save detailed results
    detailed_file = output_path / "detailed_assembly_stats.csv"
    all_stats.to_csv(detailed_file, index=False)
    print(f"\\n✓ Detailed stats saved to: {detailed_file}")

    # Calculate summary statistics
    kmer_summary = calculate_summary_stats(kmer_stats, 'kmer')
    random_summary = calculate_summary_stats(random_stats, 'random')

    # Statistical comparisons
    results = {}
    metrics = ['total_length', 'n50', 'n90', 'max_contig', 'contigs_1kb+', 'contigs_10kb+']

    try:
        from scipy.stats import mannwhitneyu
        have_scipy = True
    except ImportError:
        have_scipy = False
        print("Warning: scipy not available - using simple comparisons")

    for metric in metrics:
        if metric in kmer_stats.columns and metric in random_stats.columns:
            kmer_values = kmer_stats[metric].dropna()
            random_values = random_stats[metric].dropna()

            if len(kmer_values) > 0 and len(random_values) > 0:
                kmer_mean = kmer_values.mean()
                random_mean = random_values.mean()

                result = {
                    'metric': metric,
                    'kmer_mean': kmer_mean,
                    'random_mean': random_mean,
                    'kmer_better': kmer_mean > random_mean,
                    'improvement_ratio': kmer_mean / random_mean if random_mean > 0 else np.inf,
                    'kmer_n': len(kmer_values),
                    'random_n': len(random_values)
                }

                # Statistical test if available
                if have_scipy and len(kmer_values) >= 3 and len(random_values) >= 3:
                    try:
                        statistic, p_value = mannwhitneyu(kmer_values, random_values,
                                                        alternative='two-sided')
                        result['p_value'] = p_value
                        result['significant'] = p_value < 0.05
                    except Exception as e:
                        print(f"Warning: Statistical test failed for {metric}: {e}")
                        result['p_value'] = None
                        result['significant'] = None
                else:
                    result['p_value'] = None
                    result['significant'] = None

                results[metric] = result

    # Create summary report
    summary_file = output_path / "comparison_summary.txt"
    with open(summary_file, 'w') as f:
        f.write("MetaGrouper K-mer vs Random Grouping Comparison\\n")
        f.write("=" * 60 + "\\n\\n")

        f.write("ASSEMBLY COUNTS:\\n")
        f.write(f"  K-mer clustering assemblies: {len(kmer_stats)}\\n")
        f.write(f"  Random grouping assemblies: {len(random_stats)}\\n\\n")

        f.write("ASSEMBLY QUALITY COMPARISON:\\n")
        f.write("-" * 40 + "\\n")

        for metric, result in results.items():
            f.write(f"\\n{metric.upper()}:\\n")
            f.write(f"  K-mer mean: {result['kmer_mean']:,.0f}\\n")
            f.write(f"  Random mean: {result['random_mean']:,.0f}\\n")
            f.write(f"  K-mer better: {result['kmer_better']}\\n")
            f.write(f"  Improvement: {result['improvement_ratio']:.2f}x\\n")

            if result['p_value'] is not None:
                f.write(f"  P-value: {result['p_value']:.4f}\\n")
                f.write(f"  Significant: {result['significant']}\\n")

        # Overall assessment
        f.write("\\n" + "=" * 60 + "\\n")
        f.write("OVERALL ASSESSMENT:\\n")

        n_metrics = len(results)
        n_kmer_better = sum(1 for r in results.values() if r['kmer_better'])
        n_significant = sum(1 for r in results.values() if r.get('significant') == True)

        f.write(f"\\nMetrics where k-mer clustering is better: {n_kmer_better}/{n_metrics}\\n")
        if have_scipy:
            f.write(f"Statistically significant improvements: {n_significant}/{n_metrics}\\n")

        # Decision logic
        f.write("\\nRECOMMENDAT0N:\\n")

        if n_kmer_better >= 4 and (not have_scipy or n_significant >= 2):
            decision = "PROMISING"
            f.write("✓ K-mer clustering shows clear advantages over random grouping\\n")
            f.write("✓ RECOMMENDED: Scale up to larger sample sizes (200+ samples)\\n")

        elif n_kmer_better >= 3:
            decision = "MIXED"
            f.write("~ K-mer clustering shows some advantages\\n")
            f.write("~ RECOMMENDED: Test with larger sample size or refine method\\n")

        else:
            decision = "POOR"
            f.write("✗ K-mer clustering does not consistently beat random grouping\\n")
            f.write("✗ RECOMMENDED: Fundamental issues with approach - consider alternatives\\n")

        # Practical guidance
        f.write(f"\\nNEXT STEPS:\\n")
        if decision == "PROMISING":
            f.write("1. Scale up to 200-500 samples\\n")
            f.write("2. Test different k-mer similarity thresholds\\n")
            f.write("3. Compare against patient-based groupings\\n")
        elif decision == "MIXED":
            f.write("1. Test with 100-200 samples to get more statistical power\\n")
            f.write("2. Investigate why some metrics don't improve\\n")
            f.write("3. Consider hybrid approaches\\n")
        else:
            f.write("1. Stop investing time in k-mer clustering approach\\n")
            f.write("2. Investigate alternative grouping methods\\n")
            f.write("3. Consider metadata-based approaches instead\\n")

    print(f"\\n✓ Summary report saved to: {summary_file}")

    # Create simple results DataFrame for programmatic access
    results_df = pd.DataFrame([
        {
            'metric': metric,
            'kmer_mean': result['kmer_mean'],
            'random_mean': result['random_mean'],
            'kmer_better': result['kmer_better'],
            'improvement_ratio': result['improvement_ratio'],
            'p_value': result.get('p_value'),
            'significant': result.get('significant')
        }
        for metric, result in results.items()
    ])

    results_file = output_path / "comparison_results.csv"
    results_df.to_csv(results_file, index=False)

    # Print summary to console
    print(f"\\n" + "=" * 60)
    print("QUICK RESULTS SUMMARY:")
    print(f"K-mer better than random: {n_kmer_better}/{n_metrics} metrics")
    if have_scipy:
        print(f"Statistically significant: {n_significant}/{n_metrics} metrics")

    decision_emoji = {"PROMISING": "✅", "MIXED": "⚠️", "POOR": "❌"}
    print(f"Overall assessment: {decision_emoji.get(decision, '?')} {decision}")

    return results_df

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare k-mer vs random assembly quality")
    parser.add_argument("--kmer-dir", default="results/assemblies/kmer",
                       help="Directory with k-mer clustering assemblies")
    parser.add_argument("--random-dir", default="results/assemblies/random",
                       help="Directory with random grouping assemblies")
    parser.add_argument("--output-dir", default="results/metrics",
                       help="Output directory for comparison results")

    args = parser.parse_args()

    print(f"K-mer assemblies: {args.kmer_dir}")
    print(f"Random assemblies: {args.random_dir}")
    print(f"Output directory: {args.output_dir}")
    print()

    results = compare_assemblies(args.kmer_dir, args.random_dir, args.output_dir)

    if results is not None:
        print("\\n✓ Assembly quality comparison complete!")
        print(f"\\nView full results: cat {args.output_dir}/comparison_summary.txt")
    else:
        print("\\n✗ Assembly quality comparison failed")
        exit(1)