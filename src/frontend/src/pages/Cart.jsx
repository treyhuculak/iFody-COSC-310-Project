import { useCallback, useEffect, useMemo, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import {
    countItemsInOrders,
    fetchActiveCartOrders,
    setCartItemQuantity,
} from "../api/orders";
import { fetchRestaurantById, parseUserIdFromStorage } from "../api/restaurants";
import "../styles/cart.css";

function buildItemDraftKey(orderId, itemId) {
    return `${orderId}:${itemId}`;
}

export default function Cart() {
    const location = useLocation();
    const navigate = useNavigate();
    const userId = parseUserIdFromStorage();

    const [cartState, setCartState] = useState({
        loading: true,
        error: "",
        orders: [],
        restaurantsById: {},
    });

    const [quantityDrafts, setQuantityDrafts] = useState({});
    const [pendingItemKey, setPendingItemKey] = useState("");

    const redirectToLogin = useCallback(() => {
        const redirectPath = `${location.pathname}${location.search}`;
        const query = new URLSearchParams({ redirect: redirectPath }).toString();
        navigate(`/login?${query}`);
    }, [location.pathname, location.search, navigate]);

    const loadCart = useCallback(async () => {
        if (!userId) {
            return;
        }

        setCartState((prev) => ({ ...prev, loading: true, error: "" }));

        try {
            const orders = await fetchActiveCartOrders({ userId });
            const restaurantIds = [...new Set(orders.map((order) => order.restaurant_id))];

            const restaurants = await Promise.all(
                restaurantIds.map(async (restaurantId) => {
                    try {
                        const restaurant = await fetchRestaurantById(restaurantId);
                        return [restaurantId, restaurant];
                    } catch {
                        return [restaurantId, null];
                    }
                })
            );

            const restaurantsById = Object.fromEntries(restaurants);

            setCartState({
                loading: false,
                error: "",
                orders,
                restaurantsById,
            });

            setQuantityDrafts((prev) => {
                const nextDrafts = { ...prev };
                orders.forEach((order) => {
                    (order.order_items || []).forEach((item) => {
                        nextDrafts[buildItemDraftKey(order.id, item.item_id)] = item.quantity;
                    });
                });
                return nextDrafts;
            });
        } catch (error) {
            if (error?.status === 401) {
                redirectToLogin();
                return;
            }

            setCartState({
                loading: false,
                error: error.message || "Failed to load cart.",
                orders: [],
                restaurantsById: {},
            });
        }
    }, [redirectToLogin, userId]);

    useEffect(() => {
        if (!userId) {
            redirectToLogin();
            return;
        }

        loadCart();
    }, [loadCart, redirectToLogin, userId]);

    useEffect(() => {
        const handleCartUpdated = () => {
            loadCart();
        };

        window.addEventListener("cart:updated", handleCartUpdated);
        return () => {
            window.removeEventListener("cart:updated", handleCartUpdated);
        };
    }, [loadCart]);

    const totalItemCount = useMemo(() => countItemsInOrders(cartState.orders), [cartState.orders]);

    const resolveMenuItem = useCallback(
        (order, orderItem) => {
            const restaurant = cartState.restaurantsById[order.restaurant_id];
            if (!restaurant || !Array.isArray(restaurant.menu_items)) {
                return null;
            }

            return (
                restaurant.menu_items.find((item) => item.id === orderItem.item_id) || null
            );
        },
        [cartState.restaurantsById]
    );

    const handleQuantityDraftChange = (orderId, itemId, rawValue) => {
        const parsed = Number(rawValue);
        const normalized = Number.isNaN(parsed)
            ? 0
            : Math.min(Math.max(0, Math.floor(parsed)), 99);

        setQuantityDrafts((prev) => ({
            ...prev,
            [buildItemDraftKey(orderId, itemId)]: normalized,
        }));
    };

    const handleUpdateQuantity = async (order, orderItem, targetQuantity) => {
        const itemKey = buildItemDraftKey(order.id, orderItem.item_id);
        const menuItem = resolveMenuItem(order, orderItem);

        const payloadMenuItem = {
            id: orderItem.item_id,
            name: menuItem?.name || `Item #${orderItem.item_id}`,
            description: menuItem?.description || "",
            price: Number(menuItem?.price ?? orderItem.price_at_purchase),
        };

        setPendingItemKey(itemKey);
        setCartState((prev) => ({ ...prev, error: "" }));

        try {
            await setCartItemQuantity({
                orderId: order.id,
                userId,
                menuItem: payloadMenuItem,
                itemId: orderItem.item_id,
                currentQuantity: orderItem.quantity,
                targetQuantity,
            });

            await loadCart();
        } catch (error) {
            if (error?.status === 401) {
                redirectToLogin();
                return;
            }

            setCartState((prev) => ({
                ...prev,
                error: error.message || "Could not update cart item.",
            }));
        } finally {
            setPendingItemKey("");
        }
    };

    return (
        <main className="home-page cart-page">
            <section className="hero-banner">
                <p className="hero-kicker">Your Cart</p>
                <h1>Review and update your order items.</h1>
                <p className="hero-subtitle">
                    Changes in quantity are saved instantly and synced across pages.
                </p>
            </section>

            {cartState.error ? <p className="status-error">{cartState.error}</p> : null}

            <section className="restaurant-section">
                <div className="section-heading">
                    <h2>Items in cart</h2>
                    <p>{totalItemCount} total item{totalItemCount === 1 ? "" : "s"}</p>
                </div>

                {cartState.loading ? (
                    <div className="section-placeholder">Loading your cart...</div>
                ) : cartState.orders.length === 0 ? (
                    <div className="section-placeholder">
                        <p>Your cart is empty.</p>
                        <p>
                            <Link to="/" className="restaurant-back-link">
                                Browse restaurants
                            </Link>
                        </p>
                    </div>
                ) : (
                    <div className="cart-order-list">
                        {cartState.orders.map((order) => {
                            const restaurant = cartState.restaurantsById[order.restaurant_id];

                            return (
                                <article key={order.id} className="cart-order-card">
                                    <header className="cart-order-header">
                                        <h3>{restaurant?.name || `Restaurant #${order.restaurant_id}`}</h3>
                                        <small>Order #{order.id}</small>
                                    </header>

                                    <div className="cart-item-list">
                                        {(order.order_items || []).map((orderItem) => {
                                            const itemKey = buildItemDraftKey(order.id, orderItem.item_id);
                                            const menuItem = resolveMenuItem(order, orderItem);
                                            const itemName =
                                                menuItem?.name || `Menu item #${orderItem.item_id}`;
                                            const itemPrice = Number(
                                                menuItem?.price ?? orderItem.price_at_purchase
                                            );
                                            const draftQuantity =
                                                quantityDrafts[itemKey] ?? orderItem.quantity;
                                            const isPending = pendingItemKey === itemKey;

                                            return (
                                                <div key={itemKey} className="cart-item-row">
                                                    <div className="cart-item-main">
                                                        <p className="cart-item-name">{itemName}</p>
                                                        <p className="cart-item-meta">
                                                            ${itemPrice.toFixed(2)} each
                                                        </p>
                                                    </div>

                                                    <div className="cart-item-actions">
                                                        <input
                                                            type="number"
                                                            min="0"
                                                            step="1"
                                                            value={draftQuantity}
                                                            disabled={isPending}
                                                            onChange={(event) =>
                                                                handleQuantityDraftChange(
                                                                    order.id,
                                                                    orderItem.item_id,
                                                                    event.target.value
                                                                )
                                                            }
                                                        />

                                                        <button
                                                            type="button"
                                                            className="cart-update-button"
                                                            disabled={isPending}
                                                            onClick={() =>
                                                                handleUpdateQuantity(
                                                                    order,
                                                                    orderItem,
                                                                    Number(draftQuantity)
                                                                )
                                                            }
                                                        >
                                                            {isPending ? "Saving..." : "Update"}
                                                        </button>

                                                        <button
                                                            type="button"
                                                            className="cart-remove-button"
                                                            disabled={isPending}
                                                            onClick={() =>
                                                                handleUpdateQuantity(order, orderItem, 0)
                                                            }
                                                        >
                                                            Remove
                                                        </button>
                                                    </div>
                                                </div>
                                            );
                                        })}
                                    </div>
                                </article>
                            );
                        })}
                    </div>
                )}
            </section>
        </main>
    );
}
