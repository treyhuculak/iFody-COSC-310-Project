import { useEffect, useState } from "react";
import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import "./App.css";
import { searchRestaurantsByName } from "./api/restaurants";
import SearchDropdown from "./components/search/SearchDropdown";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Order from "./pages/Order";

export default function App() {
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchError, setSearchError] = useState("");
  const [selectedRestaurantId, setSelectedRestaurantId] = useState(null);
  const [username, setUsername] = useState(() => {
    try {
      return localStorage.getItem("username");
    } catch (err) {
      return null;
    }
  });

  useEffect(() => {
    if (!searchQuery.trim()) {
      return;
    }

    const abortController = new AbortController();
    const timer = setTimeout(() => {
      searchRestaurantsByName(searchQuery, {
        limit: 10,
        signal: abortController.signal,
      })
        .then((items) => {
          setSearchResults(items);
          setSearchLoading(false);
          setSearchError("");
        })
        .catch((error) => {
          if (error.name === "AbortError") {
            return;
          }

          setSearchResults([]);
          setSearchLoading(false);
          setSearchError(error.message || "Search is unavailable.");
        });
    }, 220);

    return () => {
      clearTimeout(timer);
      abortController.abort();
    };
  }, [searchQuery]);

  const handleSearchQueryChange = (value) => {
    setSearchQuery(value);

    if (!value.trim()) {
      setSearchResults([]);
      setSearchLoading(false);
      setSearchError("");
      return;
    }

    setSearchLoading(true);
    setSearchError("");
  };

  const handleRestaurantSelect = (restaurant) => {
    setSelectedRestaurantId(restaurant?.id ?? null);
    setSearchQuery(restaurant?.name || "");
  };

  const handleLogout = async () => {
    const keysToRemove = ["username", "userId", "auth_token", "token", "currentUserId"];
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
        try {
          localStorage.removeItem(k);
        } catch (e) {
          // ignore
        }
      });
      setUsername(null);
      // reload to ensure all components read cleared storage
      window.location.href = "/";
    }
  };

  return (
    <BrowserRouter>
      <nav className="app-nav">
        <div className="app-nav-main">
          <div className="app-brand">iFody</div>

          <SearchDropdown
            className="app-nav-search"
            inputId="app-restaurant-search"
            query={searchQuery}
            onQueryChange={handleSearchQueryChange}
            results={searchResults}
            isLoading={searchLoading}
            onSelect={handleRestaurantSelect}
            placeholder="Search restaurants"
            loadingText="Searching restaurants..."
            emptyText="No matching restaurants found."
            getItemPrimaryText={(restaurant) => restaurant.name}
            getItemSecondaryText={(restaurant) =>
              `${restaurant.cuisine} • ${restaurant.location}`
            }
          />

          <div className="app-links">
            <NavLink to="/" end>
              Home
            </NavLink>
            {username ? (
              <>
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

        {searchError ? <p className="app-nav-error">{searchError}</p> : null}
      </nav>

      <div className="app-page-shell">
        <Routes>
          <Route
            path="/"
            element={
              <Home
                navSearchResults={searchResults}
                selectedRestaurantId={selectedRestaurantId}
                onRestaurantSelect={handleRestaurantSelect}
              />
            }
          />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/order/:orderId" element={<Order />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}