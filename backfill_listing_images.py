"""Backfill listing image URLs from existing RapidAPI raw response files."""

import argparse
import json
import sys
import time
from pathlib import Path
from urllib.parse import urlsplit

from Backend.api.consolidation import build_photo_urls
from load_listings import get_connection


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_CITY_DIR = PROJECT_ROOT / "Ottawa"
SCRAPER_DIR = PROJECT_ROOT / "Backend" / "web-scraping"
sys.path.insert(0, str(SCRAPER_DIR))

from fetch_html import fetch_html
from parse_image_urls_from_html import parse_image_urls_from_html


def collect_listing_images(city_dir: Path) -> dict[str, list[str]]:
    listings = {}

    for raw_path in city_dir.rglob("raw.json"):
        with raw_path.open("r", encoding="utf-8") as file:
            response = json.load(file)

        for entry in response.get("data", []):
            home_data = entry.get("homeData") or {}
            listing_id = home_data.get("listingId")
            image_urls = build_photo_urls(home_data)
            if listing_id and image_urls:
                listings[str(listing_id)] = image_urls

    return listings


def backfill(city_dir: Path, apply_changes: bool = False) -> tuple[int, int]:
    listings = collect_listing_images(city_dir)
    if not apply_changes:
        return len(listings), 0

    connection = get_connection()
    updated = 0

    try:
        with connection:
            with connection.cursor() as cursor:
                for listing_id, image_urls in listings.items():
                    cursor.execute(
                        """
                        UPDATE listings
                        SET image_urls = %s, last_updated = NOW()
                        WHERE listing_id = %s
                        """,
                        (json.dumps(image_urls), listing_id),
                    )
                    updated += cursor.rowcount
    finally:
        connection.close()

    return len(listings), updated


def _property_page_url(listing_url: str) -> str | None:
    if listing_url.startswith("/"):
        return f"https://www.redfin.ca{listing_url}"

    parsed = urlsplit(listing_url)
    if parsed.scheme == "https" and parsed.hostname in {"redfin.ca", "www.redfin.ca"}:
        return listing_url

    return None


def scrape_missing_images(delay_seconds: float = 0.2) -> tuple[int, int, int]:
    """Backfill still-missing rows from each listing's structured page metadata."""
    connection = get_connection()
    updated = 0
    failed = 0

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT listing_id, url
                FROM listings
                WHERE (image_urls IS NULL OR image_urls = '[]'::jsonb)
                  AND url IS NOT NULL
                ORDER BY listing_id
                """
            )
            missing_listings = [(str(row[0]), row[1]) for row in cursor.fetchall()]

        with connection.cursor() as cursor:
            for index, (listing_id, listing_url) in enumerate(missing_listings, 1):
                full_url = _property_page_url(listing_url)
                if not full_url:
                    failed += 1
                    continue

                try:
                    image_urls = parse_image_urls_from_html(fetch_html(full_url))
                except Exception:
                    failed += 1
                    continue

                if image_urls:
                    cursor.execute(
                        """
                        UPDATE listings
                        SET image_urls = %s, last_updated = NOW()
                        WHERE listing_id = %s
                        """,
                        (json.dumps(image_urls), listing_id),
                    )
                    updated += cursor.rowcount

                if index % 25 == 0:
                    connection.commit()
                    print(f"Checked {index}/{len(missing_listings)} missing listings...")

                time.sleep(delay_seconds)

        connection.commit()
    finally:
        connection.close()

    return len(missing_listings), updated, failed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--city-dir", type=Path, default=DEFAULT_CITY_DIR)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Update matching database rows. Without this flag, only preview counts.",
    )
    parser.add_argument(
        "--scrape-missing",
        action="store_true",
        help="Also backfill missing rows from Redfin's structured page metadata.",
    )
    args = parser.parse_args()

    discovered, updated = backfill(args.city_dir, apply_changes=args.apply)
    print(f"Listings with API photo metadata: {discovered}")
    if args.apply:
        print(f"Database rows updated: {updated}")
        if args.scrape_missing:
            checked, scraped_updates, failed = scrape_missing_images()
            print(f"Missing-image listing pages checked: {checked}")
            print(f"Additional database rows updated: {scraped_updates}")
            print(f"Pages that could not be read: {failed}")
    else:
        print("Preview only; rerun with --apply to update the database.")


if __name__ == "__main__":
    main()
