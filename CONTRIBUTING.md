# Contributing to Assembly Clustering Validation

We welcome contributions to improve this experimental framework! This project aims to provide robust, reproducible methods for validating assembly clustering approaches.

## 🎯 Project Goals

- **Scientific rigor**: Maintain high standards for experimental design
- **Reproducibility**: Ensure all experiments can be replicated
- **Tool-agnostic**: Support multiple clustering methods and assemblers
- **Publication-ready**: Generate publication-quality analyses

## 🤝 How to Contribute

### Reporting Issues

1. Check [existing issues](https://github.com/yourusername/assembly-clustering-validation/issues) first
2. Use the issue templates when available
3. Include:
   - System information (OS, cluster scheduler, etc.)
   - Configuration file (remove sensitive information)
   - Error messages and logs
   - Steps to reproduce

### Contributing Code

1. **Fork** the repository
2. **Create a branch** for your feature: `git checkout -b feature/new-clustering-method`
3. **Make changes** following our coding standards
4. **Add tests** for new functionality
5. **Update documentation** as needed
6. **Submit a pull request**

### Adding New Clustering Methods

To add support for a new clustering method:

1. Create a new module in `scripts/utils/` (e.g., `mmseqs2_clustering.py`)
2. Implement the standard clustering interface:
   ```python
   def cluster_samples(sample_list, config):
       # Your clustering logic
       return groups_dict
   ```
3. Add configuration options to `configs/default_config.yaml`
4. Add tests in `tests/`
5. Update documentation

### Adding New Assembly Tools

To add support for a new assembler:

1. Create assembler module in `scripts/assembly/`
2. Implement the standard assembler interface
3. Add SLURM job templates
4. Update configuration schema
5. Add tests

## 📝 Coding Standards

### Python Style
- Follow [PEP 8](https://pep8.org/)
- Use [Black](https://black.readthedocs.io/) for formatting: `black .`
- Use meaningful variable names
- Add docstrings to all functions

### Documentation
- Update README.md for new features
- Add inline comments for complex logic
- Update configuration documentation
- Include examples in docstrings

### Testing
- Write unit tests for new functions
- Include integration tests for new clustering methods
- Test with small datasets in CI
- Validate output formats

## 🔬 Scientific Standards

### Experimental Design
- All changes to experimental logic require peer review
- Statistical methods should be well-established
- New metrics should be validated against known benchmarks
- Maintain compatibility with existing experiments

### Data Handling
- Never commit large data files
- Use reproducible random seeds
- Document all data processing steps
- Ensure privacy compliance for real datasets

## 🚀 Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/assembly-clustering-validation.git
cd assembly-clustering-validation

# Create development environment
conda create -n acv-dev python=3.9
conda activate acv-dev
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
pytest tests/
```

## 📋 Pull Request Checklist

- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Tests added for new functionality
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] Configuration examples updated
- [ ] No large files committed
- [ ] Sensitive information removed

## 🏆 Recognition

Contributors will be acknowledged in:
- README.md contributors section
- Any publications using this framework
- Release notes for their contributions

## 📧 Questions?

- **General questions**: [GitHub Discussions](https://github.com/yourusername/assembly-clustering-validation/discussions)
- **Bug reports**: [GitHub Issues](https://github.com/yourusername/assembly-clustering-validation/issues)
- **Security concerns**: Email maintainer directly

Thank you for contributing to reproducible computational biology! 🧬