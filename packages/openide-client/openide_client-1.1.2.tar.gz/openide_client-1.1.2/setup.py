#!/usr/bin/env python3
"""
Setup script for openide-client
"""

from setuptools import setup, find_packages

setup(
    name="openide-client",
    version="1.1.2",
    author="ArtemJS",
    author_email="artemjson@gmail.com",
    description="Python client library for OpenIDE container system",
    long_description="Python client library for OpenIDE container system with HTTP API support",
    long_description_content_type="text/plain",
    url="https://github.com/artemjs/OpenIDE/tree/openide-client",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.28.1",
        "click>=8.0.0",
        "psutil>=5.9.0",
        "colorama>=0.4.4",
        "python-dotenv>=0.19.0",
        "pyyaml>=6.0",
    ],
    entry_points={
        "console_scripts": [
            "openide-client=openide_client.cli:cli",
        ],
    },
    keywords="openide, container, docker, development, ide, python, client",
    include_package_data=True,
    zip_safe=False,
)
