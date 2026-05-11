import ListingCard from "./ListingCard";

function ListingsGrid({ listings }) {
  return (
    <div className="listings-grid">
      {listings.map((listing, index) => (
        <ListingCard
          key={listing.listing_id || listing.property_id || listing.id || index}
          listing={listing}
        />
      ))}
    </div>
  );
}

export default ListingsGrid;