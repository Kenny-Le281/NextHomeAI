import json
from pathlib import Path

# --- configuration --------------------------------------------------------
# Base dir is two levels up from this file (project root)
BASE_DIR = Path(__file__).resolve().parents[2]

# Default paths (used when running standalone)
API_INPUT_PATH = BASE_DIR / "Ottawa" / "raw.json"
OUTPUT_PATH = BASE_DIR / "Ottawa" / "selected.json"

# list of (parent‑path, field‑name) tuples to keep.
# the parent path can be a dot‑separated string for nested values.
# you can also build custom extraction logic below.
FIELDS_TO_KEEP = [
    ("homeData.propertyId", "propertyId"),
    ("homeData.addressInfo.formattedStreetLine", "address-name"),
    ("homeData.addressInfo.city", "city"),
    ("homeData.addressInfo.state", "state"),
    ("homeData.addressInfo.zip", "zip"),
    ("homeData.addressInfo.location", "location"),
    ("homeData.listingId", "listingId"),
    ("homeData.url",        "url"),
    ("homeData.propertyType", "propertyType"),
    ("homeData.beds", "beds"),
    ("homeData.baths", "baths"),
    ("homeData.priceInfo.amount", "price"),
    ("homeData.priceInfo.daysOnMarket", "daysOnMarket"),
    ("homeData.priceInfo.timeOnRedfin", "timeOnRedfin"),
    ("homeData.priceInfo.listingAddedDate", "listingAddedDate"),
    ("homeData.hoaDues.amount", "hoa-amount"),
    ("homeData.brokers", "brokers"),
    ("homeData.lastSaleData.lastSoldDate", "lastSoldDate"),
    ("homeData.bathInfo.computedPartialBaths", "partialBaths"),
    ("homeData.bathInfo.computedFullBaths", "fullBaths"),
    ("homeData.bathInfo.computedTotalBaths", "totalBaths"),
    ("homeData.addressInfo.centroid.centroid.latitude", "latitude"),
    ("homeData.addressInfo.centroid.centroid.longitude", "longitude")
]

# --- helpers --------------------------------------------------------------
def pick_field(record: dict, path: str):
    """Get a nested value by dot‑path; returns None if any step is missing."""
    cur = record
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur

def select_fields(raw: dict):
    """Return a new dict containing only the configured fields."""
    out = {}
    for src_path, dest_key in FIELDS_TO_KEEP:
        out[dest_key] = pick_field(raw, src_path)
    out["parsed_image_urls"] = build_photo_urls(raw.get("homeData", {}))
    return out


def build_photo_urls(home_data: dict) -> list[str]:
    """Build Redfin CDN photo URLs from metadata in the search API response."""
    mls_id = home_data.get("mlsId")
    data_source_id = home_data.get("dataSourceId")
    photo_ranges = (home_data.get("photosInfo") or {}).get("photoRanges") or []

    if not mls_id or data_source_id is None or not photo_ranges:
        return []

    shard = str(mls_id)[-3:]
    base_url = (
        f"https://ssl.cdn-redfin.com/photo/{data_source_id}/"
        f"bigphoto/{shard}/{mls_id}"
    )
    urls = []

    for photo_range in photo_ranges:
        try:
            start = int(photo_range["startPos"])
            end = int(photo_range["endPos"])
            version = str(photo_range["version"])
        except (KeyError, TypeError, ValueError):
            continue

        for position in range(start, end + 1):
            suffix = f"_{version}" if position == 0 else f"_{position}_{version}"
            urls.append(f"{base_url}{suffix}.jpg")

    return list(dict.fromkeys(urls))

# --- main pipeline --------------------------------------------------------
def build_selected_json(input_path: Path, output_path: Path):
    with input_path.open() as f:
        data = json.load(f)

    output = []
    for entry in data.get("data", []):
        selected = select_fields(entry)
        # optionally keep the original entry or merge, e.g.
        # selected["raw"] = entry
        output.append(selected)

    with output_path.open("w") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    build_selected_json(API_INPUT_PATH, OUTPUT_PATH)
    print(f"wrote {OUTPUT_PATH}")
