#!/usr/bin/env python3
"""
Setup script for Rose Python SDK
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="rose-python-sdk",
    version="1.1.0",
    author="luli",
    author_email="luli245683@gmail.com",
    description="Python SDK for Rose Recommendation Service API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/luli0034/rose-python-sdk",
    project_urls={
        "Bug Reports": "https://github.com/luli0034/rose-python-sdk/issues",
        "Source": "https://github.com/luli0034/rose-python-sdk",
        "Documentation": "https://github.com/luli0034/rose-python-sdk/tree/main/docs",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
            "types-requests>=2.32.0",
        ],
    },
    keywords="recommendation, machine learning, api, sdk, rose",
    include_package_data=True,
    zip_safe=False,
)
