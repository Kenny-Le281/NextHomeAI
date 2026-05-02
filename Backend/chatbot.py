import json

from agent.agent_orchestrator import run_agent
from models.housing_filters import HousingFilters
from models.booking_request import BookingRequest
from models.session_context import SessionContext, SessionMessage


def run_listing_chatbot() -> None:
    opening_message = "Hi! Tell me what kind of property you're looking for."

    print(f"Bot: {opening_message}")
    print()

    current_filters = HousingFilters()
    current_booking = BookingRequest()
    current_context = SessionContext(
        conversation_history=[
            SessionMessage(role="assistant", content=opening_message)
        ]
    )

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            print("Bot: Please type something.")
            print()
            continue

        current_context.conversation_history.append(
            SessionMessage(role="user", content=user_input)
        )

        try:
            result = run_agent(
                user_input=user_input,
                current_filters=current_filters,
                current_context=current_context,
                current_booking=current_booking,
            )
        except Exception as exception:
            print(f"Bot: I ran into a problem: {exception}")
            print()
            continue

        current_filters = result["filters"]
        current_context = result["context"]
        current_booking = result["booking"]

        assistant_reply = result["reply"]
        current_context.conversation_history.append(
            SessionMessage(role="assistant", content=assistant_reply)
        )

        print(f"Bot: {assistant_reply}")
        print()

        print("=== CURRENT FILTER OBJECT ===")
        print(json.dumps(current_filters.model_dump(mode="json"), indent=2))
        print()

        print("=== CURRENT BOOKING OBJECT ===")
        print(json.dumps(current_booking.model_dump(mode="json"), indent=2))
        print()

        print("=== CURRENT CONTEXT ===")
        print(json.dumps(current_context.model_dump(mode="json"), indent=2))
        print()

        listings = result.get("listings")
        if listings is not None:
            print(f"=== MATCHING LISTINGS ({len(listings)}) ===")

            if not listings:
                print("No listings matched the current filters.")
            else:
                base_url = "https://www.redfin.ca"

                property_type_labels = {
                    3: "Condo",
                    4: "Multi-family",
                    6: "House",
                    8: "Land",
                    10: "Other",
                    13: "Townhouse",
                }

                for listing in listings:
                    addr = listing.get("address_name", "Unknown")
                    price = listing.get("price")
                    beds = listing.get("beds")
                    baths = listing.get("total_baths")
                    raw_type = listing.get("property_type")
                    ptype = property_type_labels.get(raw_type, raw_type)
                    url = listing.get("url", "")

                    price_str = f"${price:,}" if price else "N/A"
                    link = f"{base_url}{url}" if url else "No link"

                    print(f"  {addr} — {price_str} | {beds}bd/{baths}ba | {ptype}")
                    print(f"    {link}")

            print()

        if result["done"] and result["intent"] == "end_chat":
            break


if __name__ == "__main__":
    run_listing_chatbot()
run_listing_chatbot()
