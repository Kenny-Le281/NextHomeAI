import http.client
import json
import os
from pathlib import Path

from dotenv import load_dotenv

API_HOST = "redfin-canada.p.rapidapi.com"
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def get_region_ids(city_name):
    """Return a list of (name, region_id) tuples for the given city."""
    api_key = os.getenv("REDFIN_KEY")
    if not api_key:
        raise RuntimeError(
            "REDFIN_KEY is required to retrieve Redfin region IDs from RapidAPI."
        )

    conn = http.client.HTTPSConnection(API_HOST)
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": API_HOST,
    }

    path = f"/properties/auto-complete?query={city_name}"
    try:
        conn.request("GET", path, headers=headers)
        res = conn.getresponse()
        data = res.read()
    finally:
        conn.close()

    response_text = data.decode("utf-8", errors="replace")
    if not 200 <= res.status < 300:
        raise RuntimeError(
            f"Redfin RapidAPI request failed with HTTP {res.status} {res.reason}: "
            f"{response_text[:1000]}"
        )

    try:
        parsed = json.loads(response_text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Redfin RapidAPI returned invalid JSON: {exc}. Response: {response_text[:1000]}"
        ) from exc

    if parsed.get("data") is None:
        print("\n❌ API returned no data.")
        return []

    places_section = None
    for section in parsed["data"]:
        if section.get("name") == "Places":
            places_section = section
            break

    if not places_section:
        print("\n❌ No 'Places' section found.")
        return []

    results = []
    for r in places_section["rows"]:
        name = r.get("name", "Unknown")
        region_id = r.get("id", "Unknown")
        results.append((name, region_id))

    return results


if __name__ == "__main__":
    regions = get_region_ids("Ottawa")
    print(f"\n=== Region IDs for 'Ottawa' ===\n")
    for name, rid in regions:
        print(f"{name} → {rid}")
