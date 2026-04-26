from models.booking_request import BookingRequest
from automation.redfin_tour_booking import submit_redfin_tour_request


def book_showing_tool(booking: BookingRequest) -> dict:
    if not booking.listing_url:
        return {
            "status": "error",
            "message": "Booking request is missing a listing URL."
        }
    result = submit_redfin_tour_request(booking, True)
    print(result)
    return result