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

## Results (January 2026)

### Experiment: Effect of Group Size on Assembly Quality

Tested 5 grouping strategies with 200 viral metagenomic samples using a staged assembly workflow (MEGAHIT → Flye meta-assembly):

| Strategy | Description |
|----------|-------------|
| individual | Each sample assembled separately, then meta-assembled |
| groups_size_5 | Samples grouped into sets of 5 |
| groups_size_12 | Samples grouped into sets of 12 |
| groups_size_25 | Samples grouped into sets of 25 |
| global | All samples co-assembled together |

### Basic Assembly Metrics (seqkit stats)

| Strategy | Contigs | Total Length | Avg Length | N50 | Max Contig |
|----------|---------|--------------|------------|-----|------------|
| individual | 47,826 | 118.7 Mb | 2,481 | **3,063** | 183,542 |
| groups_size_5 | 49,473 | 120.8 Mb | 2,441 | 2,956 | 183,620 |
| groups_size_12 | 51,390 | 124.4 Mb | 2,420 | 2,886 | 183,619 |
| groups_size_25 | 55,423 | 128.7 Mb | 2,323 | 2,643 | 183,598 |
| global | 69,608 | 160.2 Mb | 2,301 | 2,528 | 183,498 |

### Viral Genome Quality (CheckV)

| Strategy | Complete | High-quality | Medium-quality | Low-quality | Not-determined | Completeness % |
|----------|----------|--------------|----------------|-------------|----------------|----------------|
| individual | 195 | 325 | 386 | 26,555 | 20,365 | **7.66%** |
| groups_size_5 | **204** | 327 | 368 | 27,288 | 21,286 | 7.54% |
| groups_size_12 | 180 | **336** | 375 | 28,104 | 22,395 | 7.40% |
| groups_size_25 | 187 | 305 | 392 | 29,877 | 24,662 | 7.12% |
| global | 152 | 254 | 413 | 34,814 | 33,975 | 6.70% |

### Key Findings

**Assembly quality generally decreases with group size, but with nuances:**

| Metric | Best Strategy | Worst Strategy | Trend |
|--------|---------------|----------------|-------|
| N50 | individual (3,063) | global (2,528) | ↓ with group size |
| Avg contig length | individual (2,481) | global (2,301) | ↓ with group size |
| Complete viral genomes | **groups_size_5 (204)** | global (152) | ↓ after size 5 |
| Mean completeness | individual (7.66%) | global (6.70%) | ↓ with group size |

**Trade-off:** Groups of 5 recover slightly more complete genomes (+4.6%) but with worse assembly contiguity.

### Conclusions

1. **Individual assembly and groups of ~5 perform best** for viral metagenomics
2. **Global co-assembly performs worst** on every metric
3. The extra contigs from larger groups represent fragmentation, not improved recovery
4. Small groups may recover slightly more complete genomes at the cost of contiguity

### Decision Framework

| Priority | Recommendation |
|----------|----------------|
| Maximize complete genome recovery | Use groups of 5 |
| Prioritize assembly contiguity (N50) | Use individual assembly |
| Simple workflow | Use individual assembly |

### Biological Interpretation

Larger co-assembly groups hurt viral assembly quality because:
- **Strain diversity**: Viruses evolve rapidly; combining samples multiplies variant complexity
- **Assembly graph conflicts**: Similar but non-identical sequences create unresolvable branches
- **Diminishing returns**: Coverage gains are outweighed by complexity costs

### Practical Recommendations

| Scenario | Recommendation |
|----------|----------------|
| Same patient, multiple timepoints | Co-assemble (limit ~5 samples) |
| Known outbreak/transmission | Consider k-mer clustering with small groups |
| Unrelated samples | Individual assembly |

---

## Original Expected Outcomes

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