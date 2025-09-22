"""
TechInRealEstate - Real Estate Data Collection Package

A comprehensive package for collecting real estate data from various sources.
Organized by API service provider and platform.

Available modules:
- scrapeak.zillow: Zillow data collection via Scrapeak API
"""

__version__ = "1.0.0"
__author__ = "TechInRealEstate"

# Import main functions for easy access
from .scrapeak.zillow import (
    get_zillow_listings,
    get_property_details,
    get_listings_summary,
    get_property_details_summary
)

__all__ = [
    "get_zillow_listings",
    "get_property_details", 
    "get_listings_summary",
    "get_property_details_summary"
]
