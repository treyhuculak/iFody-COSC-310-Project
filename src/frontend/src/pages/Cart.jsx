import { useCallback, useEffect, useMemo, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import {
    countItemsInOrders,
    deleteOrder,
    fetchPendingOrders,
    fetchActiveCartOrders,
    setCartItemQuantity,
} from "../api/orders";
import { fetchRestaurantById, parseUserIdFromStorage } from "../api/restaurants";
import { fetchActiveOffer } from "../api/offers";
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
        activeOffer: null,
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
            const orders = await fetchPendingOrders({ userId });
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
                activeOffer: null,
            });

            // Try to fetch currently active offer (if any)
            try {
                const active = await fetchActiveOffer();
                setCartState((prev) => ({ ...prev, activeOffer: active }));
            } catch (err) {
                if (err?.status === 401) {
                    redirectToLogin();
                    return;
                }
                // 404 or other errors -> treat as no active offer
            }

            setQuantityDrafts((prev) => {
                const nextDrafts = {};
                orders.forEach((order) => {
                    (order.order_items || []).forEach((item) => {
                        const key = buildItemDraftKey(order.id, item.item_id);
                        nextDrafts[key] = key in prev ? prev[key] : item.quantity;
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

    const totalItemCount = useMemo(() => {
        return cartState.orders.reduce((total, order) => {
            return total + (order.order_items || []).reduce((sum, orderItem) => {
                const itemKey = buildItemDraftKey(order.id, orderItem.item_id);
                return sum + (quantityDrafts[itemKey] ?? orderItem.quantity);
            }, 0);
        }, 0);
    }, [cartState.orders, quantityDrafts]);


    const grandTotal = useMemo(() => {
        return cartState.orders.reduce((sum, order) => {
            const taxRate = order.subtotal_price > 0 ? order.tax / order.subtotal_price : 0;
            let draftSubtotal = (order.order_items || []).reduce((orderSum, orderItem) => {
                const itemKey = buildItemDraftKey(order.id, orderItem.item_id);
                const menuItem = cartState.restaurantsById[order.restaurant_id]?.menu_items?.find(
                    (item) => item.id === orderItem.item_id
                );
                const price = Number(menuItem?.price ?? orderItem.price_at_purchase);
                const qty = quantityDrafts[itemKey] ?? orderItem.quantity;
                return orderSum + price * qty;
            }, 0);

            // Apply active offer adjustments (mirror backend logic)
            const activeOffer = cartState.activeOffer;
            if (activeOffer && activeOffer.restaurant_id === order.restaurant_id) {
                // Offer types: 1=DISCOUNT,2=FREE_ITEM,3=PRICE_CEILING
                if (Number(activeOffer.offer_type) === 1) {
                    if (typeof activeOffer.discount_value === "number") {
                        draftSubtotal = draftSubtotal * (1 - activeOffer.discount_value / 100);
                    }
                } else if (Number(activeOffer.offer_type) === 2) {
                    for (const freeItemId of activeOffer.applied_items || []) {
                        for (const item of order.order_items || []) {
                            if (item.item_id === freeItemId) {
                                const menuItem = cartState.restaurantsById[order.restaurant_id]?.menu_items?.find(
                                    (m) => m.id === item.item_id
                                );
                                const price = Number(menuItem?.price ?? item.price_at_purchase);
                                if (draftSubtotal - price > 0) {
                                    draftSubtotal -= price;
                                }
                                break;
                            }
                        }
                    }
                } else if (Number(activeOffer.offer_type) === 3) {
                    for (const appliedId of activeOffer.applied_items || []) {
                        for (const item of order.order_items || []) {
                            if (item.item_id === appliedId) {
                                const menuItem = cartState.restaurantsById[order.restaurant_id]?.menu_items?.find(
                                    (m) => m.id === item.item_id
                                );
                                const price = Number(menuItem?.price ?? item.price_at_purchase);
                                if (typeof activeOffer.price_ceiling === "number") {
                                    draftSubtotal -= (price - activeOffer.price_ceiling);
                                }
                                break;
                            }
                        }
                    }
                }
            }

            return sum + draftSubtotal + draftSubtotal * taxRate + Number(order.delivery_fee);
        }, 0);
    }, [cartState.orders, cartState.restaurantsById, quantityDrafts, cartState.activeOffer]);




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
            ? 1
            : Math.min(Math.max(1, Math.floor(parsed)), 99);

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

    const handleDeleteOrder = async (orderId) => {
        try {
            await deleteOrder(orderId, userId);
            await loadCart();
        } catch (error) {
            setCartState((prev) => ({ ...prev, error: error.message || "Could not delete order." }));
        }
    };

    const handleCheckout = async () => {
        for (const order of cartState.orders) {
            for (const orderItem of (order.order_items || [])) {
                const itemKey = buildItemDraftKey(order.id, orderItem.item_id);
                const draftQty = quantityDrafts[itemKey] ?? orderItem.quantity;
                if (Number(draftQty) !== orderItem.quantity) {
                    await handleUpdateQuantity(order, orderItem, Number(draftQty));
                }
            }
        }
        navigate("/payment", {
            state: {
                orderIds: cartState.orders.map((o) => o.id),
                orderTotals: Object.fromEntries(
                    cartState.orders.map((o) => [o.id, Number(o.total_price || 1)])
                ),
            },
        });
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
                    <>
                        <div className="cart-order-list">
                            {cartState.orders.map((order) => {
                                const restaurant = cartState.restaurantsById[order.restaurant_id];

                                return (
                                    <article key={order.id} className="cart-order-card">
                                        <header className="cart-order-header">
                                            <h3>{restaurant?.name || `Restaurant #${order.restaurant_id}`}</h3>
                                            <small>Order #{order.id}</small>
                                            {(order.order_items || []).length === 0 && (
                                                <button
                                                    type="button"
                                                    className="cart-remove-button"
                                                    onClick={() => handleDeleteOrder(order.id)}
                                                >
                                                    Delete order
                                                </button>
                                            )}
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
                                                                ${itemPrice.toFixed(2)} each &mdash; ${(itemPrice * draftQuantity).toFixed(2)}
                                                            </p>
                                                        </div>

                                                        <div className="cart-item-actions">
                                                            <input
                                                                type="number"
                                                                min="1"
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
                                        <footer className="cart-order-footer">
                                            {(() => {
                                                const taxRate = order.subtotal_price > 0 ? order.tax / order.subtotal_price : 0;
                                                let draftSubtotal = (order.order_items || []).reduce((sum, orderItem) => {
                                                    const itemKey = buildItemDraftKey(order.id, orderItem.item_id);
                                                    const menuItem = resolveMenuItem(order, orderItem);
                                                    const price = Number(menuItem?.price ?? orderItem.price_at_purchase);
                                                    const qty = quantityDrafts[itemKey] ?? orderItem.quantity;
                                                    return sum + price * qty;
                                                }, 0);

                                                // Apply active offer adjustments
                                                const activeOffer = cartState.activeOffer;
                                                if (activeOffer && activeOffer.restaurant_id === order.restaurant_id) {
                                                    if (Number(activeOffer.offer_type) === 1) {
                                                        if (typeof activeOffer.discount_value === "number") {
                                                            draftSubtotal = draftSubtotal * (1 - activeOffer.discount_value / 100);
                                                        }
                                                    } else if (Number(activeOffer.offer_type) === 2) {
                                                        for (const freeItemId of activeOffer.applied_items || []) {
                                                            for (const item of order.order_items || []) {
                                                                if (item.item_id === freeItemId) {
                                                                    const menuItem = resolveMenuItem(order, item);
                                                                    const price = Number(menuItem?.price ?? item.price_at_purchase);
                                                                    if (draftSubtotal - price > 0) {
                                                                        draftSubtotal -= price;
                                                                    }
                                                                    break;
                                                                }
                                                            }
                                                        }
                                                    } else if (Number(activeOffer.offer_type) === 3) {
                                                        for (const appliedId of activeOffer.applied_items || []) {
                                                            for (const item of order.order_items || []) {
                                                                if (item.item_id === appliedId) {
                                                                    const menuItem = resolveMenuItem(order, item);
                                                                    const price = Number(menuItem?.price ?? item.price_at_purchase);
                                                                    if (typeof activeOffer.price_ceiling === "number") {
                                                                        draftSubtotal -= (price - activeOffer.price_ceiling);
                                                                    }
                                                                    break;
                                                                }
                                                            }
                                                        }
                                                    }
                                                }

                                                const draftTax = draftSubtotal * taxRate;
                                                const draftTotal = draftSubtotal + draftTax + order.delivery_fee;
                                                return (
                                                    <>
                                                        <p className="cart-summary-row">Subtotal: ${draftSubtotal.toFixed(2)}</p>
                                                        <p className="cart-summary-row">Tax: ${draftTax.toFixed(2)}</p>
                                                        <p className="cart-summary-row">Delivery fee: ${Number(order.delivery_fee).toFixed(2)}</p>
                                                    </>
                                                );
                                            })()}
                                        </footer>
                                    </article>
                                );
                            })}
                        </div>
                        {cartState.orders.length > 0 && (
                            <div className="cart-grand-total">
                                Grand total: <strong>${grandTotal.toFixed(2)}</strong>
                                <button
                                    type="button"
                                    className="cart-checkout-button"
                                    onClick={handleCheckout}
                                >
                                    Proceed to Checkout
                                </button>
                            </div>
                        )}
                    </>
                )}
            </section>
        </main >
    );
}
