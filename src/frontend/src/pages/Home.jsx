import { useEffect, useMemo, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import {
    fetchPopularRestaurants,
    fetchRecentlyOrderedRestaurants,
    fetchRestaurants,
    matchesRestaurantFilters,
    parseUserIdFromStorage,
} from "../api/restaurants";
import FilterBar from "../components/home/FilterBar";
import RestaurantSection from "../components/home/RestaurantSection";
import "../styles/home.css";

const DEFAULT_FILTERS = {
    location: "",
    cuisine: "",
    maxFee: "",
};

function dedupeById(restaurants) {
    const seen = new Set();
    return restaurants.filter((restaurant) => {
        if (seen.has(restaurant.id)) {
            return false;
        }
        seen.add(restaurant.id);
        return true;
    });
}

export default function Home({
    navSearchResults = [],
    selectedRestaurantId = null,
    onRestaurantSelect,
}) {
    const location = useLocation();
    const [filters, setFilters] = useState(DEFAULT_FILTERS);
    const [catalogRestaurants, setCatalogRestaurants] = useState([]);
    const [localSelectedRestaurantId, setLocalSelectedRestaurantId] = useState(null);

    const [restaurantsState, setRestaurantsState] = useState({
        items: [],
        loading: true,
        error: "",
    });

    const [popularState, setPopularState] = useState({
        items: [],
        loading: true,
        endpointReady: true,
        error: "",
    });

    const [recentState, setRecentState] = useState({
        items: [],
        loading: true,
        endpointReady: true,
        error: "",
    });

    useEffect(() => {
        const abortController = new AbortController();

        fetchRestaurants({ limit: 100, signal: abortController.signal })
            .then((response) => {
                setCatalogRestaurants(response.items);
            })
            .catch(() => {
                setCatalogRestaurants([]);
            });

        return () => {
            abortController.abort();
        };
    }, []);

    useEffect(() => {
        const abortController = new AbortController();

        fetchRestaurants({
            location: filters.location,
            cuisine: filters.cuisine,
            maxFee: filters.maxFee,
            limit: 24,
            signal: abortController.signal,
        })
            .then((response) => {
                setRestaurantsState({
                    items: response.items,
                    loading: false,
                    error: "",
                });
            })
            .catch((error) => {
                if (error.name === "AbortError") {
                    return;
                }

                setRestaurantsState({
                    items: [],
                    loading: false,
                    error: error.message || "Failed to load restaurants.",
                });
            });

        return () => {
            abortController.abort();
        };
    }, [filters]);

    useEffect(() => {
        const abortController = new AbortController();
        const userId = parseUserIdFromStorage();

        fetchPopularRestaurants({
            location: filters.location,
            limit: 6,
            signal: abortController.signal,
        })
            .then((result) => {
                setPopularState({
                    items: result.items,
                    loading: false,
                    endpointReady: result.endpointReady,
                    error: "",
                });
            })
            .catch((error) => {
                if (error.name === "AbortError") {
                    return;
                }

                setPopularState({
                    items: [],
                    loading: false,
                    endpointReady: true,
                    error: error.message || "Could not load popular restaurants.",
                });
            });

        fetchRecentlyOrderedRestaurants({
            userId,
            location: filters.location,
            limit: 6,
            signal: abortController.signal,
        })
            .then((result) => {
                setRecentState({
                    items: result.items,
                    loading: false,
                    endpointReady: result.endpointReady,
                    error: "",
                });
            })
            .catch((error) => {
                if (error.name === "AbortError") {
                    return;
                }

                setRecentState({
                    items: [],
                    loading: false,
                    endpointReady: true,
                    error: error.message || "Could not load recently ordered restaurants.",
                });
            });

        return () => {
            abortController.abort();
        };
    }, [filters.location]);

    const locationOptions = useMemo(() => {
        const values = new Set();

        [...catalogRestaurants, ...restaurantsState.items].forEach((restaurant) => {
            if (restaurant.location) {
                values.add(restaurant.location);
            }
        });

        return Array.from(values).sort((a, b) => a.localeCompare(b));
    }, [catalogRestaurants, restaurantsState.items]);

    const cuisineOptions = useMemo(() => {
        const values = new Set();

        [...catalogRestaurants, ...restaurantsState.items].forEach((restaurant) => {
            if (restaurant.cuisine) {
                values.add(restaurant.cuisine);
            }
        });

        return Array.from(values).sort((a, b) => a.localeCompare(b));
    }, [catalogRestaurants, restaurantsState.items]);


    const paypalNotice = useMemo(() => {
        const params = new URLSearchParams(location.search);
        const status = params.get("paypal_status");
        const message = params.get("paypal_message");
        const token = params.get("token");

        if (!status && !message) {
            return null;
        }

        return {
            status: status || "info",
            message: message || (status === "approved" ? "PayPal approval completed" : "PayPal payment was cancelled."),
            token,
        };
    }, [location.search]);

    const recommendationPool = useMemo(() => {
        const filteredNavSearchItems = navSearchResults.filter((restaurant) =>
            matchesRestaurantFilters(restaurant, filters)
        );

        return dedupeById([
            ...filteredNavSearchItems,
            ...popularState.items,
            ...recentState.items,
            ...restaurantsState.items,
        ]);
    }, [filters, navSearchResults, popularState.items, recentState.items, restaurantsState.items]);

    const filteredRecommendationPool = useMemo(() => {
        return recommendationPool.filter((restaurant) =>
            matchesRestaurantFilters(restaurant, filters)
        );
    }, [recommendationPool, filters]);

    const handleFilterChange = (field, value) => {
        if (filters[field] === value) {
            return;
        }

        setRestaurantsState((prev) => ({
            ...prev,
            loading: true,
            error: "",
        }));

        if (field === "location") {
            setPopularState((prev) => ({
                ...prev,
                loading: true,
                error: "",
            }));

            setRecentState((prev) => ({
                ...prev,
                loading: true,
                error: "",
            }));
        }

        setFilters((prev) => ({
            ...prev,
            [field]: value,
        }));
    };

    const handleRestaurantSelect = (restaurant) => {
        setLocalSelectedRestaurantId(restaurant?.id ?? null);

        if (onRestaurantSelect) {
            onRestaurantSelect(restaurant);
        }
    };

    const handleResetFilters = () => {
        const hasChanges =
            filters.location !== DEFAULT_FILTERS.location ||
            filters.cuisine !== DEFAULT_FILTERS.cuisine ||
            filters.maxFee !== DEFAULT_FILTERS.maxFee;

        if (!hasChanges) {
            setLocalSelectedRestaurantId(null);
            return;
        }

        setRestaurantsState((prev) => ({
            ...prev,
            loading: true,
            error: "",
        }));

        if (filters.location !== DEFAULT_FILTERS.location) {
            setPopularState((prev) => ({
                ...prev,
                loading: true,
                error: "",
            }));

            setRecentState((prev) => ({
                ...prev,
                loading: true,
                error: "",
            }));
        }

        setFilters({ ...DEFAULT_FILTERS });
        setLocalSelectedRestaurantId(null);
    };

    const highlightedRestaurantId = selectedRestaurantId || localSelectedRestaurantId;

    return (
        <main className="home-page">
            <section className="hero-banner">
                {paypalNotice ? (
                    <div className={`home-paypal-notice ${paypalNotice.status === "cancelled" ? "is-cancelled" : "is-approved"}`}>
                        <p>{paypalNotice.message}</p>
                        <div className="home-paypal-notice-actions">
                            <Link to={`/paypal${paypalNotice.token ? `?token=${encodeURIComponent(paypalNotice.token)}` : ""}`}>Open PayPal page</Link>
                        </div>
                    </div>
                ) : null}
                <p className="hero-kicker">Customer Home</p>
                <h1>Order from places that fit your taste in seconds.</h1>
                <p className="hero-subtitle">
                    Discover restaurants, search in real-time, and explore recommendations
                    tailored to your location and order history.
                </p>
            </section>

            <FilterBar
                filters={filters}
                locationOptions={locationOptions}
                cuisineOptions={cuisineOptions}
                onChange={handleFilterChange}
                onReset={handleResetFilters}
            />
            {restaurantsState.error && <p className="status-error">{restaurantsState.error}</p>}

            <RestaurantSection
                title="Recommended for you"
                subtitle="Live recommendations based on your current search and active filters."
                restaurants={filteredRecommendationPool}
                isLoading={restaurantsState.loading}
                emptyMessage="No recommendations yet. Try loosening your filters."
                highlightedRestaurantId={highlightedRestaurantId}
                onSelectRestaurant={handleRestaurantSelect}
            />

            <RestaurantSection
                title="Popular in this area"
                subtitle="Top restaurants for your selected location based on order activity."
                restaurants={popularState.items}
                isLoading={popularState.loading}
                endpointReady={popularState.endpointReady}
                emptyMessage="No popular restaurants available for this location yet."
                highlightedRestaurantId={highlightedRestaurantId}
                onSelectRestaurant={handleRestaurantSelect}
            />

            <RestaurantSection
                title="Your recent favorites"
                subtitle="Restaurants you ordered from most recently in this account."
                restaurants={recentState.items}
                isLoading={recentState.loading}
                endpointReady={recentState.endpointReady}
                emptyMessage="No recent restaurants yet for this user."
                highlightedRestaurantId={highlightedRestaurantId}
                onSelectRestaurant={handleRestaurantSelect}
            />

            {popularState.error && <p className="status-error">{popularState.error}</p>}
            {recentState.error && <p className="status-error">{recentState.error}</p>}
        </main>
    );
}
