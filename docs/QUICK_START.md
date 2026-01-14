# MetaGrouper Comprehensive Validation - Quick Start

## The Question
**Does k-mer clustering beat random grouping for metagenomic co-assembly?**

## The Comprehensive Experiment (4 Conditions)
1. **Individual assemblies** - 50 separate assemblies (baseline)
2. **Random groupings** - 5 different random groupings (null hypothesis)
3. **K-mer grouping** - MetaGrouper clustering (test hypothesis)
4. **Global assembly** - All 50 samples together (maximum cooperation)

This gives robust statistical comparison: if k-mer can't beat the **average** of 5 random groupings, the approach is fundamentally flawed.

## Your Setup
- **Samples**: 1150 paired-end samples at `/lts/sahlab/data4/megan/RC2_rrna_removed_reads/`
- **Naming**: `{sample_id}_rrna_removed_R{1,2}.fastq`
- **Cluster**: SLURM with 24 cores/node
- **Environment**: `metagrouper_env` conda environment

## Clone to Cluster & Run

```bash
# 1. Clone repository to your cluster
ssh your-cluster
git clone git@github.com:megjohnson1999/assembly-clustering-validation.git
cd assembly-clustering-validation

# 2. Setup experiment environment
bash scripts/setup/setup_experiment.sh

# 3. Copy your local MetaGrouper code to the cluster
# (since it's not in git yet - you can also push it to a separate repo)
scp -r ../metaGrouper your-cluster:~/assembly-clustering-validation/setup/

# 4. Configure for your experiment
cp configs/metagrouper_example.yaml configs/my_experiment.yaml
# Edit configs/my_experiment.yaml if needed

# 5. Run the comprehensive experiment (50 samples, 4 conditions, ~1-2 weeks)
bash scripts/setup/run_full_robust_experiment.sh

# OR run steps individually:
python scripts/select_samples.py                    # 5 minutes
sbatch scripts/run_metagrouper.sh                   # 2-4 hours
python scripts/create_random_groups.py              # 1 minute (creates 5 groupings)
python scripts/generate_all_assembly_commands.py    # 2 minutes (all conditions)
sbatch scripts/run_individual_assemblies.sh         # 6-12 hours (50 small assemblies)
sbatch scripts/run_kmer_assemblies.sh              # 12-24 hours (~10 group assemblies)
sbatch scripts/run_random_assemblies.sh            # 24-48 hours (~50 group assemblies, 5 seeds)
sbatch scripts/run_global_assemblies.sh            # 24-48 hours (1 large assembly)
python scripts/assess_all_conditions.py            # 10 minutes (comprehensive analysis)
```

## Key Files Created

**During experiment:**
- `samples/subset_50/` - Selected samples (symlinks)
- `results/kmer_groups/assembly_recommendations.json` - MetaGrouper clustering
- `results/random_groups/random_seed_*/assembly_recommendations.json` - 5 random groupings
- `results/assemblies/individual/` - Individual assemblies (50 separate)
- `results/assemblies/kmer/` - K-mer based assemblies (~10 groups)
- `results/assemblies/random/` - Random grouping assemblies (~50 groups, 5 seeds)
- `results/assemblies/global/` - Global assembly (all 50 samples)

**THE CRITICAL RESULT:**
- `results/comprehensive_analysis/comprehensive_analysis_report.txt` - **THE DEFINITIVE ANSWER**

**Supporting data:**
- `results/comprehensive_analysis/detailed_assembly_statistics.csv` - Raw metrics for all conditions

## Expected Outcomes

The comprehensive analysis will classify results into one of four categories:

**🎉 STRONGLY PROMISING**: K-mer beats even the BEST random groupings
- Strong evidence the approach is fundamentally sound
- Scale up to 200+ samples and consider publication

**✅ PROMISING**: K-mer consistently beats average random performance
- Approach shows merit and is worth further development
- Scale up with method refinements

**⚠️ MIXED**: K-mer shows some promise but inconsistent performance
- Test with larger sample size or investigate method parameters
- Consider hybrid approaches

**❌ NOT PROMISING**: K-mer doesn't consistently beat random
- Fundamental issues with approach
- Abandon k-mer clustering and try alternatives

## Resource Requirements

**50 samples (comprehensive experiment):**
- MetaGrouper: 16 cores, 64GB, 2-4 hours
- Individual assemblies: 50 × (8 cores, 32GB, 4-8 hours) = ~300 core-hours
- K-mer assemblies: ~10 × (16 cores, 120GB, 12-24 hours) = ~2000 core-hours
- Random assemblies: ~50 × (16 cores, 120GB, 12-24 hours) = ~10000 core-hours
- Global assembly: 1 × (20 cores, 200GB, 24-48 hours) = ~600 core-hours
- **Total: ~13,000 core-hours over 1-2 weeks**

This is 5x more compute than the simple experiment, but gives definitive statistical evidence instead of a "maybe" answer.

## Troubleshooting

**MetaGrouper fails**: Check logs in `logs/metagrouper_*.err`
**Assembly fails**: Check individual job logs in `logs/assembly_*`
**No results**: Verify file paths and conda environment
**Need help**: Check script comments or contact for assistance

## The Bottom Line

This experiment will definitively answer whether MetaGrouper's core premise is valid. If k-mer clustering can't beat random grouping, the entire 7,000-line codebase is solving the wrong problem.