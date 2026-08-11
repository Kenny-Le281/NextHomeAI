import http.client
import json
import os
from pathlib import Path

from dotenv import load_dotenv

API_HOST = "redfin-canada.p.rapidapi.com"
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

def fetch_properties_for_region(region_id, output_dir):
    """Fetch sale listings for a region and save the raw JSON to output_dir."""
    api_key = os.getenv("REDFIN_KEY")
    if not api_key:
        raise RuntimeError(
            "REDFIN_KEY is required to fetch Redfin listings from RapidAPI."
        )

    conn = http.client.HTTPSConnection(API_HOST)
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": API_HOST,
    }

    try:
        conn.request("GET", f"/properties/search-sale?regionId={region_id}", headers=headers)
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
