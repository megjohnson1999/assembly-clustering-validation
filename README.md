# Assembly Clustering Validation

A robust experimental framework for testing whether similarity-based clustering approaches outperform random grouping for metagenomic co-assembly.

## 🧪 The Scientific Question

**Does k-mer similarity clustering produce better co-assemblies than random chance?**

This repository provides a publication-quality experimental design to definitively answer this question for any clustering method.

## 🎯 Experimental Design

### Four-Condition Comparison

1. **Individual Assemblies** (baseline)
   - Each sample assembled separately
   - Establishes minimum cooperation baseline

2. **Random Groupings** (null hypothesis)
   - 5 different random groupings with identical structure to test method
   - Provides statistical distribution for comparison

3. **Similarity Clustering** (test hypothesis)
   - Groups samples by k-mer similarity (or other similarity metric)
   - The method being tested

4. **Global Assembly** (maximum cooperation reference)
   - All samples assembled together
   - Establishes maximum cooperation potential

### Statistical Analysis

The framework determines if similarity clustering significantly outperforms random grouping by comparing:
- Assembly quality metrics (N50, total length, contig count, etc.)
- Performance across multiple assembly quality dimensions
- Statistical significance through comparison with random distribution

## 🔬 Key Features

- **Tool-agnostic**: Can test any clustering method (MetaGrouper, MMseqs2, custom approaches)
- **Statistically robust**: Multiple random replicates instead of single comparisons
- **Comprehensive metrics**: Multiple assembly quality measures
- **Scalable**: Designed for 50-1000+ samples
- **Reproducible**: Complete automation with parameter tracking
- **Publication-ready**: Generates publication-quality analysis reports

## 📁 Repository Structure

```
├── scripts/
│   ├── setup/           # Experimental setup and workflow orchestration
│   ├── assembly/        # Assembly command generation and execution
│   ├── analysis/        # Quality assessment and statistical analysis
│   └── utils/           # Sample selection and grouping utilities
├── configs/             # Experimental parameters and configurations
├── results/             # Experimental outputs (gitignored large files)
├── analysis/            # Post-experiment analysis notebooks
├── docs/                # Detailed documentation
└── tests/               # Unit tests for experimental scripts
```

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/yourusername/assembly-clustering-validation.git
cd assembly-clustering-validation

# Configure for your system
cp configs/default_config.yaml configs/my_experiment.yaml
# Edit configs/my_experiment.yaml with your paths and parameters
```

### 2. Run Complete Experiment

```bash
# Full automated experiment
bash scripts/setup/run_full_experiment.sh configs/my_experiment.yaml

# OR run individual steps:
python scripts/utils/select_samples.py --config configs/my_experiment.yaml
sbatch scripts/assembly/run_clustering_analysis.sh
python scripts/utils/create_random_groups.py --config configs/my_experiment.yaml
python scripts/assembly/generate_all_assembly_commands.py --config configs/my_experiment.yaml
# Submit assembly jobs...
python scripts/analysis/assess_all_conditions.py --config configs/my_experiment.yaml
```

### 3. Analyze Results

```bash
# View the definitive answer
cat results/comprehensive_analysis/comprehensive_analysis_report.txt

# Detailed statistics
open results/comprehensive_analysis/detailed_assembly_statistics.csv
```

## 📊 Expected Outcomes

The analysis classifies results into four categories:

- **🎉 STRONGLY PROMISING**: Clustering beats even best random groupings
- **✅ PROMISING**: Clustering consistently beats average random performance
- **⚠️ MIXED**: Inconsistent performance, needs refinement
- **❌ NOT PROMISING**: Doesn't beat random, fundamental issues

## ⚙️ Configuration

Edit `configs/my_experiment.yaml` to customize:

```yaml
# Sample configuration
samples:
  input_directory: "/path/to/fastq/files"
  file_pattern: "{sample_id}_R{1,2}.fastq.gz"
  subset_size: 50
  random_seed: 42

clustering:
  method: "kmer"  # or "mash", "sourmash", etc.
  similarity_threshold: 0.3
  min_group_size: 2
  max_group_size: 5

assembly:
  assembler: "megahit"  # or "spades", "flye"
  threads: 16
  memory: "120G"

analysis:
  random_seeds: [42, 43, 44, 45, 46]
  metrics: ["n50", "total_length", "n_contigs", "max_contig"]
```

## 🧬 Clustering Methods Supported

- **K-mer clustering** (MetaGrouper, Sourmash)
- **Sequence similarity** (MMseqs2, DIAMOND)
- **Taxonomic clustering** (Kraken2 + grouping)
- **Custom methods** (via plugin interface)

## 📝 Publications & Citations

If you use this framework in your research, please cite:

```bibtex
@software{assembly_clustering_validation,
  title = {Assembly Clustering Validation Framework},
  author = {Your Name},
  year = {2024},
  url = {https://github.com/yourusername/assembly-clustering-validation}
}
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/assembly-clustering-validation/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/assembly-clustering-validation/discussions)
- **Email**: your.email@institution.edu

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 🏃‍♀️ Current Example: MetaGrouper Validation

This repository currently contains a complete validation of MetaGrouper's k-mer clustering approach. See `configs/metagrouper_example.yaml` and `docs/metagrouper_case_study.md` for details.

**Research Question**: Does MetaGrouper's k-mer clustering outperform random grouping for metagenomic co-assembly?

**Status**: Ready to run comprehensive validation on 50-1000 samples.