#!/usr/bin/env python3
"""
Setup script for Scorpius - World's Strongest Smart Contract Scanner
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README_PACKAGE.md").read_text(encoding='utf-8')

# Read requirements
requirements = []
with open('requirements-scorpius.txt', 'r') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="scorpius-scanner",
    version="1.0.0",
    author="Scorpius Security Team",
    author_email="security@scorpius.io",
    description="World's Strongest Smart Contract Security Scanner with Machine Learning",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/scorpius-security/scorpius",
    project_urls={
        "Bug Reports": "https://github.com/scorpius-security/scorpius/issues",
        "Documentation": "https://docs.scorpius.io",
        "Source": "https://github.com/scorpius-security/scorpius",
    },
    packages=find_packages(include=['scorpius', 'scorpius.*']),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Natural Language :: English",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "ruff>=0.1.0",
            "mypy>=1.0.0",
        ],
        "api": [
            "fastapi>=0.100.0",
            "uvicorn[standard]>=0.20.0",
        ],
        "pdf": [
            "reportlab>=4.0.0",
            "pypdf>=3.0.0",
        ],
        "enterprise": [
            "redis>=4.0.0",
            "celery>=5.0.0",
            "prometheus-client>=0.15.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "scorpius=scorpius.cli:main",
            "scorpius-api=scorpius.api:start_server",
            "scorpius-train=scorpius.training:main",
        ],
    },
    include_package_data=True,
    package_data={
        "scorpius": [
            "data/*.json",
            "templates/*.html",
            "templates/*.css",
            "config/*.yaml",
            "patterns/*.json",
        ],
    },
    exclude_package_data={
        "": [
            "test_*",
            "*_test.py",
            "exploit_*",
            "simulation_*",
            "*exploit*",
            "*simulation*",
            "benchmark_*",
            "demo_*",
            "working_*",
        ],
    },
    zip_safe=False,
    keywords=[
        "smart-contract", "security", "vulnerability", "scanner", "blockchain",
        "ethereum", "solidity", "defi", "audit", "machine-learning", "ai"
    ],
    license="MIT",
)