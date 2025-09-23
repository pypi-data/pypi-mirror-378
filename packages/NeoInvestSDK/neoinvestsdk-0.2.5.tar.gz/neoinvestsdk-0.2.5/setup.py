"""Setup configuration for NeoInvestSDK"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="NeoInvestSDK",
    version="0.1.0",
    author="VPBankS NeoPro Development Team",
    description="Modern async Python SDK for VPBankS NeoPro Trading Platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/private/NeoInvestSDK",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: AsyncIO",
    ],
    python_requires=">=3.8",
    keywords="trading, finance, stock, market, async, websocket, api, vpbanks",
    project_urls={
        "Bug Reports": "https://github.com/private/NeoInvestSDK/issues",
        "Source": "https://github.com/private/NeoInvestSDK",
    },
)
