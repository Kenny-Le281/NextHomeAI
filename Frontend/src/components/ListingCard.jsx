import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  getListingImages,
  NO_IMAGE_URL,
  resolveFirstListingImage,
} from "../utils/listingImages";

const PROPERTY_TYPE_LABELS = {
  3: "Condo",
  4: "Multi-family",
  6: "House",
  8: "Land",
  10: "Other",
  13: "Townhouse",
};

function getPropertyTypeLabel(listing) {
  const rawValue = listing.property_type_label || listing.property_type;

  if (rawValue === null || rawValue === undefined || rawValue === "") {
    return null;
  }

  const numericValue = Number(rawValue);

  if (!Number.isNaN(numericValue) && PROPERTY_TYPE_LABELS[numericValue]) {
    return PROPERTY_TYPE_LABELS[numericValue];
  }

  return String(rawValue);
}

function ListingCard({ listing }) {
  const listingId = listing.listing_id || listing.property_id || listing.id;
  const images = getListingImages(listing);
  const imageKey = images.join("\n");
  const [imageUrl, setImageUrl] = useState(NO_IMAGE_URL);

  useEffect(() => {
    let cancelled = false;
    const sourceImages = imageKey ? imageKey.split("\n") : [];

    resolveFirstListingImage(sourceImages).then((resolvedImage) => {
      if (!cancelled) {
        setImageUrl(resolvedImage || NO_IMAGE_URL);
      }
    });

    return () => {
      cancelled = true;
    };
  }, [imageKey]);

  const price =
    listing.price !== null && listing.price !== undefined
      ? `$${Number(listing.price).toLocaleString()}`
      : "Price unavailable";

  const baths = listing.total_baths ?? listing.baths;
  const propertyType = getPropertyTypeLabel(listing);

  return (
    <Link to={`/listing/${listingId}`} state={{ listing }} className="listing-card-link">
      <article className="listing-card">
        <div className="listing-image-wrapper">
          <img src={imageUrl} alt={listing.address_name || "Property"} />
        </div>

        <div className="listing-card-content">
          <p className="listing-price">{price}</p>

          <h3>{listing.address_name || "Unknown address"}</h3>

          <div className="listing-meta">
            {listing.beds !== null && listing.beds !== undefined && (
              <span>{listing.beds} beds</span>
            )}

            {baths !== null && baths !== undefined && (
              <span>{baths} baths</span>
            )}

            {listing.sqft !== null && listing.sqft !== undefined && (
              <span>{Number(listing.sqft).toLocaleString()} sqft</span>
            )}

            {propertyType && <span>{propertyType}</span>}
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
