import { Link } from "react-router-dom";
import "../styles/settings.css";

const LOGOUT_KEYS = [
    "username",
    "userId",
    "user_id",
    "id",
    "auth_token",
    "token",
    "currentUserId",
    "userRole",
    "active_order_ids_by_restaurant",
    "email",
];

function getStorageItem(key) {
    try {
        return localStorage.getItem(key) || "";
    } catch {
        return "";
    }
}

export default function Settings() {
    const username = getStorageItem("username");
    const email = getStorageItem("email");
    const role = getStorageItem("userRole");

    const handleLogout = () => {
        LOGOUT_KEYS.forEach((k) => {
            try {
                localStorage.removeItem(k);
            } catch {
                // ignore
            }
        });
        window.location.href = "/";
    };

    return (
        <main className="home-page settings-page">
            <section className="hero-banner">
                <p className="hero-kicker">Account</p>
                <h1>Settings</h1>
                <p className="hero-subtitle">Manage your account details and preferences.</p>
            </section>

            <section className="restaurant-section">
                <div className="settings-card">
                    <h2>Account Info</h2>
                    <div className="settings-row">
                        <span className="settings-label">Username</span>
                        <span className="settings-value">{username || "—"}</span>
                    </div>
                    <div className="settings-row">
                        <span className="settings-label">Email</span>
                        <span className="settings-value">{email || "—"}</span>
                    </div>
                    <div className="settings-row">
                        <span className="settings-label">Role</span>
                        <span className="settings-value">{role || "—"}</span>
                    </div>
                </div>

                <div className="settings-card">
                    <h2>Orders</h2>
                    <div className="settings-row">
                        <span className="settings-label">History</span>
                        <Link to="/orders" className="settings-link">View Order History</Link>
                    </div>
                </div>

                <div className="settings-card">
                    <h2>Session</h2>
                    <button
                        type="button"
                        className="settings-logout-button"
                        onClick={handleLogout}
                    >
                        Log Out
                    </button>
                </div>
            </section>
        </main>
    );
}
