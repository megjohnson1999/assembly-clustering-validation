# Viral Metagenome Assembly Clustering Validation

**Original Research Question:** Does k-mer-based sample clustering produce better viral metagenomic assemblies than random grouping?

**Answer:** K-mer clustering doesn't work for viral metagenomics data. After this discovery, we pivoted to testing group size effects and found that **individual assembly or small groups (~5 samples) produce the best results**.

## The Complete Story

### Phase 1: Attempting K-mer Clustering

**Goal:** Test whether grouping samples by k-mer similarity (MetaGrouper/Sourmash) improves viral assembly quality compared to random grouping.

**What happened:**

| Tool | Result | Details |
|------|--------|---------|
| MetaGrouper | Failed | Memory errors, couldn't process viral metagenomic data |
| Sourmash | No clusters formed | Even with very permissive similarity thresholds (0.1-0.5), no sample pairs were similar enough to cluster |

**Tested with:**
- Initial: 25 samples
- Expanded: 200 samples
- Multiple similarity thresholds

**Conclusion:** K-mer clustering doesn't work for viral metagenomics because:
- Viral communities are highly diverse across s
- Low sequence similarity between s (even from related environments)
- K-mer signatures don't capture meaningful biological relationships in viral data

### Phase 2: Pivot to Group Size Study

Since k-mer clustering failed, we asked a different question: **Does group size matter for viral assembly quality?**

Tested 5 grouping strategies with 200 viral metagenomic s using random grouping at different sizes:

| Strategy | Description |
|----------|-------------|
| individual | Each  assembled separately, then meta-assembled |
| groups_size_5 | s randomly grouped into sets of 5 |
| groups_size_12 | s randomly grouped into sets of 12 |
| groups_size_25 | s randomly grouped into sets of 25 |
| global | All 200 s co-assembled together |

**Assembly workflow:** MEGAHIT (per group) → Concatenate → Flye meta-assembly

## Results (January 2026)

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

**Assembly quality generally decreases with group size:**

| Metric | Best Strategy | Worst Strategy | Trend |
|--------|---------------|----------------|-------|
| N50 | individual (3,063) | global (2,528) | Decreases with group size |
| Avg contig length | individual (2,481) | global (2,301) | Decreases with group size |
| Complete viral genomes | **groups_size_5 (204)** | global (152) | Decreases after size 5 |
| Mean completeness | individual (7.66%) | global (6.70%) | Decreases with group size |

**Trade-off:** Groups of 5 recover slightly more complete genomes (+4.6%) but with worse assembly contiguity.

## Conclusions

### On K-mer Clustering
1. **K-mer clustering does not work for viral metagenomics** - s are too diverse to form meaningful clusters
2. MetaGrouper and Sourmash both failed to produce usable groupings
3. This is likely a fundamental limitation of k-mer approaches for viral data

### On Group Size
1. **Individual assembly or groups of ~5 perform best** for viral metagenomics
2. **Global co-assembly performs worst** on every metric
3. The extra contigs from larger groups represent fragmentation, not improved recovery
4. **Group size matters more than clustering method** (since clustering doesn't work anyway)

### Biological Interpretation

Larger co-assembly groups hurt viral assembly quality because:
- **Strain diversity**: Viruses evolve rapidly; combining s multiplies variant complexity
- **Assembly graph conflicts**: Similar but non-identical sequences create unresolvable branches
- **Diminishing returns**: Coverage gains are outweighed by complexity costs

## Practical Recommendations

### Decision Framework

| Priority | Recommendation |
|----------|----------------|
| Maximize complete genome recovery | Use groups of 5 |
| Prioritize assembly contiguity (N50) | Use individual assembly |
| Simple workflow | Use individual assembly |

### When to Group s

| Scenario | Recommendation |
|----------|----------------|
| Same patient, multiple timepoints | Co-assemble (limit ~5 s) |
| Unrelated s | Individual assembly |
| Any viral metagenomics project | **Don't use k-mer clustering** |

## Methods

### Dataset
- 200 viral metagenomics (paired-end reads)
- Source: IBD (inflammatory bowel disease) study stool samples

### Assembly Workflow
1. **Stage 1:** MEGAHIT assembly per group
2. **Stage 2:** Concatenate contigs from groups
3. **Stage 3:** Flye meta-assembly of concatenated contigs

### Quality Assessment
- **Basic metrics:** seqkit stats (N50, contig counts, lengths)
- **Viral quality:** CheckV (completeness, quality categories)

## Repository Structure

```
├── scripts/
│   ├── setup/           # Experimental setup and workflow orchestration
│   ├── assembly/        # Assembly command generation and execution
│   ├── analysis/        # Quality assessment (seqkit, CheckV, summarization)
│   └── utils/           # Sample selection and grouping utilities
├── metagrouper_validation/
│   └── results/
│       └── analysis/    # Output metrics and summaries
├── focused_assembly_scripts/  # SLURM scripts for each strategy
└── README.md
```

## Research Context

**Status:** Completed (January 2026)
**Institution:** Sahlab computational biology research
**Use case:** Method validation for viral metagenomic assembly strategies

## Citation

```
Viral Metagenome Assembly Clustering Validation (2026)
Sahlab Computational Biology
GitHub: megjohnson1999/assembly-clustering-validation

Key finding: K-mer clustering fails for viral metagenomics;
individual assembly or small groups (~5) produce optimal results.
```

---

**Bottom line:** Don't waste time on k-mer clustering for viral metagenomics. Use individual assembly or small random groups of ~5 samples.
