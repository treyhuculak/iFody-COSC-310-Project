import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import {
    deleteOrder,
    fetchDeliveryByOrder,
    fetchPendingOrders,
    setCartItemQuantity,
} from "../api/orders";
import {
    fetchPaymentMethodsByUser,
    getPaymentLabel,
    updatePaymentMethod,
} from "../api/payments";
import { fetchRestaurantById, parseUserIdFromStorage } from "../api/restaurants";
import { fetchActiveOffer } from "../api/offers";
import { createTransaction } from "../api/transactions";
import "../styles/cart.css";

const CHECKOUT_SECONDS = 10;

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

    const [paymentMethods, setPaymentMethods] = useState([]);
    const [selectedPaymentMethodId, setSelectedPaymentMethodId] = useState("");
    const [checkoutBusy, setCheckoutBusy] = useState(false);
    const [deliveriesByOrderId, setDeliveriesByOrderId] = useState({});
    const [checkoutCountdown, setCheckoutCountdown] = useState(null);
    const [checkoutMessage, setCheckoutMessage] = useState("");
    const [pendingCheckout, setPendingCheckout] = useState(null);
    const timerRef = useRef(null);
    const checkoutTriggeredRef = useRef(false);

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
            
            const deliveryEntries = await Promise.all(
                orders.map(async (order) => {
                    try {
                        const delivery = await fetchDeliveryByOrder(order.id);
                        return [order.id, delivery];
                    } catch {
                        return [order.id, null];
                    }
                })
            );

            const deliveriesMap = Object.fromEntries(
                deliveryEntries.filter(([, delivery]) => delivery)
            );

            setCartState({
                loading: false,
                error: "",
                orders,
                restaurantsById,
                activeOffer: null,
            });

            setDeliveriesByOrderId(deliveriesMap);

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

            setDeliveriesByOrderId({});
        }
    }, [redirectToLogin, userId]);

    const loadPaymentMethods = useCallback(async () => {
        if (!userId) return;

        try {
            const methods = await fetchPaymentMethodsByUser(userId);
            const safeMethods = Array.isArray(methods) ? methods : [];

            setPaymentMethods(safeMethods);

            setSelectedPaymentMethodId((prev) => {
                if (prev && safeMethods.some((item) => String(item.id) === String(prev))) {
                    return String(prev);
                }

                const activeMethod = safeMethods.find((item) => item.is_active);
                if (activeMethod) return String(activeMethod.id);

                if (safeMethods.length > 0) return String(safeMethods[0].id);

                return "";
            });
        } catch (error) {
            if (error?.status === 401) {
                redirectToLogin();
                return;
            }

            setPaymentMethods([]);
            setSelectedPaymentMethodId("");
            setCartState((prev) => ({
                ...prev,
                error: prev.error || error.message || "Could not load payment methods.",
            }));
        }
    }, [redirectToLogin, userId]);

    useEffect(() => {
        if (!userId) {
            redirectToLogin();
            return;
        }

        loadCart();
        loadPaymentMethods();
    }, [loadCart, loadPaymentMethods, redirectToLogin, userId]);

    useEffect(() => {
        const handleCartUpdated = () => {
            loadCart();
        };

        window.addEventListener("cart:updated", handleCartUpdated);
        return () => {
            window.removeEventListener("cart:updated", handleCartUpdated);
        };
    }, [loadCart]);

    useEffect(() => {
        return () => {
            if (timerRef.current) {
                clearInterval(timerRef.current);
            }
        };
    }, []);

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
            const taxRate =
                Number(order.subtotal_price) > 0
                    ? Number(order.tax) / Number(order.subtotal_price)
                    : 0;

            let draftSubtotal = (order.order_items || []).reduce((orderSum, orderItem) => {
                const itemKey = buildItemDraftKey(order.id, orderItem.item_id);
                const menuItem = cartState.restaurantsById[order.restaurant_id]?.menu_items?.find(
                    (item) => item.id === orderItem.item_id
                );
                const price = Number(menuItem?.price ?? orderItem.price_at_purchase ?? 0);
                const qty = Number(quantityDrafts[itemKey] ?? orderItem.quantity ?? 0);
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

    const selectedPaymentMethod = useMemo(() => {
        return (
            paymentMethods.find(
                (item) => String(item.id) === String(selectedPaymentMethodId)
            ) || null
        );
    }, [paymentMethods, selectedPaymentMethodId]);

    const resolveMenuItem = useCallback(
        (order, orderItem) => {
            const restaurant = cartState.restaurantsById[order.restaurant_id];
            if (!restaurant || !Array.isArray(restaurant.menu_items)) {
                return null;
            }

            return restaurant.menu_items.find((item) => item.id === orderItem.item_id) || null;
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
            price: Number(menuItem?.price ?? orderItem.price_at_purchase ?? 0),
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
            setCartState((prev) => ({
                ...prev,
                error: error.message || "Could not delete order.",
            }));
        }
    };

    const syncDraftQuantities = async () => {
        for (const order of cartState.orders) {
            for (const orderItem of order.order_items || []) {
                const itemKey = buildItemDraftKey(order.id, orderItem.item_id);
                const draftQty = quantityDrafts[itemKey] ?? orderItem.quantity;

                if (Number(draftQty) !== Number(orderItem.quantity)) {
                    await handleUpdateQuantity(order, orderItem, Number(draftQty));
                }
            }
        }
    };

    const clearPendingCheckout = () => {
        if (timerRef.current) {
            clearInterval(timerRef.current);
            timerRef.current = null;
        }
        checkoutTriggeredRef.current = false;
        setCheckoutCountdown(null);
        setPendingCheckout(null);
    };

    const cancelPendingCheckout = () => {
        clearPendingCheckout();
        checkoutTriggeredRef.current = false;
        setCheckoutBusy(false);
        setCheckoutMessage("Checkout cancelled before any transaction was created.");
    };

    const finalizeStandardCheckout = async (checkoutPayload) => {
        if (checkoutTriggeredRef.current) return;
        checkoutTriggeredRef.current = true;
        setCheckoutBusy(true);
        setCartState((prev) => ({ ...prev, error: "" }));
        setCheckoutMessage("");

        try {
            const createdTransactions = [];

            for (const order of checkoutPayload.orders) {
                const created = await createTransaction({
                    payment_method_id: checkoutPayload.payment_method_id,
                    order_id: order.id,
                    amount: Number(order.total),
                });
                createdTransactions.push(created);
            }

            clearPendingCheckout();
            navigate("/order-tracking", {
                state: {
                    orderIds: checkoutPayload.orders.map((o) => o.id),
                    transactionIds: createdTransactions.map((t) => t.id),
                },
            });
        } catch (error) {
            clearPendingCheckout();
            setCartState((prev) => ({
                ...prev,
                error: error.message || "Could not create the checkout transaction.",
            }));
        } finally {
            setCheckoutBusy(false);
        }
    };

    const handlePaymentMethodChange = async (event) => {
        const newMethodId = String(event.target.value);
        setSelectedPaymentMethodId(newMethodId);

        const chosenMethod = paymentMethods.find(
            (item) => String(item.id) === newMethodId
        );

        if (!chosenMethod) return;

        try {
            const payload = {
                user_id: chosenMethod.user_id,
                method: chosenMethod.method,
                is_active: true,
            };

            if (chosenMethod.card_type !== undefined) payload.card_type = chosenMethod.card_type;
            if (chosenMethod.card_number !== undefined) payload.card_number = chosenMethod.card_number;
            if (chosenMethod.expiry_date !== undefined) payload.expiry_date = chosenMethod.expiry_date;
            if (chosenMethod.cv2 !== undefined) payload.cv2 = chosenMethod.cv2;
            if (chosenMethod.paypal_email !== undefined) payload.paypal_email = chosenMethod.paypal_email;

            await updatePaymentMethod(chosenMethod.id, payload);

            setPaymentMethods((prev) =>
                prev.map((method) => ({
                    ...method,
                    is_active: String(method.id) === newMethodId,
                }))
            );
        } catch (error) {
            setCartState((prev) => ({
                ...prev,
                error: error.message || "Could not set default payment method.",
            }));
        }
    };

    const handleCheckout = async () => {
        setCheckoutMessage("");
        setCartState((prev) => ({ ...prev, error: "" }));

        if (paymentMethods.length === 0) {
            setCartState((prev) => ({
                ...prev,
                error: "Add a payment method first using the Manage payments button.",
            }));
            return;
        }

        if (!selectedPaymentMethod) {
            setCartState((prev) => ({
                ...prev,
                error: "Choose a payment method before checkout.",
            }));
            return;
        }

        await syncDraftQuantities();

        const checkoutOrders = cartState.orders.map((order) => ({
            id: order.id,
            total: Number(order.total_price || 0),
        }));

        if (checkoutOrders.length === 0) {
            setCartState((prev) => ({
                ...prev,
                error: "Your cart is empty.",
            }));
            return;
        }

        if (selectedPaymentMethod.method === "paypal") {
            navigate("/paypal", {
                state: {
                    orderIds: checkoutOrders.map((order) => order.id),
                    orderTotals: Object.fromEntries(
                        checkoutOrders.map((order) => [order.id, order.total])
                    ),
                    preferredPaymentMethodId: Number(selectedPaymentMethod.id),
                },
            });
            return;
        }

        clearPendingCheckout();
        setPendingCheckout({
            payment_method_id: Number(selectedPaymentMethod.id),
            payment_label: getPaymentLabel(selectedPaymentMethod.method),
            orders: checkoutOrders,
        });
        setCheckoutCountdown(CHECKOUT_SECONDS);
        setCheckoutMessage(
            "Checkout started. You have 10 seconds to cancel before transactions are created."
        );

        timerRef.current = setInterval(() => {
            setCheckoutCountdown((prev) => {
                if (prev === null) return null;

                if (prev <= 1) {
                    if (timerRef.current) {
                        clearInterval(timerRef.current);
                        timerRef.current = null;
                    }

                    finalizeStandardCheckout({
                        payment_method_id: Number(selectedPaymentMethod.id),
                        orders: checkoutOrders,
                    });

                    return 0;
                }

                return prev - 1;
            });
        }, 1000);
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
            {checkoutMessage ? <p className="status-success">{checkoutMessage}</p> : null}

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
                                            <div>
                                                <h3>{restaurant?.name || `Restaurant #${order.restaurant_id}`}</h3>
                                                <small>Order #{order.id}</small>
                                                <p className="cart-order-status">
                                                    Status: <strong>{order.status}</strong>
                                                </p>

                                                {deliveriesByOrderId[order.id] ? (
                                                    <p style={{ marginTop: "0.5rem" }}>
                                                        <Link
                                                            to="/order-tracking"
                                                            state={{ orderIds: [order.id] }}
                                                            className="restaurant-back-link"
                                                        >
                                                            Go to delivery view
                                                        </Link>
                                                    </p>
                                                ) : null}
                                            </div>

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
                                                const itemName = menuItem?.name || `Menu item #${orderItem.item_id}`;
                                                const itemPrice = Number(
                                                    menuItem?.price ?? orderItem.price_at_purchase ?? 0
                                                );
                                                const draftQuantity =
                                                    quantityDrafts[itemKey] ?? orderItem.quantity;
                                                const isPending = pendingItemKey === itemKey;

                                                return (
                                                    <div key={itemKey} className="cart-item-row">
                                                        <div className="cart-item-main">
                                                            <p className="cart-item-name">{itemName}</p>
                                                            <p className="cart-item-meta">
                                                                ${itemPrice.toFixed(2)} each &mdash; $
                                                                {(itemPrice * draftQuantity).toFixed(2)}
                                                            </p>
                                                        </div>

                                                        <div className="cart-item-actions">
                                                            <input
                                                                type="number"
                                                                min="1"
                                                                step="1"
                                                                value={draftQuantity}
                                                                disabled={
                                                                    isPending ||
                                                                    checkoutBusy ||
                                                                    checkoutCountdown !== null
                                                                }
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
                                                                disabled={
                                                                    isPending ||
                                                                    checkoutBusy ||
                                                                    checkoutCountdown !== null
                                                                }
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
                                                const taxRate =
                                                    Number(order.subtotal_price) > 0
                                                        ? Number(order.tax) / Number(order.subtotal_price)
                                                        : 0;

                                                let draftSubtotal = (order.order_items || []).reduce(
                                                    (sum, orderItem) => {
                                                        const itemKey = buildItemDraftKey(
                                                            order.id,
                                                            orderItem.item_id
                                                        );
                                                        const menuItem = resolveMenuItem(order, orderItem);
                                                        const price = Number(
                                                            menuItem?.price ??
                                                                orderItem.price_at_purchase ??
                                                                0
                                                        );
                                                        const qty = Number(
                                                            quantityDrafts[itemKey] ?? orderItem.quantity ?? 0
                                                        );
                                                        return sum + price * qty;
                                                    },
                                                    0
                                                );

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

                                                return (
                                                    <>
                                                        <p className="cart-summary-row">
                                                            Subtotal: ${draftSubtotal.toFixed(2)}
                                                        </p>
                                                        <p className="cart-summary-row">
                                                            Tax: ${draftTax.toFixed(2)}
                                                        </p>
                                                        <p className="cart-summary-row">
                                                            Delivery fee: $
                                                            {Number(order.delivery_fee || 0).toFixed(2)}
                                                        </p>
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
                                <div className="cart-payment-panel">
                                    <div className="cart-payment-header-row">
                                        <label
                                            className="cart-payment-label"
                                            htmlFor="cart-payment-method"
                                        >
                                            Payment method for checkout
                                        </label>

                                        <Link
                                            to="/payment"
                                            className="cart-manage-payments-button"
                                        >
                                            Manage payments
                                        </Link>
                                    </div>

                                    {paymentMethods.length > 0 ? (
                                        <>
                                            <select
                                                id="cart-payment-method"
                                                className="cart-payment-select"
                                                value={selectedPaymentMethodId}
                                                onChange={handlePaymentMethodChange}
                                                disabled={
                                                    checkoutBusy || checkoutCountdown !== null
                                                }
                                            >
                                                {paymentMethods.map((payment) => (
                                                    <option key={payment.id} value={payment.id}>
                                                        #{payment.id} — {getPaymentLabel(payment.method)}
                                                        {payment.is_active ? " (default)" : ""}
                                                    </option>
                                                ))}
                                            </select>

                                            <p className="cart-payment-helper">
                                                {selectedPaymentMethod?.method === "paypal"
                                                    ? "PayPal checkout opens the PayPal page so you can approve and capture the payment."
                                                    : "Standard checkout creates transactions after the 10-second countdown ends."}
                                            </p>
                                        </>
                                    ) : (
                                        <div className="cart-no-payment-box">
                                            <p className="cart-payment-helper">
                                                No payment methods found yet. Click "Manage payments" to add one.
                                            </p>
                                        </div>
                                    )}
                                </div>

                                <div className="cart-checkout-row">
                                    <span>
                                        Grand total: <strong>${grandTotal.toFixed(2)}</strong>
                                    </span>
                                    <button
                                        type="button"
                                        className="cart-checkout-button"
                                        onClick={handleCheckout}
                                        disabled={checkoutBusy || cartState.loading}
                                    >
                                        {checkoutBusy
                                            ? "Creating transactions..."
                                            : selectedPaymentMethod?.method === "paypal"
                                            ? "Continue to PayPal"
                                            : "Proceed to Checkout"}
                                    </button>
                                </div>

                                {checkoutCountdown !== null && pendingCheckout ? (
                                    <div className="cart-checkout-timer-card">
                                        <p>
                                            Checkout with <strong>{pendingCheckout.payment_label}</strong> will create
                                            <strong> {pendingCheckout.orders.length}</strong>
                                            {pendingCheckout.orders.length === 1
                                                ? " transaction"
                                                : " transactions"}{" "}
                                            in <strong>{checkoutCountdown}s</strong>.
                                        </p>
                                        <button
                                            type="button"
                                            className="cart-remove-button"
                                            onClick={cancelPendingCheckout}
                                        >
                                            Cancel checkout
                                        </button>
                                    </div>
                                ) : null}
                            </div>
                        )}
                    </>
                )}
            </section>
        </main>
    );
}