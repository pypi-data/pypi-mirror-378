"""
Basic tests for TechInRealEstate package
"""

import pytest
from techinrealestate import (
    get_zillow_listings,
    get_property_details,
    get_listings_summary,
    get_property_details_summary
)


def test_imports():
    """Test that all main functions can be imported"""
    assert callable(get_zillow_listings)
    assert callable(get_property_details)
    assert callable(get_listings_summary)
    assert callable(get_property_details_summary)


def test_package_structure():
    """Test that the package structure is correct"""
    import techinrealestate
    import techinrealestate.scrapeak
    import techinrealestate.scrapeak.zillow
    
    # Test that modules exist
    assert hasattr(techinrealestate.scrapeak.zillow, 'listings')
    assert hasattr(techinrealestate.scrapeak.zillow, 'property_details')


def test_function_signatures():
    """Test that function signatures are correct"""
    import inspect
    
    # Test get_zillow_listings signature
    sig = inspect.signature(get_zillow_listings)
    expected_params = ['api_key', 'listing_url', 'all_properties_flag', 'batch_size', 'clean_data', 'enable_logging']
    actual_params = list(sig.parameters.keys())
    
    for param in expected_params:
        assert param in actual_params, f"Missing parameter: {param}"
    
    # Test get_property_details signature
    sig = inspect.signature(get_property_details)
    expected_params = ['api_key', 'zpids', 'batch_size', 'clean_data', 'enable_logging']
    actual_params = list(sig.parameters.keys())
    
    for param in expected_params:
        assert param in actual_params, f"Missing parameter: {param}"


def test_empty_inputs():
    """Test behavior with empty inputs"""
    # Test empty ZPIDs list
    result = get_property_details("fake_key", [])
    assert result['data'] == []
    assert result['summary']['total'] == 0
    assert result['summary']['successful'] == 0
    assert result['summary']['failed'] == 0


def test_invalid_api_key():
    """Test behavior with invalid API key"""
    # This should return empty results, not crash
    result = get_zillow_listings("invalid_key", "https://example.com")
    assert isinstance(result, dict)
    # Should handle error gracefully
    assert 'data' in result or 'error' in result


if __name__ == "__main__":
    pytest.main([__file__])
