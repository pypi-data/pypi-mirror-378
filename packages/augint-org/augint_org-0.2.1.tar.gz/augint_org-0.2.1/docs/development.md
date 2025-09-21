# Development Guide

This guide covers setting up your development environment, coding standards, and best practices for contributing to aillc-org.

## Development Environment Setup

### Prerequisites

- Python 3.9 or higher
- Docker (for containerized development)
- AWS CLI configured with appropriate credentials
- Git

### Using uv (Recommended)

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/svange/aillc-org.git
cd aillc-org

# Install dependencies
uv sync

# Install pre-commit hooks
uv run pre-commit install
```

### Using Docker

```bash
# Build and launch development environment
make claude

# Or with specific flags
make claude-x  # Skip permission checks

# Join existing container
make join-claude
```

### Traditional Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install package in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## Project Structure

```
aillc-org/
├── src/
│   └── ai_org/
│       ├── __init__.py
│       ├── cli.py              # CLI entry point
│       ├── commands/           # CLI commands
│       │   ├── account.py
│       │   ├── sso.py
│       │   └── stackset.py
│       ├── core/              # Core business logic
│       │   ├── account_manager.py
│       │   ├── aws_client.py
│       │   ├── config_manager.py
│       │   ├── org_manager.py
│       │   └── sso_manager.py
│       └── utils/             # Utility functions
│           ├── cache.py
│           ├── config_loader.py
│           └── output.py
├── tests/
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   └── fixtures/              # Test fixtures
├── stacksets/                 # CloudFormation templates
├── scripts/                   # Deployment scripts
├── docs/                      # Documentation
├── planning/                  # Planning documents
└── pdoc/                      # Auto-generated API docs
```

## Development Workflow

### 1. Create a Feature Branch

```bash
# Create branch following naming convention
git checkout -b feat/issue-123-new-feature

# For bug fixes
git checkout -b fix/issue-124-bug-description

# For documentation
git checkout -b docs/issue-125-update-readme
```

### 2. Make Changes

Follow the coding standards and ensure:
- Code is properly formatted
- Tests are written/updated
- Documentation is updated

### 3. Run Quality Checks

```bash
# Run all pre-commit checks
make pre-commit

# Or individually:
make lint      # Run ruff linter
make format    # Format code with ruff
make typecheck # Run mypy type checking
make test      # Run tests
```

### 4. Test Your Changes

```bash
# Run all tests
make test

# Run specific test file
uv run pytest tests/unit/test_account_manager.py

# Run with coverage
make test-coverage

# Run only unit tests
uv run pytest tests/unit/

# Run only integration tests
uv run pytest tests/integration/
```

### 5. Commit and Push

```bash
# Stage changes
git add .

# Commit with conventional commit message
git commit -m "feat: add account tagging support

- Add tag parameter to account creation
- Update CloudFormation templates
- Add tests for tagging functionality

Closes #123"

# Push to GitHub
git push origin feat/issue-123-new-feature
```

### 6. Create Pull Request

```bash
# Using GitHub CLI
gh pr create --title "feat: add account tagging support" \
  --body "Description of changes"

# Or create via GitHub web interface
```

## Coding Standards

### Python Style Guide

We use Ruff for linting and formatting:

```python
# Good: Clear, type-annotated function
def create_account(
    name: str,
    email: str,
    ou_id: Optional[str] = None,
) -> dict[str, Any]:
    """Create a new AWS account.

    Args:
        name: Account name
        email: Root email address
        ou_id: Organizational Unit ID

    Returns:
        Account creation response
    """
    # Implementation
```

### Type Hints

Always use type hints:

```python
from typing import Any, Optional, list, dict

def process_accounts(
    accounts: list[dict[str, Any]],
    filter_ou: Optional[str] = None,
) -> list[str]:
    """Process account list."""
    return [acc["Id"] for acc in accounts if _matches_ou(acc, filter_ou)]
```

### Error Handling

Use specific exceptions with context:

```python
try:
    response = client.create_account(Name=name, Email=email)
except ClientError as e:
    error_code = e.response.get("Error", {}).get("Code")
    if error_code == "DuplicateAccount":
        raise ValueError(f"Account with email {email} already exists") from e
    raise Exception(f"Failed to create account: {str(e)}") from e
```

### Logging

Use structured logging:

```python
import logging

logger = logging.getLogger(__name__)

def deploy_stackset(name: str) -> None:
    logger.info("Deploying StackSet", extra={"stackset": name})
    try:
        # Deployment logic
        logger.info("StackSet deployed successfully", extra={
            "stackset": name,
            "status": "SUCCESS"
        })
    except Exception as e:
        logger.error("StackSet deployment failed", extra={
            "stackset": name,
            "error": str(e)
        }, exc_info=True)
        raise
```

## Testing

### Writing Tests

#### Unit Tests

```python
# tests/unit/test_account_manager.py
from unittest.mock import Mock, patch
import pytest
from ai_org.core.account_manager import AccountManager

@pytest.fixture
def mock_aws_client():
    """Create mock AWS client."""
    client = Mock()
    client.client.return_value = Mock()
    return client

def test_create_account_success(mock_aws_client):
    """Test successful account creation."""
    # Arrange
    manager = AccountManager()
    manager.aws = mock_aws_client
    mock_aws_client.client().create_account.return_value = {
        "CreateAccountStatus": {"State": "SUCCEEDED", "AccountId": "123456789012"}
    }

    # Act
    result = manager.create_account("Test", "test@example.com")

    # Assert
    assert result["AccountId"] == "123456789012"
    mock_aws_client.client().create_account.assert_called_once()
```

#### Integration Tests

```python
# tests/integration/test_stackset_deployment.py
import pytest
from moto import mock_cloudformation
from ai_org.core.stackset_manager import StackSetManager

@mock_cloudformation
def test_deploy_stackset():
    """Test StackSet deployment with mocked AWS."""
    manager = StackSetManager()

    # Deploy StackSet
    result = manager.deploy(
        name="test-stackset",
        template_path="stacksets/test-template.yaml",
        parameters={"Key": "Value"}
    )

    # Verify deployment
    assert result["Status"] == "SUCCEEDED"
    instances = manager.list_instances("test-stackset")
    assert len(instances) > 0
```

### Running Tests

```bash
# All tests with coverage
make test-coverage

# Specific test markers
uv run pytest -m unit
uv run pytest -m integration
uv run pytest -m "not slow"

# Parallel execution
uv run pytest -n auto

# With specific verbosity
uv run pytest -vv
```

## Debugging

### Local Testing

```python
# Debug CLI commands locally
if __name__ == "__main__":
    import sys
    import os

    # Add src to path for development
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

    from ai_org.cli import cli
    cli()
```

### Using IPython

```bash
# Install IPython
uv pip install ipython

# Start interactive session
uv run ipython

# In IPython
from ai_org.core.account_manager import AccountManager
manager = AccountManager(profile="org")
accounts = manager.list_accounts()
```

### AWS SDK Debugging

```python
import boto3
import logging

# Enable boto3 debug logging
boto3.set_stream_logger('boto3', logging.DEBUG)

# Or for specific service
boto3.set_stream_logger('boto3.resources.cloudformation', logging.DEBUG)
```

## Documentation

### Updating Documentation

1. **User-facing docs**: Edit files in `docs/`
2. **API documentation**: Docstrings are auto-generated
3. **README**: Keep the main README.md concise

### Docstring Format

```python
def complex_function(
    param1: str,
    param2: Optional[int] = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Short description of function.

    Longer description explaining what the function does,
    any important behavior, side effects, etc.

    Args:
        param1: Description of param1
        param2: Optional parameter description
        **kwargs: Additional keyword arguments:
            - key1: Description of key1
            - key2: Description of key2

    Returns:
        Description of return value structure

    Raises:
        ValueError: When param1 is invalid
        ClientError: When AWS API call fails

    Example:
        >>> result = complex_function("test", param2=42)
        >>> print(result["status"])
        'SUCCESS'
    """
```

### Generating API Docs

```bash
# Generate HTML documentation
make docs

# Serve documentation locally
make docs-serve
# Open http://localhost:8080
```

## Common Development Tasks

### Adding a New CLI Command

1. Create command file in `src/ai_org/commands/`
2. Implement command logic
3. Register in `cli.py`
4. Add tests
5. Update documentation

### Adding a New StackSet

1. Create CloudFormation template in `stacksets/`
2. Add deployment configuration
3. Update deployment script
4. Document the StackSet purpose
5. Test deployment

### Updating Dependencies

```bash
# Add a new dependency
uv add package-name

# Add development dependency
uv add --dev package-name

# Update all dependencies
uv sync --upgrade

# Update specific package
uv add package-name@latest
```

## Performance Optimization

### Profiling

```python
import cProfile
import pstats

def profile_function():
    profiler = cProfile.Profile()
    profiler.enable()

    # Code to profile
    result = expensive_operation()

    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)

    return result
```

### Caching

```python
from functools import lru_cache
from ai_org.utils.cache import CacheManager

# Function-level caching
@lru_cache(maxsize=128)
def expensive_lookup(account_id: str) -> dict:
    return fetch_account_details(account_id)

# Persistent caching
cache = CacheManager(ttl=3600)
result = cache.get_or_compute(
    namespace="accounts",
    key=account_id,
    compute_fn=lambda: fetch_account_details(account_id)
)
```

## Troubleshooting Development Issues

### Common Issues

#### Import Errors

```bash
# Ensure package is installed in development mode
uv pip install -e .

# Or reinstall
uv sync --force-reinstall
```

#### Type Checking Errors

```bash
# Install type stubs
uv add --dev types-requests types-pyyaml boto3-stubs

# Ignore specific errors
# mypy: ignore-errors
```

#### Test Failures

```bash
# Run failed test with more detail
uv run pytest tests/unit/test_file.py::test_name -vv

# Debug with pdb
uv run pytest tests/unit/test_file.py --pdb
```

## Release Process

1. Ensure all tests pass
2. Update CHANGELOG.md
3. Create pull request to main
4. After merge, semantic-release handles:
   - Version bumping
   - Tag creation
   - PyPI publishing
   - GitHub release

## Getting Help

- 📚 [API Documentation](../pdoc/index.html)
- 💬 [GitHub Discussions](https://github.com/svange/aillc-org/discussions)
- 🐛 [Issue Tracker](https://github.com/svange/aillc-org/issues)
- 📧 Email: sam@augmentingintegrations.com

## Contributing

See [Contributing Guide](contributing.md) for:
- Code of conduct
- Pull request process
- Issue reporting guidelines
- Community guidelines
