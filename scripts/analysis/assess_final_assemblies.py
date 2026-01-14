#!/usr/bin/env python3
"""
Assess and compare the 8 final assemblies from the staged assembly workflow:
1. Individual meta-assembly (1 assembly)
2. Random grouping meta-assemblies (5 assemblies)
3. K-mer grouping meta-assembly (1 assembly)
4. Global assembly (1 assembly)

This provides the definitive answer: Does k-mer clustering beat random for final assembly quality?
"""
import os
import pandas as pd
from pathlib import Path
import numpy as np
import argparse

def parse_fasta_stats(fasta_file):
    """Calculate comprehensive assembly statistics from FASTA file."""
    if not Path(fasta_file).exists():
        print(f"Warning: Assembly file not found: {fasta_file}")
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
        print(f"Warning: No contigs found in {fasta_file}")
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
    contigs_1kb = sum(1 for c in contigs if c >= 1000)
    contigs_5kb = sum(1 for c in contigs if c >= 5000)
    contigs_10kb = sum(1 for c in contigs if c >= 10000)
    contigs_50kb = sum(1 for c in contigs if c >= 50000)
    contigs_100kb = sum(1 for c in contigs if c >= 100000)

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
        'contigs_1kb+': contigs_1kb,
        'contigs_5kb+': contigs_5kb,
        'contigs_10kb+': contigs_10kb,
        'contigs_50kb+': contigs_50kb,
        'contigs_100kb+': contigs_100kb,
        'longest_10_sum': longest_10,
        'assembly_file': str(fasta_file)
    }

def get_final_assembly_stats(assemblies_dir):
    """Get assembly statistics for all 8 final assemblies."""

    assemblies_path = Path(assemblies_dir)

    # Expected assembly files
    expected_assemblies = [
        ("individual_meta_assembly.fasta", "individual"),
        ("random_42_meta_assembly.fasta", "random_42"),
        ("random_43_meta_assembly.fasta", "random_43"),
        ("random_44_meta_assembly.fasta", "random_44"),
        ("random_45_meta_assembly.fasta", "random_45"),
        ("random_46_meta_assembly.fasta", "random_46"),
        ("kmer_meta_assembly.fasta", "kmer"),
        ("global_assembly.fasta", "global")
    ]

    all_stats = []

    print("Analyzing final assemblies...")

    for filename, condition in expected_assemblies:
        assembly_file = assemblies_path / filename

        print(f"  Processing {condition}: {assembly_file}")

        stats_dict = parse_fasta_stats(assembly_file)
        if stats_dict:
            # Add condition metadata
            stats_dict['condition'] = condition
            stats_dict['assembly_name'] = filename

            # Categorize condition type
            if condition == 'individual':
                stats_dict['condition_type'] = 'individual'
            elif condition.startswith('random_'):
                stats_dict['condition_type'] = 'random'
                stats_dict['random_seed'] = condition.split('_')[1]
            elif condition == 'kmer':
                stats_dict['condition_type'] = 'kmer'
            elif condition == 'global':
                stats_dict['condition_type'] = 'global'

            all_stats.append(stats_dict)
        else:
            print(f"    Warning: Failed to process {filename}")

    if not all_stats:
        print("ERROR: No assembly statistics found!")
        return pd.DataFrame()

    return pd.DataFrame(all_stats)

def analyze_kmer_vs_random(df):
    """Key analysis: How does k-mer meta-assembly compare to random meta-assemblies?"""

    kmer_df = df[df['condition_type'] == 'kmer']
    random_df = df[df['condition_type'] == 'random']

    if kmer_df.empty:
        print("ERROR: No k-mer assembly found")
        return None

    if random_df.empty:
        print("ERROR: No random assemblies found")
        return None

    # K-mer assembly (single value)
    kmer_stats = kmer_df.iloc[0]

    # Random assemblies (5 values)
    analysis_results = {}

    # Key metrics to compare
    metrics = ['total_length', 'n50', 'n75', 'n90', 'max_contig', 'contigs_1kb+',
               'contigs_10kb+', 'contigs_50kb+', 'contigs_100kb+']

    for metric in metrics:
        if metric not in random_df.columns:
            continue

        kmer_value = kmer_stats[metric]
        random_values = random_df[metric].values

        # Random distribution statistics
        random_mean = np.mean(random_values)
        random_std = np.std(random_values)
        random_median = np.median(random_values)
        random_min = np.min(random_values)
        random_max = np.max(random_values)

        # Where does k-mer fall in the random distribution?
        random_sorted = sorted(random_values)
        kmer_rank = sum(1 for rv in random_sorted if kmer_value > rv)
        kmer_percentile = (kmer_rank / len(random_sorted)) * 100

        # Performance comparisons
        improvement_ratio = kmer_value / random_mean if random_mean > 0 else np.inf

        # Z-score
        z_score = None
        if random_std > 0:
            z_score = (kmer_value - random_mean) / random_std

        analysis_results[metric] = {
            'kmer_value': kmer_value,
            'random_mean': random_mean,
            'random_std': random_std,
            'random_median': random_median,
            'random_min': random_min,
            'random_max': random_max,
            'kmer_percentile': kmer_percentile,
            'improvement_ratio': improvement_ratio,
            'z_score': z_score,
            'kmer_better_than_avg': kmer_value > random_mean,
            'kmer_better_than_median': kmer_value > random_median,
            'kmer_better_than_best': kmer_value > random_max,
            'kmer_worse_than_worst': kmer_value < random_min,
            'beats_n_random': kmer_rank
        }

    return analysis_results

def generate_comprehensive_report(df, kmer_vs_random, output_dir):
    """Generate the comprehensive analysis report."""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Main report file
    report_file = output_path / "final_assembly_comparison_report.txt"

    with open(report_file, 'w') as f:
        f.write("Assembly Clustering Validation: Final Results\\n")
        f.write("=" * 60 + "\\n\\n")

        f.write(f"Analysis Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\\n\\n")

        # Assembly overview
        f.write("FINAL ASSEMBLIES ANALYZED:\\n")
        f.write("-" * 40 + "\\n")

        condition_counts = df['condition_type'].value_counts()
        f.write(f"Individual meta-assembly: {condition_counts.get('individual', 0)}\\n")
        f.write(f"Random meta-assemblies: {condition_counts.get('random', 0)}\\n")
        f.write(f"K-mer meta-assembly: {condition_counts.get('kmer', 0)}\\n")
        f.write(f"Global assembly: {condition_counts.get('global', 0)}\\n")

        f.write("\\n" + "=" * 60 + "\\n")
        f.write("KEY QUESTION: DOES K-MER CLUSTERING BEAT RANDOM?\\n")
        f.write("=" * 60 + "\\n\\n")

        if kmer_vs_random:
            # Quick summary statistics
            f.write("QUICK SUMMARY:\\n")
            f.write("-" * 20 + "\\n")

            better_count = sum(1 for r in kmer_vs_random.values() if r.get('kmer_better_than_avg', False))
            beats_all_count = sum(1 for r in kmer_vs_random.values() if r.get('kmer_better_than_best', False))
            total_metrics = len(kmer_vs_random)

            f.write(f"K-mer beats random average: {better_count}/{total_metrics} metrics\\n")
            f.write(f"K-mer beats ALL random assemblies: {beats_all_count}/{total_metrics} metrics\\n\\n")

            # Detailed metric analysis
            f.write("DETAILED COMPARISON:\\n")
            f.write("-" * 40 + "\\n")

            for metric, results in kmer_vs_random.items():
                f.write(f"\\n{metric.upper().replace('_', ' ')}:\\n")
                f.write(f"  K-mer value: {results['kmer_value']:,.0f}\\n")
                f.write(f"  Random mean ± std: {results['random_mean']:,.0f} ± {results['random_std']:,.0f}\\n")
                f.write(f"  Random range: {results['random_min']:,.0f} - {results['random_max']:,.0f}\\n")
                f.write(f"  K-mer percentile: {results['kmer_percentile']:.1f}%\\n")
                f.write(f"  Improvement ratio: {results['improvement_ratio']:.2f}x\\n")
                f.write(f"  Beats {results['beats_n_random']}/5 random assemblies\\n")

                if results['z_score'] is not None:
                    f.write(f"  Z-score: {results['z_score']:.2f}\\n")

                # Clear interpretation
                if results['kmer_better_than_best']:
                    f.write("  → 🎉 K-mer BETTER than ALL random assemblies!\\n")
                elif results['beats_n_random'] >= 4:
                    f.write("  → ✅ K-mer beats most random assemblies\\n")
                elif results['beats_n_random'] >= 3:
                    f.write("  → ~ K-mer beats some random assemblies\\n")
                elif results['kmer_worse_than_worst']:
                    f.write("  → ❌ K-mer WORSE than ALL random assemblies\\n")
                else:
                    f.write("  → ~ K-mer performance mixed\\n")

            # Overall assessment
            f.write("\\n" + "=" * 60 + "\\n")
            f.write("OVERALL ASSESSMENT\\n")
            f.write("=" * 60 + "\\n")

            # Decision logic based on results
            beats_all_in_most = sum(1 for r in kmer_vs_random.values() if r.get('kmer_better_than_best', False))
            beats_most_in_most = sum(1 for r in kmer_vs_random.values() if r.get('beats_n_random', 0) >= 4)
            beats_avg_in_most = sum(1 for r in kmer_vs_random.values() if r.get('kmer_better_than_avg', False))
            worse_than_all = sum(1 for r in kmer_vs_random.values() if r.get('kmer_worse_than_worst', False))

            f.write(f"Metrics where k-mer beats ALL random: {beats_all_in_most}/{total_metrics}\\n")
            f.write(f"Metrics where k-mer beats 4+ random: {beats_most_in_most}/{total_metrics}\\n")
            f.write(f"Metrics where k-mer beats average: {beats_avg_in_most}/{total_metrics}\\n")
            f.write(f"Metrics where k-mer worse than ALL: {worse_than_all}/{total_metrics}\\n\\n")

            # Final recommendation
            if beats_all_in_most >= 4:
                decision = "STRONGLY PROMISING"
                f.write("🎉 RECOMMENDATION: STRONGLY PROMISING\\n")
                f.write("K-mer clustering consistently produces better meta-assemblies than even\\n")
                f.write("the BEST random groupings across multiple quality metrics.\\n\\n")
                f.write("This is strong evidence that k-mer clustering captures biologically\\n")
                f.write("meaningful relationships for co-assembly.\\n\\n")
                f.write("NEXT STEPS:\\n")
                f.write("1. Scale up to 200+ samples to confirm robustness\\n")
                f.write("2. Test different similarity thresholds (0.2, 0.4, 0.5)\\n")
                f.write("3. Compare against metadata-based grouping strategies\\n")
                f.write("4. Consider publication of validation results\\n")

            elif beats_most_in_most >= 4 and worse_than_all == 0:
                decision = "PROMISING"
                f.write("✅ RECOMMENDATION: PROMISING\\n")
                f.write("K-mer clustering consistently beats most random groupings,\\n")
                f.write("indicating the approach has merit.\\n\\n")
                f.write("NEXT STEPS:\\n")
                f.write("1. Test with larger sample size (100-200 samples)\\n")
                f.write("2. Optimize similarity threshold and group size parameters\\n")
                f.write("3. Investigate why performance varies across metrics\\n")

            elif beats_avg_in_most >= 4 and worse_than_all <= 1:
                decision = "MIXED"
                f.write("⚠️  RECOMMENDATION: MIXED RESULTS\\n")
                f.write("K-mer clustering shows some advantages but inconsistent performance.\\n")
                f.write("Results suggest potential but need refinement.\\n\\n")
                f.write("NEXT STEPS:\\n")
                f.write("1. Investigate parameter optimization\\n")
                f.write("2. Test with different sample sizes and compositions\\n")
                f.write("3. Consider hybrid approaches combining k-mer and metadata\\n")

            else:
                decision = "NOT PROMISING"
                f.write("❌ RECOMMENDATION: NOT PROMISING\\n")
                f.write("K-mer clustering does not consistently outperform random grouping\\n")
                f.write("for meta-assembly quality. The fundamental premise appears flawed.\\n\\n")
                f.write("NEXT STEPS:\\n")
                f.write("1. Stop development of pure k-mer clustering approach\\n")
                f.write("2. Investigate alternative grouping methods:\\n")
                f.write("   - Taxonomic similarity\\n")
                f.write("   - Metadata-based grouping\\n")
                f.write("   - Phylogenetic approaches\\n")
                f.write("3. Focus resources on more promising directions\\n")

            # Contextual comparisons
            f.write("\\n" + "=" * 60 + "\\n")
            f.write("CONTEXTUAL COMPARISONS\\n")
            f.write("=" * 60 + "\\n")

            # Individual vs grouping approaches
            if 'individual' in df['condition_type'].values:
                individual_stats = df[df['condition_type'] == 'individual'].iloc[0]
                kmer_stats = df[df['condition_type'] == 'kmer'].iloc[0]

                f.write("\\nGrouping vs Individual Assembly:\\n")
                f.write("-" * 35 + "\\n")

                for metric in ['total_length', 'n50', 'max_contig']:
                    if metric in individual_stats and metric in kmer_stats:
                        ind_val = individual_stats[metric]
                        kmer_val = kmer_stats[metric]
                        ratio = kmer_val / ind_val if ind_val > 0 else np.inf

                        f.write(f"{metric}: Individual={ind_val:,.0f}, K-mer={kmer_val:,.0f} ({ratio:.2f}x)\\n")

            # Global assembly comparison
            if 'global' in df['condition_type'].values:
                global_stats = df[df['condition_type'] == 'global'].iloc[0]

                f.write("\\nGlobal Assembly (Maximum Cooperation):\\n")
                f.write("-" * 40 + "\\n")
                f.write("Global assembly represents the maximum possible cooperation\\n")
                f.write("but also maximum contamination risk.\\n")

                for metric in ['total_length', 'n50', 'n_contigs']:
                    if metric in global_stats:
                        f.write(f"{metric}: {global_stats[metric]:,.0f}\\n")

        else:
            f.write("ERROR: Could not perform k-mer vs random comparison\\n")
            decision = "ANALYSIS_FAILED"

    print(f"\\n✓ Comprehensive report saved to: {report_file}")
    return decision

def main():
    parser = argparse.ArgumentParser(description="Assess final meta-assemblies from staged workflow")
    parser.add_argument("--assemblies-dir", default="results/assemblies/final_assemblies",
                       help="Directory containing the 8 final assemblies")
    parser.add_argument("--output-dir", default="results/final_analysis",
                       help="Output directory for analysis results")

    args = parser.parse_args()

    print("Final Assembly Quality Assessment")
    print("=" * 60)
    print(f"Assemblies directory: {args.assemblies_dir}")
    print(f"Output directory: {args.output_dir}")
    print()

    # Check if assemblies directory exists
    if not Path(args.assemblies_dir).exists():
        print(f"ERROR: Assemblies directory not found: {args.assemblies_dir}")
        print("Make sure the staged assembly workflow completed successfully.")
        exit(1)

    # Get assembly statistics
    df = get_final_assembly_stats(args.assemblies_dir)

    if df.empty:
        print("ERROR: No assembly statistics found")
        exit(1)

    print(f"\\nLoaded statistics for {len(df)} final assemblies")

    # Save detailed stats
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    detailed_file = output_path / "final_assembly_statistics.csv"
    df.to_csv(detailed_file, index=False)
    print(f"✓ Detailed statistics saved: {detailed_file}")

    # Key analysis: K-mer vs Random
    kmer_vs_random = analyze_kmer_vs_random(df)

    # Generate comprehensive report
    decision = generate_comprehensive_report(df, kmer_vs_random, args.output_dir)

    # Console summary
    print("\\n" + "=" * 60)
    print("FINAL ANSWER")
    print("=" * 60)

    if kmer_vs_random:
        better_count = sum(1 for r in kmer_vs_random.values() if r.get('kmer_better_than_avg', False))
        total_metrics = len(kmer_vs_random)
        beats_all_count = sum(1 for r in kmer_vs_random.values() if r.get('kmer_better_than_best', False))

        print(f"K-mer beats random average: {better_count}/{total_metrics} metrics")
        print(f"K-mer beats ALL random assemblies: {beats_all_count}/{total_metrics} metrics")

    decision_emojis = {
        "STRONGLY PROMISING": "🎉",
        "PROMISING": "✅",
        "MIXED": "⚠️",
        "NOT PROMISING": "❌",
        "ANALYSIS_FAILED": "💥"
    }

    print(f"{decision_emojis.get(decision, '?')} Overall assessment: {decision}")
    print(f"\\nFull report: {args.output_dir}/final_assembly_comparison_report.txt")
    print("=" * 60)

if __name__ == "__main__":
    main()