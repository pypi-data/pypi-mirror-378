# TechInRealEstate

A comprehensive Python package for collecting and analyzing real estate market data from various sources, organized by API service provider and platform.

## 🚀 Quick Example

```python
from techinrealestate.scrapeak import get_zillow_listings, get_property_details

# Get property listings
api_key = "your_scrapeak_api_key"  # Get your API key at: https://www.scrapeak.com/zillow-scraper/?ref=ariel
url = "https://www.zillow.com/toledo-oh/?searchQueryState=..."
listings = get_zillow_listings(api_key, url, batch_size=2)

# Get detailed property information
zpids = [prop['zpid'] for prop in listings['properties']]
details = get_property_details(api_key, zpids, batch_size=2, clean_data=True)
```

## 🔑 Get Your API Key

This package requires a Scrapeak API key for Zillow data access. Get yours here:

** [Get Scrapeak API Key](https://www.scrapeak.com/zillow-scraper/?ref=ariel)**

- Free tier available
- No credit card required
- Instant activation

## Package Structure

```
techinrealestate/
├── scrapeak/           # Scrapeak API services
│   └── zillow/        # Zillow data collection
│       ├── listings.py
│       └── property_details.py
└── README.md
```

## Installation

### From PyPI (Recommended)

```bash
pip install techinrealestate
```

### From Source (Development)

```bash
# Note: Source code is private
# Contact the maintainer for access to development version
pip install techinrealestate
```

### Development Installation

```bash
# For contributors with access to private repository
git clone https://github.com/analyticsariel/techinrealestate-package.git
cd techinrealestate-package
pip install -e ".[dev]"
```

## Quick Start

### Zillow Listings

```python
from techinrealestate.scrapeak import get_zillow_listings, get_listings_summary

api_key = "your_scrapeak_api_key"
url = "https://www.zillow.com/toledo-oh/?searchQueryState=..."

listings = get_zillow_listings(
    api_key=api_key,
    listing_url=url,
    all_properties_flag=True,  # Get all pages
    clean_data=True,          # Clean the data
    enable_logging=True       # Show progress
)

summary = get_listings_summary(listings)
print(f"Retrieved {summary['pagination']['properties_retrieved']} properties")
```

### Property Details

```python
from techinrealestate.scrapeak import get_property_details, get_property_details_summary

# Single property
details = get_property_details(api_key, "45099121", clean_data=True)

# Multiple properties
zpids = ["45099121", "34648268", "121349556"]
details = get_property_details(api_key, zpids, clean_data=True, enable_logging=True)

summary = get_property_details_summary(details)
print(f"Success rate: {summary['summary']['success_rate']}")
```

## Features

### Listings Module
- **Pagination Support**: Fetch all pages or just the first page
- **Batch Processing**: Concurrent requests with rate limiting
- **Data Cleaning**: Extract essential fields from raw API responses
- **Progress Logging**: Optional progress tracking for large datasets

### Property Details Module
- **Single/Multiple Properties**: Handle one or many ZPIDs
- **Comprehensive Data**: 61+ fields including zoning, photos, descriptions
- **Batch Processing**: Efficient concurrent processing
- **Data Cleaning**: Structured, clean data output

## Data Fields

The package extracts 61+ essential fields organized into categories:

- **Basic Identification** (7 fields): ZPID, address, coordinates
- **Pricing & Financial** (11 fields): Price, estimates, taxes
- **Property Specifications** (13 fields): Beds, baths, size, year built
- **Features & Amenities** (10 fields): Heating, cooling, appliances
- **Location & Zoning** (4 fields): Zoning, neighborhood
- **Schools** (6 fields): Elementary, middle, high school info
- **Property Description & Media** (3 fields): Description, photos
- **Listing & Agent Info** (7 fields): Agent, broker, listing terms

## API Services

### Scrapeak
- **Zillow Listings**: Property search results
- **Zillow Property Details**: Detailed property information

## Future Expansion

The package structure supports easy addition of:
- Other API services (e.g., `techinrealestate/another_api/`)
- Other platforms (e.g., `techinrealestate/scrapeak/redfin/`)
- Additional data sources

## Requirements

- Python 3.7+
- **Scrapeak API key** for Zillow data access ([Get yours here](https://www.scrapeak.com/zillow-scraper/?ref=ariel))
- requests
- concurrent.futures

## Contributing

This is a private package. For contributions, feature requests, or bug reports:

1. Open an issue on the [GitHub Issues](https://github.com/analyticsariel/techinrealestate-package/issues) page
2. Contact the maintainer for access to the private repository
3. For major changes, please discuss your ideas first

**Note**: Source code is private. Only the maintainer can accept contributions directly.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [PyPI Package](https://pypi.org/project/techinrealestate/)
- **Issues**: [GitHub Issues](https://github.com/analyticsariel/techinrealestate-package/issues)
- **Email**: your-email@example.com

## Changelog

### v1.0.0 (2024-01-XX)
- Initial release
- Zillow listings collection via Scrapeak API
- Property details collection with 61+ fields
- Batch processing with rate limiting
- Data cleaning and structured output
- Comprehensive documentation

## Acknowledgments

- [Scrapeak](https://app.scrapeak.com/) for providing the API service
- [Zillow](https://www.zillow.com/) for the data source
- The Python community for excellent libraries and tools
