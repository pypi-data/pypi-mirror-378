"""
Setup script for Crimson7 NPM Security Scanner
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="npmscanner",
    version="0.1.2",
    author="Crimson7 Security",
    author_email="security@crimson7.io",
    description="Advanced NPM Security Scanner for supply chain analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://crimson7.io",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Security",
        "Topic :: Software Development :: Quality Assurance",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.28.0",
        "urllib3>=1.26.0",
    ],
    entry_points={
        "console_scripts": [
            "npmscanner=npmscanner.__main__:main",
        ],
    },
    include_package_data=True,
    package_data={
        "npmscanner": ["*.json"],
    },
    keywords="security, npm, supply-chain, vulnerability, malware, obfuscation",
    project_urls={
        "Bug Reports": "https://github.com/crimson7/npmscanner/issues",
        "Source": "https://github.com/crimson7/npmscanner",
        "Documentation": "https://crimson7.io/docs",
        "Homepage": "https://crimson7.io",
    },
)
