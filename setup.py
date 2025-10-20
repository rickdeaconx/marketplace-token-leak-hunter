"""
Setup configuration for Marketplace Token Leak Hunter.

Copyright (c) 2025 Rick Deacon / Knostic Labs
Licensed under the MIT License
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="marketplace-token-leak-hunter",
    version="1.0.0",
    author="Rick Deacon",
    author_email="rick@knosticlabs.com",
    description="Lightweight scanner focused on detecting leaked IDE extension marketplace tokens (VS Code, Open VSX, npm)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rickdeaconx/marketplace-token-leak-hunter",
    project_urls={
        "Bug Tracker": "https://github.com/rickdeaconx/marketplace-token-leak-hunter/issues",
        "Documentation": "https://github.com/rickdeaconx/marketplace-token-leak-hunter/blob/master/README.md",
        "Source Code": "https://github.com/rickdeaconx/marketplace-token-leak-hunter",
        "Security": "https://github.com/rickdeaconx/marketplace-token-leak-hunter/blob/master/SECURITY.md",
    },
    packages=find_packages(exclude=["tests", "tests.*", "sample-data"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Security",
        "Topic :: Software Development :: Quality Assurance",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Natural Language :: English",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "token-leak-hunter=src.scan_repo:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "security",
        "scanner",
        "tokens",
        "credentials",
        "leak-detection",
        "github",
        "npm",
        "ci-cd",
        "marketplace",
    ],
    license="MIT",
)
