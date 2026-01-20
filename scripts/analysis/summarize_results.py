#!/usr/bin/env python3
"""
Summarize assembly comparison results from seqkit stats and CheckV.

This script reads the output from both analysis tools and generates
a comparison summary across all 5 assembly strategies.
"""

import argparse
import pandas as pd
from pathlib import Path
import sys


def load_seqkit_stats(stats_file):
    """Load seqkit stats output."""
    df = pd.read_csv(stats_file, sep='\t')

    # Extract strategy name from file path
    def extract_strategy(path):
        if 'individual' in path:
            return 'individual'
        elif 'groups_size_5' in path:
            return 'groups_size_5'
        elif 'groups_size_12' in path:
            return 'groups_size_12'
        elif 'groups_size_25' in path:
            return 'groups_size_25'
        elif 'global' in path:
            return 'global'
        return 'unknown'

    df['strategy'] = df['file'].apply(extract_strategy)
    return df


def load_checkv_results(checkv_dir, strategy):
    """Load CheckV quality summary for a strategy."""
    quality_file = Path(checkv_dir) / strategy / 'quality_summary.tsv'

    if not quality_file.exists():
        print(f"Warning: CheckV results not found for {strategy}")
        return None

    df = pd.read_csv(quality_file, sep='\t')
    df['strategy'] = strategy
    return df


def summarize_checkv(checkv_df):
    """Generate summary statistics from CheckV results."""
    if checkv_df is None or len(checkv_df) == 0:
        return {
            'total_contigs': 0,
            'complete': 0,
            'high_quality': 0,
            'medium_quality': 0,
            'low_quality': 0,
            'not_determined': 0,
            'viral_genes_mean': 0,
            'host_genes_mean': 0,
            'completeness_mean': 0
        }

    # Count by checkv_quality
    quality_counts = checkv_df['checkv_quality'].value_counts()

    return {
        'total_contigs': len(checkv_df),
        'complete': quality_counts.get('Complete', 0),
        'high_quality': quality_counts.get('High-quality', 0),
        'medium_quality': quality_counts.get('Medium-quality', 0),
        'low_quality': quality_counts.get('Low-quality', 0),
        'not_determined': quality_counts.get('Not-determined', 0),
        'viral_genes_mean': checkv_df['viral_genes'].mean() if 'viral_genes' in checkv_df.columns else 0,
        'host_genes_mean': checkv_df['host_genes'].mean() if 'host_genes' in checkv_df.columns else 0,
        'completeness_mean': checkv_df['completeness'].mean() if 'completeness' in checkv_df.columns else 0
    }


def main():
    parser = argparse.ArgumentParser(description='Summarize assembly comparison results')
    parser.add_argument('--results-dir', default='results/analysis',
                        help='Directory containing analysis results')
    parser.add_argument('--output', default='results/analysis/comparison_summary.tsv',
                        help='Output file for comparison summary')

    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    strategies = ['individual', 'groups_size_5', 'groups_size_12', 'groups_size_25', 'global']

    print("=" * 60)
    print("Assembly Comparison Summary")
    print("=" * 60)

    # Load seqkit stats
    seqkit_file = results_dir / 'basic_metrics.tsv'
    if seqkit_file.exists():
        seqkit_df = load_seqkit_stats(seqkit_file)
        print("\n### Basic Assembly Metrics (seqkit stats) ###\n")

        # Select and rename columns for display
        display_cols = ['strategy', 'num_seqs', 'sum_len', 'min_len', 'avg_len', 'max_len', 'N50']
        available_cols = [c for c in display_cols if c in seqkit_df.columns]
        print(seqkit_df[available_cols].to_string(index=False))
    else:
        print(f"Warning: seqkit stats file not found: {seqkit_file}")
        seqkit_df = None

    # Load CheckV results for each strategy
    print("\n### CheckV Viral Quality Assessment ###\n")

    checkv_summaries = []
    for strategy in strategies:
        checkv_df = load_checkv_results(results_dir / 'checkv', strategy)
        summary = summarize_checkv(checkv_df)
        summary['strategy'] = strategy
        checkv_summaries.append(summary)

    checkv_summary_df = pd.DataFrame(checkv_summaries)

    # Reorder columns
    col_order = ['strategy', 'total_contigs', 'complete', 'high_quality', 'medium_quality',
                 'low_quality', 'not_determined', 'completeness_mean']
    available_cols = [c for c in col_order if c in checkv_summary_df.columns]
    checkv_summary_df = checkv_summary_df[available_cols]

    print(checkv_summary_df.to_string(index=False))

    # Calculate percentages for quality categories
    print("\n### Quality Distribution (% of contigs) ###\n")

    pct_df = checkv_summary_df.copy()
    for col in ['complete', 'high_quality', 'medium_quality', 'low_quality', 'not_determined']:
        if col in pct_df.columns:
            pct_df[f'{col}_pct'] = (pct_df[col] / pct_df['total_contigs'] * 100).round(1)

    pct_cols = ['strategy', 'complete_pct', 'high_quality_pct', 'medium_quality_pct',
                'low_quality_pct', 'not_determined_pct']
    available_pct_cols = [c for c in pct_cols if c in pct_df.columns]
    print(pct_df[available_pct_cols].to_string(index=False))

    # Save combined summary
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Merge seqkit and checkv summaries
    if seqkit_df is not None:
        combined_df = seqkit_df.merge(checkv_summary_df, on='strategy', how='outer')
    else:
        combined_df = checkv_summary_df

    combined_df.to_csv(output_path, sep='\t', index=False)
    print(f"\nCombined summary saved to: {output_path}")

    # Key insights
    print("\n" + "=" * 60)
    print("Key Insights")
    print("=" * 60)

    if len(checkv_summary_df) > 0 and 'complete' in checkv_summary_df.columns:
        best_complete = checkv_summary_df.loc[checkv_summary_df['complete'].idxmax()]
        print(f"\nMost complete genomes: {best_complete['strategy']} ({best_complete['complete']} complete)")

        best_hq = checkv_summary_df.loc[(checkv_summary_df['complete'] + checkv_summary_df['high_quality']).idxmax()]
        hq_total = best_hq['complete'] + best_hq['high_quality']
        print(f"Most high-quality+ genomes: {best_hq['strategy']} ({hq_total} complete + high-quality)")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
