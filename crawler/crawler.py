#!/usr/bin/env python3
"""
Online Directory Project — Google Places API (New) Crawler

Crawls Google Places API (New) for businesses in configured suburbs,
outputs Excel spreadsheets (per suburb) and a master JSON file.

Uses the Places (New) API endpoints:
  - searchNearby (POST)
  - places/{id} (GET)
"""

import json
import os
import sys
import time

import requests
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill

from config import API_KEY, SUBURBS, CATEGORIES, SEARCH_RADIUS, EXCEL_DIR, JSON_DIR

API_BASE = "https://places.googleapis.com/v1"


def check_api_key():
    """Verify the API key is set."""
    if not API_KEY:
        print("ERROR: GOOGLE_PLACES_API_KEY environment variable not set.")
        print("  export GOOGLE_PLACES_API_KEY='your-api-key-here'")
        sys.exit(1)
    print(f"API key loaded: {API_KEY[:8]}...{API_KEY[-4:]}")


def geocode_suburb(suburb):
    """Get the lat/lng centre of a suburb using searchText."""
    url = f"{API_BASE}/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": "places.location,places.displayName",
    }
    body = {
        "textQuery": f"{suburb['name']}, {suburb['state']}, {suburb['country']}",
        "maxResultCount": 1,
    }

    resp = requests.post(url, headers=headers, json=body)
    if resp.status_code != 200:
        print(f"  WARNING: Geocode failed for {suburb['name']}: {resp.status_code} {resp.text}")
        return None

    data = resp.json()
    places = data.get("places", [])
    if not places:
        print(f"  WARNING: No geocode results for {suburb['name']}")
        return None

    location = places[0]["location"]
    print(f"  Geocoded {suburb['name']}: {location['latitude']}, {location['longitude']}")
    return location


def search_nearby(location, place_types, radius):
    """Search for businesses near a location using Places (New) searchNearby."""
    url = f"{API_BASE}/places:searchNearby"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": (
            "places.id,places.displayName,places.formattedAddress,"
            "places.nationalPhoneNumber,places.websiteUri,"
            "places.currentOpeningHours,places.rating,"
            "places.userRatingCount,places.businessStatus,"
            "places.googleMapsUri,places.regularOpeningHours"
        ),
    }
    body = {
        "includedTypes": place_types,
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": location["latitude"],
                    "longitude": location["longitude"],
                },
                "radius": radius,
            }
        },
        "maxResultCount": 20,
    }

    all_places = []
    resp = requests.post(url, headers=headers, json=body)

    if resp.status_code != 200:
        print(f"    API error: {resp.status_code} {resp.text[:200]}")
        return []

    data = resp.json()
    all_places.extend(data.get("places", []))

    # Deduplicate by place id
    seen = set()
    unique = []
    for p in all_places:
        pid = p.get("id", "")
        if pid not in seen:
            seen.add(pid)
            unique.append(p)

    return unique


def format_hours(place):
    """Extract and format opening hours from a place."""
    hours = place.get("regularOpeningHours") or place.get("currentOpeningHours")
    if not hours:
        return "Hours not available"
    weekday_descriptions = hours.get("weekdayDescriptions", [])
    if weekday_descriptions:
        return " | ".join(weekday_descriptions)
    return "Hours not available"


def parse_place(place):
    """Convert a Places (New) API result into our standard business format."""
    display_name = place.get("displayName", {})
    name = display_name.get("text", "Unknown") if isinstance(display_name, dict) else str(display_name)

    return {
        "name": name,
        "address": place.get("formattedAddress", "N/A"),
        "phone": place.get("nationalPhoneNumber", "N/A"),
        "website": place.get("websiteUri", "N/A"),
        "hours": format_hours(place),
        "rating": place.get("rating", "N/A"),
        "total_reviews": place.get("userRatingCount", 0),
        "status": place.get("businessStatus", "OPERATIONAL"),
        "google_maps_url": place.get("googleMapsUri", "N/A"),
        "place_id": place.get("id", ""),
    }


def crawl_suburb(suburb):
    """Crawl all categories for a single suburb. Returns structured data."""
    print(f"\n{'='*60}")
    print(f"Crawling: {suburb['name']}, {suburb['state']}")
    print(f"{'='*60}")

    location = geocode_suburb(suburb)
    if not location:
        return None

    suburb_data = {
        "name": suburb["name"],
        "state": suburb["state"],
        "slug": suburb["slug"],
        "categories": {},
    }

    for category_name, category_types in CATEGORIES.items():
        print(f"\n  Searching: {category_name}...")
        places = search_nearby(location, category_types, SEARCH_RADIUS)
        print(f"    Found {len(places)} results")

        businesses = []
        for place in places:
            business = parse_place(place)
            businesses.append(business)
            print(f"    ✓ {business['name']}")

        # Only include categories that have results
        if businesses:
            # Sort by rating (highest first), put N/A at the end
            businesses.sort(
                key=lambda b: (b["rating"] if isinstance(b["rating"], (int, float)) else 0),
                reverse=True,
            )
            suburb_data["categories"][category_name] = businesses

        time.sleep(0.2)  # Be nice to the API

    return suburb_data


def save_excel(suburb_data):
    """Save suburb data to an Excel spreadsheet."""
    os.makedirs(EXCEL_DIR, exist_ok=True)
    filename = f"{suburb_data['slug'].replace('-', '_')}.xlsx"
    filepath = os.path.join(EXCEL_DIR, filename)

    wb = openpyxl.Workbook()
    wb.remove(wb.active)  # Remove default sheet

    header_font = Font(bold=True, size=12, color="FFFFFF")
    header_fill = PatternFill(start_color="2C3E50", end_color="2C3E50", fill_type="solid")
    header_align = Alignment(horizontal="center", vertical="center")

    for category_name, businesses in suburb_data["categories"].items():
        sheet_name = category_name[:31]
        ws = wb.create_sheet(title=sheet_name)

        headers = ["Name", "Address", "Phone", "Website", "Hours", "Rating", "Reviews", "Status", "Google Maps"]
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_align

        for row, biz in enumerate(businesses, 2):
            ws.cell(row=row, column=1, value=biz["name"])
            ws.cell(row=row, column=2, value=biz["address"])
            ws.cell(row=row, column=3, value=biz["phone"])
            ws.cell(row=row, column=4, value=biz["website"])
            ws.cell(row=row, column=5, value=biz["hours"])
            ws.cell(row=row, column=6, value=biz["rating"])
            ws.cell(row=row, column=7, value=biz["total_reviews"])
            ws.cell(row=row, column=8, value=biz["status"])
            ws.cell(row=row, column=9, value=biz["google_maps_url"])

        for col in ws.columns:
            max_len = max(len(str(cell.value or "")) for cell in col)
            ws.column_dimensions[col[0].column_letter].width = min(max_len + 2, 50)

    wb.save(filepath)
    print(f"\n  Saved Excel: {filepath}")


def save_json(all_data):
    """Save all suburb data to a master JSON file."""
    os.makedirs(JSON_DIR, exist_ok=True)
    filepath = os.path.join(JSON_DIR, "directory.json")

    output = {
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "suburbs": all_data,
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nSaved JSON: {filepath}")


def main():
    print("Online Directory Project — Crawler (Places API New)")
    print("=" * 50)

    check_api_key()
    all_data = []

    for suburb in SUBURBS:
        suburb_data = crawl_suburb(suburb)
        if suburb_data:
            save_excel(suburb_data)
            all_data.append(suburb_data)

    save_json(all_data)

    total_businesses = sum(
        len(biz)
        for suburb in all_data
        for biz in suburb["categories"].values()
    )
    print(f"\n{'='*50}")
    print(f"Done! Crawled {len(all_data)} suburbs, {total_businesses} total businesses.")
    print(f"Excel files: {EXCEL_DIR}/")
    print(f"JSON file:   {JSON_DIR}/directory.json")


if __name__ == "__main__":
    main()
