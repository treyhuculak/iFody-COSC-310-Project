import { useCallback, useEffect, useState } from "react";
import {
    BrowserRouter,
    NavLink,
    Route,
    Routes,
    useLocation,
    useNavigate,
} from "react-router-dom";
import "./App.css";
import { getCartItemCount } from "./api/orders";
import {
    parseUserIdFromStorage,
    searchRestaurantMenuItems,
    searchRestaurantsByName,
} from "./api/restaurants";
import SearchDropdown from "./components/search/SearchDropdown";
import Cart from "./pages/Cart";
import Home from "./pages/Home";
import Login from "./pages/Login";
import OrderHistory from "./pages/OrderHistory";
import Payment from "./pages/Payment";
import RestaurantDetails from "./pages/RestaurantDetails";
import Register from "./pages/Register";
import Offers from "./pages/Offers";
import Settings from "./pages/Settings";

export default function App() {
    return (
        <BrowserRouter>
            <AppShell />
        </BrowserRouter>
    );
}

function AppShell() {
    const location = useLocation();
    const navigate = useNavigate();

    const [restaurantSearchQuery, setRestaurantSearchQuery] = useState("");
    const [restaurantSearchResults, setRestaurantSearchResults] = useState([]);
    const [restaurantSearchLoading, setRestaurantSearchLoading] = useState(false);
    const [restaurantSearchError, setRestaurantSearchError] = useState("");

    const [menuSearchQuery, setMenuSearchQuery] = useState("");
    const [menuSearchResults, setMenuSearchResults] = useState([]);
    const [menuSearchLoading, setMenuSearchLoading] = useState(false);
    const [menuSearchError, setMenuSearchError] = useState("");

    const [selectedRestaurantId, setSelectedRestaurantId] = useState(null);
    const [selectedMenuItemId, setSelectedMenuItemId] = useState(null);
    const [cartItemCount, setCartItemCount] = useState(0);

    const [username, setUsername] = useState(() => {
        try {
            return localStorage.getItem("username");
        } catch {
            return null;
        }
    });

    const restaurantPathMatch = /^\/restaurants\/(\d+)\/?$/.exec(location.pathname);
    const activeRestaurantId = restaurantPathMatch
        ? Number(restaurantPathMatch[1])
        : null;
    const isRestaurantPage =
        activeRestaurantId !== null && Number.isInteger(activeRestaurantId);

    const refreshCartCount = useCallback(async () => {
        const userId = parseUserIdFromStorage();
        if (!userId) {
            setCartItemCount(0);
            return;
        }

        try {
            const count = await getCartItemCount(userId);
            setCartItemCount(count);
        } catch {
            setCartItemCount(0);
        }
    }, []);

    useEffect(() => {
        refreshCartCount();
    }, [location.pathname, refreshCartCount, username]);

    useEffect(() => {
        const handleCartUpdate = () => {
            refreshCartCount();
        };

        window.addEventListener("cart:updated", handleCartUpdate);
        return () => {
            window.removeEventListener("cart:updated", handleCartUpdate);
        };
    }, [refreshCartCount]);

    useEffect(() => {
        if (isRestaurantPage || !restaurantSearchQuery.trim()) {
            return;
        }

        const abortController = new AbortController();
        const timer = setTimeout(() => {
            searchRestaurantsByName(restaurantSearchQuery, {
                limit: 10,
                signal: abortController.signal,
            })
                .then((items) => {
                    setRestaurantSearchResults(items);
                    setRestaurantSearchLoading(false);
                    setRestaurantSearchError("");
                })
                .catch((error) => {
                    if (error.name === "AbortError") {
                        return;
                    }

                    setRestaurantSearchResults([]);
                    setRestaurantSearchLoading(false);
                    setRestaurantSearchError(error.message || "Search is unavailable.");
                });
        }, 220);

        return () => {
            clearTimeout(timer);
            abortController.abort();
        };
    }, [restaurantSearchQuery, isRestaurantPage]);

    useEffect(() => {
        if (!isRestaurantPage || !menuSearchQuery.trim()) {
            return;
        }

        const abortController = new AbortController();
        const timer = setTimeout(() => {
            searchRestaurantMenuItems({
                restaurantId: activeRestaurantId,
                name: menuSearchQuery,
                limit: 12,
                signal: abortController.signal,
            })
                .then((items) => {
                    setMenuSearchResults(items);
                    setMenuSearchLoading(false);
                    setMenuSearchError("");
                })
                .catch((error) => {
                    if (error.name === "AbortError") {
                        return;
                    }

                    setMenuSearchResults([]);
                    setMenuSearchLoading(false);
                    setMenuSearchError(error.message || "Search is unavailable.");
                });
        }, 220);

        return () => {
            clearTimeout(timer);
            abortController.abort();
        };
    }, [activeRestaurantId, menuSearchQuery, isRestaurantPage]);

    useEffect(() => {
        setMenuSearchQuery("");
        setMenuSearchResults([]);
        setMenuSearchLoading(false);
        setMenuSearchError("");
        setSelectedMenuItemId(null);
    }, [activeRestaurantId]);

    const handleSearchQueryChange = (value) => {
        if (isRestaurantPage) {
            setMenuSearchQuery(value);

            if (!value.trim()) {
                setMenuSearchResults([]);
                setMenuSearchLoading(false);
                setMenuSearchError("");
                setSelectedMenuItemId(null);
                return;
            }

            setMenuSearchLoading(true);
            setMenuSearchError("");
            return;
        }

        setRestaurantSearchQuery(value);

        if (!value.trim()) {
            setRestaurantSearchResults([]);
            setRestaurantSearchLoading(false);
            setRestaurantSearchError("");
            return;
        }

        setRestaurantSearchLoading(true);
        setRestaurantSearchError("");
    };

    const handleRestaurantSelect = (restaurant) => {
        setSelectedRestaurantId(restaurant?.id ?? null);
        setRestaurantSearchQuery(restaurant?.name || "");

        if (restaurant?.id) {
            navigate(`/restaurants/${restaurant.id}`);
        }
    };

    const handleMenuItemSelect = (menuItem) => {
        setSelectedMenuItemId(menuItem?.id ?? null);
        setMenuSearchQuery(menuItem?.name || "");
    };

    const handleLogout = async () => {
        const keysToRemove = [
            "username",
            "userId",
            "user_id",
            "id",
            "auth_token",
            "token",
            "currentUserId",
            "userRole",
            "active_order_ids_by_restaurant",
        ];
        try {
            const token = localStorage.getItem("auth_token") || localStorage.getItem("token");
            const headers = { "Content-Type": "application/json" };
            if (token) headers["Authorization"] = `Bearer ${token}`;
            const resp = await fetch("/auth/logout", {
                method: "POST",
                headers,
                credentials: "include",
            });
            if (!resp.ok && resp.status !== 401) {
                console.warn("Logout request failed:", resp.status);
            }
        } catch (err) {
            console.warn("Logout request error:", err);
        } finally {
            // remove per-user cached offers if present
            try {
                const uid = parseUserIdFromStorage();
                if (uid) {
                    try {
                        localStorage.removeItem(`weekly_offers_user_${uid}`);
                    } catch {}
                }
            } catch {}

            keysToRemove.forEach((k) => {
                try {
                    localStorage.removeItem(k);
                } catch {
                    // ignore
                }
            });
            setUsername(null);
            setCartItemCount(0);
            // reload to ensure all components read cleared storage
            window.location.href = "/";
        }
    };

    const activeSearchQuery = isRestaurantPage
        ? menuSearchQuery
        : restaurantSearchQuery;
    const activeSearchResults = isRestaurantPage
        ? menuSearchResults
        : restaurantSearchResults;
    const activeSearchLoading = isRestaurantPage
        ? menuSearchLoading
        : restaurantSearchLoading;
    const activeSearchError = isRestaurantPage
        ? menuSearchError
        : restaurantSearchError;

    return (
        <>
            <nav className="app-nav">
                <div className="app-nav-main">
                    <div className="app-brand">iFody</div>

                    <SearchDropdown
                        className="app-nav-search"
                        inputId={isRestaurantPage ? "app-menu-search" : "app-restaurant-search"}
                        query={activeSearchQuery}
                        onQueryChange={handleSearchQueryChange}
                        results={activeSearchResults}
                        isLoading={activeSearchLoading}
                        onSelect={isRestaurantPage ? handleMenuItemSelect : handleRestaurantSelect}
                        placeholder={isRestaurantPage ? "Find menu items" : "Search restaurants"}
                        loadingText={
                            isRestaurantPage ? "Searching menu items..." : "Searching restaurants..."
                        }
                        emptyText={
                            isRestaurantPage
                                ? "No matching menu items found."
                                : "No matching restaurants found."
                        }
                        getItemPrimaryText={(item) => item.name}
                        getItemSecondaryText={(item) =>
                            isRestaurantPage
                                ? `$${Number(item.price ?? 0).toFixed(2)}`
                                : `${item.cuisine} • ${item.location}`
                        }
                    />

                    <div className="app-links">
                        <NavLink to="/" end>
                            Home
                        </NavLink>
                        {username ? (
                            <NavLink to="/offers">Offers</NavLink>
                        ) : null}
                        <NavLink to="/cart" className="cart-link" aria-label="View cart">
                            Cart
                            <span className={`cart-badge ${cartItemCount > 0 ? "has-items" : ""}`}>
                                {cartItemCount}
                            </span>
                        </NavLink>
                        {username ? (
                            <>
                                <NavLink to="/orders">Order History</NavLink>
                                <NavLink to="/settings">Settings</NavLink>
                                <span className="app-username">Hi, {username}</span>
                                <button className="link-button" onClick={handleLogout}>
                                    Logout
                                </button>
                            </>
                        ) : (
                            <>
                                <NavLink to="/login">Login</NavLink>
                                <NavLink to="/register">Register</NavLink>
                            </>
                        )}
                    </div>
                </div>

                {activeSearchError ? <p className="app-nav-error">{activeSearchError}</p> : null}
            </nav>

            <div className="app-page-shell">
                <Routes>
                    <Route
                        path="/"
                        element={
                            <Home
                                navSearchResults={restaurantSearchResults}
                                selectedRestaurantId={selectedRestaurantId}
                                onRestaurantSelect={handleRestaurantSelect}
                            />
                        }
                    />
                    <Route
                        path="/restaurants/:restaurantId"
                        element={
                            <RestaurantDetails
                                navMenuSearchResults={menuSearchResults}
                                menuSearchQuery={menuSearchQuery}
                                highlightedMenuItemId={selectedMenuItemId}
                            />
                        }
                    />
                    <Route path="/cart" element={<Cart />} />
                    <Route path="/payment" element={<Payment />} />
                    <Route path="/offers" element={<Offers />} />
                    <Route path="/orders" element={<OrderHistory />} />
                    <Route path="/settings" element={<Settings />} />
                    <Route path="/login" element={<Login />} />
                    <Route path="/register" element={<Register />} />
                </Routes>
            </div>

        </>
    );
}