import re
from difflib import get_close_matches


def _normalize_address(text: str) -> str:
    text = text.lower().strip()
    text = text.replace("street", "st")
    text = text.replace("avenue", "ave")
    text = text.replace("road", "rd")
    text = text.replace("drive", "dr")
    text = text.replace("boulevard", "blvd")
    text = text.replace("court", "ct")
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _match_against_listings(
    address_query: str,
    listings: list[dict],
    cutoff: float = 0.72,
) -> dict:
    if not address_query or not listings:
        return {"status": "none", "listing": None}

    normalized_query = _normalize_address(address_query)

    normalized_map = {}

    for listing in listings:
        address = listing.get("address_name", "")

        if address:
            normalized_map[_normalize_address(address)] = listing

    if normalized_query in normalized_map:
        return {
            "status": "exact",
            "listing": normalized_map[normalized_query],
        }

    candidates = get_close_matches(
        normalized_query,
        list(normalized_map.keys()),
        n=1,
        cutoff=cutoff,
    )

    if candidates:
        return {
            "status": "candidate",
            "listing": normalized_map[candidates[0]],
        }

    return {"status": "none", "listing": None}


def find_listing_for_booking_service(
    address_query: str,
    latest_listings: list[dict],
    cutoff: float = 0.72,
) -> dict:
    """
    Match a booking address against the listings most recently returned
    by query_listings(filters).

    Returns:
    {
        "status": "exact" | "candidate" | "none",
        "listing": dict | None,
        "source": "latest_listings" | None
    }
    """
    match = _match_against_listings(
        address_query=address_query,
        listings=latest_listings,
        cutoff=cutoff,
    )

    if match["status"] in {"exact", "candidate"} and match["listing"] is not None:
        return {
            "status": match["status"],
            "listing": match["listing"],
            "source": "latest_listings",
        }

    return {
        "status": "none",
        "listing": None,
        "source": None,
    }