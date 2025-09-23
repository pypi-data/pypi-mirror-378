#!/usr/bin/env python3
"""
Setup script for friendly_exceptions package
"""

from setuptools import setup, find_packages
import os

# Читаем README для длинного описания
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Читаем requirements
def read_requirements():
    requirements = []
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", "r", encoding="utf-8") as fh:
            requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    return requirements

setup(
    name="friendly-exceptions",
    version="0.0.1",
    author="artemjs",
    author_email="artemjson@gmail.com",
    description="Human-readable exception explanations in Russian and English with smart suggestions",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/artemjs/Pythonlibs/tree/friendly_exceptions/friendly_exceptions%200.0.1",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
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
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Quality Assurance",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "friendly-exceptions=friendly_exceptions.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="exceptions, error-handling, debugging, human-readable, russian, english",
    project_urls={
        "Bug Reports": "https://github.com/artemjs/Pythonlibs/issues",
        "Source": "https://github.com/artemjs/Pythonlibs/tree/friendly_exceptions/friendly_exceptions%200.0.1",
        "Documentation": "https://github.com/artemjs/Pythonlibs/tree/friendly_exceptions/friendly_exceptions%200.0.1",
    },
)