import RestaurantCard from "./RestaurantCard";

export default function RestaurantSection({
    title,
    subtitle,
    restaurants,
    isLoading,
    emptyMessage,
    endpointReady = true,
    highlightedRestaurantId,
    onSelectRestaurant,
}) {
    return (
        <section className="restaurant-section">
            <div className="section-heading">
                <h2>{title}</h2>
                {subtitle && <p>{subtitle}</p>}
            </div>

            {!endpointReady ? (
                <div className="section-placeholder">
                    <h3>Coming soon</h3>
                    <p>
                        This section is ready in the UI and will automatically populate once the
                        endpoint is merged.
                    </p>
                </div>
            ) : isLoading ? (
                <div className="section-placeholder">Loading restaurants...</div>
            ) : restaurants.length === 0 ? (
                <div className="section-placeholder">{emptyMessage}</div>
            ) : (
                <div className="restaurant-grid">
                    {restaurants.map((restaurant) => (
                        <RestaurantCard
                            key={restaurant.id}
                            restaurant={restaurant}
                            onSelect={onSelectRestaurant}
                            isHighlighted={restaurant.id === highlightedRestaurantId}
                        />
                    ))}
                </div>
            )}
        </section>
    );
}
