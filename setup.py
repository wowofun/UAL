from setuptools import setup, find_packages
import os

# Read the contents of your README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ual-lang",
    version="1.0.1",
    author="UAL Contributors",
    author_email="open@ual-lang.org",
    description="Universal Action Language (UAL) - A binary-first, semantic protocol for AI agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wowofun/UAL",
    project_urls={
        "Bug Tracker": "https://github.com/wowofun/UAL/issues",
        "Documentation": "https://github.com/wowofun/UAL/tree/main/docs",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: System :: Hardware",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "protobuf>=4.25.0",
        "networkx>=3.0",
        "numpy>=1.24.0",
    ],
    extras_require={
        "viz": ["matplotlib>=3.7.0"],
        "dev": ["pytest", "twine", "build"],
        "studio": ["flask>=3.0.0", "deep-translator>=1.11.4"],
    },
    entry_points={
        "console_scripts": [
            "ual=ual.cli:main",
        ],
    },
    include_package_data=True,
)
