# Quick Start: GitHub Actions Setup

Quick reference for setting up GitHub Actions for the Rose Python SDK.

## 🚀 Quick Setup (5 minutes)

### 1. Set up PyPI API Token
```bash
# 1. Go to https://pypi.org and create account
# 2. Create API token in Account Settings → API tokens
# 3. Copy the token (starts with pypi-)
```

### 2. Add Token to GitHub
```bash
# 1. Go to your GitHub repository
# 2. Settings → Secrets and variables → Actions
# 3. New repository secret: PYPI_API_TOKEN
# 4. Paste your PyPI token
```

### 3. Update Repository URLs
Replace `your-username` and `your-org` in these files:
- `README.md` (badge URLs)
- `setup.py` (project_urls)
- `docs/GITHUB_ACTIONS_SETUP.md` (example URLs)

### 4. Test the Setup
```bash
# Run the setup script
./scripts/setup_github_actions.sh

# Push to trigger tests
git add .
git commit -m "Add GitHub Actions workflows"
git push origin main
```

## 📦 Publishing a New Version

### 1. Update Version
```bash
# Edit setup.py
version="1.1.0"  # Update this

# Update CHANGELOG.md
# Add your changes under [1.1.0] section
```

### 2. Create and Push Tag
```bash
git add .
git commit -m "Bump version to 1.1.0"
git tag v1.1.0
git push origin main
git push origin v1.1.0
```

### 3. Monitor Workflows
- Go to GitHub repository → Actions tab
- Watch the workflows run
- Check PyPI for your published package

## 🔧 Workflow Files

| File | Purpose | Triggers |
|------|---------|----------|
| `test.yml` | Run tests, linting, type checking | Push, PR to main/develop |
| `publish.yml` | Publish to PyPI | Version tags (v*) |
| `release.yml` | Create GitHub release | Version tags (v*) |

## 🐛 Troubleshooting

### Common Issues

**PyPI Publishing Fails:**
- Check `PYPI_API_TOKEN` secret is set correctly
- Verify token has proper permissions

**Tests Fail:**
- Check dependencies in `requirements.txt`
- Run tests locally: `pytest tests/`

**Version Already Exists:**
- Update version number in `setup.py`
- Create new tag with updated version

### Debug Commands
```bash
# Test locally
pip install -r requirements.txt
pip install -e .[dev]
pytest tests/
flake8 rose_sdk/
mypy rose_sdk/

# Check workflows
git log --oneline
git tag -l
```

## 📊 Status Badges

Add these to your README.md:
```markdown
![Tests](https://github.com/your-username/rose-python-sdk/workflows/Test/badge.svg)
![PyPI](https://img.shields.io/pypi/v/rose-python-sdk)
![Python](https://img.shields.io/pypi/pyversions/rose-python-sdk)
![License](https://img.shields.io/pypi/l/rose-python-sdk)
```

## 📚 Full Documentation

For complete setup instructions, see [GitHub Actions Setup Guide](GITHUB_ACTIONS_SETUP.md).

---

**Need help?** Check the [full setup guide](GITHUB_ACTIONS_SETUP.md) or create an issue on GitHub.
