"""
Zillow Listings Module - Scrapeak API

This module provides functions to fetch property listings from Zillow using the Scrapeak API.
"""

import requests
import json
import urllib.parse
import re
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Union


def get_zillow_listings(
    api_key: str, 
    listing_url: str, 
    all_properties_flag: bool = False, 
    batch_size: int = 2,
    clean_data: bool = True,
    enable_logging: bool = False
) -> Dict:
    """
    Dynamically fetch Zillow property listings using Scrapeak API
    
    Parameters:
    -----------
    api_key : str
        Your Scrapeak API key
    listing_url : str
        The base Zillow search URL (e.g., from zillow.com search results)
    all_properties_flag : bool, optional
        If True, fetches all pages; if False, just first page (default: False)
    batch_size : int, optional
        Number of concurrent requests per second (default: 2)
    clean_data : bool, optional
        If True, returns cleaned data with essential fields only; if False, returns raw data (default: True)
    enable_logging : bool, optional
        If True, enables progress logging for multi-page requests (default: False)
    
    Returns:
    --------
    dict
        Single consolidated response with combined data from all pages containing:
        - data: List of property listings
        - pagination: Information about pages and results
        - credits: API credit usage information
        - metadata: Region and search metadata
    
    Example:
    --------
    >>> api_key = "your_scrapeak_api_key"
    >>> url = "https://www.zillow.com/toledo-oh/?searchQueryState=..."
    >>> listings = get_zillow_listings(api_key, url, all_properties_flag=False)
    >>> print(f"Found {len(listings['data'])} properties")
    """
    
    api_url = "https://app.scrapeak.com/v1/scrapers/zillow/listing"
    all_responses = []
    
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
    
    def clean_property_data(property_data):
        """Clean and extract essential fields from property data"""
        try:
            p = property_data
            hdp = p.get("hdpData", {}).get("homeInfo", {})
            
            return {
                # IDs & links
                "zpid": p.get("zpid") or hdp.get("zpid"),
                "detailUrl": p.get("detailUrl"),
                "imgSrc": p.get("imgSrc"),
                
                # Address & geo
                "street": p.get("addressStreet") or hdp.get("streetAddress"),
                "city": p.get("addressCity") or hdp.get("city"),
                "state": p.get("addressState") or hdp.get("state"),
                "zip": p.get("addressZipcode") or hdp.get("zipcode"),
                "lat": (p.get("latLong") or {}).get("latitude") or hdp.get("latitude"),
                "lng": (p.get("latLong") or {}).get("longitude") or hdp.get("longitude"),
                
                # Status & pricing
                "status": p.get("statusText") or p.get("rawHomeStatusCd") or hdp.get("homeStatus"),
                "price": p.get("unformattedPrice") or hdp.get("price"),
                "price_str": p.get("price"),
                
                # Beds/baths/size
                "beds": p.get("beds") or hdp.get("bedrooms"),
                "baths": p.get("baths") or hdp.get("bathrooms"),
                "sqft": p.get("area") or hdp.get("livingArea"),
                
                # Lot
                "lot_sqft": hdp.get("lotAreaValue"),
                "lot_unit": hdp.get("lotAreaUnit"),
                
                # Estimates
                "zestimate": p.get("zestimate") or hdp.get("zestimate"),
                "rent_zestimate": hdp.get("rentZestimate"),
                
                # Listing meta
                "home_type": hdp.get("homeType"),
                "broker": p.get("brokerName"),
                "is_zillow_owned": p.get("isZillowOwned", hdp.get("isZillowOwned")),
                
                # Activity & media
                "days_on_zillow": hdp.get("daysOnZillow") or (
                    int(re.search(r"(\d+)", p.get("flexFieldText", "") or "").group(1))
                    if "day" in (p.get("flexFieldText", "") or "").lower() else None
                ),
                "time_on_zillow_ms": hdp.get("timeOnZillow"),
                "photo_count": len((p.get("carouselPhotosComposable") or {}).get("photoData") or []) or None,
            }
        except Exception:
            # Return minimal data if cleaning fails
            return {
                "zpid": p.get("zpid"),
                "address": p.get("address"),
                "price": p.get("unformattedPrice"),
                "beds": p.get("beds"),
                "baths": p.get("baths"),
                "sqft": p.get("area")
            }
    
    def extract_response_data(response):
        """Helper function to extract key data from a response"""
        try:
            response_data = response.json()
            raw_data = response_data['data']['cat1']['searchResults']['listResults']
            
            # Apply data cleaning if requested
            if clean_data:
                cleaned_data = [clean_property_data(prop) for prop in raw_data]
            else:
                cleaned_data = raw_data
                
            return {
                'data': cleaned_data,
                'usedCredits': response_data['info']['used_credits'],
                'remainingCredits': response_data['info']['remaining_credits'],
                'totalPages': response_data['data']['cat1']['searchList']['totalPages'],
                'totalResultCount': response_data['data']['cat1']['searchList']['totalResultCount'],
                'resultsPerPage': response_data['data']['cat1']['searchList']['resultsPerPage'],
                'regionId': response_data['data']['regionState']['regionInfo'][0]['regionId'],
                'displayName': response_data['data']['regionState']['regionInfo'][0]['displayName'],
                'regionBounds': response_data['data']['regionState']['regionBounds'],
                'baseUrl': response_data['data']['searchPageSeoObject']['baseUrl'],
                'windowTitle': response_data['data']['searchPageSeoObject']['windowTitle'],
                'metaDescription': response_data['data']['searchPageSeoObject']['metaDescription']
            }
        except Exception as e:
            # Log error silently for package use
            return None
    
    def consolidate_responses(responses):
        """Helper function to consolidate multiple responses into a single object"""
        if not responses:
            return {}
        
        # Start with the first response as base
        first_response = responses[0]
        
        # Calculate estimated credits for all properties (10 credits per request)
        all_properties_estimated_credits = first_response['totalPages'] * 10
        
        # If only one response, return with estimated credits
        if len(responses) == 1:
            return {
                'data': first_response['data'],
                'pagination': {
                    'pagesRetrieved': 1,
                    'totalPages': first_response['totalPages'],
                    'propertiesRetrieved': len(first_response['data']),
                    'totalResultCount': first_response['totalResultCount'],
                    'resultsPerPage': first_response['resultsPerPage']
                },
                'credits': {
                    'usedCredits': first_response['usedCredits'],
                    'remainingCredits': first_response['remainingCredits'],
                    'allPropertiesEstimatedCredits': all_properties_estimated_credits
                },
                'metadata': {
                    'regionId': first_response['regionId'],
                    'displayName': first_response['displayName'],
                    'regionBounds': first_response['regionBounds'],
                    'baseUrl': first_response['baseUrl'],
                    'windowTitle': first_response['windowTitle'],
                    'metaDescription': first_response['metaDescription']
                }
            }
        
        # Combine data from all responses
        all_properties = []
        total_used_credits = 0
        
        for response in responses:
            all_properties.extend(response['data'])
            total_used_credits += response['usedCredits']
        
        # Return consolidated response with organized structure
        return {
            'data': all_properties,
            'pagination': {
                'pagesRetrieved': len(responses),
                'totalPages': first_response['totalPages'],
                'propertiesRetrieved': len(all_properties),
                'totalResultCount': first_response['totalResultCount'],
                'resultsPerPage': first_response['resultsPerPage']
            },
            'credits': {
                'usedCredits': total_used_credits,
                'remainingCredits': responses[-1]['remainingCredits'],
                'allPropertiesEstimatedCredits': all_properties_estimated_credits
            },
            'metadata': {
                'regionId': first_response['regionId'],
                'displayName': first_response['displayName'],
                'regionBounds': first_response['regionBounds'],
                'baseUrl': first_response['baseUrl'],
                'windowTitle': first_response['windowTitle'],
                'metaDescription': first_response['metaDescription']
            }
        }
    
    try:
        # First, get the first page to determine total pages
        if logger:
            logger.info("Fetching first page to get pagination info...")
        
        parameters = {"api_key": api_key, "url": listing_url}
        response = requests.get(api_url, params=parameters)
        
        if response.status_code != 200:
            if logger:
                logger.error(f"Error fetching first page: {response.status_code}")
            return {}
            
        # Extract data from first page
        first_page_data = extract_response_data(response)
        if first_page_data:
            all_responses.append(first_page_data)
        
        total_pages = first_page_data.get('totalPages', 1) if first_page_data else 1
        results_per_page = first_page_data.get('resultsPerPage', 0) if first_page_data else 0
        total_results = first_page_data.get('totalResultCount', 0) if first_page_data else 0
        
        if logger:
            logger.info(f"Found {total_pages} pages with {results_per_page} results per page ({total_results} total)")
        
        # If all_properties_flag is False, return just the first page
        if not all_properties_flag:
            if logger:
                logger.info("Returning first page only")
            return consolidate_responses(all_responses)
            
        # If all_properties_flag is True, fetch all remaining pages
        if logger:
            logger.info(f"Fetching all {total_pages} pages...")
        
        # Parse the base URL to extract the searchQueryState
        parsed_url = urllib.parse.urlparse(listing_url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        if 'searchQueryState' not in query_params:
            if logger:
                logger.error("Could not find searchQueryState in URL")
            return consolidate_responses(all_responses)
            
        # Parse the searchQueryState JSON
        search_query_state = json.loads(query_params['searchQueryState'][0])
        
        # Generate URLs for pages 2 through total_pages
        remaining_pages = list(range(2, total_pages + 1))
        total_batches = (len(remaining_pages) + batch_size - 1) // batch_size
        processed_pages = 0
        all_futures = []
        
        def fetch_page(page_num):
            """Fetch a single page"""
            try:
                # Update the searchQueryState with current page
                page_search_state = search_query_state.copy()
                page_search_state['pagination'] = {"currentPage": page_num}
                
                # Reconstruct the URL
                updated_query_state = json.dumps(page_search_state)
                new_query_params = urllib.parse.urlencode({'searchQueryState': updated_query_state})
                
                # Build the new URL with page number in path
                if page_num == 2:
                    new_path = parsed_url.path.replace('/toledo-oh/', '/toledo-oh/2_p/')
                else:
                    new_path = parsed_url.path.replace('/toledo-oh/', f'/toledo-oh/{page_num}_p/')
                
                new_url = f"{parsed_url.scheme}://{parsed_url.netloc}{new_path}?{new_query_params}"
                
                # Make the API request
                parameters = {"api_key": api_key, "url": new_url}
                response = requests.get(api_url, params=parameters)
                
                if response.status_code == 200:
                    page_data = extract_response_data(response)
                    if page_data:
                        return {
                            'success': True,
                            'data': page_data,
                            'page': page_num
                        }
                    else:
                        return {
                            'success': False,
                            'error': f"Error extracting data from page {page_num}",
                            'page': page_num
                        }
                else:
                    return {
                        'success': False,
                        'error': f"Error fetching page {page_num}: {response.status_code}",
                        'page': page_num
                    }
            except Exception as e:
                return {
                    'success': False,
                    'error': f"Exception fetching page {page_num}: {str(e)}",
                    'page': page_num
                }
        
        # Use a single executor with higher max_workers for better concurrency
        max_workers = max(1, min(batch_size * 3, len(remaining_pages)))
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all requests with 1-second intervals between batches
            for i, page_num in enumerate(remaining_pages):
                # Calculate which batch this request belongs to
                batch_num = i // batch_size
                
                # Submit the request immediately
                future = executor.submit(fetch_page, page_num)
                all_futures.append(future)
                
                # Rate limiting: wait 1 second between batches
                if (i + 1) % batch_size == 0 and i < len(remaining_pages) - 1:
                    time.sleep(1.0)
            
            # Process all results as they complete
            for future in as_completed(all_futures):
                result = future.result()
                processed_pages += 1
                
                # Log progress every 10 pages or for single page
                if logger and (processed_pages % 10 == 0 or len(remaining_pages) == 1 or processed_pages == len(remaining_pages)):
                    logger.info(f"Processing page {processed_pages + 1}/{total_pages}")
                
                if result['success']:
                    all_responses.append(result['data'])
                else:
                    if logger:
                        logger.warning(result['error'])
            
        if logger:
            logger.info(f"Successfully fetched {len(all_responses)} pages!")
        return consolidate_responses(all_responses)
        
    except Exception as e:
        if logger:
            logger.error(f"Error in get_zillow_listings: {str(e)}")
        return consolidate_responses(all_responses)


def get_listings_summary(listings: Dict) -> Dict:
    """
    Get a structured summary of the listings data
    
    Parameters:
    -----------
    listings : dict
        The response from get_zillow_listings function
    
    Returns:
    --------
    dict
        Structured summary with pagination, credits, and metadata info
    """
    if not listings:
        return {"error": "No listings data available"}
    
    pagination = listings.get('pagination', {})
    credits = listings.get('credits', {})
    metadata = listings.get('metadata', {})
    data = listings.get('data', [])
    
    return {
        "pagination": {
            "properties_retrieved": pagination.get('propertiesRetrieved', 0),
            "pages_retrieved": pagination.get('pagesRetrieved', 0),
            "total_pages": pagination.get('totalPages', 0),
            "total_available": pagination.get('totalResultCount', 0)
        },
        "credits": {
            "used": credits.get('usedCredits', 0),
            "remaining": credits.get('remainingCredits', 0),
            "estimated_for_all": credits.get('allPropertiesEstimatedCredits', 0)
        },
        "location": {
            "display_name": metadata.get('displayName', 'Unknown'),
            "region_id": metadata.get('regionId', 'N/A')
        },
        "sample_properties": [
            {
                "address": f"{prop.get('street', '')} {prop.get('city', '')} {prop.get('state', '')} {prop.get('zip', '')}".strip() or 'Unknown address',
                "price": prop.get('price_str', prop.get('price', 'N/A')),
                "beds": prop.get('beds', 'N/A'),
                "baths": prop.get('baths', 'N/A'),
                "sqft": prop.get('sqft', 'N/A')
            }
            for prop in data[:3]
        ]
    }
