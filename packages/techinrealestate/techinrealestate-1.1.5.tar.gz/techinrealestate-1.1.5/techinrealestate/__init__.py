"""
TechInRealEstate - Real Estate Data Collection Package

A comprehensive package for collecting real estate data from various sources.
Organized by API service provider and platform.

Available services:
- scrapeak: Scrapeak API services (Zillow, etc.)
- apimaker: Apimaker API services (future)

Usage:
    # Service-specific imports (recommended)
    from techinrealestate.scrapeak import get_zillow_listings
    from techinrealestate.apimaker import get_zillow_listings  # future
    
    # Or direct imports (backward compatibility)
    from techinrealestate import get_zillow_listings
"""

__version__ = "1.1.5"
__author__ = "AnalyticsAriel"

# Import service modules
from . import scrapeak

# For backward compatibility, import main functions
from .scrapeak.zillow import (
    get_zillow_listings,
    get_property_details,
    get_listings_summary,
    get_property_details_summary
)

__all__ = [
    "scrapeak",
    "get_zillow_listings",
    "get_property_details", 
    "get_listings_summary",
    "get_property_details_summary"
]
