#!/usr/bin/env python3
"""
Online Directory Project — Static Site Builder

Reads data/json/directory.json and generates static HTML pages
in the site/ directory, ready for GitHub Pages deployment.
"""

import json
import os
import shutil

from jinja2 import Environment, FileSystemLoader

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "json", "directory.json")
SITE_DIR = os.path.join(BASE_DIR, "docs")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")


def load_data():
    """Load the directory JSON data."""
    if not os.path.exists(DATA_FILE):
        print(f"ERROR: Data file not found: {DATA_FILE}")
        print("Run the crawler first: cd crawler && python crawler.py")
        # For development/testing, return sample data
        return generate_sample_data()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_sample_data():
    """Generate sample data for development/testing."""
    print("Generating sample data for development...")
    return {
        "generated": "2026-03-30 12:00:00 (SAMPLE DATA)",
        "suburbs": [
            {
                "name": "Capalaba",
                "state": "QLD",
                "slug": "capalaba",
                "categories": {
                    "Hairdressers & Barbers": [
                        {
                            "name": "Capalaba Cuts",
                            "address": "12 Redland Bay Rd, Capalaba QLD 4157",
                            "phone": "(07) 3245 1234",
                            "website": "https://example.com",
                            "hours": "Mon-Fri: 9am-5pm | Sat: 9am-1pm",
                            "rating": 4.5,
                            "total_reviews": 87,
                            "status": "OPERATIONAL",
                            "google_maps_url": "https://maps.google.com",
                        },
                        {
                            "name": "The Barber House",
                            "address": "5/38 Moreton Bay Rd, Capalaba QLD 4157",
                            "phone": "(07) 3823 5678",
                            "website": "N/A",
                            "hours": "Mon-Sat: 8am-6pm",
                            "rating": 4.8,
                            "total_reviews": 124,
                            "status": "OPERATIONAL",
                            "google_maps_url": "https://maps.google.com",
                        },
                    ],
                    "Plumbers": [
                        {
                            "name": "Redlands Plumbing Co",
                            "address": "Unit 3, 20 Industrial Ave, Capalaba QLD 4157",
                            "phone": "(07) 3390 9876",
                            "website": "https://example.com",
                            "hours": "Mon-Fri: 7am-5pm",
                            "rating": 4.2,
                            "total_reviews": 56,
                            "status": "OPERATIONAL",
                            "google_maps_url": "https://maps.google.com",
                        },
                    ],
                    "Cafes": [
                        {
                            "name": "Bean There Cafe",
                            "address": "1 Mt Cotton Rd, Capalaba QLD 4157",
                            "phone": "(07) 3245 0000",
                            "website": "https://example.com",
                            "hours": "Daily: 6am-3pm",
                            "rating": 4.6,
                            "total_reviews": 210,
                            "status": "OPERATIONAL",
                            "google_maps_url": "https://maps.google.com",
                        },
                    ],
                    "Restaurants": [
                        {
                            "name": "Capalaba Thai",
                            "address": "45 Old Cleveland Rd, Capalaba QLD 4157",
                            "phone": "(07) 3823 1111",
                            "website": "N/A",
                            "hours": "Tue-Sun: 11am-9pm",
                            "rating": 4.3,
                            "total_reviews": 178,
                            "status": "OPERATIONAL",
                            "google_maps_url": "https://maps.google.com",
                        },
                    ],
                    "Electricians": [
                        {
                            "name": "Bayside Electrical Services",
                            "address": "8 Commerce St, Capalaba QLD 4157",
                            "phone": "(07) 3245 7777",
                            "website": "https://example.com",
                            "hours": "Mon-Fri: 7am-4pm",
                            "rating": 4.7,
                            "total_reviews": 93,
                            "status": "OPERATIONAL",
                            "google_maps_url": "https://maps.google.com",
                        },
                    ],
                },
            },
            {
                "name": "Manly West",
                "state": "QLD",
                "slug": "manly-west",
                "categories": {
                    "Restaurants": [
                        {
                            "name": "Manly West Sushi",
                            "address": "2/15 Manly Rd, Manly West QLD 4179",
                            "phone": "(07) 3396 2222",
                            "website": "https://example.com",
                            "hours": "Mon-Sat: 11am-8:30pm",
                            "rating": 4.4,
                            "total_reviews": 145,
                            "status": "OPERATIONAL",
                            "google_maps_url": "https://maps.google.com",
                        },
                    ],
                    "Mechanics": [
                        {
                            "name": "Wynnum Road Auto",
                            "address": "88 Wynnum Rd, Manly West QLD 4179",
                            "phone": "(07) 3893 3333",
                            "website": "https://example.com",
                            "hours": "Mon-Fri: 7:30am-5pm",
                            "rating": 4.6,
                            "total_reviews": 201,
                            "status": "OPERATIONAL",
                            "google_maps_url": "https://maps.google.com",
                        },
                    ],
                    "Chemists & Pharmacies": [
                        {
                            "name": "Manly West Pharmacy",
                            "address": "Manly West Shopping Village, QLD 4179",
                            "phone": "(07) 3396 4444",
                            "website": "N/A",
                            "hours": "Mon-Fri: 8am-6pm | Sat: 8am-1pm",
                            "rating": 4.1,
                            "total_reviews": 67,
                            "status": "OPERATIONAL",
                            "google_maps_url": "https://maps.google.com",
                        },
                    ],
                    "Hairdressers & Barbers": [
                        {
                            "name": "Bayside Hair Studio",
                            "address": "12 Manly Rd, Manly West QLD 4179",
                            "phone": "(07) 3396 5555",
                            "website": "https://example.com",
                            "hours": "Tue-Sat: 9am-5pm",
                            "rating": 4.9,
                            "total_reviews": 88,
                            "status": "OPERATIONAL",
                            "google_maps_url": "https://maps.google.com",
                        },
                    ],
                },
            },
            {
                "name": "Mt Gravatt",
                "state": "QLD",
                "slug": "mt-gravatt",
                "categories": {
                    "Dentists": [
                        {
                            "name": "Mt Gravatt Dental",
                            "address": "1/55 Creek Rd, Mt Gravatt QLD 4122",
                            "phone": "(07) 3349 6666",
                            "website": "https://example.com",
                            "hours": "Mon-Fri: 8am-5pm | Sat: 8am-12pm",
                            "rating": 4.7,
                            "total_reviews": 312,
                            "status": "OPERATIONAL",
                            "google_maps_url": "https://maps.google.com",
                        },
                    ],
                    "Gyms & Fitness": [
                        {
                            "name": "Anytime Fitness Mt Gravatt",
                            "address": "Garden City Shopping Centre, Mt Gravatt QLD 4122",
                            "phone": "(07) 3849 7777",
                            "website": "https://example.com",
                            "hours": "Open 24 hours",
                            "rating": 4.3,
                            "total_reviews": 189,
                            "status": "OPERATIONAL",
                            "google_maps_url": "https://maps.google.com",
                        },
                    ],
                    "Real Estate Agents": [
                        {
                            "name": "Ray White Mt Gravatt",
                            "address": "1440 Logan Rd, Mt Gravatt QLD 4122",
                            "phone": "(07) 3219 8888",
                            "website": "https://example.com",
                            "hours": "Mon-Fri: 8:30am-5pm | Sat: 9am-12pm",
                            "rating": 4.5,
                            "total_reviews": 76,
                            "status": "OPERATIONAL",
                            "google_maps_url": "https://maps.google.com",
                        },
                    ],
                    "Bakeries": [
                        {
                            "name": "Bakers Delight Mt Gravatt",
                            "address": "Garden City, Mt Gravatt QLD 4122",
                            "phone": "(07) 3849 9999",
                            "website": "https://example.com",
                            "hours": "Mon-Sun: 7am-6pm",
                            "rating": 4.4,
                            "total_reviews": 95,
                            "status": "OPERATIONAL",
                            "google_maps_url": "https://maps.google.com",
                        },
                    ],
                    "Cafes": [
                        {
                            "name": "Grind & Brew",
                            "address": "22 Logan Rd, Mt Gravatt QLD 4122",
                            "phone": "(07) 3349 0101",
                            "website": "N/A",
                            "hours": "Mon-Fri: 5:30am-2pm | Sat-Sun: 6am-1pm",
                            "rating": 4.8,
                            "total_reviews": 267,
                            "status": "OPERATIONAL",
                            "google_maps_url": "https://maps.google.com",
                        },
                    ],
                },
            },
        ],
    }


def build_site(data):
    """Generate the static site from templates and data."""
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

    suburbs = data.get("suburbs", [])
    generated_date = data.get("generated", "Unknown")

    # Build stats for landing page
    total_businesses = sum(
        len(biz)
        for suburb in suburbs
        for biz in suburb["categories"].values()
    )
    total_categories = len(
        set(cat for suburb in suburbs for cat in suburb["categories"].keys())
    )

    # --- Generate index.html ---
    template = env.get_template("index.html")
    html = template.render(
        suburbs=suburbs,
        generated=generated_date,
        total_businesses=total_businesses,
        total_categories=total_categories,
    )
    write_file(os.path.join(SITE_DIR, "index.html"), html)

    # --- Generate suburb pages ---
    template = env.get_template("suburb.html")
    os.makedirs(os.path.join(SITE_DIR, "suburb"), exist_ok=True)
    for suburb in suburbs:
        html = template.render(
            suburb=suburb,
            suburbs=suburbs,
            generated=generated_date,
        )
        write_file(os.path.join(SITE_DIR, "suburb", f"{suburb['slug']}.html"), html)

    # --- Copy data JSON for client-side search ---
    os.makedirs(os.path.join(SITE_DIR, "data"), exist_ok=True)
    data_dest = os.path.join(SITE_DIR, "data", "directory.json")
    with open(data_dest, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

    # --- Copy static assets ---
    assets_src = os.path.join(BASE_DIR, "site", "assets")
    # Assets are written directly to site/assets by this script, no copy needed

    # --- Write CNAME ---
    write_file(os.path.join(SITE_DIR, "CNAME"), "directory.skylostudios.com")

    print(f"\nSite built successfully!")
    print(f"  Pages: index.html + {len(suburbs)} suburb pages")
    print(f"  Businesses: {total_businesses}")
    print(f"  Output: {SITE_DIR}/")


def write_file(path, content):
    """Write content to a file, creating directories as needed."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  Generated: {os.path.relpath(path, BASE_DIR)}")


def main():
    print("Online Directory Project — Site Builder")
    print("=" * 40)

    data = load_data()
    build_site(data)


if __name__ == "__main__":
    main()
