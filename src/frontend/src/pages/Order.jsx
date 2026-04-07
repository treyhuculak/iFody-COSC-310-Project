import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { fetchOrder, deleteOrderItem } from "../api/orders";
import { parseUserIdFromStorage } from "../api/restaurants";
import "../styles/order.css";

const API_URL = import.meta.env.VITE_API_URL || "/api";

export default function Order() {
    const { orderId } = useParams();
    const navigate = useNavigate();
    const userId = parseUserIdFromStorage();

    const [order, setOrder] = useState(null);
    const [menuItems, setMenuItems] = useState({});  // { item_id: name }
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        if (!userId) {
            navigate("/login");
            return;
        }

        const abortController = new AbortController();

        fetchOrder(orderId, { signal: abortController.signal })
            .then(async (orderData) => {
                setOrder(orderData);

                // Fetch menu items for this restaurant to get item names
                const res = await fetch(
                    `${API_URL}/restaurants/${orderData.restaurant_id}/menu?limit=100`,
                    { signal: abortController.signal }
                );
                const menuData = await res.json();
                const items = menuData.items || menuData;

                // Build a lookup map { item_id: item_name }
                const lookup = {};
                items.forEach((item) => {
                    lookup[item.id] = item.name;
                });
                setMenuItems(lookup);
                setLoading(false);
            })
            .catch((err) => {
                if (err.name === "AbortError") return;
                setError(err.message || "Failed to load order.");
                setLoading(false);
            });

        return () => abortController.abort();
    }, [orderId]);

    const handleRemoveItem = async (itemId) => {
        try {
            await deleteOrderItem(orderId, itemId, userId);
            setOrder((prev) => ({
                ...prev,
                order_items: prev.order_items.filter((item) => item.item_id !== itemId),
            }));
        } catch (err) {
            setError(err.message || "Failed to remove item.");
        }
    };

    const handleQuantityChange = (itemId, newQuantity) => {
        if (newQuantity < 1) return;
        setOrder((prev) => ({
            ...prev,
            order_items: prev.order_items.map((item) =>
                item.item_id === itemId ? { ...item, quantity: newQuantity } : item
            ),
        }));
    };

    // Calculate totals from local state instead of backend values
    const subtotal = order
        ? order.order_items.reduce(
            (sum, item) => sum + item.price_at_purchase * item.quantity,
            0
        )
        : 0;
    const tax = order ? order.tax : 0;
    const deliveryFee = order ? order.delivery_fee : 0;
    const total = subtotal + tax + deliveryFee;

    if (loading) return <p className="status-loading">Loading order...</p>;
    if (error) return <p className="status-error">{error}</p>;
    if (!order) return null;

    return (
        <main className="order-page">
            <section className="hero-banner">
                <p className="hero-kicker">Your Order</p>
                <h1>Review your order before paying.</h1>
                <p className="hero-subtitle">
                    Order #{order.id} • Status: {order.status}
                </p>
            </section>

            <section className="order-items-section">
                <h2>Order items</h2>

                {order.order_items.length === 0 ? (
                    <p className="order-empty">No items in this order.</p>
                ) : (
                    <div className="order-items-list">
                        {order.order_items.map((item) => (
                            <div key={item.item_id} className="order-item-card">
                                <div className="order-item-info">
                                    <h3>{menuItems[item.item_id] || `Item #${item.item_id}`}</h3>
                                    <p className="order-item-price">
                                        ${item.price_at_purchase.toFixed(2)} each
                                    </p>
                                </div>

                                <div className="order-item-controls">
                                    <div className="quantity-controls">
                                        <button
                                            className="quantity-btn"
                                            onClick={() =>
                                                handleQuantityChange(item.item_id, item.quantity - 1)
                                            }
                                        >
                                            −
                                        </button>
                                        <span className="quantity-value">{item.quantity}</span>
                                        <button
                                            className="quantity-btn"
                                            onClick={() =>
                                                handleQuantityChange(item.item_id, item.quantity + 1)
                                            }
                                        >
                                            +
                                        </button>
                                    </div>

                                    <p className="order-item-subtotal">
                                        ${(item.price_at_purchase * item.quantity).toFixed(2)}
                                    </p>

                                    <button
                                        className="order-item-remove"
                                        onClick={() => handleRemoveItem(item.item_id)}
                                    >
                                        Remove
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </section>

            <section className="order-summary">
                <h2>Summary</h2>
                <div className="order-summary-row">
                    <span>Subtotal</span>
                    <span>${subtotal.toFixed(2)}</span>
                </div>
                <div className="order-summary-row">
                    <span>Tax</span>
                    <span>${tax.toFixed(2)}</span>
                </div>
                <div className="order-summary-row">
                    <span>Delivery fee</span>
                    <span>${deliveryFee.toFixed(2)}</span>
                </div>
                <div className="order-summary-row order-summary-total">
                    <span>Total</span>
                    <span>${total.toFixed(2)}</span>
                </div>

                <button
                    className="restaurant-action"
                    onClick={() => navigate(`/payment/${orderId}`)}
                    disabled={order.order_items.length === 0}
                >
                    Proceed to payment
                </button>
            </section>
        </main>
    );
}