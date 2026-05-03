# This file initially calls fetch_html to get the HTML content of the page, then calls all the individual parsing functions to extract the relevant information.
# Finally it writes the enriched property records back to each selected.json file.

import json
from pathlib import Path

from fetch_html import fetch_html
from parse_description_from_html import parse_description_from_html
from parse_image_urls_from_html import parse_image_urls_from_html
from parse_parking_from_html import parse_parking_from_html
from parse_property_type_from_html import parse_property_type_from_html
from parse_property_details_from_html import parse_property_details_from_html
from parse_sqft_from_html import parse_sqft_from_html
# Missing Realtor info parsing for now, will add later when we have a better idea of the structure of the HTML and the data we want to extract from it.


BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_CITY_DIR = BASE_DIR / "Ottawa"
SELECTED_FILENAME = "selected.json"
BASE_URL = "https://www.redfin.ca"


def process_file(input_path: Path):
    with input_path.open("r", encoding="utf-8") as file:
        properties = json.load(file)

    total = len(properties)
    index = 0

    for property in properties:
        index += 1
        print(f"Processing property {index}/{total} (ID: {property.get('propertyId')})")

        url = property.get("url")
        if not url:
            print("No URL found for property, skipping.")
            continue

        full_url = BASE_URL + url
        html_content = fetch_html(full_url)

        property["parsed_description"] = parse_description_from_html(html_content)
        property["parsed_image_urls"] = parse_image_urls_from_html(html_content)
        property["parsed_parking"] = parse_parking_from_html(html_content)
        property["parsed_property_type"] = parse_property_type_from_html(html_content)
        property["parsed_property_details"] = parse_property_details_from_html(html_content)
        property["parsed_sqft"] = parse_sqft_from_html(html_content)

    with input_path.open("w", encoding="utf-8") as file:
        json.dump(properties, file, indent=2)

    print(f"Updated {input_path} with parsed data.")


def main(input_path: Path | str = DEFAULT_CITY_DIR):
    input_path = Path(input_path)

    if input_path.is_file():
        print(f"Running web scraper on single file: {input_path}")
        process_file(input_path)
        return

    if not input_path.is_dir():
        raise ValueError(f"Input path must be a file or directory: {input_path}")

    selected_files = []
    for child in sorted(input_path.iterdir()):
        selected_path = child / SELECTED_FILENAME
        if child.is_dir() and selected_path.exists():
            selected_files.append(selected_path)

    if not selected_files:
        print(f"No '{SELECTED_FILENAME}' files found under {input_path}")
        return

    for selected_path in selected_files:
        print(f"\n=== Processing region file: {selected_path} ===")
        process_file(selected_path)


if __name__ == "__main__":
    main()

    