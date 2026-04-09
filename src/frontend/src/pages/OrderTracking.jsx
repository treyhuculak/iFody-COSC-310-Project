import { useEffect, useMemo, useRef, useState } from "react";
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
const TRACKING_STATE_KEY = "tracking_order_states";

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

function readTrackingStateMap() {
    try {
        const raw = localStorage.getItem(TRACKING_STATE_KEY);
        if (!raw) return {};
        const parsed = JSON.parse(raw);
        return parsed && typeof parsed === "object" ? parsed : {};
    } catch {
        return {};
    }
}

function writeTrackingStateMap(map) {
    try {
        localStorage.setItem(TRACKING_STATE_KEY, JSON.stringify(map));
    } catch {
        // ignore storage failures
    }
}

function getCountdownFromEnd(phaseEndsAt) {
    if (!phaseEndsAt) return 0;
    const diffMs = new Date(phaseEndsAt).getTime() - Date.now();
    return Math.max(0, Math.ceil(diffMs / 1000));
}

function createFreshPreparingState() {
    return {
        phase: "preparing",
        countdown: PREPARING_SECONDS,
        deliveryInfo: null,
        deliveredAt: null,
        error: null,
        phaseStartedAt: new Date().toISOString(),
        phaseEndsAt: new Date(Date.now() + PREPARING_SECONDS * 1000).toISOString(),
    };
}

function buildInitialOrderState(orderId) {
    const stored = readTrackingStateMap()[orderId];
    if (!stored) {
        return createFreshPreparingState();
    }

    return {
        phase: stored.phase || "preparing",
        countdown: getCountdownFromEnd(stored.phaseEndsAt),
        deliveryInfo: stored.deliveryInfo || null,
        deliveredAt: stored.deliveredAt || null,
        error: stored.error || null,
        phaseStartedAt: stored.phaseStartedAt || new Date().toISOString(),
        phaseEndsAt: stored.phaseEndsAt || null,
    };
}

function persistOrderState(orderId, nextState) {
    const map = readTrackingStateMap();
    map[orderId] = nextState;
    writeTrackingStateMap(map);
}

function removePersistedOrderState(orderId) {
    const map = readTrackingStateMap();
    delete map[orderId];
    writeTrackingStateMap(map);
}

function TrackingCard({ orderId, state }) {
    const { phase, countdown, deliveryInfo, deliveredAt, error } = state;

    const preparingElapsed =
        phase === "preparing" ? PREPARING_SECONDS - countdown : PREPARING_SECONDS;

    const deliveryElapsed =
        phase === "out_for_delivery" ? DELIVERY_SECONDS - countdown : DELIVERY_SECONDS;

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

    const orderIds = useMemo(() => {
        const fromState = location.state?.orderIds;
        if (Array.isArray(fromState) && fromState.length > 0) return fromState;

        try {
            const stored = localStorage.getItem("tracking_order_ids");
            return stored ? JSON.parse(stored) : [];
        } catch {
            return [];
        }
    }, [location.state]);

    const [orderStates, setOrderStates] = useState(() =>
        Object.fromEntries(orderIds.map((id) => [id, buildInitialOrderState(id)]))
    );

    const orderStatesRef = useRef(orderStates);
    const intervalRef = useRef(null);
    const inFlightTransitionsRef = useRef({});

    useEffect(() => {
        orderStatesRef.current = orderStates;
    }, [orderStates]);

    function patchOrder(orderId, patchOrUpdater) {
        setOrderStates((prev) => {
            const current = prev[orderId] || buildInitialOrderState(orderId);
            const patch =
                typeof patchOrUpdater === "function" ? patchOrUpdater(current) : patchOrUpdater;
            const next = { ...current, ...patch };

            persistOrderState(orderId, next);

            return {
                ...prev,
                [orderId]: next,
            };
        });
    }

    useEffect(() => {
        if (!userId) {
            navigate("/login");
            return;
        }

        if (orderIds.length === 0) {
            navigate("/");
            return;
        }

        try {
            localStorage.setItem("tracking_order_ids", JSON.stringify(orderIds));
            window.dispatchEvent(new CustomEvent("tracking:updated"));
        } catch {
            // ignore
        }
    }, [navigate, orderIds, userId]);

    async function runOutForDeliveryTransition(orderId) {
        if (inFlightTransitionsRef.current[`out-${orderId}`]) return;
        inFlightTransitionsRef.current[`out-${orderId}`] = true;

        try {
            await updateOrderStatus(orderId, "out for delivery");
            const delivery = await fetchDeliveryByOrder(orderId);

            patchOrder(orderId, {
                phase: "out_for_delivery",
                countdown: DELIVERY_SECONDS,
                deliveryInfo: delivery,
                error: null,
                phaseStartedAt: new Date().toISOString(),
                phaseEndsAt: new Date(Date.now() + DELIVERY_SECONDS * 1000).toISOString(),
            });
        } catch (err) {
            patchOrder(orderId, {
                phase: "error",
                countdown: 0,
                error: err.message || "Failed to update order status.",
                phaseEndsAt: null,
            });
        } finally {
            delete inFlightTransitionsRef.current[`out-${orderId}`];
        }
    }

    async function runDeliveredTransition(orderId, deliveryInfo) {
        if (inFlightTransitionsRef.current[`done-${orderId}`]) return;
        inFlightTransitionsRef.current[`done-${orderId}`] = true;

        try {
            await updateOrderStatus(orderId, "delivered");

            const now = new Date().toISOString();

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
                error: null,
                phaseEndsAt: null,
            });
        } catch (err) {
            patchOrder(orderId, {
                phase: "error",
                countdown: 0,
                error: err.message || "Failed to mark order as delivered.",
                phaseEndsAt: null,
            });
        } finally {
            delete inFlightTransitionsRef.current[`done-${orderId}`];
        }
    }

    useEffect(() => {
        if (orderIds.length === 0) return;

        const tick = async () => {
            const currentStates = orderStatesRef.current;

            for (const orderId of orderIds) {
                const current = currentStates[orderId] || buildInitialOrderState(orderId);

                if (current.phase === "delivered" || current.phase === "error") {
                    continue;
                }

                const nextCountdown = getCountdownFromEnd(current.phaseEndsAt);

                if (nextCountdown !== current.countdown) {
                    patchOrder(orderId, { countdown: nextCountdown });
                }

                if (nextCountdown > 0) {
                    continue;
                }

                if (current.phase === "preparing") {
                    await runOutForDeliveryTransition(orderId);
                } else if (current.phase === "out_for_delivery") {
                    await runDeliveredTransition(orderId, current.deliveryInfo);
                }
            }
        };

        tick();
        intervalRef.current = setInterval(tick, 1000);

        return () => {
            if (intervalRef.current) {
                clearInterval(intervalRef.current);
                intervalRef.current = null;
            }
        };
    }, [orderIds]);

    const allSettled =
        orderIds.length > 0 &&
        orderIds.every((id) => {
            const phase = orderStates[id]?.phase;
            return phase === "delivered" || phase === "error";
        });

    useEffect(() => {
        if (!allSettled) return;

        try {
            localStorage.removeItem("tracking_order_ids");
            orderIds.forEach(removePersistedOrderState);
            window.dispatchEvent(new CustomEvent("tracking:updated"));
        } catch {
            // ignore
        }
    }, [allSettled, orderIds]);

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
                            <TrackingCard
                                key={id}
                                orderId={id}
                                state={orderStates[id] ?? buildInitialOrderState(id)}
                            />
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