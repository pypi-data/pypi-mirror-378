from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "techinrealestate", "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "A comprehensive Python package for collecting real estate data from various sources"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(requirements_path):
        with open(requirements_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return ["requests>=2.25.0"]

setup(
    name="techinrealestate",
        version="1.1.5",
    author="AnalyticsAriel",
    author_email="arielherrera@analyticsariel.com",
    description="A comprehensive Python package for collecting and analyzing real estate market data with built-in rate limiting, data cleaning, and batch processing",
    license="MIT",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/techinrealestate/",
    project_urls={
        "Bug Reports": "https://github.com/analyticsariel/techinrealestate-package/issues",
        "Documentation": "https://pypi.org/project/techinrealestate/",
        "Homepage": "https://pypi.org/project/techinrealestate/",
        "Get API Key": "https://www.scrapeak.com/zillow-scraper/?ref=ariel",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.900",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
        keywords="real estate, zillow, data collection, web scraping, property data, real estate api, property listings, real estate analysis, property details, zpid, scrapeak, batch processing, rate limiting",
    include_package_data=True,
    zip_safe=False,
)
