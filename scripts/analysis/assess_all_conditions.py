#!/usr/bin/env python3
"""
Comprehensive assembly quality assessment across all experimental conditions:
1. Individual assemblies (50 separate assemblies)
2. Random groupings (5 different seeds)
3. K-mer grouping (1 grouping from MetaGrouper)
4. Global assembly (all 50 samples together)

This script provides the definitive answer: Does k-mer clustering beat random?
"""
import os
import pandas as pd
from pathlib import Path
import numpy as np
import argparse
from collections import defaultdict
import json

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
            if current_seq:
                contigs.append(len(current_seq))

    except Exception as e:
        print(f"Error reading {fasta_file}: {e}")
        return None

    if not contigs:
        return None

    # Sort contigs by length (descending)
    contigs.sort(reverse=True)

    # Calculate comprehensive statistics
    total_length = sum(contigs)
    n_contigs = len(contigs)
    max_contig = max(contigs)
    min_contig = min(contigs)
    mean_contig = np.mean(contigs)
    median_contig = np.median(contigs)

    # Calculate Nx statistics
    def calculate_nx(contigs, percentage):
        cumsum = 0
        target = total_length * percentage
        for length in contigs:
            cumsum += length
            if cumsum >= target:
                return length
        return 0

    n50 = calculate_nx(contigs, 0.5)
    n75 = calculate_nx(contigs, 0.75)
    n90 = calculate_nx(contigs, 0.9)

    # Contig size categories
    contigs_500 = sum(1 for c in contigs if c >= 500)
    contigs_1kb = sum(1 for c in contigs if c >= 1000)
    contigs_5kb = sum(1 for c in contigs if c >= 5000)
    contigs_10kb = sum(1 for c in contigs if c >= 10000)

    # Assembly continuity metrics
    longest_10 = sum(sorted(contigs, reverse=True)[:10]) if len(contigs) >= 10 else total_length

    return {
        'total_length': total_length,
        'n_contigs': n_contigs,
        'n50': n50,
        'n75': n75,
        'n90': n90,
        'max_contig': max_contig,
        'min_contig': min_contig,
        'mean_contig': mean_contig,
        'median_contig': median_contig,
        'contigs_500+': contigs_500,
        'contigs_1kb+': contigs_1kb,
        'contigs_5kb+': contigs_5kb,
        'contigs_10kb+': contigs_10kb,
        'longest_10_sum': longest_10,
        'assembly_file': str(fasta_file)
    }

def get_assembly_stats_by_condition(base_assembly_dir):
    """Get assembly stats organized by experimental condition."""

    base_path = Path(base_assembly_dir)
    all_stats = []

    conditions = {
        'individual': 'Individual assemblies',
        'kmer': 'K-mer clustering',
        'random': 'Random grouping',
        'global': 'Global assembly'
    }

    for condition_dir, condition_name in conditions.items():
        condition_path = base_path / condition_dir

        if not condition_path.exists():
            print(f"Warning: {condition_name} directory not found: {condition_path}")
            continue

        print(f"\\nAnalyzing {condition_name}...")

        # Handle different file patterns
        assembly_files = list(condition_path.glob("*/final.contigs.fa"))
        if not assembly_files:
            assembly_files = list(condition_path.glob("*/*.contigs.fa"))
        if not assembly_files:
            assembly_files = list(condition_path.glob("*/*.fa"))

        if not assembly_files:
            print(f"  Warning: No assembly files found in {condition_path}")
            continue

        print(f"  Found {len(assembly_files)} assemblies")

        for assembly_file in assembly_files:
            group_name = assembly_file.parent.name

            # Parse condition and subcondition from group name
            if condition_dir == 'random':
                # Extract seed number for random conditions
                parts = group_name.split('_')
                if 'random' in group_name and any(p.isdigit() for p in parts):
                    seed = next(p for p in parts if p.isdigit())
                    subcondition = f"random_seed_{seed}"
                else:
                    subcondition = "random_unknown"
            else:
                subcondition = condition_dir

            stats_dict = parse_fasta_stats(assembly_file)
            if stats_dict:
                stats_dict.update({
                    'condition': condition_dir,
                    'subcondition': subcondition,
                    'group_name': group_name,
                    'condition_display': condition_name
                })
                all_stats.append(stats_dict)
            else:
                print(f"    Warning: Failed to parse {assembly_file}")

    return pd.DataFrame(all_stats)

def calculate_condition_summaries(df):
    """Calculate summary statistics for each condition."""

    summaries = {}

    # Group by main condition
    for condition in df['condition'].unique():
        condition_df = df[df['condition'] == condition]

        if condition == 'random':
            # For random, we want to summarize across all seeds
            summaries[condition] = {
                'n_assemblies': len(condition_df),
                'condition_type': 'multiple_assemblies'
            }
        else:
            summaries[condition] = {
                'n_assemblies': len(condition_df),
                'condition_type': 'single_group' if condition != 'individual' else 'multiple_assemblies'
            }

        # Calculate statistics for numeric columns
        numeric_cols = ['total_length', 'n_contigs', 'n50', 'n75', 'n90',
                       'max_contig', 'mean_contig', 'contigs_1kb+', 'contigs_10kb+']

        for col in numeric_cols:
            if col in condition_df.columns:
                values = condition_df[col].dropna()
                if len(values) > 0:
                    summaries[condition][f'{col}_mean'] = values.mean()
                    summaries[condition][f'{col}_std'] = values.std()
                    summaries[condition][f'{col}_median'] = values.median()
                    summaries[condition][f'{col}_min'] = values.min()
                    summaries[condition][f'{col}_max'] = values.max()

    return summaries

def analyze_kmer_vs_random(df, output_dir):
    """Key analysis: How does k-mer clustering compare to random groupings?"""

    kmer_df = df[df['condition'] == 'kmer']
    random_df = df[df['condition'] == 'random']

    if kmer_df.empty:
        print("ERROR: No k-mer clustering results found")
        return None

    if random_df.empty:
        print("ERROR: No random grouping results found")
        return None

    analysis_results = {}

    # Key metrics to compare
    metrics = ['total_length', 'n50', 'n90', 'max_contig', 'contigs_1kb+', 'contigs_10kb+']

    for metric in metrics:
        if metric not in kmer_df.columns or metric not in random_df.columns:
            continue

        kmer_values = kmer_df[metric].dropna()
        random_values = random_df[metric].dropna()

        if len(kmer_values) == 0 or len(random_values) == 0:
            continue

        # K-mer statistics
        kmer_mean = kmer_values.mean()
        kmer_median = kmer_values.median()

        # Random statistics
        random_mean = random_values.mean()
        random_std = random_values.std()
        random_median = random_values.median()
        random_min = random_values.min()
        random_max = random_values.max()

        # Where does k-mer fall in the random distribution?
        random_sorted = sorted(random_values)
        kmer_rank = sum(1 for rv in random_sorted if kmer_mean > rv)
        kmer_percentile = (kmer_rank / len(random_sorted)) * 100

        # Is k-mer significantly different?
        improvement_ratio = kmer_mean / random_mean if random_mean > 0 else np.inf

        # Z-score (if we have enough random samples)
        z_score = None
        if random_std > 0 and len(random_values) >= 3:
            z_score = (kmer_mean - random_mean) / random_std

        analysis_results[metric] = {
            'kmer_mean': kmer_mean,
            'kmer_median': kmer_median,
            'random_mean': random_mean,
            'random_std': random_std,
            'random_median': random_median,
            'random_min': random_min,
            'random_max': random_max,
            'kmer_percentile': kmer_percentile,
            'improvement_ratio': improvement_ratio,
            'z_score': z_score,
            'kmer_better_than_avg': kmer_mean > random_mean,
            'kmer_better_than_median': kmer_mean > random_median,
            'kmer_better_than_best': kmer_mean > random_max,
            'kmer_worse_than_worst': kmer_mean < random_min
        }

    return analysis_results

def generate_comprehensive_report(df, kmer_vs_random, summaries, output_dir):
    """Generate the comprehensive analysis report."""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Main report file
    report_file = output_path / "comprehensive_analysis_report.txt"

    with open(report_file, 'w') as f:
        f.write("MetaGrouper Comprehensive Validation Results\\n")
        f.write("=" * 60 + "\\n\\n")

        f.write(f"Analysis Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\\n\\n")

        # Experimental overview
        f.write("EXPERIMENTAL DESIGN:\\n")
        f.write("-" * 30 + "\\n")
        for condition in ['individual', 'random', 'kmer', 'global']:
            if condition in summaries:
                n_assemblies = summaries[condition]['n_assemblies']
                f.write(f"{condition.capitalize()} assemblies: {n_assemblies}\\n")

        f.write("\\n" + "=" * 60 + "\\n")
        f.write("KEY QUESTION: DOES K-MER CLUSTERING BEAT RANDOM?\\n")
        f.write("=" * 60 + "\\n\\n")

        if kmer_vs_random:
            # Overall assessment
            better_count = sum(1 for r in kmer_vs_random.values() if r.get('kmer_better_than_avg', False))
            total_metrics = len(kmer_vs_random)

            f.write(f"SUMMARY: K-mer clustering beats random average in {better_count}/{total_metrics} metrics\\n\\n")

            # Detailed metric analysis
            f.write("DETAILED COMPARISON:\\n")
            f.write("-" * 40 + "\\n")

            for metric, results in kmer_vs_random.items():
                f.write(f"\\n{metric.upper().replace('_', ' ')}:\\n")
                f.write(f"  K-mer mean: {results['kmer_mean']:,.0f}\\n")
                f.write(f"  Random mean ± std: {results['random_mean']:,.0f} ± {results['random_std']:,.0f}\\n")
                f.write(f"  Random range: {results['random_min']:,.0f} - {results['random_max']:,.0f}\\n")
                f.write(f"  K-mer percentile in random distribution: {results['kmer_percentile']:.1f}%\\n")
                f.write(f"  Improvement ratio: {results['improvement_ratio']:.2f}x\\n")

                if results['z_score'] is not None:
                    f.write(f"  Z-score: {results['z_score']:.2f}\\n")

                # Interpretation
                if results['kmer_better_than_best']:
                    f.write("  → K-mer BETTER than best random grouping\\n")
                elif results['kmer_better_than_avg']:
                    f.write("  → K-mer better than random average\\n")
                elif results['kmer_worse_than_worst']:
                    f.write("  → K-mer WORSE than worst random grouping\\n")
                else:
                    f.write("  → K-mer within random range\\n")

            # Decision logic
            f.write("\\n" + "=" * 60 + "\\n")
            f.write("OVERALL ASSESSMENT:\\n")
            f.write("=" * 60 + "\\n")

            # Count strong signals
            beats_best = sum(1 for r in kmer_vs_random.values() if r.get('kmer_better_than_best', False))
            beats_avg = sum(1 for r in kmer_vs_random.values() if r.get('kmer_better_than_avg', False))
            worse_than_worst = sum(1 for r in kmer_vs_random.values() if r.get('kmer_worse_than_worst', False))

            f.write(f"Metrics where k-mer beats BEST random: {beats_best}/{total_metrics}\\n")
            f.write(f"Metrics where k-mer beats average random: {beats_avg}/{total_metrics}\\n")
            f.write(f"Metrics where k-mer worse than WORST random: {worse_than_worst}/{total_metrics}\\n\\n")

            # Final recommendation
            if beats_best >= 4:
                decision = "STRONGLY PROMISING"
                f.write("🎉 RECOMMENDATION: STRONGLY PROMISING\\n")
                f.write("K-mer clustering consistently beats even the best random groupings.\\n")
                f.write("This provides strong evidence that the approach is fundamentally sound.\\n\\n")
                f.write("NEXT STEPS:\\n")
                f.write("1. Scale up to 200-500 samples\\n")
                f.write("2. Test different similarity thresholds\\n")
                f.write("3. Compare against patient-based groupings\\n")
                f.write("4. Consider publication of results\\n")

            elif beats_avg >= 4 and worse_than_worst == 0:
                decision = "PROMISING"
                f.write("✅ RECOMMENDATION: PROMISING\\n")
                f.write("K-mer clustering consistently beats random average.\\n")
                f.write("Approach shows merit and is worth further development.\\n\\n")
                f.write("NEXT STEPS:\\n")
                f.write("1. Scale up to 200+ samples for more statistical power\\n")
                f.write("2. Investigate why it doesn't beat best random groupings\\n")
                f.write("3. Consider method refinements\\n")

            elif beats_avg >= 3 and worse_than_worst <= 1:
                decision = "MIXED"
                f.write("⚠️  RECOMMENDATION: MIXED RESULTS\\n")
                f.write("K-mer clustering shows some promise but inconsistent performance.\\n\\n")
                f.write("NEXT STEPS:\\n")
                f.write("1. Test with larger sample size (100-200 samples)\\n")
                f.write("2. Investigate method parameters\\n")
                f.write("3. Consider hybrid approaches\\n")

            else:
                decision = "NOT PROMISING"
                f.write("❌ RECOMMENDATION: NOT PROMISING\\n")
                f.write("K-mer clustering does not consistently outperform random grouping.\\n")
                f.write("The fundamental premise appears flawed.\\n\\n")
                f.write("NEXT STEPS:\\n")
                f.write("1. Stop development of k-mer clustering approach\\n")
                f.write("2. Investigate alternative grouping methods\\n")
                f.write("3. Focus on metadata-based or phylogenetic approaches\\n")

        else:
            f.write("ERROR: Could not perform k-mer vs random comparison\\n")
            decision = "ANALYSIS_FAILED"

        # Additional context from other conditions
        f.write("\\n" + "=" * 60 + "\\n")
        f.write("CONTEXTUAL RESULTS:\\n")
        f.write("=" * 60 + "\\n")

        # Individual vs grouped comparison
        if 'individual' in summaries and 'kmer' in summaries:
            f.write("\\nGrouping vs Individual Assembly:\\n")
            f.write("-" * 35 + "\\n")

            if 'n50_mean' in summaries['individual'] and 'n50_mean' in summaries['kmer']:
                ind_n50 = summaries['individual']['n50_mean']
                kmer_n50 = summaries['kmer']['n50_mean']
                ratio = kmer_n50 / ind_n50 if ind_n50 > 0 else np.inf

                f.write(f"Individual assembly N50: {ind_n50:,.0f}\\n")
                f.write(f"K-mer grouping N50: {kmer_n50:,.0f}\\n")
                f.write(f"Grouping improvement: {ratio:.2f}x\\n")

                if ratio > 1.2:
                    f.write("→ Grouping provides clear assembly improvement\\n")
                elif ratio > 0.8:
                    f.write("→ Grouping provides similar assembly quality\\n")
                else:
                    f.write("→ Individual assemblies may be better\\n")

        # Global assembly comparison
        if 'global' in summaries:
            f.write("\\nGlobal Assembly Performance:\\n")
            f.write("-" * 30 + "\\n")
            f.write("Note: Global assembly represents maximum cooperation but highest contamination risk.\\n")

    print(f"\\n✓ Comprehensive report saved to: {report_file}")
    return decision

def main():
    parser = argparse.ArgumentParser(description="Comprehensive assembly quality assessment")
    parser.add_argument("--assemblies-dir", default="results/assemblies",
                       help="Base directory containing all assembly results")
    parser.add_argument("--output-dir", default="results/comprehensive_analysis",
                       help="Output directory for analysis results")

    args = parser.parse_args()

    print("Comprehensive Multi-Condition Assembly Analysis")
    print("=" * 60)
    print(f"Assembly base directory: {args.assemblies_dir}")
    print(f"Output directory: {args.output_dir}")
    print()

    # Get assembly statistics for all conditions
    df = get_assembly_stats_by_condition(args.assemblies_dir)

    if df.empty:
        print("ERROR: No assembly statistics found")
        exit(1)

    print(f"\\nLoaded {len(df)} assembly results across {df['condition'].nunique()} conditions")

    # Save detailed stats
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    detailed_file = output_path / "detailed_assembly_statistics.csv"
    df.to_csv(detailed_file, index=False)
    print(f"✓ Detailed statistics saved: {detailed_file}")

    # Calculate condition summaries
    summaries = calculate_condition_summaries(df)

    # Key analysis: K-mer vs Random
    kmer_vs_random = analyze_kmer_vs_random(df, args.output_dir)

    # Generate comprehensive report
    decision = generate_comprehensive_report(df, kmer_vs_random, summaries, args.output_dir)

    # Console summary
    print("\\n" + "=" * 60)
    print("FINAL ANSWER")
    print("=" * 60)

    if kmer_vs_random:
        better_count = sum(1 for r in kmer_vs_random.values() if r.get('kmer_better_than_avg', False))
        total_metrics = len(kmer_vs_random)
        print(f"K-mer clustering beats random in {better_count}/{total_metrics} metrics")

    decision_emojis = {
        "STRONGLY PROMISING": "🎉",
        "PROMISING": "✅",
        "MIXED": "⚠️",
        "NOT PROMISING": "❌",
        "ANALYSIS_FAILED": "💥"
    }

    print(f"{decision_emojis.get(decision, '?')} Overall assessment: {decision}")
    print(f"\\nFull report: {args.output_dir}/comprehensive_analysis_report.txt")
    print("=" * 60)

if __name__ == "__main__":
    main()