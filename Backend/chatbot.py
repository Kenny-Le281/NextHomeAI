import json

from agent.agent_orchestrator import run_agent
from models.housing_filters import HousingFilters
from models.session_context import SessionContext, SessionMessage


def run_listing_chatbot() -> None:
    opening_message = "Hi! Tell me what kind of property you're looking for."

    print(f"Bot: {opening_message}")
    print()

    current_filters = HousingFilters()
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
            )
        except Exception as exception:
            print(f"Bot: I ran into a problem: {exception}")
            print()
            continue

        current_filters = result["filters"]
        current_context = result["context"]

        assistant_reply = result["reply"]
        current_context.conversation_history.append(
            SessionMessage(role="assistant", content=assistant_reply)
        )

        print(f"Bot: {assistant_reply}")
        print()

        print("=== CURRENT FILTER OBJECT ===")
        print(json.dumps(current_filters.model_dump(mode="json"), indent=2))
        print()

        print("=== CURRENT CONTEXT ===")
        print(json.dumps(current_context.model_dump(mode="json"), indent=2))
        print()

        listings = result.get("listings")
        if listings is not None:
            print(f"=== MATCHING LISTINGS ({len(listings)}) ===")

            if len(listings) == 0:
                print("No listings matched the current filters.")
            else:
                for index, listing in enumerate(listings[:5], start=1):
                    address = listing.get("address_name", "Unknown address")
                    city = listing.get("city", "Unknown city")
                    price = listing.get("price", "N/A")
                    beds = listing.get("beds", "N/A")
                    baths = listing.get("total_baths", "N/A")

                    print(f"{index}. {address} | {city} | ${price} | {beds} beds | {baths} baths")
            print()

        if result["done"] and result["intent"] == "end_chat":
            break


if __name__ == "__main__":
    run_listing_chatbot()