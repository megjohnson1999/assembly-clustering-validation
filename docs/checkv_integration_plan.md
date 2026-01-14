# CheckV Integration Plan: Viral Assembly Analysis

**Date**: January 14, 2026
**Status**: Planning document for post-assembly viral analysis
**Goal**: Determine if k-mer clustering improves viral genome recovery vs random grouping

## Overview

This document outlines the plan for integrating CheckV analysis as "Phase 2" of the assembly clustering validation. While Phase 1 answers "Does k-mer clustering improve general assembly quality?", Phase 2 will answer "Does k-mer clustering improve viral genome recovery?"

## Scientific Rationale

**Why viral-specific analysis matters:**
- General assembly metrics (N50, contig count) don't capture viral genome completeness
- Fragmented/incomplete viral genomes are a major challenge in viral metagenomics
- K-mer clustering might specifically benefit viral genome assembly due to sequence similarity patterns
- CheckV provides standardized viral genome quality assessment

## CheckV Metrics Strategy

### Primary Viral Recovery Metrics

**1. Viral Genome Completeness** (Most Important)
```python
# Key metrics per assembly:
- complete_genomes_count = checkv_quality == "Complete"
- high_quality_count = checkv_quality == "High-quality"
- medium_quality_count = checkv_quality == "Medium-quality"
- completeness_scores = mean(completeness_percentage)
```

**2. Viral Sequence Recovery**
```python
- total_viral_length = sum(viral_contig_lengths)
- viral_contig_count = count(viral_contigs)
- viral_n50 = calculate_n50(viral_contigs_only)  # Not total assembly N50
- large_viral_contigs = count(viral_contigs > 10kb)
- very_large_viral_contigs = count(viral_contigs > 50kb)
```

**3. Viral Diversity & Quality**
```python
- unique_viral_families = count(distinct_taxonomic_families)
- proviral_detection = count(proviruses_found)
- contamination_rate = mean(host_contamination_percentage)
- viral_density = total_viral_length / total_assembly_length
```

### Statistical Comparison Framework

**Comparison Structure:**
```python
# Compare k-mer vs random (5 baselines)
kmer_metrics = extract_metrics("kmer_meta_assembly")
random_metrics = [extract_metrics(f"random_{seed}_meta_assembly")
                  for seed in [42,43,44,45,46]]

# Statistical tests:
- wilcoxon_test(kmer_metrics.complete_genomes, random_metrics.complete_genomes)
- effect_size = (kmer_mean - random_mean) / pooled_std
- percentile_rank = kmer_score vs random_distribution
```

**Key Research Questions:**
1. **"Does k-mer clustering recover more complete viral genomes?"**
2. **"Does k-mer clustering increase viral sequence length recovered?"**
3. **"Does k-mer clustering improve viral diversity capture?"**
4. **"Does k-mer clustering reduce viral genome fragmentation?"**

## Implementation Plan

### Step 1: CheckV Execution
```bash
# Run CheckV on all 8 final assemblies
mkdir -p checkv_results/

for assembly in results/assemblies/final_assemblies/*.fasta; do
    assembly_name=$(basename $assembly .fasta)
    echo "Running CheckV on $assembly_name..."

    checkv end_to_end $assembly checkv_results/$assembly_name/ \
        --threads 8 \
        --restart
done
```

### Step 2: Viral Analysis Script
**Create: `scripts/analysis/assess_viral_recovery.py`**

```python
#!/usr/bin/env python3
"""
Compare viral recovery across 8 final assemblies using CheckV results.

Input: CheckV results directories for each assembly
Output:
- viral_comparison_report.txt  # Executive summary
- viral_metrics.csv           # Raw data
- viral_plots.png            # Visualizations
"""

def analyze_viral_recovery(assemblies_dir, checkv_results_dir):
    """Main analysis function"""

def parse_checkv_results(checkv_dir):
    """Extract metrics from CheckV quality_summary.tsv"""

def compare_kmer_vs_random(kmer_metrics, random_metrics_list):
    """Statistical comparison with effect sizes"""

def generate_viral_plots(metrics_df):
    """Create visualization comparing viral recovery"""
```

### Step 3: Combined Analysis
**Create: `scripts/analysis/generate_final_recommendation.py`**

```python
# Combine general assembly + viral analysis
python scripts/analysis/generate_final_recommendation.py \
    --assembly-analysis results/final_analysis/ \
    --viral-analysis results/viral_analysis/ \
    --output final_recommendation.txt
```

## Expected Output Reports

### Viral Recovery Report Example
```
VIRAL GENOME RECOVERY COMPARISON
================================

K-mer Clustering vs Random Grouping:
• Complete genomes: 45 vs 32 ± 6 (p=0.02, +41% improvement)
• High-quality genomes: 89 vs 67 ± 12 (p=0.03, +33% improvement)
• Total viral sequence: 2.4 Mb vs 1.8 ± 0.3 Mb (p=0.01, +33% longer)
• Viral N50: 15.2 kb vs 11.7 ± 2.1 kb (p=0.04, +30% improvement)
• Large viral contigs (>10kb): 23 vs 16 ± 4 (p=0.05, +44% more)
• Viral families detected: 45 vs 38 ± 3 (p=0.03, +18% more diversity)

Individual vs Global Comparison:
• Complete genomes: Individual: 28, Global: 52, K-mer: 45
• Recommendation: K-mer clustering outperforms individual assembly
  but global assembly recovers most complete genomes

RECOMMENDATION: K-mer clustering significantly improves viral genome
recovery compared to random grouping, achieving 85% of global assembly
performance while maintaining computational efficiency.
```

### Key Visualizations

**Planned plots:**
1. **Completeness distribution** - violin plots by method showing completeness scores
2. **Viral genome counts** - bar chart: Complete/High/Medium/Low quality by method
3. **Viral sequence recovery** - total viral length and N50 by method
4. **Viral diversity** - number of taxonomic families recovered
5. **Size distribution** - histogram of viral contig lengths by method

## Implementation Workflow for Tomorrow

**Prerequisites:** Main experiment must complete overnight

**Morning workflow:**
```bash
# 1. Check experiment completion
cd metagrouper_validation/
ls results/assemblies/final_assemblies/  # Should have 8 .fasta files

# 2. Pull latest changes
cd ../
git pull

# 3. Copy CheckV analysis scripts
cp scripts/analysis/assess_viral_recovery.py metagrouper_validation/scripts/

# 4. Run CheckV on all assemblies (2-4 hours)
bash scripts/analysis/run_checkv_all_assemblies.sh

# 5. Analyze viral recovery patterns
python scripts/assess_viral_recovery.py \
    --assemblies-dir results/assemblies/final_assemblies \
    --checkv-results checkv_results/ \
    --output results/viral_analysis

# 6. Generate combined recommendation
python scripts/generate_final_recommendation.py \
    --assembly-analysis results/final_analysis/ \
    --viral-analysis results/viral_analysis/ \
    --output final_recommendation.txt
```

## Decision Framework

**Strong k-mer improvement (>30% better):**
- Scale up k-mer clustering for viral projects
- Worth computational overhead for viral genome recovery

**Marginal k-mer improvement (10-30% better):**
- Cost/benefit analysis needed
- Consider for high-priority viral studies

**No k-mer improvement (<10% difference):**
- Focus optimization efforts elsewhere
- Random grouping is sufficient for current workflows

**Global assembly dominates:**
- Consider computational resources vs viral recovery needs
- K-mer clustering as compromise between individual and global

## Technical Notes

**CheckV Requirements:**
- CheckV database must be installed and accessible
- Sufficient disk space for intermediate files (~10-50GB)
- Allow 2-4 hours for CheckV analysis of 8 assemblies

**Environment:**
- CheckV should run in same environment as other tools
- May need to install CheckV in `coassembly_env`

**Data Management:**
- CheckV produces large intermediate files
- Plan to compress/archive results after analysis
- Keep final summary files for future reference

## Success Metrics

**This analysis is successful if it provides:**
1. ✅ Clear statistical evidence for/against k-mer clustering for viral recovery
2. ✅ Quantified improvement metrics with confidence intervals
3. ✅ Actionable recommendations for future viral assembly projects
4. ✅ Publication-quality viral analysis complementing general assembly results

---

**This document serves as the roadmap for tomorrow's viral analysis implementation.**