# Contributing to Chronicle

Thank you for your interest in contributing to Chronicle!

## How to Contribute

### Reporting Issues

- Use GitHub Issues to report bugs or request features
- Include all relevant details (OS, Python version, Chronicle version)
- Include steps to reproduce if reporting a bug

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests to ensure nothing is broken
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to your branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Setup

```bash
# Clone the repository
git clone https://github.com/distortedteen/chronicle.git
cd chronicle

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate  # Windows

# Install dependencies
pip install -e .

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

### Coding Standards

- Follow PEP 8 style guidelines
- Use type hints where possible
- Add docstrings to new functions
- Keep changes focused and minimal

## Contact

For questions or discussions, open an issue on GitHub.