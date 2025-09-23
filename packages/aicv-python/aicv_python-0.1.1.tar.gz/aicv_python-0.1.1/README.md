# AiCV Python SDK

[![PyPI version](https://badge.fury.io/py/aicv-python.svg)](https://badge.fury.io/py/aicv-python)
[![Python Support](https://img.shields.io/pypi/pyversions/aicv-python.svg)](https://pypi.org/project/aicv-python/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A comprehensive AI-powered CV analysis and generation toolkit for Python developers.

## Features

- 🤖 **AI-Powered Analysis**: Analyze CVs with advanced AI algorithms
- ✍️ **Content Generation**: Generate CV sections with AI assistance
- 🎯 **Optimization**: Optimize CVs for ATS compatibility and impact
- 🔧 **Easy Integration**: Simple Python SDK with comprehensive documentation
- 🚀 **High Performance**: Built with modern Python async/await support
- 📊 **Rich Analytics**: Detailed insights and recommendations

## Installation

```bash
pip install aicv-python
```

## Quick Start

### Basic Usage

```python
from aicv import AiCVClient

# Initialize the client
client = AiCVClient(api_key="your-api-key")

# Analyze a CV
result = client.analyze_cv("""
John Doe
Software Engineer
5 years of experience in Python development
...
""")

print(result)
```

### Advanced Usage

```python
from aicv import AiCVClient

# Initialize with custom settings
client = AiCVClient(
    api_key="your-api-key",
    base_url="https://api.aicv.chat",
    timeout=60.0
)

# Generate a CV section
section = client.generate_cv_section(
    section_type="summary",
    context="Senior Python Developer with 5 years experience",
    requirements="Focus on AI/ML expertise"
)

# Optimize a CV
optimized = client.optimize_cv(
    cv_text="Your CV content here...",
    target_job="Senior Python Developer at Tech Company"
)
```

### Context Manager Usage

```python
from aicv import AiCVClient

with AiCVClient(api_key="your-api-key") as client:
    result = client.analyze_cv("Your CV content...")
    print(result)
```

## API Reference

### AiCVClient

The main client class for interacting with the AiCV API.

#### Constructor

```python
AiCVClient(
    api_key: str,
    base_url: str = "https://api.aicv.chat",
    timeout: float = 30.0,
    **kwargs
)
```

**Parameters:**
- `api_key` (str): Your AiCV API key
- `base_url` (str): Base URL for the API (default: https://api.aicv.chat)
- `timeout` (float): Request timeout in seconds (default: 30.0)
- `**kwargs`: Additional arguments passed to httpx.Client

#### Methods

##### analyze_cv(cv_text: str, analysis_type: str = "comprehensive")

Analyze a CV and provide insights.

**Parameters:**
- `cv_text` (str): The CV text to analyze
- `analysis_type` (str): Type of analysis ('comprehensive', 'skills', 'experience')

**Returns:** Analysis results as dictionary

##### generate_cv_section(section_type: str, context: str, requirements: str = None)

Generate a specific CV section.

**Parameters:**
- `section_type` (str): Type of section ('summary', 'experience', 'skills', 'education')
- `context` (str): Context information for generation
- `requirements` (str, optional): Specific requirements for the section

**Returns:** Generated content as dictionary

##### optimize_cv(cv_text: str, target_job: str = None)

Optimize a CV for better ATS compatibility and impact.

**Parameters:**
- `cv_text` (str): The CV text to optimize
- `target_job` (str, optional): Target job description for optimization

**Returns:** Optimization suggestions as dictionary

##### get_account_info()

Get account information and usage statistics.

**Returns:** Account information as dictionary

##### health_check()

Check API health status.

**Returns:** Health status as dictionary

## Command Line Interface

The SDK also provides a command-line interface:

```bash
# Analyze a CV
aicv analyze --api-key YOUR_KEY --cv-text "Your CV content..."

# Generate content
aicv generate --api-key YOUR_KEY --section-type summary --context "Senior Developer"

# Optimize a CV
aicv optimize --api-key YOUR_KEY --cv-text "Your CV content..." --target-job "Job description"

# Check account info
aicv account --api-key YOUR_KEY

# Health check
aicv health --api-key YOUR_KEY
```

## Error Handling

The SDK provides comprehensive error handling:

```python
from aicv import AiCVClient, AuthenticationError, APIError, ValidationError

try:
    client = AiCVClient(api_key="your-api-key")
    result = client.analyze_cv("CV content...")
except AuthenticationError:
    print("Invalid API key")
except APIError as e:
    print(f"API error: {e}")
except ValidationError as e:
    print(f"Validation error: {e}")
```

## Examples

### Complete CV Analysis Workflow

```python
from aicv import AiCVClient

def analyze_and_optimize_cv(cv_text, target_job=None):
    """Complete workflow for CV analysis and optimization."""
    
    with AiCVClient(api_key="your-api-key") as client:
        # Step 1: Analyze the CV
        analysis = client.analyze_cv(cv_text, analysis_type="comprehensive")
        print("Analysis Results:", analysis)
        
        # Step 2: Optimize if target job is provided
        if target_job:
            optimization = client.optimize_cv(cv_text, target_job)
            print("Optimization Suggestions:", optimization)
        
        # Step 3: Generate improved sections if needed
        if analysis.get('needs_improvement'):
            improved_summary = client.generate_cv_section(
                section_type="summary",
                context=cv_text,
                requirements="Professional and impactful"
            )
            print("Improved Summary:", improved_summary)
        
        return analysis

# Usage
result = analyze_and_optimize_cv(
    cv_text="Your CV content...",
    target_job="Senior Python Developer at AI Company"
)
```

### Batch Processing

```python
from aicv import AiCVClient

def batch_analyze_cvs(cv_list, api_key):
    """Analyze multiple CVs in batch."""
    
    results = []
    with AiCVClient(api_key=api_key) as client:
        for i, cv_text in enumerate(cv_list):
            try:
                result = client.analyze_cv(cv_text)
                results.append({
                    'index': i,
                    'status': 'success',
                    'result': result
                })
            except Exception as e:
                results.append({
                    'index': i,
                    'status': 'error',
                    'error': str(e)
                })
    
    return results

# Usage
cv_list = ["CV 1 content...", "CV 2 content...", "CV 3 content..."]
results = batch_analyze_cvs(cv_list, "your-api-key")
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/AIGility-Cloud-Innovation/aicv-python.git
cd aicv-python

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=aicv --cov-report=html

# Run specific test
pytest tests/test_client.py -v
```

### Code Quality

```bash
# Format code
black aicv/ tests/

# Sort imports
isort aicv/ tests/

# Lint code
flake8 aicv/ tests/

# Type checking
mypy aicv/
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📧 Email: contact@aigility.cn
- 📖 Documentation: [https://aicv-python.readthedocs.io](https://aicv-python.readthedocs.io)
- 🐛 Issues: [GitHub Issues](https://github.com/AIGility-Cloud-Innovation/aicv-python/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/AIGility-Cloud-Innovation/aicv-python/discussions)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes and version history.

---

Made with ❤️ by [AIGility Cloud Innovation](https://aigility.cn)
