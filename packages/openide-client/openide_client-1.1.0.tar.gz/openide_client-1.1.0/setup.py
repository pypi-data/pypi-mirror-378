#!/usr/bin/env python3
"""
Setup script for openide-client
"""

from setuptools import setup, find_packages
import os

def read_requirements():
    """Read requirements from requirements.txt"""
    try:
        with open('requirements.txt', 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        # Default requirements if file not found
        return ['requests>=2.25.0', 'click>=8.0.0']

def read_readme():
    """Read README file"""
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "OpenIDE Client Library"

setup(
    name="openide-client",
    version="1.1.0",  # Обновленная версия с исправлениями
    author="OpenIDE Team",
    author_email="team@openide.dev",
    description="Python client library for OpenIDE API",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/openide/openide-client",
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
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "openide-client=openide_client.cli:main",
        ],
    },
    keywords="openide, container, api, client, python",
    project_urls={
        "Bug Reports": "https://github.com/openide/openide-client/issues",
        "Source": "https://github.com/openide/openide-client",
        "Documentation": "https://openide.dev/docs",
    },
)
