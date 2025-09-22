"""
Scrapeak API Services

This module provides access to various real estate platforms through the Scrapeak API.
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
