#!/usr/bin/env python3
"""
Setup script for SmartDecision Python SDK
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "SmartDecision Python SDK for AI-powered ensemble decision making"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(requirements_path):
        with open(requirements_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return [
        "httpx>=0.24.0",
        "pydantic>=2.0.0",
        "typing-extensions>=4.0.0",
    ]

setup(
    name="smartdecision-sdk",
        version="1.0.1",
    description="Python SDK for SmartDecision AI-powered ensemble decision making",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Alex Zhang",
    author_email="1108alexzhang@gmail.com",
    url="https://github.com/ankryptonite/smartdecision-python-sdk",
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
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "isort>=5.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    keywords="ai, decision-making, ensemble, llm, machine-learning, api, sdk",
    project_urls={
        "Homepage": "https://smartdecision.ai",
        "Documentation": "https://github.com/ankryptonite/smartdecision-python-sdk",
        "Repository": "https://github.com/ankryptonite/smartdecision-python-sdk",
        "Bug Reports": "https://github.com/smartdecision-python-sdk/issues",
    },
    include_package_data=True,
    zip_safe=False,
)
