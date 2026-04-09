import { useCallback, useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import {
    blockUser,
    deleteRestaurant,
    deleteUser,
    getAllOrders,
    getAverageDeliveryTime,
    getGrossRevenue,
    getMostPopularRestaurant,
    toggleRestaurantAvailability,
    unblockUser,
} from "../api/admin";
import { parseUserIdFromStorage } from "../api/restaurants";
import "../styles/admin.css";

export default function Admin() {
    const location = useLocation();
    const navigate = useNavigate();
    const userId = parseUserIdFromStorage();
    const userRole =
        typeof localStorage !== "undefined" ? localStorage.getItem("userRole") || "" : "";

    const redirectToLogin = useCallback(() => {
        const redirectPath = `${location.pathname}${location.search}`;
        navigate(`/login?${new URLSearchParams({ redirect: redirectPath })}`);
    }, [location.pathname, location.search, navigate]);

    // Stats
    const [totalOrders, setTotalOrders] = useState(null);
    const [avgDelivery, setAvgDelivery] = useState(null);
    const [mostPopular, setMostPopular] = useState(null);
    const [statsError, setStatsError] = useState("");

    // Orders table
    const [orders, setOrders] = useState([]);
    const [showOrders, setShowOrders] = useState(false);
    const [ordersError, setOrdersError] = useState("");
    const [ordersLoading, setOrdersLoading] = useState(false);

    // Revenue lookup
    const [revenueRestaurantId, setRevenueRestaurantId] = useState("");
    const [revenueResult, setRevenueResult] = useState(null);
    const [revenueError, setRevenueError] = useState("");
    const [revenueBusy, setRevenueBusy] = useState(false);

    // Restaurant management
    const [restIdInput, setRestIdInput] = useState("");
    const [restActionBusy, setRestActionBusy] = useState("");
    const [restActionMessage, setRestActionMessage] = useState("");
    const [restActionError, setRestActionError] = useState("");

    // Orders filter
    const [orderFilterId, setOrderFilterId] = useState("");

    // User management
    const [usernameInput, setUsernameInput] = useState("");
    const [userActionBusy, setUserActionBusy] = useState("");
    const [userActionMessage, setUserActionMessage] = useState("");
    const [userActionError, setUserActionError] = useState("");

    useEffect(() => {
        if (!userId || userRole !== "administrator") {
            redirectToLogin();
            return;
        }
        loadStats();
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [userId]);

    const loadStats = async () => {
        setStatsError("");
        try {
            const [ordersData, avgData, popularData] = await Promise.allSettled([
                getAllOrders(userId),
                getAverageDeliveryTime(userId),
                getMostPopularRestaurant(userId),
            ]);

            if (ordersData.status === "fulfilled") {
                const data = ordersData.value;
                setTotalOrders(Array.isArray(data) ? data.length : data?.count ?? "—");
            }
            if (avgData.status === "fulfilled") {
                const raw = avgData.value?.average_delivery_time ?? avgData.value?.average ?? avgData.value;
                setAvgDelivery(typeof raw === "number" ? raw.toFixed(1) + " min" : JSON.stringify(raw));
            }
            if (popularData.status === "fulfilled") {
                const data = popularData.value;
                setMostPopular(
                    data?.name ?? data?.restaurant_name ?? data?.restaurant_id ?? JSON.stringify(data)
                );
            }
        } catch (err) {
            setStatsError(err.message || "Failed to load stats.");
        }
    };

    const handleToggleOrders = async () => {
        if (showOrders) {
            setShowOrders(false);
            return;
        }
        setOrdersLoading(true);
        setOrdersError("");
        try {
            const data = await getAllOrders(userId);
            setOrders(Array.isArray(data) ? data : []);
            setShowOrders(true);
        } catch (err) {
            setOrdersError(err.message || "Failed to load orders.");
        } finally {
            setOrdersLoading(false);
        }
    };

    const handleRevenueSearch = async (e) => {
        e.preventDefault();
        if (!revenueRestaurantId) return;
        setRevenueBusy(true);
        setRevenueError("");
        setRevenueResult(null);
        try {
            const data = await getGrossRevenue(revenueRestaurantId, userId);
            setRevenueResult(data);
        } catch (err) {
            setRevenueError(err.message || "Failed to fetch gross revenue.");
        } finally {
            setRevenueBusy(false);
        }
    };

    const handleRestaurantAction = async (action) => {
        if (!restIdInput.trim()) return;
        setRestActionBusy(action);
        setRestActionMessage("");
        setRestActionError("");
        try {
            if (action === "enable") {
                await toggleRestaurantAvailability(restIdInput, true, userId);
                setRestActionMessage(`Restaurant ${restIdInput} is now enabled.`);
            } else if (action === "disable") {
                await toggleRestaurantAvailability(restIdInput, false, userId);
                setRestActionMessage(`Restaurant ${restIdInput} has been disabled.`);
            } else if (action === "delete") {
                await deleteRestaurant(restIdInput, userId);
                setRestActionMessage(`Restaurant ${restIdInput} has been deleted.`);
                setRestIdInput("");
            }
        } catch (err) {
            setRestActionError(err.message || "Action failed.");
        } finally {
            setRestActionBusy("");
        }
    };

    const handleUserAction = async (action) => {
        if (!usernameInput.trim()) return;
        setUserActionBusy(action);
        setUserActionMessage("");
        setUserActionError("");
        try {
            if (action === "block") {
                await blockUser(usernameInput.trim(), userId);
                setUserActionMessage(`User "${usernameInput.trim()}" has been blocked.`);
            } else if (action === "unblock") {
                await unblockUser(usernameInput.trim(), userId);
                setUserActionMessage(`User "${usernameInput.trim()}" has been unblocked.`);
            } else if (action === "delete") {
                await deleteUser(usernameInput.trim(), userId);
                setUserActionMessage(`User "${usernameInput.trim()}" has been deleted.`);
                setUsernameInput("");
            }
        } catch (err) {
            setUserActionError(err.message || "Action failed.");
        } finally {
            setUserActionBusy("");
        }
    };

    return (
        <main className="home-page">
            <section className="hero-banner">
                <p className="hero-kicker">Administration</p>
                <h1>Admin Dashboard</h1>
                <p className="hero-subtitle">Manage users, monitor orders, and view platform statistics.</p>
            </section>

            {statsError && <p className="status-error">{statsError}</p>}

            {/* Stats */}
            <section className="restaurant-section">
                <h2 className="section-title">Platform Statistics</h2>
                <div className="admin-stats-grid">
                    <div className="admin-stat-card">
                        <span className="admin-stat-label">Total Orders</span>
                        <span className="admin-stat-value">{totalOrders ?? "—"}</span>
                    </div>
                    <div className="admin-stat-card">
                        <span className="admin-stat-label">Avg Delivery Time</span>
                        <span className="admin-stat-value">{avgDelivery ?? "—"}</span>
                    </div>
                    <div className="admin-stat-card">
                        <span className="admin-stat-label">Most Popular Restaurant</span>
                        <span className="admin-stat-value" style={{ fontSize: "1rem" }}>
                            {mostPopular ?? "—"}
                        </span>
                    </div>
                </div>

                {/* All orders table with filter */}
                <button type="button" className="admin-toggle-btn" onClick={handleToggleOrders} disabled={ordersLoading}>
                    {ordersLoading ? "Loading…" : showOrders ? "Hide all orders" : "Show all orders"}
                </button>
                {ordersError && <p className="status-error">{ordersError}</p>}
                {showOrders && (
                    <>
                        <div className="admin-lookup-form" style={{ marginTop: "0.75rem" }}>
                            <label>
                                Filter by Restaurant ID
                                <input
                                    type="number"
                                    min="1"
                                    value={orderFilterId}
                                    onChange={(e) => setOrderFilterId(e.target.value)}
                                    placeholder="All restaurants"
                                />
                            </label>
                        </div>
                        {orders.filter((o) => !orderFilterId || String(o.restaurant_id) === orderFilterId).length > 0 ? (
                            <div className="admin-table-wrap">
                                <table className="admin-table">
                                    <thead>
                                        <tr>
                                            <th>ID</th>
                                            <th>Customer</th>
                                            <th>Restaurant</th>
                                            <th>Status</th>
                                            <th>Total</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {orders
                                            .filter((o) => !orderFilterId || String(o.restaurant_id) === orderFilterId)
                                            .map((o) => (
                                                <tr key={o.id}>
                                                    <td>{o.id}</td>
                                                    <td>{o.customer_id}</td>
                                                    <td>{o.restaurant_id}</td>
                                                    <td>{o.status}</td>
                                                    <td>${Number(o.total_price ?? 0).toFixed(2)}</td>
                                                </tr>
                                            ))}
                                    </tbody>
                                </table>
                            </div>
                        ) : (
                            <div className="section-placeholder">No orders found.</div>
                        )}
                    </>
                )}
            </section>

            {/* Gross revenue lookup */}
            <section className="restaurant-section">
                <h2 className="section-title">Gross Revenue by Restaurant</h2>
                <form className="admin-lookup-form" onSubmit={handleRevenueSearch}>
                    <label>
                        Restaurant ID
                        <input
                            type="number"
                            min="1"
                            value={revenueRestaurantId}
                            onChange={(e) => setRevenueRestaurantId(e.target.value)}
                            placeholder="e.g. 1"
                            required
                        />
                    </label>
                    <button type="submit" disabled={revenueBusy}>
                        {revenueBusy ? "Loading…" : "Look up"}
                    </button>
                </form>
                {revenueError && <p className="status-error">{revenueError}</p>}
                {revenueResult !== null && (
                    <div className="admin-result-box">
                        ${typeof revenueResult === "number" ? revenueResult.toFixed(2) : JSON.stringify(revenueResult)}
                    </div>
                )}
            </section>

            {/* Restaurant management */}
            <section className="restaurant-section">
                <h2 className="section-title">Restaurant Management</h2>
                {restActionMessage && <p className="status-success">{restActionMessage}</p>}
                {restActionError && <p className="status-error">{restActionError}</p>}
                <div className="admin-user-form">
                    <label>
                        Restaurant ID
                        <input
                            type="number"
                            min="1"
                            value={restIdInput}
                            onChange={(e) => setRestIdInput(e.target.value)}
                            placeholder="Enter restaurant ID"
                        />
                    </label>
                </div>
                <div className="admin-action-buttons">
                    <button
                        type="button"
                        className="admin-action-btn unblock"
                        disabled={!!restActionBusy || !restIdInput.trim()}
                        onClick={() => handleRestaurantAction("enable")}
                    >
                        {restActionBusy === "enable" ? "Enabling…" : "Enable"}
                    </button>
                    <button
                        type="button"
                        className="admin-action-btn block"
                        disabled={!!restActionBusy || !restIdInput.trim()}
                        onClick={() => handleRestaurantAction("disable")}
                    >
                        {restActionBusy === "disable" ? "Disabling…" : "Disable"}
                    </button>
                    <button
                        type="button"
                        className="admin-action-btn delete"
                        disabled={!!restActionBusy || !restIdInput.trim()}
                        onClick={() => handleRestaurantAction("delete")}
                    >
                        {restActionBusy === "delete" ? "Deleting…" : "Delete restaurant"}
                    </button>
                </div>
            </section>

            {/* User management */}
            <section className="restaurant-section">
                <h2 className="section-title">User Management</h2>
                {userActionMessage && <p className="status-success">{userActionMessage}</p>}
                {userActionError && <p className="status-error">{userActionError}</p>}
                <div className="admin-user-form">
                    <label>
                        Username
                        <input
                            type="text"
                            value={usernameInput}
                            onChange={(e) => setUsernameInput(e.target.value)}
                            placeholder="Enter username"
                        />
                    </label>
                </div>
                <div className="admin-action-buttons">
                    <button
                        type="button"
                        className="admin-action-btn block"
                        disabled={!!userActionBusy || !usernameInput.trim()}
                        onClick={() => handleUserAction("block")}
                    >
                        {userActionBusy === "block" ? "Blocking…" : "Block"}
                    </button>
                    <button
                        type="button"
                        className="admin-action-btn unblock"
                        disabled={!!userActionBusy || !usernameInput.trim()}
                        onClick={() => handleUserAction("unblock")}
                    >
                        {userActionBusy === "unblock" ? "Unblocking…" : "Unblock"}
                    </button>
                    <button
                        type="button"
                        className="admin-action-btn delete"
                        disabled={!!userActionBusy || !usernameInput.trim()}
                        onClick={() => handleUserAction("delete")}
                    >
                        {userActionBusy === "delete" ? "Deleting…" : "Delete user"}
                    </button>
                </div>
            </section>
        </main>
    );
}
