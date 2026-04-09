import { useCallback, useEffect, useRef, useState } from "react";
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
import { getUnreadCount } from "./api/notifications";
import {
  parseUserIdFromStorage,
  searchRestaurantMenuItems,
  searchRestaurantsByName,
} from "./api/restaurants";
import SearchDropdown from "./components/search/SearchDropdown";
import Admin from "./pages/Admin";
import Cart from "./pages/Cart";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Notifications from "./pages/Notifications";
import OrderHistory from "./pages/OrderHistory";
import OrderTracking from "./pages/OrderTracking";
import RestaurantDetails from "./pages/RestaurantDetails";
import RestaurantManager from "./pages/RestaurantManager";
import Register from "./pages/Register";
import Review from "./pages/Review";
import Settings from "./pages/Settings";
import Payment from "./pages/Payment";
import Transactions from "./pages/Transaction";
import PayPalPage from "./pages/PayPal";

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
  const [unreadCount, setUnreadCount] = useState(0);

  const [activeTrackingIds, setActiveTrackingIds] = useState(() => {
    try {
      const stored = localStorage.getItem("tracking_order_ids");
      return stored ? JSON.parse(stored) : [];
    } catch { return []; }
  });

  const [paymentDropdownOpen, setPaymentDropdownOpen] = useState(false);
  const paymentDropdownRef = useRef(null);

  const [userDropdownOpen, setUserDropdownOpen] = useState(false);
  const userDropdownRef = useRef(null);

  const [username, setUsername] = useState(() => {
    try {
      return localStorage.getItem("username");
    } catch {
      return null;
    }
  });

  const [userRole, setUserRole] = useState(() => {
    try {
      return localStorage.getItem("userRole") || "";
    } catch {
      return "";
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

  const refreshUnreadCount = useCallback(async () => {
    const userId = parseUserIdFromStorage();
    if (!userId) {
      setUnreadCount(0);
      return;
    }
    try {
      const count = await getUnreadCount(userId);
      setUnreadCount(count);
    } catch {
      setUnreadCount(0);
    }
  }, []);

  useEffect(() => {
    refreshCartCount();
    refreshUnreadCount();
  }, [location.pathname, refreshCartCount, refreshUnreadCount, username]);

  useEffect(() => {
    const handleCartUpdate = () => refreshCartCount();
    window.addEventListener("cart:updated", handleCartUpdate);
    return () => window.removeEventListener("cart:updated", handleCartUpdate);
  }, [refreshCartCount]);

  useEffect(() => {
    const handleTrackingUpdate = () => {
      try {
        const stored = localStorage.getItem("tracking_order_ids");
        setActiveTrackingIds(stored ? JSON.parse(stored) : []);
      } catch { setActiveTrackingIds([]); }
    };
    window.addEventListener("tracking:updated", handleTrackingUpdate);
    return () => window.removeEventListener("tracking:updated", handleTrackingUpdate);
  }, []);

  // Close payment dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (paymentDropdownRef.current && !paymentDropdownRef.current.contains(e.target)) {
        setPaymentDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Close user dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (userDropdownRef.current && !userDropdownRef.current.contains(e.target)) {
        setUserDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  useEffect(() => {
    if (isRestaurantPage || !restaurantSearchQuery.trim()) return;

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
          if (error.name === "AbortError") return;
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
    if (!isRestaurantPage || !menuSearchQuery.trim()) return;

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
          if (error.name === "AbortError") return;
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
    if (restaurant?.id) navigate(`/restaurants/${restaurant.id}`);
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
      "email",
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
      keysToRemove.forEach((k) => {
        try { localStorage.removeItem(k); } catch { /* ignore */ }
      });
      setUsername(null);
      setUserRole("");
      setCartItemCount(0);
      setUnreadCount(0);
      setUserDropdownOpen(false);
      window.location.href = "/";
    }
  };

  const activeSearchQuery = isRestaurantPage ? menuSearchQuery : restaurantSearchQuery;
  const activeSearchResults = isRestaurantPage ? menuSearchResults : restaurantSearchResults;
  const activeSearchLoading = isRestaurantPage ? menuSearchLoading : restaurantSearchLoading;
  const activeSearchError = isRestaurantPage ? menuSearchError : restaurantSearchError;

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
            loadingText={isRestaurantPage ? "Searching menu items..." : "Searching restaurants..."}
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
            <NavLink to="/" end>Home</NavLink>

            {/* Payments dropdown */}
            <div className="nav-dropdown" ref={paymentDropdownRef}>
              <button
                className="nav-dropdown-trigger link-button"
                onClick={() => setPaymentDropdownOpen((prev) => !prev)}
                aria-expanded={paymentDropdownOpen}
              >
                Payments{" "}
                <span className="nav-dropdown-caret">{paymentDropdownOpen ? "▴" : "▾"}</span>
              </button>
              {paymentDropdownOpen && (
                <div className="nav-dropdown-menu">
                  <NavLink to="/payment" onClick={() => setPaymentDropdownOpen(false)}>
                    Payment Methods
                  </NavLink>
                  <NavLink to="/transactions" onClick={() => setPaymentDropdownOpen(false)}>
                    Transactions
                  </NavLink>
                  <NavLink to="/paypal" onClick={() => setPaymentDropdownOpen(false)}>
                    PayPal
                  </NavLink>
                </div>
              )}
            </div>

            {/* Live tracking indicator */}
            {activeTrackingIds.length > 0 && location.pathname !== "/order-tracking" && (
              <NavLink to="/order-tracking" className="tracking-nav-link">
                <span className="tracking-nav-dot" />
                Live Tracking
              </NavLink>
            )}

            {/* Cart */}
            <NavLink to="/cart" className="cart-link" aria-label="View cart">
              Cart
              <span className={`cart-badge ${cartItemCount > 0 ? "has-items" : ""}`}>
                {cartItemCount}
              </span>
            </NavLink>

            {username ? (
              /* User dropdown */
              <div className="nav-dropdown" ref={userDropdownRef}>
                <button
                  className="nav-dropdown-trigger link-button app-username-btn"
                  onClick={() => setUserDropdownOpen((prev) => !prev)}
                  aria-expanded={userDropdownOpen}
                >
                  Hi, {username}{" "}
                  <span className="nav-dropdown-caret">{userDropdownOpen ? "▴" : "▾"}</span>
                </button>
                {userDropdownOpen && (
                  <div className="nav-dropdown-menu nav-dropdown-menu-right">
                    <NavLink to="/orders" onClick={() => setUserDropdownOpen(false)}>
                      Order History
                    </NavLink>
                    <NavLink
                      to="/notifications"
                      className="notif-nav-link"
                      onClick={() => setUserDropdownOpen(false)}
                    >
                      Notifications
                      {unreadCount > 0 && (
                        <span className="notif-nav-badge">{unreadCount}</span>
                      )}
                    </NavLink>
                    <NavLink to="/settings" onClick={() => setUserDropdownOpen(false)}>
                      Settings
                    </NavLink>
                    {userRole === "administrator" && (
                      <NavLink to="/admin" onClick={() => setUserDropdownOpen(false)}>
                        Admin Dashboard
                      </NavLink>
                    )}
                    {userRole === "restaurant owner" && (
                      <NavLink to="/my-restaurants" onClick={() => setUserDropdownOpen(false)}>
                        My Restaurants
                      </NavLink>
                    )}
                    <button className="link-button dropdown-logout-btn" onClick={handleLogout}>
                      Logout
                    </button>
                  </div>
                )}
              </div>
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
          <Route path="/order-tracking" element={<OrderTracking />} />
          <Route path="/payment" element={<Payment />} />
          <Route path="/transactions" element={<Transactions />} />
          <Route path="/paypal" element={<PayPalPage />} />
          <Route path="/orders" element={<OrderHistory />} />
          <Route path="/notifications" element={<Notifications />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/admin" element={<Admin />} />
          <Route path="/my-restaurants" element={<RestaurantManager />} />
          <Route path="/review/:orderId" element={<Review />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
        </Routes>
      </div>
    </>
  );
}
