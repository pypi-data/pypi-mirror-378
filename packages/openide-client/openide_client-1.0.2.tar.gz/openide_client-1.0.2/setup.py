#!/usr/bin/env python3
"""
Setup script for OpenIDE Client
"""

from setuptools import setup, find_packages
import os

# Читаем README
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Читаем requirements
def read_requirements():
    try:
        with open("requirements.txt", "r", encoding="utf-8") as fh:
            return [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        return [
            "requests>=2.25.0",
            "click>=8.0.0", 
            "psutil>=5.8.0",
            "pyyaml>=6.0.0",
            "colorama>=0.4.0"
        ]

setup(
    name="openide-client",
    version="1.0.2",
    author="OpenIDE Team",
    author_email="openide@example.com",
    description="Python client library for OpenIDE container system",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/artemjs/OpenIDE",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "Topic :: Software Development :: Build Tools",
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
        "api": [
            "requests>=2.25.0",
            "flask>=2.0.0",
            "flask-cors>=3.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "openide-client=openide_client.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "openide_client": ["*.py", "*.md", "*.txt"],
    },
    keywords="openide, container, docker, development, ide, python",
    project_urls={
        "Bug Reports": "https://github.com/artemjs/OpenIDE/issues",
        "Source": "https://github.com/artemjs/OpenIDE",
        "Documentation": "https://github.com/artemjs/OpenIDE/blob/main/README.md",
    },
)
