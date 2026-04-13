import http.client
import json

API_HOST = "redfin-canada.p.rapidapi.com"
API_KEY = "190a6ed5b8mshbe58323ae965f75p10774djsnde2c1a93eb6b"


def get_region_ids(city_name):
    """Return a list of (name, region_id) tuples for the given city."""
    conn = http.client.HTTPSConnection(API_HOST)
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": API_HOST,
    }

    path = f"/properties/auto-complete?query={city_name}"
    conn.request("GET", path, headers=headers)

    res = conn.getresponse()
    data = res.read()
    parsed = json.loads(data.decode("utf-8"))

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
