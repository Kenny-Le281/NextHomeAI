import re
from difflib import get_close_matches

from tools.query_listings_tool import query_listing_by_address


def _normalize_address(text: str) -> str:
    text = text.lower().strip()
    text = text.replace("street", "st")
    text = text.replace("avenue", "ave")
    text = text.replace("road", "rd")
    text = text.replace("drive", "dr")
    text = text.replace("boulevard", "blvd")
    text = text.replace("court", "ct")
    text = text.replace("crescent", "cres")
    text = text.replace("terrace", "terr")
    text = text.replace("lane", "ln")
    text = text.replace("place", "pl")
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _match_against_listings(
    address_query: str,
    listings: list[dict] | None,
    cutoff: float = 0.72,
) -> dict:
    if not address_query or not address_query.strip():
        return {
            "status": "none",
            "listing": None,
        }

    if not listings:
        return {
            "status": "none",
            "listing": None,
        }

    normalized_query = _normalize_address(address_query)

    normalized_map = {}

    for listing in listings:
        address = listing.get("address_name", "")

        if not address:
            continue

        normalized_address = _normalize_address(address)
        normalized_map[normalized_address] = listing

    if not normalized_map:
        return {
            "status": "none",
            "listing": None,
        }

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

    return {
        "status": "none",
        "listing": None,
    }


def find_listing_for_booking_service(
    address_query: str,
    latest_listings: list[dict] | None,
    cutoff: float = 0.72,
) -> dict:
    """
    Booking lookup strategy:

    1. Try matching against latest_listings first.
    2. If no match is found, query the database by address.
    3. Match against the database candidates.

    Returns:
    {
        "status": "exact" | "candidate" | "none",
        "listing": dict | None,
        "source": "latest_listings" | "database" | None
    }
    """
    if not address_query or not address_query.strip():
        return {
            "status": "none",
            "listing": None,
            "source": None,
        }

    latest_match = _match_against_listings(
        address_query=address_query,
        listings=latest_listings,
        cutoff=cutoff,
    )

    if latest_match["status"] in {"exact", "candidate"} and latest_match["listing"] is not None:
        return {
            "status": latest_match["status"],
            "listing": latest_match["listing"],
            "source": "latest_listings",
        }

    db_candidates = query_listing_by_address(address_query)

    db_match = _match_against_listings(
        address_query=address_query,
        listings=db_candidates,
        cutoff=cutoff,
    )

    if db_match["status"] in {"exact", "candidate"} and db_match["listing"] is not None:
        return {
            "status": db_match["status"],
            "listing": db_match["listing"],
            "source": "database",
        }

    return {
        "status": "none",
        "listing": None,
        "source": None,
    }