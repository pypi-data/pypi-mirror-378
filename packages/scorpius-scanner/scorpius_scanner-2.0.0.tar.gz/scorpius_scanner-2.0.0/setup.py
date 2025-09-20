#!/usr/bin/env python3
"""
Scorpius Scanner 2.0.0 - World's Strongest Smart Contract Security Scanner
Setup script for PyPI distribution
"""

from setuptools import setup, find_packages
import os
from pathlib import Path

# Read the README file
def read_readme():
    readme_path = Path(__file__).parent / "README.md"
    if readme_path.exists():
        return readme_path.read_text(encoding="utf-8")
    return "World's Strongest Smart Contract Security Scanner"

# Read requirements
def read_requirements():
    requirements_path = Path(__file__).parent / "requirements_scorpius.txt"
    if requirements_path.exists():
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="scorpius-scanner",
    version="2.0.0",
    author="Scorpius Security Team",
    author_email="security@scorpius.io",
    description="World's Strongest Smart Contract Security Scanner - Advanced ML-powered vulnerability detection",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/scorpius-security/scorpius-scanner",
    project_urls={
        "Bug Reports": "https://github.com/scorpius-security/scorpius-scanner/issues",
        "Source": "https://github.com/scorpius-security/scorpius-scanner",
        "Documentation": "https://docs.scorpius.io",
        "Homepage": "https://scorpius.io",
    },
    packages=find_packages(include=["scorpius*"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Security",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    keywords=[
        "security", "smart-contracts", "blockchain", "ethereum", "solidity",
        "vulnerability-detection", "static-analysis", "defi", "web3",
        "machine-learning", "ai", "audit", "penetration-testing",
        "reentrancy", "access-control", "oracle-manipulation", "flash-loans"
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "ml": [
            "torch>=2.0.0",
            "transformers>=4.30.0",
            "sentence-transformers>=2.2.0",
            "scikit-learn>=1.3.0",
            "networkx>=3.1",
        ],
        "analysis": [
            "slither-analyzer>=0.10.0",
            "py-solc-x>=2.0.0",
        ],
        "reporting": [
            "reportlab>=4.0.0",
            "jinja2>=3.1.0",
            "weasyprint>=60.0",
        ],
        "all": [
            "torch>=2.0.0",
            "transformers>=4.30.0",
            "sentence-transformers>=2.2.0",
            "scikit-learn>=1.3.0",
            "networkx>=3.1",
            "slither-analyzer>=0.10.0",
            "py-solc-x>=2.0.0",
            "reportlab>=4.0.0",
            "jinja2>=3.1.0",
            "weasyprint>=60.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "scorpius=scorpius.cli.main:main",
            "scorpius-scan=scorpius.cli.main:scan",
            "scorpius-benchmark=scorpius.cli.main:benchmark",
        ],
    },
    include_package_data=True,
    package_data={
        "scorpius": [
            "data/*.json",
            "data/*.yaml",
            "data/*.yml",
            "patterns/*.json",
            "patterns/*.yaml",
            "templates/*.html",
            "templates/*.jinja2",
            "templates/*.md",
        ],
    },
    zip_safe=False,
    platforms=["any"],
    license="MIT",
    download_url="https://github.com/scorpius-security/scorpius-scanner/archive/v2.0.0.tar.gz",
)