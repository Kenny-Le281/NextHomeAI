function BookingSummary({ booking }) {
    const address = booking.matched_listing_address || booking.listing_address_requested;
  
    if (!address && !booking.preferred_date && !booking.preferred_time) {
      return null;
    }
  
    return (
      <aside className="booking-summary">
        <h3>Booking progress</h3>
  
        <div className="summary-row">
          <span>Property</span>
          <strong>{address || "Not selected"}</strong>
        </div>
  
        <div className="summary-row">
          <span>Date</span>
          <strong>{booking.preferred_date || "Not provided"}</strong>
        </div>
  
        <div className="summary-row">
          <span>Time</span>
          <strong>{booking.preferred_time || "Not provided"}</strong>
        </div>
  
        <div className="summary-row">
          <span>Tour type</span>
          <strong>
            {booking.virtual_tour === true
              ? "Virtual"
              : booking.virtual_tour === false
                ? "In person"
                : "Not selected"}
          </strong>
        </div>
      </aside>
    );
  }
  
  export default BookingSummary;