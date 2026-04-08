import { useEffect, useRef, useState } from "react";
import { fetchRestaurantById, parseUserIdFromStorage } from "../api/restaurants";
import "../styles/orders.css";

const API_URL = import.meta.env.VITE_API_URL || "/api";

async function fetchRestaurantData(restaurantId) {
    try {
        const restaurant = await fetchRestaurantById(restaurantId);
        const itemNames = {};
        (restaurant?.menu_items || []).forEach((item) => {
            itemNames[item.id] = item.name;
        });
        return { name: restaurant?.name || null, itemNames };
    } catch {
        return { name: null, itemNames: {} };
    }
}

const DONE_STATUSES = ["delivered", "payment failed"];

function isLiveOrder(order) {
    return !DONE_STATUSES.includes(order.status);
}

function statusBadgeClass(status) {
    if (status === "delivered") return "order-status-badge status-delivered";
    if (status === "payment failed") return "order-status-badge status-failed";
    return "order-status-badge status-active";
}

function formatTimestamp(ts) {
    if (!ts) return "";
    try {
        return new Date(ts).toLocaleString();
    } catch {
        return ts;
    }
}

async function fetchAllOrders(userId) {
    const res = await fetch(`${API_URL}/orders/customer/${userId}`);
    if (!res.ok) throw new Error("Failed to load orders.");
    return res.json();
}

async function fetchDeliveryInfo(orderId) {
    const res = await fetch(`${API_URL}/deliveries/order/${orderId}`);
    if (!res.ok) return null;
    return res.json();
}

function OrderCard({ order, eta, itemNames = {}, restaurantName }) {
    const items = order.order_items || [];
    const subtotal = Number(order.subtotal_price ?? 0);
    const tax = Number(order.tax ?? 0);
    const deliveryFee = Number(order.delivery_fee ?? 0);
    const total = Number(order.total_price ?? subtotal + tax + deliveryFee);

    return (
        <article className="order-card">
            <div className="order-card-header">
                <div>
                    <h3>Order #{order.id}</h3>
                    <span className="order-card-meta">
                        {restaurantName || `Restaurant #${order.restaurant_id}`} &mdash; {formatTimestamp(order.created_at || order.timestamp)}
                    </span>
                </div>
                <span className={statusBadgeClass(order.status)}>{order.status}</span>
            </div>

            <div className="order-items-list">
                {items.map((item) => (
                    <div key={item.item_id ?? item.id} className="order-item-row">
                        <span className="order-item-name">{itemNames[item.item_id] || item.name || `Item #${item.item_id ?? item.id}`}</span>
                        <span className="order-item-qty">x{item.quantity}</span>
                        <span className="order-item-price">
                            ${(Number(item.price_at_purchase ?? item.price ?? 0) * item.quantity).toFixed(2)}
                        </span>
                    </div>
                ))}
            </div>

            <div className="order-card-footer">
                <p className="order-summary-row">Subtotal: ${subtotal.toFixed(2)}</p>
                <p className="order-summary-row">Tax: ${tax.toFixed(2)}</p>
                <p className="order-summary-row">Delivery fee: ${deliveryFee.toFixed(2)}</p>
                <p className="order-summary-row order-summary-total">Total: ${total.toFixed(2)}</p>
                {eta && (
                    <p className="order-eta">Estimated delivery: {formatTimestamp(eta)}</p>
                )}
            </div>
        </article>
    );
}

export default function OrderHistory() {
    const userId = parseUserIdFromStorage();
    const [orders, setOrders] = useState([]);
    const [etaMap, setEtaMap] = useState({});
    const [itemNamesMap, setItemNamesMap] = useState({});
    const [restaurantNamesMap, setRestaurantNamesMap] = useState({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const intervalRef = useRef(null);

    const loadOrders = async () => {
        if (!userId) return 0;
        try {
            const all = await fetchAllOrders(userId);
            const filtered = (all || []).filter((o) => o.status !== "pending");

            const live = filtered.filter(isLiveOrder);
            const done = filtered.filter((o) => !isLiveOrder(o));

            const sortByTime = (a, b) => {
                const ta = new Date(a.created_at || a.timestamp || 0).getTime();
                const tb = new Date(b.created_at || b.timestamp || 0).getTime();
                return tb - ta;
            };

            live.sort(sortByTime);
            done.sort(sortByTime);

            setOrders([...live, ...done]);

            // Fetch restaurant names and item names for each unique restaurant
            const restaurantIds = [...new Set(filtered.map((o) => o.restaurant_id))];
            const dataEntries = await Promise.all(
                restaurantIds.map(async (rid) => [rid, await fetchRestaurantData(rid)])
            );
            setItemNamesMap(Object.fromEntries(dataEntries.map(([rid, d]) => [rid, d.itemNames])));
            setRestaurantNamesMap(Object.fromEntries(dataEntries.map(([rid, d]) => [rid, d.name])));

            // Fetch ETAs for "out for delivery" orders
            const outForDelivery = live.filter((o) => o.status === "out for delivery");
            if (outForDelivery.length > 0) {
                const etaEntries = await Promise.all(
                    outForDelivery.map(async (o) => {
                        const info = await fetchDeliveryInfo(o.id);
                        return [o.id, info?.estimated_delivery_time ?? null];
                    })
                );
                setEtaMap(Object.fromEntries(etaEntries));
            }

            // Only count "preparing" or "out for delivery" as needing live polling
            const activeCount = live.filter((o) =>
                o.status === "preparing" || o.status === "out for delivery"
            ).length;
            return activeCount;
        } catch (err) {
            setError(err.message || "Failed to load order history.");
            return 0;
        }
    };

    useEffect(() => {
        let cancelled = false;

        const init = async () => {
            setLoading(true);
            const activeCount = await loadOrders();
            if (!cancelled) {
                setLoading(false);
                if (activeCount > 0) {
                    intervalRef.current = setInterval(async () => {
                        const remaining = await loadOrders();
                        if (remaining === 0 && intervalRef.current) {
                            clearInterval(intervalRef.current);
                            intervalRef.current = null;
                        }
                    }, 10000);
                }
            }
        };

        init();

        return () => {
            cancelled = true;
            if (intervalRef.current) {
                clearInterval(intervalRef.current);
                intervalRef.current = null;
            }
        };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [userId]);

    const liveOrders = orders.filter(isLiveOrder);
    const doneOrders = orders.filter((o) => !isLiveOrder(o));

    return (
        <main className="home-page orders-page">
            <section className="hero-banner">
                <p className="hero-kicker">Your Orders</p>
                <h1>Order History</h1>
                <p className="hero-subtitle">Track live orders and review past deliveries.</p>
            </section>

            {error && <p className="status-error">{error}</p>}

            <section className="restaurant-section">
                {loading ? (
                    <div className="section-placeholder">Loading your orders...</div>
                ) : (
                    <>
                        {liveOrders.length > 0 && (
                            <>
                                <h2 className="orders-section-title">Live Orders</h2>
                                <div className="orders-list">
                                    {liveOrders.map((order) => (
                                        <OrderCard
                                            key={order.id}
                                            order={order}
                                            eta={etaMap[order.id] ?? null}
                                            itemNames={itemNamesMap[order.restaurant_id] ?? {}}
                                            restaurantName={restaurantNamesMap[order.restaurant_id]}
                                        />
                                    ))}
                                </div>
                                <hr className="orders-separator" />
                            </>
                        )}

                        <h2 className="orders-section-title">
                            {liveOrders.length > 0 ? "Past Orders" : "Order History"}
                        </h2>
                        {doneOrders.length === 0 ? (
                            <div className="orders-empty">No completed orders yet.</div>
                        ) : (
                            <div className="orders-list">
                                {doneOrders.map((order) => (
                                    <OrderCard key={order.id} order={order} eta={null} itemNames={itemNamesMap[order.restaurant_id] ?? {}} restaurantName={restaurantNamesMap[order.restaurant_id]} />
                                ))}
                            </div>
                        )}

                        {orders.length === 0 && (
                            <div className="orders-empty">You have no orders yet.</div>
                        )}
                    </>
                )}
            </section>
        </main>
    );
}
