import { useEffect, useRef, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import {
    fetchDeliveryByOrder,
    markDeliveryDelivered,
    updateOrderStatus,
} from "../api/orders";
import { parseUserIdFromStorage } from "../api/restaurants";
import "../styles/order-tracking.css";

const PREPARING_SECONDS = 10;
const DELIVERY_SECONDS = 10;

function formatTime(ts) {
    if (!ts) return "—";
    try {
        return new Date(ts).toLocaleString();
    } catch {
        return String(ts);
    }
}

function ProgressBar({ elapsed, total }) {
    const pct = Math.min(100, Math.round((elapsed / total) * 100));
    return (
        <div className="tracking-progress-bar">
            <div className="tracking-progress-fill" style={{ width: `${pct}%` }} />
        </div>
    );
}

function TrackingCard({ orderId, state }) {
    const { phase, countdown, deliveryInfo, deliveredAt, error } = state;

    const preparingElapsed = PREPARING_SECONDS - (phase === "preparing" ? countdown : 0);
    const deliveryElapsed = DELIVERY_SECONDS - (phase === "out_for_delivery" ? countdown : 0);

    return (
        <article className="tracking-card">
            <div className="tracking-card-header">
                <h3>Order #{orderId}</h3>
                <span className={`tracking-status-badge tracking-status-${phase}`}>
                    {phase === "preparing"
                        ? "Preparing"
                        : phase === "out_for_delivery"
                        ? "Out for Delivery"
                        : phase === "delivered"
                        ? "Delivered"
                        : "Error"}
                </span>
            </div>

            {phase === "preparing" && (
                <div className="tracking-phase-info">
                    <p className="tracking-phase-label">Your order is being prepared in the kitchen…</p>
                    <div className="tracking-countdown-row">
                        <span className="tracking-countdown-num">{countdown}</span>
                        <span className="tracking-countdown-unit">s until pickup</span>
                    </div>
                    <ProgressBar elapsed={preparingElapsed} total={PREPARING_SECONDS} />
                </div>
            )}

            {(phase === "out_for_delivery" || phase === "delivered") && deliveryInfo && (
                <div className="tracking-delivery-info">
                    <div className="tracking-info-row">
                        <span className="tracking-info-label">Driver ID</span>
                        <span className="tracking-info-value">#{deliveryInfo.driver_id}</span>
                    </div>
                    <div className="tracking-info-row">
                        <span className="tracking-info-label">Assigned at</span>
                        <span className="tracking-info-value">{formatTime(deliveryInfo.assigned_at)}</span>
                    </div>
                    <div className="tracking-info-row">
                        <span className="tracking-info-label">Estimated delivery</span>
                        <span className="tracking-info-value">
                            {formatTime(deliveryInfo.estimated_delivery_time)}
                        </span>
                    </div>
                    {phase === "delivered" && deliveredAt && (
                        <div className="tracking-info-row">
                            <span className="tracking-info-label">Delivered at</span>
                            <span className="tracking-info-value">{formatTime(deliveredAt)}</span>
                        </div>
                    )}
                </div>
            )}

            {phase === "out_for_delivery" && (
                <div className="tracking-phase-info">
                    <p className="tracking-phase-label">Your driver is on the way!</p>
                    <div className="tracking-countdown-row">
                        <span className="tracking-countdown-num">{countdown}</span>
                        <span className="tracking-countdown-unit">s until delivery</span>
                    </div>
                    <ProgressBar elapsed={deliveryElapsed} total={DELIVERY_SECONDS} />
                </div>
            )}

            {phase === "delivered" && (
                <div className="tracking-delivered-banner">✓ Delivered — enjoy your meal!</div>
            )}

            {phase === "error" && (
                <div className="tracking-error-banner">
                    {error || "An error occurred during order processing."}
                </div>
            )}
        </article>
    );
}

export default function OrderTracking() {
    const location = useLocation();
    const navigate = useNavigate();
    const userId = parseUserIdFromStorage();

    // Fall back to localStorage if state was lost (e.g. navigated away and came back)
    const orderIds = (() => {
        const fromState = location.state?.orderIds;
        if (Array.isArray(fromState) && fromState.length > 0) return fromState;
        try {
            const stored = localStorage.getItem("tracking_order_ids");
            return stored ? JSON.parse(stored) : [];
        } catch {
            return [];
        }
    })();

    const [orderStates, setOrderStates] = useState(() =>
        Object.fromEntries(
            orderIds.map((id) => [
                id,
                {
                    phase: "preparing",
                    countdown: PREPARING_SECONDS,
                    deliveryInfo: null,
                    deliveredAt: null,
                    error: null,
                },
            ])
        )
    );

    const timersRef = useRef({});
    // Keep a ref to always have current orderIds without needing them as a dep
    const orderIdsRef = useRef(orderIds);

    function patchOrder(orderId, patch) {
        setOrderStates((prev) => ({
            ...prev,
            [orderId]: { ...prev[orderId], ...patch },
        }));
    }

    useEffect(() => {
        if (orderIdsRef.current.length === 0) {
            navigate("/");
            return;
        }

        // Persist so the user can return to this page after navigating away
        try {
            localStorage.setItem("tracking_order_ids", JSON.stringify(orderIdsRef.current));
            window.dispatchEvent(new CustomEvent("tracking:updated"));
        } catch { /* ignore */ }

        orderIdsRef.current.forEach((orderId) => {
            runPreparingPhase(orderId);
        });

        return () => {
            Object.values(timersRef.current).forEach(clearInterval);
            timersRef.current = {};
        };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    function runPreparingPhase(orderId) {
        let remaining = PREPARING_SECONDS;
        const key = `prep-${orderId}`;

        timersRef.current[key] = setInterval(() => {
            remaining -= 1;
            patchOrder(orderId, { countdown: remaining });

            if (remaining <= 0) {
                clearInterval(timersRef.current[key]);
                delete timersRef.current[key];
                runOutForDeliveryTransition(orderId);
            }
        }, 1000);
    }

    async function runOutForDeliveryTransition(orderId) {
        try {
            await updateOrderStatus(orderId, "out for delivery");

            // The backend automatically creates the delivery record when status becomes
            // "out for delivery", so we just fetch it
            const delivery = await fetchDeliveryByOrder(orderId);

            patchOrder(orderId, {
                phase: "out_for_delivery",
                countdown: DELIVERY_SECONDS,
                deliveryInfo: delivery,
            });

            runDeliveryPhase(orderId, delivery);
        } catch (err) {
            patchOrder(orderId, { phase: "error", error: err.message });
        }
    }

    function runDeliveryPhase(orderId, deliveryInfo) {
        let remaining = DELIVERY_SECONDS;
        const key = `del-${orderId}`;

        timersRef.current[key] = setInterval(() => {
            remaining -= 1;
            patchOrder(orderId, { countdown: remaining });

            if (remaining <= 0) {
                clearInterval(timersRef.current[key]);
                delete timersRef.current[key];
                runDeliveredTransition(orderId, deliveryInfo);
            }
        }, 1000);
    }

    async function runDeliveredTransition(orderId, deliveryInfo) {
        try {
            await updateOrderStatus(orderId, "delivered");

            const now = new Date().toISOString();

            // Record the delivered_at time on the delivery record (non-fatal if it fails)
            if (deliveryInfo?.id) {
                try {
                    await markDeliveryDelivered(deliveryInfo.id, now);
                } catch {
                    // ignore
                }
            }

            patchOrder(orderId, {
                phase: "delivered",
                countdown: 0,
                deliveredAt: now,
            });
        } catch (err) {
            patchOrder(orderId, { phase: "error", error: err.message });
        }
    }

    const allSettled = orderIds.length > 0 &&
        orderIds.every((id) => {
            const phase = orderStates[id]?.phase;
            return phase === "delivered" || phase === "error";
        });

    // Once all orders are done, remove the tracking record from localStorage
    useEffect(() => {
        if (allSettled) {
            try {
                localStorage.removeItem("tracking_order_ids");
                window.dispatchEvent(new CustomEvent("tracking:updated"));
            } catch { /* ignore */ }
        }
    }, [allSettled]);

    return (
        <main className="home-page order-tracking-page">
            <section className="hero-banner">
                <p className="hero-kicker">Live Tracking</p>
                <h1>Your order is on its way!</h1>
                <p className="hero-subtitle">
                    We'll update you as your order moves through each stage.
                </p>
            </section>

            <section className="restaurant-section">
                {orderIds.length === 0 ? (
                    <div className="section-placeholder">
                        No orders to track.{" "}
                        <Link to="/" className="restaurant-back-link">
                            Browse restaurants
                        </Link>
                    </div>
                ) : (
                    <div className="tracking-list">
                        {orderIds.map((id) => (
                            <TrackingCard key={id} orderId={id} state={orderStates[id] ?? {}} />
                        ))}
                    </div>
                )}

                {allSettled && (
                    <div className="tracking-done-row">
                        <p className="tracking-done-message">All orders have been delivered!</p>
                        <Link to="/orders" className="tracking-history-link">
                            View Order History
                        </Link>
                    </div>
                )}
            </section>
        </main>
    );
}
