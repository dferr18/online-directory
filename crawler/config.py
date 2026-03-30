"""
Configuration for the Online Directory Project crawler.
"""

import os

# Google Places API key — set via environment variable
API_KEY = os.environ.get("GOOGLE_PLACES_API_KEY", "")

# Suburbs to crawl (name, state, country for precise geocoding)
SUBURBS = [
    {"name": "Capalaba", "state": "QLD", "country": "AU", "slug": "capalaba"},
    {"name": "Manly West", "state": "QLD", "country": "AU", "slug": "manly-west"},
    {"name": "Mt Gravatt", "state": "QLD", "country": "AU", "slug": "mt-gravatt"},
]

# Business categories to search for in each suburb
# Maps display name -> Google Places type(s)
CATEGORIES = {
    "Painters": ["painter"],
    "Hairdressers & Barbers": ["hair_salon", "barber_shop"],
    "Plumbers": ["plumber"],
    "Electricians": ["electrician"],
    "Mechanics": ["car_repair"],
    "Restaurants": ["restaurant"],
    "Cafes": ["cafe"],
    "Dentists": ["dentist"],
    "Doctors & GPs": ["doctor"],
    "Vets": ["veterinary_care"],
    "Real Estate Agents": ["real_estate_agency"],
    "Accountants": ["accounting"],
    "Lawyers": ["lawyer"],
    "Gyms & Fitness": ["gym"],
    "Pet Shops": ["pet_store"],
    "Florists": ["florist"],
    "Bakeries": ["bakery"],
    "Fish & Chip Shops": ["meal_takeaway"],
    "Pizza Shops": ["meal_delivery"],
    "Chemists & Pharmacies": ["pharmacy"],
}

# Search radius in meters from suburb centre
SEARCH_RADIUS = 3000

# Output paths
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
EXCEL_DIR = os.path.join(DATA_DIR, "excel")
JSON_DIR = os.path.join(DATA_DIR, "json")
