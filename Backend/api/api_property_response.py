import http.client
import json
import os

API_HOST = "redfin-canada.p.rapidapi.com"
API_KEY = os.getenv("REDFIN_KEY")

if not API_KEY:
    raise RuntimeError("Missing RAPIDAPI_KEY in .env")

def fetch_properties_for_region(region_id, output_dir):
    """Fetch sale listings for a region and save the raw JSON to output_dir."""
    conn = http.client.HTTPSConnection(API_HOST)
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": API_HOST,
    }

    conn.request("GET", f"/properties/search-sale?regionId={region_id}", headers=headers)

    res = conn.getresponse()
    data = res.read()
    parsed = json.loads(data.decode("utf-8"))

    print(json.dumps(parsed, indent=4))

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "raw.json")
    with open(output_path, "w") as f:
        json.dump(parsed, f, indent=4)

    print(f"Saved to {output_path}")
    return output_path


if __name__ == "__main__":
    # Default standalone run for Ottawa
    output = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "Ottawa"))
    fetch_properties_for_region("33_2187", output)
