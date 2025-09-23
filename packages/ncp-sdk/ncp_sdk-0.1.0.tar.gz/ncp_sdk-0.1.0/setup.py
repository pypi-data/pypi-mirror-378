#!/usr/bin/env python3
"""Setup script for NCP SDK."""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="ncp_sdk",
    version="0.1.0",
    author="Aviz Networks",
    author_email="support@aviznetworks.com",
    description="Network Copilot SDK for AI agent development",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://aviznetworks.com",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pydantic>=2.0.0",
        "click>=8.0.0",
        "requests>=2.28.0",
        "rich>=13.0.0",
        "typing-extensions>=4.0.0",
        "toml>=0.10.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ncp=ncp.cli.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "ncp": ["templates/*", "schemas/*"],
    },
)