# 🚀 Publishing AtaData CLI to PyPI - Complete Guide

## Overview

This guide will walk you through publishing your AtaData CLI package to PyPI so anyone can install it with `pip install atadata-cli`.

## ✅ Prerequisites Completed

- ✅ Package built successfully
- ✅ Distribution files created (`dist/atadata_cli-1.0.0-py3-none-any.whl` and `atadata_cli-1.0.0.tar.gz`)
- ✅ Package validation passed (`twine check`)

## 📋 Step-by-Step Publishing Process

### Step 1: Create PyPI Account

1. **Go to PyPI**: Visit [https://pypi.org/](https://pypi.org/)
2. **Sign Up**: Click "Register" and create an account
3. **Verify Email**: Check your email and verify your account
4. **Enable 2FA**: For security, enable two-factor authentication

### Step 2: Create API Token (Recommended)

1. **Go to Account Settings**: Click your username → "Account settings"
2. **API Tokens**: Go to "API tokens" section
3. **Create Token**: Click "Add API token"
4. **Scope**: Choose "Entire account" (or create project-specific token)
5. **Copy Token**: Save the token securely (you won't see it again)

### Step 3: Configure Authentication

Create a `.pypirc` file in your home directory:

```bash
# Create the file
touch ~/.pypirc

# Edit with your credentials
cat > ~/.pypirc << EOF
[distutils]
index-servers = pypi

[pypi]
username = __token__
password = pypi-YOUR_API_TOKEN_HERE
EOF
```

**Replace `pypi-YOUR_API_TOKEN_HERE` with your actual API token.**

### Step 4: Upload to PyPI

#### Option A: Upload to Production PyPI (Public)

```bash
cd /Users/robertoscalas/Documents/atadata-cli
source venv/bin/activate

# Upload to PyPI
twine upload dist/*
```

#### Option B: Test on Test PyPI First (Recommended)

```bash
# Upload to Test PyPI first
twine upload --repository testpypi dist/*

# Test installation from Test PyPI
pip install --index-url https://test.pypi.org/simple/ atadata-cli
```

### Step 5: Verify Installation

After uploading, test the installation:

```bash
# Create a new virtual environment to test
python3 -m venv test_env
source test_env/bin/activate

# Install from PyPI
pip install atadata-cli

# Test the CLI
atadata --help
atadata auth status
```

## 🔧 Alternative Upload Methods

### Method 1: Using Username/Password

```bash
twine upload dist/*
# Enter your PyPI username and password when prompted
```

### Method 2: Using Environment Variables

```bash
export TWINE_USERNAME=your_username
export TWINE_PASSWORD=your_password
twine upload dist/*
```

### Method 3: Using Keyring

```bash
# Store credentials in keyring
keyring set https://upload.pypi.org/legacy/ your_username

# Upload
twine upload dist/*
```

## 📝 Package Information

Your package will be available at:
- **PyPI URL**: https://pypi.org/project/atadata-cli/
- **Installation**: `pip install atadata-cli`
- **Command**: `atadata`

## 🎯 Post-Publication Steps

### 1. Update Documentation

Update your README.md to include PyPI installation instructions:

```markdown
## Installation

### From PyPI (Recommended)
```bash
pip install atadata-cli
```

### From Source
```bash
git clone https://github.com/yourusername/atadata-cli.git
cd atadata-cli
pip install -e .
```
```

### 2. Create GitHub Release

1. Go to your GitHub repository
2. Click "Releases" → "Create a new release"
3. Tag version: `v1.0.0`
4. Release title: `AtaData CLI v1.0.0`
5. Description: Include changelog and installation instructions

### 3. Update Package Version

For future updates:

1. **Update version** in `setup.py` and `pyproject.toml`
2. **Build new package**: `python -m build`
3. **Upload**: `twine upload dist/*`

## 🚨 Important Notes

### Package Name Availability

The package name `atadata-cli` might already be taken. If so, you'll need to:

1. **Check availability**: Visit https://pypi.org/project/atadata-cli/
2. **Choose alternative name**: e.g., `atadata-cli-tool`, `atadata-command-line`, etc.
3. **Update package name** in `setup.py` and `pyproject.toml`

### Version Management

- **First release**: Use `1.0.0`
- **Bug fixes**: Increment patch version (`1.0.1`, `1.0.2`)
- **New features**: Increment minor version (`1.1.0`, `1.2.0`)
- **Breaking changes**: Increment major version (`2.0.0`)

### Security Best Practices

- ✅ Use API tokens instead of passwords
- ✅ Enable 2FA on PyPI account
- ✅ Never commit API tokens to version control
- ✅ Use `.pypirc` file for authentication

## 🎉 Success!

Once published, users can install your CLI with:

```bash
pip install atadata-cli
atadata --help
```

## 📞 Support

If you encounter issues:

1. **Check PyPI status**: https://status.python.org/
2. **PyPI documentation**: https://packaging.python.org/tutorials/packaging-projects/
3. **Twine documentation**: https://twine.readthedocs.io/

**Your AtaData CLI is ready for the world! 🌍**
