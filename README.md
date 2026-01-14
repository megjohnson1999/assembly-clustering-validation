# MetaGrouper Assembly Clustering Validation

**Research Question:** Does k-mer-based sample clustering produce better metagenomic assemblies than random grouping?

## Overview

This repository contains a validation framework for testing whether MetaGrouper's k-mer clustering approach produces superior co-assemblies compared to random sample grouping. The experiment uses a staged assembly workflow (MEGAHIT → concatenate → Flye meta-assembly) to generate comparable final assemblies across different grouping strategies.

## Current Implementation

**What this tool does:**
- ✅ Tests MetaGrouper k-mer clustering against 5 random grouping baselines
- ✅ Implements staged assembly workflow matching hecatomb patterns
- ✅ Runs efficiently on SLURM clusters (2-3 days vs weeks)
- ✅ Generates statistical comparison of assembly quality metrics
- ✅ Provides clear recommendation on clustering effectiveness

**Validation scope:**
- **Sample size**: 50 paired-end metagenomic samples
- **Clustering method**: MetaGrouper k-mer similarity (threshold=0.3)
- **Assembly workflow**: MEGAHIT → concatenation → Flye meta-assembly
- **Comparison**: 8 final meta-assemblies (Individual, Random×5, K-mer, Global)

## Experimental Design

**Four-condition comparison:**
1. **Individual approach**: Each sample assembled separately, then meta-assembled
2. **Random grouping**: 5 different random sample groupings (seeds 42-46)
3. **K-mer clustering**: MetaGrouper similarity-based grouping
4. **Global assembly**: All samples co-assembled together

**Statistical approach:**
- Multiple random baselines ensure robust null hypothesis testing
- Assembly quality metrics: N50, total length, contig counts, completeness
- Statistical significance testing with effect size calculations

## Expected Outcomes

**Definitive answer to:** "Should I use k-mer clustering or is random grouping just as good?"

**Possible results:**
- **Strong evidence**: K-mer clustering significantly outperforms random (p<0.05, large effect size)
- **Marginal evidence**: Small but consistent improvements (cost/benefit decision needed)
- **No evidence**: Random grouping performs equivalently (focus efforts elsewhere)

## Current Limitations

**This is a research validation, not a production tool:**
- ⚠️ **Single clustering method**: Only tests MetaGrouper (not CONCOCT, MaxBin, etc.)
- ⚠️ **Limited scale**: Validated on 50 samples (not 100-1000+ samples)
- ⚠️ **Preliminary results**: Requires peer review and broader validation
- ⚠️ **Specific workflow**: Designed for hecatomb-style staged assembly

## Quick Start

**Prerequisites:**
- SLURM cluster with `metagrouper_env` and `coassembly_env`
- MetaGrouper installed in `setup/metaGrouper/`
- Paired-end metagenomic reads

**Run validation:**
```bash
# Setup experiment workspace
bash scripts/setup/setup_experiment_fixed.sh

# Run complete validation (2-3 days)
cd metagrouper_validation/
bash scripts/setup/run_staged_experiment.sh

# Results in: results/final_analysis/
```

## Repository Structure

```
├── scripts/
│   ├── setup/           # Experimental setup and workflow orchestration
│   ├── assembly/        # Assembly command generation and execution
│   ├── analysis/        # Quality assessment and statistical analysis
│   └── utils/           # Sample selection and grouping utilities
├── configs/             # Experimental parameters (documentation)
├── setup/               # MetaGrouper installation location
└── README.md           # This file
```

## Research Context

**Status**: Active validation study (January 2026)
**Institution**: Sahlab computational biology research
**Use case**: Method validation for viral metagenomic assembly strategies

**This framework provides:**
- Reproducible methodology for testing co-assembly strategies
- Statistical framework for comparing clustering approaches
- Working example that can be extended to other clustering tools
- Foundation for scaling to larger sample sizes

## Future Development

**Planned enhancements:**
- 🔄 Support for multiple clustering methods (CONCOCT, MaxBin2, VAMB)
- 🔄 Scaling validation to 100-1000+ samples
- 🔄 CheckV integration for viral genome recovery analysis
- 🔄 Additional assembly workflows (SPAdes, Unicycler)
- 🔄 Publication and community peer review

**Contributing**: This is currently a single-researcher project. Contact for collaboration opportunities.

## Citation

```
Assembly Clustering Validation Framework (2026)
Sahlab Computational Biology
GitHub: megjohnson1999/assembly-clustering-validation
Status: Research validation - results pending peer review
```

---

**Key insight**: This framework definitively tests whether k-mer clustering solves a real problem in metagenomic assembly, providing evidence-based guidance for method selection.