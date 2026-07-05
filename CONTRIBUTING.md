# Contributing to ALEX/JARVIS

Thank you for your interest in contributing to ALEX/JARVIS! This document provides guidelines and instructions for contributing.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contribution Workflow](#contribution-workflow)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)

## Code of Conduct

Be respectful, inclusive, and professional in all interactions.

## Getting Started

### Prerequisites
- Python 3.9+
- Git
- Docker (optional)

### Development Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/jarvis_organized.git
cd jarvis_organized
```

2. **Create virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
pip install -e .  # Install in editable mode
```

4. **Run tests**
```bash
cd jarvis
pytest tests/ -v
```

## Contribution Workflow

### 1. Create a Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Changes
- Write code following our standards
- Add tests for new functionality
- Update documentation

### 3. Test Your Changes
```bash
# Run tests
pytest tests/ -v --cov

# Run linting
ruff check jarvis/
black jarvis/
mypy jarvis/
```

### 4. Commit Changes
```bash
git add .
git commit -m "feat: add new feature"
```

**Commit message format:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `test:` Tests
- `refactor:` Code refactoring
- `style:` Formatting
- `chore:` Maintenance

### 5. Push and Create PR
```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Coding Standards

### Python Style
- Follow PEP 8
- Use Black for formatting
- Use type hints
- Maximum line length: 100 characters

### Example
```python
from typing import List, Optional

def process_data(items: List[str], limit: Optional[int] = None) -> List[str]:
    \"\"\"
    Process data items.
    
    Args:
        items: List of items to process
        limit: Optional limit on results
        
    Returns:
        Processed items
    \"\"\"
    processed = [item.strip().lower() for item in items]
    return processed[:limit] if limit else processed
```

### Code Organization
- Keep functions small and focused
- Use descriptive variable names
- Add docstrings to all public functions/classes
- Handle errors appropriately

## Testing

### Writing Tests
```python
import pytest

def test_function_name():
    \"\"\"Test description.\"\"\"
    # Arrange
    input_data = "test"
    
    # Act
    result = function_under_test(input_data)
    
    # Assert
    assert result == expected_output
```

### Test Coverage
- Aim for >80% coverage
- Test edge cases
- Test error conditions

### Running Tests
```bash
# All tests
pytest tests/

# Specific file
pytest tests/unit/test_personality_engine.py

# With coverage
pytest tests/ --cov=. --cov-report=html
```

## Documentation

### Docstrings
Use Google-style docstrings:

```python
def example_function(param1: str, param2: int) -> bool:
    \"\"\"
    Short description.
    
    Longer description if needed.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param2 is negative
    \"\"\"
    pass
```

### Documentation Files
- Update README.md for user-facing changes
- Update relevant docs/ files
- Add examples for new features

## Project Structure

```
jarvis_organized/
├── astra/                  # Main application
│   ├── core/              # Core functionality
│   ├── modules/           # Feature modules
│   ├── api_server/        # REST API
│   ├── utils/             # Utilities
│   └── tests/             # Tests
├── docs/                  # Documentation
├── examples/              # Usage examples
└── .github/               # CI/CD workflows
```

## Need Help?

- Check existing issues
- Read the documentation
- Ask in discussions

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md
- Release notes
- Project documentation

Thank you for contributing! 🚀
