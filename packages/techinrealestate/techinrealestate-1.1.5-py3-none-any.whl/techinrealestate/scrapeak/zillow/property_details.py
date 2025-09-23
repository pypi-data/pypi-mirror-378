"""
Zillow Property Details Module - Scrapeak API

This module provides functions to fetch detailed property information from Zillow using the Scrapeak API.
"""

import requests
import logging
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Union


def ms_to_date(ms):
    """Convert milliseconds timestamp to date string"""
    if not ms:
        return None
    
    # Handle both string and numeric timestamps
    try:
        if isinstance(ms, str):
            ms = int(ms)
        return datetime.utcfromtimestamp(ms / 1000).strftime("%Y-%m-%d")
    except (ValueError, TypeError, OSError):
        # If conversion fails, return the original value
        return str(ms)


def _extract_listed_by_number(property_data):
    """Extract phone number from listedBy data"""
    try:
        listed_by = property_data.get("listedBy", [])
        if listed_by:
            for elem in listed_by[0].get("elements", []):
                if elem.get("id") == "PHONE":
                    return elem.get("text")
        return None
    except (IndexError, KeyError, AttributeError):
        return None


def clean_property_details_data(property_data):
    """Clean and extract essential fields from property details data"""
    try:
        p = property_data
        
        # Extract nested data structures
        reso_facts = p.get("resoFacts", {})
        home_info = p.get("homeInfo", {})
        address = p.get("address", {})
        lat_long = p.get("latLong", {})
        price_history = p.get("priceHistory", [])
        tax_history = p.get("taxHistory", [])
        responsive_photos = p.get("responsivePhotos", [])
        
        # Convert timestamps in price history and clean fields
        cleaned_price_history = []
        for entry in price_history:
            if "date" in entry:
                entry["date"] = ms_to_date(entry["date"])
            
            # Extract only essential fields
            cleaned_entry = {
                "date": entry.get("date"),
                "price": entry.get("price"),
                "pricePerSquareFoot": entry.get("pricePerSquareFoot"),
                "priceChangeRate": entry.get("priceChangeRate"),
                "event": entry.get("event"),
                "source": entry.get("source")
            }
            cleaned_price_history.append(cleaned_entry)
        
        price_history = cleaned_price_history
        
        # Convert timestamps in tax history
        for entry in tax_history:
            if "time" in entry:
                entry["time"] = ms_to_date(entry["time"])
        
        # Get price change info from price history
        price_change = None
        price_change_date = None
        if price_history and len(price_history) > 1:
            latest_price = price_history[0].get("price", 0)
            previous_price = price_history[1].get("price", 0)
            if latest_price != previous_price:
                price_change = latest_price - previous_price
                price_change_date = price_history[0].get("date", "")
        
        # Extract photo URLs
        photo_urls = []
        if responsive_photos:
            photo_urls = [photo.get("url", "") for photo in responsive_photos]
        
        return {
            # BASIC IDENTIFICATION
            "zpid": p.get("zpid"),
            "streetAddress": address.get("streetAddress"),
            "city": address.get("city"),
            "state": address.get("state"),
            "zipcode": address.get("zipcode"),
            "latitude": p.get("latitude"),
            "longitude": p.get("longitude"),
            "parcelId": p.get("parcelId"),
            
            # PRICING & FINANCIAL
            "price": p.get("price"),
            "priceChange": price_change,
            "priceChangeDate": price_change_date,
            "pricePerSquareFoot": reso_facts.get("pricePerSquareFoot"),
            "zestimate": p.get("zestimate"),
            "rentZestimate": p.get("rentZestimate"),
            "taxAnnualAmount": reso_facts.get("taxAnnualAmount"),
            "taxAssessedValue": reso_facts.get("taxAssessedValue"),
            "propertyTaxRate": p.get("propertyTaxRate"),
            
            # PROPERTY SPECIFICATIONS
            "bedrooms": reso_facts.get("bedrooms"),
            "bathrooms": reso_facts.get("bathrooms"),
            "bathroomsFull": reso_facts.get("bathroomsFull"),
            "bathroomsHalf": reso_facts.get("bathroomsHalf"),
            "livingArea": p.get("livingAreaValue"),
            "lotSize": reso_facts.get("lotSize"),
            "yearBuilt": reso_facts.get("yearBuilt"),
            "homeType": reso_facts.get("homeType"),
            "architecturalStyle": reso_facts.get("architecturalStyle"),
            "levels": reso_facts.get("levels"),
            "basement": reso_facts.get("basement"),
            "garageParkingCapacity": reso_facts.get("garageParkingCapacity"),
            "parkingCapacity": reso_facts.get("parkingCapacity"),
            
            # FEATURES & AMENITIES
            "heating": reso_facts.get("heating"),
            "cooling": reso_facts.get("cooling"),
            "fireplaceFeatures": reso_facts.get("fireplaceFeatures"),
            "appliances": reso_facts.get("appliances"),
            "flooring": reso_facts.get("flooring"),
            "roofType": reso_facts.get("roofType"),
            "constructionMaterials": reso_facts.get("constructionMaterials"),
            "lotFeatures": reso_facts.get("lotFeatures"),
            "parkingFeatures": reso_facts.get("parkingFeatures"),
            "patioAndPorchFeatures": reso_facts.get("patioAndPorchFeatures"),
            
            # LOCATION & ZONING
            "zoning": reso_facts.get("zoning"),
            "zoningDescription": reso_facts.get("zoningDescription"),
            "neighborhood": address.get("neighborhood"),
            "subdivision": address.get("subdivision"),
            
            # SCHOOLS
            "elementarySchool": reso_facts.get("elementarySchool"),
            "elementarySchoolDistrict": reso_facts.get("elementarySchoolDistrict"),
            "middleOrJuniorSchool": reso_facts.get("middleOrJuniorSchool"),
            "middleOrJuniorSchoolDistrict": reso_facts.get("middleOrJuniorSchoolDistrict"),
            "highSchool": reso_facts.get("highSchool"),
            "highSchoolDistrict": reso_facts.get("highSchoolDistrict"),
            
            # PROPERTY DESCRIPTION & MEDIA
            "description": p.get("description"),
            "photoCount": len(photo_urls),
            "photoUrls": photo_urls,
            "listingSubType": p.get("listingSubType"),
            
            # HISTORY DATA
            "priceHistory": price_history,
            "taxHistory": tax_history,
            
            # LISTING & AGENT INFO
            "agentName": p.get("attributionInfo", {}).get("agentName"),
            "agentPhoneNumber": p.get("attributionInfo", {}).get("agentPhoneNumber"),
            "brokerName": p.get("attributionInfo", {}).get("brokerName"),
            "brokerPhoneNumber": p.get("attributionInfo", {}).get("brokerPhoneNumber"),
            "listedByNumber": _extract_listed_by_number(p),
            "listingTerms": reso_facts.get("listingTerms"),
            "onMarketDate": datetime.utcfromtimestamp(p.get("resoFacts", {}).get("onMarketDate", 0) / 1000).strftime("%Y-%m-%d") if p.get("resoFacts", {}).get("onMarketDate") else None,
            "daysOnZillow": p.get("daysOnZillow")
        }
    except Exception as e:
        # Return minimal data if cleaning fails
        return {
            "zpid": p.get("zpid"),
            "streetAddress": p.get("address", {}).get("streetAddress"),
            "city": p.get("address", {}).get("city"),
            "state": p.get("address", {}).get("state"),
            "price": p.get("price"),
            "bedrooms": p.get("resoFacts", {}).get("bedrooms"),
            "bathrooms": p.get("resoFacts", {}).get("bathrooms"),
            "livingArea": p.get("resoFacts", {}).get("aboveGradeFinishedArea")
        }


def get_property_details(
    api_key: str,
    zpids: Union[str, List[str]],
    batch_size: int = 2,
    clean_data: bool = True,
    enable_logging: bool = False
) -> Dict:
    """
    Get detailed property information for one or more ZPIDs using Scrapeak API
    
    Parameters:
    -----------
    api_key : str
        Your Scrapeak API key
    zpids : str or list of str
        Single ZPID string or list of ZPIDs to get details for
    batch_size : int, optional
        Number of concurrent requests per second (default: 2)
    clean_data : bool, optional
        If True, returns cleaned data with essential fields only; if False, returns raw data (default: True)
    enable_logging : bool, optional
        If True, enables progress logging for multiple ZPIDs (default: False)
    
    Returns:
    --------
    dict
        Dictionary containing:
        - data: List of property details (one per ZPID)
        - credits: API credit usage information
        - summary: Summary statistics
        
    Example:
    --------
    >>> # Single property
    >>> details = get_property_details(api_key, "34648268")
    >>> 
    >>> # Multiple properties
    >>> zpids = ["34648268", "121349556", "45037932"]
    >>> details = get_property_details(api_key, zpids, enable_logging=True)
    >>> 
    >>> # From listings data
    >>> listings = get_zillow_listings(api_key, url)
    >>> zpids = [prop['zpid'] for prop in listings['data']]
    >>> details = get_property_details(api_key, zpids)
    """
    
    # Normalize input to list
    if isinstance(zpids, str):
        zpids = [zpids]
    
    if not zpids:
        return {"data": [], "credits": {"used": 0, "remaining": 0}, "summary": {"total": 0, "successful": 0, "failed": 0}}
    
    api_url = "https://app.scrapeak.com/v1/scrapers/zillow/property"
    all_properties = []
    total_used_credits = 0
    successful_count = 0
    failed_count = 0
    
    # Setup logging if enabled
    if enable_logging:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        logger = logging.getLogger(__name__)
    else:
        logger = None
    
    if logger:
        logger.info(f"Fetching property details for {len(zpids)} properties...")
    
    def fetch_single_property(zpid):
        """Fetch a single property by ZPID"""
        try:
            params = {"api_key": api_key, "zpid": str(zpid)}
            response = requests.get(api_url, params=params)
            
            if response.status_code == 200:
                response_data = response.json()
                
                if response_data.get('is_success', False):
                    property_data = response_data.get('data', {})
                    property_data['zpid'] = str(zpid)
                    credits_used = response_data.get('info', {}).get('used_credits', 0)
                    return {
                        'success': True,
                        'data': property_data,
                        'credits': credits_used,
                        'zpid': str(zpid)
                    }
                else:
                    return {
                        'success': False,
                        'error': f"API returned unsuccessful response for ZPID {zpid}",
                        'zpid': str(zpid)
                    }
            else:
                return {
                    'success': False,
                    'error': f"HTTP error {response.status_code} for ZPID {zpid}",
                    'zpid': str(zpid)
                }
        except Exception as e:
            return {
                'success': False,
                'error': f"Exception fetching ZPID {zpid}: {str(e)}",
                'zpid': str(zpid)
            }
    
    # Process with continuous rate limiting using a single executor
    processed_count = 0
    all_futures = []
    
    # Use a single executor with higher max_workers for better concurrency
    max_workers = max(1, min(batch_size * 3, len(zpids)))  # Allow more concurrent workers
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all requests with 1-second intervals between batches
        for i, zpid in enumerate(zpids):
            # Calculate which batch this request belongs to
            batch_num = i // batch_size
            
            # Submit the request immediately
            future = executor.submit(fetch_single_property, zpid)
            all_futures.append(future)
            
            # Rate limiting: wait 1 second between batches
            if (i + 1) % batch_size == 0 and i < len(zpids) - 1:
                time.sleep(1.0)
        
        # Process all results as they complete
        for future in as_completed(all_futures):
            result = future.result()
            processed_count += 1
            
            # Log progress every 10 properties or for single property
            if logger and (processed_count % 10 == 0 or len(zpids) == 1 or processed_count == len(zpids)):
                logger.info(f"Processing property {processed_count}/{len(zpids)}")
            
            if result['success']:
                # Apply data cleaning if requested
                if clean_data:
                    cleaned_data = clean_property_details_data(result['data'])
                    all_properties.append(cleaned_data)
                else:
                    all_properties.append(result['data'])
                total_used_credits += result['credits']
                successful_count += 1
            else:
                failed_count += 1
                if logger:
                    logger.warning(result['error'])
    
    if logger:
        logger.info(f"Completed: {successful_count} successful, {failed_count} failed")
    
    return {
        "data": all_properties,
        "credits": {
            "used": total_used_credits,
            "remaining": 0  # Would need to track this from last response
        },
        "summary": {
            "total": len(zpids),
            "successful": successful_count,
            "failed": failed_count
        }
    }


def get_property_details_summary(details: Dict) -> Dict:
    """
    Get a structured summary of the property details data
    
    Parameters:
    -----------
    details : dict
        The response from get_property_details function
    
    Returns:
    --------
    dict
        Structured summary with statistics and sample data
    """
    if not details or not details.get('data'):
        return {"error": "No property details data available"}
    
    data = details.get('data', [])
    summary = details.get('summary', {})
    credits = details.get('credits', {})
    
    # Extract sample property info
    sample_properties = []
    for prop in data[:3]:  # First 3 properties
        sample_properties.append({
            "zpid": prop.get('zpid', 'N/A'),
            "address": f"{prop.get('streetAddress', '')} {prop.get('city', '')} {prop.get('state', '')} {prop.get('zipcode', '')}".strip(),
            "price": prop.get('price', 'N/A'),
            "bedrooms": prop.get('bedrooms', 'N/A'),
            "bathrooms": prop.get('bathrooms', 'N/A'),
            "living_area": prop.get('livingArea', 'N/A')
        })
    
    return {
        "summary": {
            "total_requested": summary.get('total', 0),
            "successful": summary.get('successful', 0),
            "failed": summary.get('failed', 0),
            "success_rate": f"{(summary.get('successful', 0) / max(summary.get('total', 1), 1)) * 100:.1f}%"
        },
        "credits": {
            "used": credits.get('used', 0),
            "remaining": credits.get('remaining', 0)
        },
        "sample_properties": sample_properties
    }
