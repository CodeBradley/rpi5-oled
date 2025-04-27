#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

# Read requirements from requirements.txt
with open('requirements.txt') as f:
    requirements = f.read().splitlines()
    # Remove comments and empty lines
    requirements = [line for line in requirements if line and not line.startswith('#')]

# Read long description from README.md
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="rpi5-oled",
    version="0.1.0",
    description="A modular grid-based framework for OLED displays on Raspberry Pi",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Bradley",
    author_email="brad@example.com",
    url="https://github.com/CodeBradley/rpi5-oled",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Hardware",
        "Topic :: System :: Monitoring",
    ],
    entry_points={
        "console_scripts": [
            "rpi5-oled=app:main",
        ],
    },
    package_data={
        "": ["fonts/*.ttf"],
    },
)
