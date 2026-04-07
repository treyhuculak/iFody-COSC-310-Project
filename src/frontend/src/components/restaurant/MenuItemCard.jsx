export default function MenuItemCard({
    item,
    quantity,
    onQuantityChange,
    onAddToCart,
    isSubmitting = false,
    isHighlighted = false,
}) {
    return (
        <article className={`menu-item-card ${isHighlighted ? "is-highlighted" : ""}`}>
            <div className="menu-item-top">
                <h3>{item.name}</h3>
                <span className="menu-item-price">${item.price.toFixed(2)}</span>
            </div>

            {item.description ? <p className="menu-item-description">{item.description}</p> : null}

            <div className="menu-item-actions">
                <label className="menu-item-quantity-label" htmlFor={`menu-qty-${item.id}`}>
                    Quantity
                </label>
                <input
                    id={`menu-qty-${item.id}`}
                    className="menu-item-quantity-input"
                    type="number"
                    min="1"
                    step="1"
                    value={quantity}
                    onChange={(event) => onQuantityChange(item.id, event.target.value)}
                />

                <button
                    type="button"
                    className="menu-item-add-button"
                    disabled={isSubmitting}
                    onClick={() => onAddToCart(item)}
                >
                    {isSubmitting ? "Adding..." : "Add to cart"}
                </button>
            </div>
        </article>
    );
}
