import { Link, useLocation, useParams } from "react-router-dom";

function ListingDetailsPage() {
  const { listingId } = useParams();
  const location = useLocation();
  const listing = location.state?.listing;

  if (!listing) {
    return (
      <main className="details-page">
        <Link to="/" className="back-link">
          ← Back home
        </Link>

        <div className="details-card">
          <h1>Listing details unavailable</h1>
          <p>
            This listing was not passed to the detail page. You can return home and
            select the listing again.
          </p>
        </div>
      </main>
    );
  }

  const imageUrl =
    listing.main_image ||
    listing.image_url ||
    listing.photo_url ||
    listing.photos?.[0] ||
    "https://placehold.co/900x500?text=No+Image";

  return (
    <main className="details-page">
      <Link to="/" className="back-link">
        ← Back home
      </Link>

      <article className="details-card">
        <div className="details-image-wrapper">
          <img src={imageUrl} alt={listing.address_name || "Property"} />
        </div>

        <div className="details-content">
          <p className="listing-id">Listing ID: {listingId}</p>

          <h1>{listing.address_name || "Unknown address"}</h1>

          <p className="details-price">
            {listing.price ? `$${Number(listing.price).toLocaleString()}` : "Price unavailable"}
          </p>

          <div className="details-meta">
            {listing.beds && <span>{listing.beds} beds</span>}
            {listing.baths && <span>{listing.baths} baths</span>}
            {listing.sqft && <span>{Number(listing.sqft).toLocaleString()} sqft</span>}
            {listing.property_type && <span>{listing.property_type}</span>}
          </div>

          <section>
            <h2>Location</h2>
            <p>{[listing.city, listing.state, listing.zip].filter(Boolean).join(", ")}</p>
          </section>

          <section>
            <h2>Description</h2>
            <p>{listing.description || "No description available."}</p>
          </section>

          {listing.source_url && (
            <a
              className="primary-link-button"
              href={listing.source_url}
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