#!/usr/bin/env python3
"""
Setup script for atadata-cli package.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "AtaData CLI - Command line interface for AtaData Job Scheduler Backend API"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="atadata-cli",
    version="1.0.0",
    author="AtaData Team",
    author_email="support@atadata.com",
    description="Command line interface for AtaData Job Scheduler Backend API",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/atadata/atadata-cli",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "test": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "pytest-mock>=3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "atadata=atadata_cli.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="cli, atadata, job-scheduler, api, backend, automation",
    project_urls={
        "Bug Reports": "https://github.com/atadata/atadata-cli/issues",
        "Source": "https://github.com/atadata/atadata-cli",
        "Documentation": "https://github.com/atadata/atadata-cli#readme",
    },
)
