"""
Setup script for Selective Self-Attention (SSA) implementation.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
requirements = []
with open("requirements.txt", "r") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#"):
            requirements.append(line)

setup(
    name="selective-self-attention",
    version="1.0.0",
    author="DeepCode Research Team",
    author_email="research@deepcode.ai",
    description="Complete PyTorch implementation of Selective Self-Attention (SSA) from NeurIPS 2024",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/selective-self-attention",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=22.0",
            "isort>=5.0",
            "flake8>=4.0",
        ],
        "examples": [
            "jupyter>=1.0",
            "matplotlib>=3.0",
            "seaborn>=0.11",
        ],
    },
    entry_points={
        "console_scripts": [
            "ssa-train=scripts.train:main",
            "ssa-evaluate=scripts.evaluate:main",
            "ssa-predict=scripts.predict:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
