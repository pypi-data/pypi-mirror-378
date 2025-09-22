"""
BitCrawl Package Setup
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read the requirements file
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="bitcrawl",
    version="0.0.1",
    author="Goosy Pvt. Ltd.",
    author_email="goosy.official@gmail.com",
    description="Universal web crawling SDK for developers",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/Akash-nath29/BitCrawl",
    project_urls={
        "Bug Tracker": "https://github.com/Akash-nath29/BitCrawl/issues",
        "Documentation": "https://github.com/Akash-nath29/BitCrawl#readme",
        "Source Code": "https://github.com/Akash-nath29/BitCrawl",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Software Development :: Libraries :: Python Modules", 
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.812",
            "pre-commit>=2.0",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "bitcrawl=bitcrawl.cli:main",
        ],
    },
    keywords=[
        "web scraping",
        "web crawler", 
        "html parser",
        "content extraction",
        "contextual filtering",
        "firecrawl alternative",
        "website scraper",
        "link crawler",
        "data mining",
        "llm preprocessing"
    ],
    include_package_data=True,
    zip_safe=False,
)