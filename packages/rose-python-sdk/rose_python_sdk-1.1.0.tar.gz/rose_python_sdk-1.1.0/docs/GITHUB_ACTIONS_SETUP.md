# GitHub Actions Setup Guide

This guide explains how to set up GitHub Actions for automated testing and PyPI publishing for the Rose Python SDK.

## Overview

The project includes three GitHub Actions workflows:

1. **Test Workflow** (`test.yml`) - Runs tests on every push and pull request
2. **Publish Workflow** (`publish.yml`) - Publishes to PyPI when a version tag is pushed
3. **Release Workflow** (`release.yml`) - Creates GitHub releases when a version tag is pushed

## Setup Instructions

### 1. Enable GitHub Actions

GitHub Actions are automatically enabled when you push the workflow files to your repository. No additional setup is required.

### 2. Set up PyPI Publishing

To enable automatic PyPI publishing, you need to set up a PyPI API token:

#### Option A: Using PyPI API Token (Recommended)

1. **Create a PyPI Account** (if you don't have one):
   - Go to [PyPI](https://pypi.org) and create an account
   - Verify your email address

2. **Create an API Token**:
   - Log in to PyPI
   - Go to Account Settings → API tokens
   - Click "Add API token"
   - Give it a name (e.g., "GitHub Actions")
   - Set scope to "Entire account" or "Specific projects"
   - Copy the token (it starts with `pypi-`)

3. **Add Token to GitHub Secrets**:
   - Go to your GitHub repository
   - Click Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `PYPI_API_TOKEN`
   - Value: Your PyPI API token
   - Click "Add secret"

#### Option B: Using Trusted Publishing (Advanced)

If you want to use trusted publishing (no API token needed):

1. **Set up Trusted Publishing on PyPI**:
   - Go to your PyPI project settings
   - Add GitHub as a trusted publisher
   - Configure the repository and workflow

2. **Update the publish workflow**:
   - Remove the `password` line from the publish step
   - The workflow will use trusted publishing automatically

### 3. Configure Code Coverage (Optional)

To enable code coverage reporting:

1. **Sign up for Codecov**:
   - Go to [Codecov](https://codecov.io)
   - Sign in with GitHub
   - Add your repository

2. **The workflow is already configured** to upload coverage reports automatically.

## Workflow Details

### Test Workflow (`test.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

**What it does:**
- Tests on Python 3.11 and 3.12
- Runs linting with flake8
- Runs type checking with mypy
- Runs format checking with black
- Runs tests with pytest
- Uploads coverage to Codecov

### Publish Workflow (`publish.yml`)

**Triggers:**
- Push of version tags (e.g., `v1.0.0`, `v1.1.0`)

**What it does:**
- Builds the package using `python -m build`
- Checks the package with `twine check`
- Publishes to PyPI using the API token

### Release Workflow (`release.yml`)

**Triggers:**
- Push of version tags (e.g., `v1.0.0`, `v1.1.0`)

**What it does:**
- Extracts version from the tag
- Generates release notes from CHANGELOG.md
- Creates a GitHub release

## Publishing a New Version

### 1. Update Version

Update the version in `setup.py`:

```python
version="1.1.0",  # Update this
```

### 2. Update Changelog

Add your changes to `CHANGELOG.md`:

```markdown
## [1.1.0] - 2024-01-20

### Added
- New feature description
- Another feature

### Changed
- Updated feature description

### Fixed
- Bug fix description
```

### 3. Commit and Push

```bash
git add .
git commit -m "Bump version to 1.1.0"
git push origin main
```

### 4. Create and Push Tag

```bash
# Create a version tag
git tag v1.1.0

# Push the tag
git push origin v1.1.0
```

### 5. Monitor the Workflows

1. Go to your GitHub repository
2. Click on the "Actions" tab
3. Watch the workflows run:
   - The publish workflow will build and publish to PyPI
   - The release workflow will create a GitHub release

## Workflow Status Badges

Add these badges to your README.md to show workflow status:

```markdown
![Tests](https://github.com/your-username/rose-python-sdk/workflows/Test/badge.svg)
![PyPI](https://img.shields.io/pypi/v/rose-python-sdk)
![Python](https://img.shields.io/pypi/pyversions/rose-python-sdk)
![License](https://img.shields.io/pypi/l/rose-python-sdk)
```

## Troubleshooting

### Common Issues

#### 1. PyPI Publishing Fails

**Error:** `403 Client Error: Invalid or non-existent authentication information`

**Solution:** Check that your `PYPI_API_TOKEN` secret is correctly set in GitHub.

#### 2. Tests Fail

**Error:** Tests are failing in CI but pass locally

**Solution:** 
- Check that all dependencies are in `requirements.txt`
- Ensure test environment matches local environment
- Check for any environment-specific code

#### 3. Version Already Exists

**Error:** `409 Client Error: File already exists`

**Solution:** 
- Update the version number in `setup.py`
- Create a new tag with the updated version

#### 4. Coverage Upload Fails

**Error:** Codecov upload fails

**Solution:** 
- This is usually not critical for the build
- Check that the repository is added to Codecov
- The workflow is configured to not fail on coverage upload errors

### Debugging Workflows

1. **Check Workflow Logs**:
   - Go to Actions tab in GitHub
   - Click on the failed workflow
   - Click on the failed job
   - Review the logs

2. **Test Locally**:
   - Run the same commands locally that the workflow runs
   - Install dependencies: `pip install -r requirements.txt && pip install -e .[dev]`
   - Run tests: `pytest tests/`
   - Run linting: `flake8 rose_sdk/`
   - Run type checking: `mypy rose_sdk/`

3. **Check Secrets**:
   - Go to Settings → Secrets and variables → Actions
   - Verify that `PYPI_API_TOKEN` is set correctly

## Security Considerations

### API Token Security

- **Never commit API tokens** to the repository
- **Use GitHub Secrets** for sensitive information
- **Rotate tokens regularly**
- **Use least privilege** - only give the token the permissions it needs

### Workflow Permissions

The workflows are configured with minimal required permissions:
- `contents: read` - To checkout the code
- `id-token: write` - For trusted publishing (if used)
- `contents: write` - For creating releases

## Advanced Configuration

### Custom Test Matrix

To test on additional Python versions or operating systems:

```yaml
strategy:
  matrix:
    python-version: [3.8, 3.9, 3.10, 3.11, 3.12]
    os: [ubuntu-latest, windows-latest, macos-latest]
```

### Custom PyPI Index

To publish to a custom PyPI index:

```yaml
- name: Publish to PyPI
  uses: pypa/gh-action-pypi-publish@release/v1
  with:
    repository-url: https://your-custom-index.com/simple/
    user: __token__
    password: ${{ secrets.CUSTOM_PYPI_TOKEN }}
```

### Conditional Publishing

To only publish on certain conditions:

```yaml
- name: Publish to PyPI
  if: github.ref == 'refs/heads/main' && github.event_name == 'push'
  uses: pypa/gh-action-pypi-publish@release/v1
  # ... rest of configuration
```

## Support

If you encounter issues with the GitHub Actions setup:

1. Check the [GitHub Actions documentation](https://docs.github.com/en/actions)
2. Review the workflow logs for specific error messages
3. Create an issue in the repository with details about the problem
4. Contact support at luli245683@gmail.com

---

This setup provides a robust CI/CD pipeline for your Python package, ensuring code quality and automated publishing.
