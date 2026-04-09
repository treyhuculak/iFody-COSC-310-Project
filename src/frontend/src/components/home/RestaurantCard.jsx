export default function RestaurantCard({ restaurant, onSelect, isHighlighted = false }) {
    const avgRating = restaurant.avg_review_rating;
    const hasRating = typeof avgRating === "number" && avgRating > 0;

    return (
        <article className={`restaurant-card ${isHighlighted ? "is-highlighted" : ""}`}>
            <div className="restaurant-card-top">
                <h3>
                    {restaurant.name}
                    {hasRating && (
                        <span className="restaurant-rating-badge">
                            ★ {avgRating.toFixed(1)}
                        </span>
                    )}
                </h3>
                <span
                    className={`availability-pill ${restaurant.is_available ? "is-open" : "is-closed"
                        }`}
                >
                    {restaurant.is_available ? "Open" : "Closed"}
                </span>
            </div>

            <p className="restaurant-meta">
                <strong>{restaurant.cuisine}</strong> • {restaurant.location}
            </p>
            <p className="delivery-fee">Delivery fee: ${restaurant.delivery_fee.toFixed(2)}</p>

            {onSelect && (
                <button
                    type="button"
                    className="restaurant-action"
                    onClick={() => onSelect(restaurant)}
                >
                    View restaurant
                </button>
            )}
        </article>
    );
}
