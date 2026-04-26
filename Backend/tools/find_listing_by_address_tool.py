from configs.supabase_client import supabase


def find_listing_by_address_tool(address_query: str, limit: int = 10) -> list[dict]:
    """
    Search the listings table by partial address match.
    Assumes the row includes a URL column like source_url.
    """
    if not address_query or not address_query.strip():
        return []

    response = (
        supabase
        .table("listings")
        .select("*")
        .ilike("address_name", f"%{address_query.strip()}%")
        .limit(limit)
        .execute()
    )

    return response.data or []