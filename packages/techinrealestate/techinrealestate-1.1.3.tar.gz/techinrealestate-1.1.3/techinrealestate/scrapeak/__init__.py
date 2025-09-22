"""
Scrapeak API Services

This module provides access to various real estate platforms through the Scrapeak API.

Available platforms:
- zillow: Zillow data collection via Scrapeak API

Usage:
    from techinrealestate.scrapeak import get_zillow_listings
    from techinrealestate.scrapeak.zillow import get_listings, get_property_details
"""

from .zillow import (
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
