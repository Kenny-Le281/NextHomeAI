import { Link } from "react-router-dom";

function ListingCard({ listing }) {
  const listingId = listing.listing_id || listing.property_id || listing.id;
  const imageUrl =
    listing.main_image ||
    listing.image_url ||
    listing.photo_url ||
    listing.photos?.[0] ||
    "https://placehold.co/600x400?text=No+Image";

  return (
    <Link to={`/listing/${listingId}`} state={{ listing }} className="listing-card-link">
      <article className="listing-card">
        <div className="listing-image-wrapper">
          <img src={imageUrl} alt={listing.address_name || "Property"} />
        </div>

        <div className="listing-card-content">
          <p className="listing-price">
            {listing.price ? `$${Number(listing.price).toLocaleString()}` : "Price unavailable"}
          </p>

          <h3>{listing.address_name || "Unknown address"}</h3>

          <div className="listing-meta">
            {listing.beds && <span>{listing.beds} beds</span>}
            {listing.baths && <span>{listing.baths} baths</span>}
            {listing.sqft && <span>{Number(listing.sqft).toLocaleString()} sqft</span>}
          </div>

          <p className="listing-location">
            {[listing.city, listing.state, listing.zip].filter(Boolean).join(", ")}
          </p>
        </div>
      </article>
    </Link>
  );
}

export default ListingCard;