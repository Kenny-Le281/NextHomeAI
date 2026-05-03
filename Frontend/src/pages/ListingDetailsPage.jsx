import { useState } from "react";
import { Link, useLocation, useParams } from "react-router-dom";

const PROPERTY_TYPE_LABELS = {
  3: "Condo",
  4: "Multi-family",
  6: "House",
  8: "Land",
  10: "Other",
  13: "Townhouse",
};

function getPropertyTypeLabel(listing) {
  const rawValue = listing?.property_type_label || listing?.property_type;

  if (rawValue === null || rawValue === undefined || rawValue === "") {
    return null;
  }

  const numericValue = Number(rawValue);

  if (!Number.isNaN(numericValue) && PROPERTY_TYPE_LABELS[numericValue]) {
    return PROPERTY_TYPE_LABELS[numericValue];
  }

  return String(rawValue);
}

function getListingImages(listing) {
  if (Array.isArray(listing?.image_urls)) {
    return listing.image_urls.filter(Boolean);
  }

  if (Array.isArray(listing?.photos)) {
    return listing.photos.filter(Boolean);
  }

  const singleImage =
    listing?.main_image ||
    listing?.image_url ||
    listing?.photo_url ||
    null;

  return singleImage ? [singleImage] : [];
}

function getListingUrl(listing) {
  const rawUrl = listing?.source_url || listing?.listing_url || listing?.url;

  if (!rawUrl) {
    return null;
  }

  if (rawUrl.startsWith("http://") || rawUrl.startsWith("https://")) {
    return rawUrl;
  }

  if (rawUrl.startsWith("/")) {
    return `https://www.redfin.ca${rawUrl}`;
  }

  return `https://www.redfin.ca/${rawUrl}`;
}

function formatPrice(value) {
  if (value === null || value === undefined || value === "") {
    return "Not available";
  }

  return `$${Number(value).toLocaleString()}`;
}

function formatDate(value) {
  if (!value) {
    return "Not available";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return String(value);
  }

  return date.toLocaleDateString("en-CA", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

function formatNumber(value) {
  if (value === null || value === undefined || value === "") {
    return "Not available";
  }

  return Number(value).toLocaleString();
}

function DetailRow({ label, value }) {
  return (
    <div className="detail-row">
      <span>{label}</span>
      <strong>{value || "Not available"}</strong>
    </div>
  );
}

function ListingImageGallery({ images, address }) {
  const [selectedIndex, setSelectedIndex] = useState(0);

  const hasImages = images.length > 0;
  const selectedImage = hasImages
    ? images[selectedIndex]
    : "https://placehold.co/900x500?text=No+Image";

  function showPrevious() {
    setSelectedIndex((currentIndex) =>
      currentIndex === 0 ? images.length - 1 : currentIndex - 1
    );
  }

  function showNext() {
    setSelectedIndex((currentIndex) =>
      currentIndex === images.length - 1 ? 0 : currentIndex + 1
    );
  }

  return (
    <div className="listing-gallery">
      <div className="details-image-wrapper">
        <img src={selectedImage} alt={address || "Property"} />

        {images.length > 1 && (
          <div className="gallery-controls">
            <button type="button" onClick={showPrevious}>
              Previous
            </button>

            <span>
              {selectedIndex + 1} / {images.length}
            </span>

            <button type="button" onClick={showNext}>
              Next
            </button>
          </div>
        )}
      </div>

      {images.length > 1 && (
        <div className="thumbnail-strip" aria-label="Listing images">
          {images.map((image, index) => (
            <button
              key={image}
              type="button"
              className={`thumbnail-button ${index === selectedIndex ? "active" : ""}`}
              onClick={() => setSelectedIndex(index)}
              aria-label={`Show listing image ${index + 1}`}
            >
              <img src={image} alt={`${address || "Property"} ${index + 1}`} />
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

function ListingDetailsPage() {
  const { listingId } = useParams();
  const location = useLocation();

  const listingFromState = location.state?.listing;
  let listing = listingFromState;

  if (!listing) {
    try {
      const saved = localStorage.getItem("nextHomeAI.homeState");
      const parsed = saved ? JSON.parse(saved) : null;
      const savedListings = Array.isArray(parsed?.listings) ? parsed.listings : [];

      listing = savedListings.find((item) => {
        const id = item.listing_id || item.property_id || item.id;
        return String(id) === String(listingId);
      });
    } catch {
      listing = null;
    }
  }

  if (!listing) {
    return (
      <main className="details-page">
        <Link to="/" className="back-link">
          ← Back home
        </Link>

        <div className="details-card">
          <h1>Listing details unavailable</h1>
          <p>
            This listing was not found in your saved search results. Return home and
            run the search again.
          </p>
        </div>
      </main>
    );
  }

  const images = getListingImages(listing);
  const price = formatPrice(listing.price);
  const baths = listing.total_baths ?? listing.baths;
  const propertyType = getPropertyTypeLabel(listing);
  const listingUrl = getListingUrl(listing);

  return (
    <main className="details-page">
      <Link to="/" className="back-link">
        ← Back home
      </Link>

      <article className="details-card">
        <ListingImageGallery images={images} address={listing.address_name} />

        <div className="details-content">
          <p className="listing-id">Listing ID: {listingId}</p>

          <h1>{listing.address_name || "Unknown address"}</h1>

          <p className="details-price">{price}</p>

          <div className="details-meta">
            {listing.beds !== null && listing.beds !== undefined && (
              <span>{listing.beds} beds</span>
            )}

            {baths !== null && baths !== undefined && (
              <span>{baths} baths</span>
            )}

            {listing.sqft !== null && listing.sqft !== undefined && (
              <span>{formatNumber(listing.sqft)} sqft</span>
            )}

            {propertyType && <span>{propertyType}</span>}
          </div>

          <section>
            <h2>Property details</h2>

            <div className="details-grid">
              <DetailRow label="Address" value={listing.address_name} />
              <DetailRow
                label="Location"
                value={[listing.city, listing.state, listing.zip].filter(Boolean).join(", ")}
              />
              <DetailRow label="City" value={listing.city} />
              <DetailRow label="Province / State" value={listing.state} />
              <DetailRow label="Postal code" value={listing.zip} />
              <DetailRow label="Property type" value={propertyType} />
              <DetailRow label="Bedrooms" value={listing.beds} />
              <DetailRow label="Bathrooms" value={baths} />
              <DetailRow label="Square footage" value={formatNumber(listing.sqft)} />
              <DetailRow label="HOA amount" value={formatPrice(listing.hoa_amount)} />
              <DetailRow label="Days on market" value={listing.days_on_market} />
              <DetailRow label="Last sold date" value={formatDate(listing.last_sold_date)} />
            </div>
          </section>

          <section>
            <h2>Location coordinates</h2>

            <div className="details-grid">
              <DetailRow label="Latitude" value={listing.latitude} />
              <DetailRow label="Longitude" value={listing.longitude} />
            </div>
          </section>

          <section>
            <h2>Description</h2>
            <p>{listing.description || "No description available."}</p>
          </section>

          {listingUrl && (
            <a
              className="primary-link-button"
              href={listingUrl}
              target="_blank"
              rel="noreferrer"
            >
              View original listing
            </a>
          )}
        </div>
      </article>
    </main>
  );
}

export default ListingDetailsPage;