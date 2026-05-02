import json

from agent.agent_orchestrator import run_agent
from models.housing_filters import HousingFilters


def run_listing_chatbot() -> None:
    print("Bot: Hi! Tell me what kind of property you're looking for.")
    print()

    current_filters = HousingFilters()

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            print("Bot: Please type something.")
            print()
            continue

        try:
            result = run_agent(user_input, current_filters)
        except Exception as exception:
            print(f"Bot: I ran into a problem: {exception}")
            print()
            continue

        current_filters = result["filters"]

        print(f"Bot: {result['reply']}")
        print()

        print("=== CURRENT FILTER OBJECT ===")
        print(json.dumps(current_filters.model_dump(mode="json"), indent=2))
        print()

        if result["api_params"] is not None:
            print("=== DETERMINISTIC API PARAMS ===")
            print(json.dumps(result["api_params"], indent=2))
            print()

        if result.get("listings"):
            base_url = "https://www.redfin.ca"
            print(f"=== MATCHING LISTINGS ({len(result['listings'])}) ===")
            for listing in result["listings"]:
                addr = listing.get("address_name", "Unknown")
                price = listing.get("price")
                beds = listing.get("beds")
                baths = listing.get("total_baths")
                ptype = listing.get("property_type", "")
                url = listing.get("url", "")
                price_str = f"${price:,}" if price else "N/A"
                link = f"{base_url}{url}" if url else "No link"
                print(f"  {addr} — {price_str} | {beds}bd/{baths}ba | {ptype}")
                print(f"    {link}")
            print()

        if result["done"] and result["intent"] == "end_chat":
            break


run_listing_chatbot()
