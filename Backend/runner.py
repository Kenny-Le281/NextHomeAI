"""Run the full pipeline for each region returned by the auto-complete API:
1) Fetch region IDs for a city
2) For each region: fetch sale listings, consolidate fields, run web scraper
"""

import sys
from pathlib import Path

# Make sure we can import from sibling directories
repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))
sys.path.insert(0, str(repo_root / "Backend" / "web-scraping"))

from Get_Region_Ids_helper import get_region_ids_for_runner
from Backend.API.api_property_response import fetch_properties_for_region
from Backend.API.consolidation import build_selected_json
from web_scraper import main as run_web_scraper
from load_listings import load_from_file as load_listings, get_connection


def sanitize_name(name):
    """Turn a region name into a safe folder name."""
    return name.replace(",", "").replace(" ", "_").strip()


def main():
    city = "Ottawa"
    print(f"\n=== Fetching region IDs for '{city}' ===")
    regions = get_region_ids_for_runner(city)

    if not regions:
        print("No regions found. Exiting.")
        return

    city_dir = repo_root / city

    db_conn = get_connection()
    db_conn.autocommit = True

    for name, region_id in regions:
        folder_name = sanitize_name(name)
        output_dir = city_dir / folder_name
        print(f"\n--- Processing: {name} (region_id={region_id}) ---")

        # Step 1: Fetch raw listings
        fetch_properties_for_region(region_id, str(output_dir))

        # Step 2: Consolidate / select fields
        raw_path = output_dir / "raw.json"
        selected_path = output_dir / "selected.json"
        build_selected_json(raw_path, selected_path)
        print(f"Consolidated → {selected_path}")

        # Step 3: Web scrape additional details
        print(f"Running web scraper for {name}...")
        run_web_scraper(input_path=selected_path, output_path=selected_path)

        # Step 4: Load into Supabase
        print(f"Loading listings into Supabase for {name}...")
        load_listings(selected_path, conn=db_conn)

    db_conn.close()
    print("\n=== Done ===")


if __name__ == "__main__":
    main()
