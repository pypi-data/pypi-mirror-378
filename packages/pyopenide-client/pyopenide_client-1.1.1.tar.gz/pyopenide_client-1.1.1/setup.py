#!/usr/bin/env python3
"""
Setup script for pyopenide-client
"""

from setuptools import setup, find_packages
from pathlib import Path

# Читаем README
def read_readme():
    readme_path = Path(__file__).parent / "README_pyopenide.md"
    if readme_path.exists():
        return readme_path.read_text(encoding='utf-8')
    return "PyOpenIDE Client - Упрощенные клиенты для OpenIDE"

# Читаем requirements
def read_requirements():
    requirements_path = Path(__file__).parent / "requirements_pyopenide.txt"
    if requirements_path.exists():
        return requirements_path.read_text(encoding='utf-8').strip().split('\n')
    return [
        "requests>=2.28.1",
        "Flask>=2.0.0",
        "Flask-Cors>=3.0.10",
        "click>=8.0.0",
        "uuid>=1.30",
        "psutil>=5.9.0",
        "colorama>=0.4.4",
        "python-dotenv>=0.19.0",
        "pyyaml>=6.0",
        "setuptools>=65.5.1",
        "twine>=4.0.2"
    ]

setup(
    name="pyopenide-client",
    version="1.1.1",
    author="OpenIDE Team",
    author_email="openide@example.com",
    description="Упрощенные клиенты для OpenIDE с разными уровнями простоты синтаксиса",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/openide/pyopenide-client",
    project_urls={
        "Bug Reports": "https://github.com/openide/pyopenide-client/issues",
        "Source": "https://github.com/openide/pyopenide-client",
        "Documentation": "https://pypi.org/project/pyopenide-client/",
    },
    packages=find_packages(include=['pyopenide_client*']),
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
    install_requires=read_requirements(),
    extras_require={
        "global_openide": ["global-openide>=1.0.0"],
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.900",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "pyopenide=pyopenide_client:quick_start",
        ],
    },
    keywords="openide, container, docker, development, ide, python, client",
    include_package_data=True,
    zip_safe=False,
)
