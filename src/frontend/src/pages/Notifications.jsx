import { useCallback, useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import {
    deleteNotification,
    getNotifications,
    markAllAsRead,
    markAsRead,
} from "../api/notifications";
import { parseUserIdFromStorage } from "../api/restaurants";
import "../styles/notifications.css";

function formatTime(ts) {
    if (!ts) return "";
    try {
        return new Date(ts).toLocaleString();
    } catch {
        return String(ts);
    }
}

export default function Notifications() {
    const location = useLocation();
    const navigate = useNavigate();
    const userId = parseUserIdFromStorage();

    const [notifications, setNotifications] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [busyId, setBusyId] = useState(null);

    const redirectToLogin = useCallback(() => {
        const redirectPath = `${location.pathname}${location.search}`;
        navigate(`/login?${new URLSearchParams({ redirect: redirectPath })}`);
    }, [location.pathname, location.search, navigate]);

    const loadNotifications = useCallback(async () => {
        if (!userId) return;
        try {
            const data = await getNotifications(userId);
            const sorted = [...(data || [])].sort((a, b) => {
                const ta = new Date(a.created_at || 0).getTime();
                const tb = new Date(b.created_at || 0).getTime();
                return tb - ta;
            });
            setNotifications(sorted);
            setError("");
        } catch (err) {
            setError(err.message || "Failed to load notifications.");
        } finally {
            setLoading(false);
        }
    }, [userId]);

    useEffect(() => {
        if (!userId) {
            redirectToLogin();
            return;
        }
        loadNotifications();
    }, [loadNotifications, redirectToLogin, userId]);

    const handleMarkRead = async (notif) => {
        if (notif.is_read) return;
        setBusyId(notif.id);
        try {
            await markAsRead(notif.id, userId);
            await loadNotifications();
        } catch (err) {
            setError(err.message || "Could not mark as read.");
        } finally {
            setBusyId(null);
        }
    };

    const handleDelete = async (notif) => {
        setBusyId(notif.id);
        try {
            await deleteNotification(notif.id, userId);
            await loadNotifications();
        } catch (err) {
            setError(err.message || "Could not delete notification.");
        } finally {
            setBusyId(null);
        }
    };

    const handleMarkAllRead = async () => {
        setBusyId("all");
        try {
            await markAllAsRead(userId);
            await loadNotifications();
        } catch (err) {
            setError(err.message || "Could not mark all as read.");
        } finally {
            setBusyId(null);
        }
    };

    const hasUnread = notifications.some((n) => !n.is_read);

    return (
        <main className="home-page notifications-page">
            <section className="hero-banner">
                <p className="hero-kicker">Inbox</p>
                <h1>Notifications</h1>
                <p className="hero-subtitle">Stay up to date with your orders and account activity.</p>
            </section>

            {error && <p className="status-error">{error}</p>}

            <section className="restaurant-section">
                {hasUnread && (
                    <div className="notif-toolbar">
                        <button
                            type="button"
                            className="notif-mark-all-btn"
                            disabled={busyId === "all"}
                            onClick={handleMarkAllRead}
                        >
                            {busyId === "all" ? "Marking…" : "Mark all as read"}
                        </button>
                    </div>
                )}

                {loading ? (
                    <div className="section-placeholder">Loading notifications…</div>
                ) : notifications.length === 0 ? (
                    <div className="section-placeholder">You have no notifications yet.</div>
                ) : (
                    <div className="notif-list">
                        {notifications.map((notif) => (
                            <div
                                key={notif.id}
                                className={`notif-card ${!notif.is_read ? "unread" : ""}`}
                            >
                                {!notif.is_read && <span className="notif-unread-dot" />}
                                <div className="notif-body">
                                    <p className="notif-message">{notif.message}</p>
                                    <span className="notif-meta">{formatTime(notif.created_at)}</span>
                                </div>
                                <div className="notif-actions">
                                    {!notif.is_read && (
                                        <button
                                            type="button"
                                            className="notif-action-btn"
                                            disabled={busyId === notif.id}
                                            onClick={() => handleMarkRead(notif)}
                                        >
                                            Mark read
                                        </button>
                                    )}
                                    <button
                                        type="button"
                                        className="notif-action-btn danger"
                                        disabled={busyId === notif.id}
                                        onClick={() => handleDelete(notif)}
                                    >
                                        Delete
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </section>
        </main>
    );
}
