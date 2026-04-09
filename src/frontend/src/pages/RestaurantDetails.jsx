import { useEffect, useMemo, useState } from "react";
import { Link, useLocation, useNavigate, useParams } from "react-router-dom";
import { addMenuItemToCart } from "../api/orders";
import { getRestaurantReviews } from "../api/restaurantManager";
import {
    fetchRestaurantById,
    fetchRestaurantMenuItems,
    parseUserIdFromStorage,
} from "../api/restaurants";
import MenuItemCard from "../components/restaurant/MenuItemCard";
import "../styles/restaurant.css";

const REVIEWS_PAGE_SIZE = 8;

function StarsDisplay({ rating }) {
    const filled = Math.round(Number(rating ?? 0));
    return (
        <span className="rd-stars" aria-label={`${filled} out of 5 stars`}>
            {[1, 2, 3, 4, 5].map((n) => (
                <span key={n} className={n <= filled ? "rd-star filled" : "rd-star"}>★</span>
            ))}
        </span>
    );
}

function toDefaultQuantityMap(menuItems) {
    return menuItems.reduce((quantityMap, item) => {
        quantityMap[item.id] = 1;
        return quantityMap;
    }, {});
}

export default function RestaurantDetails({
    navMenuSearchResults = [],
    menuSearchQuery = "",
    highlightedMenuItemId = null,
}) {
    const params = useParams();
    const location = useLocation();
    const navigate = useNavigate();
    const restaurantId = Number(params.restaurantId);
    const hasValidRestaurantId = Number.isInteger(restaurantId) && restaurantId > 0;

    const [restaurantState, setRestaurantState] = useState({
        item: null,
        loading: true,
        error: "",
    });

    const [menuState, setMenuState] = useState({
        items: [],
        loading: true,
        error: "",
    });

    const [reviewsState, setReviewsState] = useState({
        items: [],
        loading: true,
        page: 1,
        totalPages: 1,
        hasNext: false,
        hasPrev: false,
        error: "",
    });

    const [quantityByItemId, setQuantityByItemId] = useState({});
    const [cartState, setCartState] = useState({
        pendingMenuItemId: null,
        success: "",
        error: "",
    });

    useEffect(() => {
        if (!hasValidRestaurantId) {
            return;
        }

        const abortController = new AbortController();

        Promise.all([
            fetchRestaurantById(restaurantId, { signal: abortController.signal }),
            fetchRestaurantMenuItems({
                restaurantId,
                skip: 0,
                limit: 100,
                signal: abortController.signal,
            }),
        ])
            .then(([restaurant, menuResponse]) => {
                setRestaurantState({
                    item: restaurant,
                    loading: false,
                    error: "",
                });

                setMenuState({
                    items: menuResponse.items,
                    loading: false,
                    error: "",
                });

                setQuantityByItemId((previousMap) => ({
                    ...toDefaultQuantityMap(menuResponse.items),
                    ...previousMap,
                }));
            })
            .catch((error) => {
                if (error.name === "AbortError") {
                    return;
                }

                setRestaurantState({
                    item: null,
                    loading: false,
                    error: error.message || "Failed to load restaurant.",
                });

                setMenuState({
                    items: [],
                    loading: false,
                    error: "",
                });
            });

        return () => {
            abortController.abort();
        };
    }, [restaurantId, hasValidRestaurantId]);

    useEffect(() => {
        if (!hasValidRestaurantId) return;
        let cancelled = false;
        setReviewsState((prev) => ({ ...prev, loading: true, error: "", page: 1 }));
        getRestaurantReviews(restaurantId, { skip: 0, limit: REVIEWS_PAGE_SIZE })
            .then((data) => {
                if (cancelled) return;
                setReviewsState({
                    items: data.items ?? [],
                    loading: false,
                    page: 1,
                    totalPages: data.total_pages ?? 1,
                    hasNext: data.has_next ?? false,
                    hasPrev: data.has_prev ?? false,
                    error: "",
                });
            })
            .catch((err) => {
                if (cancelled) return;
                setReviewsState({ items: [], loading: false, page: 1, totalPages: 1, hasNext: false, hasPrev: false, error: err.message || "Failed to load reviews." });
            });
        return () => { cancelled = true; };
    }, [restaurantId, hasValidRestaurantId]);

    const loadReviewsPage = (page) => {
        const skip = (page - 1) * REVIEWS_PAGE_SIZE;
        setReviewsState((prev) => ({ ...prev, loading: true, error: "" }));
        getRestaurantReviews(restaurantId, { skip, limit: REVIEWS_PAGE_SIZE })
            .then((data) => {
                setReviewsState({
                    items: data.items ?? [],
                    loading: false,
                    page,
                    totalPages: data.total_pages ?? 1,
                    hasNext: data.has_next ?? false,
                    hasPrev: data.has_prev ?? false,
                    error: "",
                });
            })
            .catch((err) => {
                setReviewsState((prev) => ({ ...prev, loading: false, error: err.message || "Failed to load reviews." }));
            });
    };

    const displayedMenuItems = useMemo(() => {
        const normalizedQuery = menuSearchQuery.trim().toLowerCase();
        if (!normalizedQuery) {
            return menuState.items;
        }

        if (Array.isArray(navMenuSearchResults) && navMenuSearchResults.length > 0) {
            return navMenuSearchResults;
        }

        return menuState.items.filter((item) => {
            const name = item.name.toLowerCase();
            const description = item.description.toLowerCase();
            return name.includes(normalizedQuery) || description.includes(normalizedQuery);
        });
    }, [menuSearchQuery, navMenuSearchResults, menuState.items]);

    const handleQuantityChange = (menuItemId, rawValue) => {
        const parsed = Number(rawValue);
        const normalized = Number.isNaN(parsed) ? 1 : Math.min(Math.max(1, Math.floor(parsed)), 99);

        setQuantityByItemId((prev) => ({
            ...prev,
            [menuItemId]: normalized,
        }));
    };

    const redirectToLogin = () => {
        const redirectPath = `${location.pathname}${location.search}`;
        const query = new URLSearchParams({ redirect: redirectPath }).toString();
        navigate(`/login?${query}`);
    };

    const handleAddToCart = async (menuItem) => {
        const userId = parseUserIdFromStorage();
        if (!userId) {
            redirectToLogin();
            return;
        }

        const quantity = Number(quantityByItemId[menuItem.id] ?? 1);
        if (!Number.isInteger(quantity) || quantity <= 0) {
            setCartState({
                pendingMenuItemId: null,
                success: "",
                error: "Quantity must be a positive whole number.",
            });
            return;
        }

        setCartState({
            pendingMenuItemId: menuItem.id,
            success: "",
            error: "",
        });

        try {
            const result = await addMenuItemToCart({
                restaurantId,
                userId,
                menuItem,
                quantity,
            });

            setCartState({
                pendingMenuItemId: null,
                success: `Added ${quantity} × ${menuItem.name} to cart (Order #${result.orderId}).`,
                error: "",
            });
        } catch (error) {
            if (error?.status === 401) {
                redirectToLogin();
                return;
            }

            setCartState({
                pendingMenuItemId: null,
                success: "",
                error: error.message || "Failed to add item to cart.",
            });
        }
    };

    const restaurant = restaurantState.item;
    const isSearchingMenu = menuSearchQuery.trim().length > 0;

    if (!hasValidRestaurantId) {
        return (
            <main className="home-page restaurant-page">
                <section className="hero-banner">
                    <p className="hero-kicker">Restaurant</p>
                    <h1>Restaurant not found</h1>
                    <p className="hero-subtitle">
                        This restaurant link is invalid. Return to Home and pick another restaurant.
                    </p>
                    <p className="restaurant-back-link-wrap">
                        <Link to="/" className="restaurant-back-link">
                            Back to Home
                        </Link>
                    </p>
                </section>
                <p className="status-error">Invalid restaurant id.</p>
            </main>
        );
    }

    return (
        <main className="home-page restaurant-page">
            <section className="hero-banner">
                <p className="hero-kicker">Restaurant</p>
                <h1>{restaurant?.name || "Loading restaurant..."}</h1>
                <p className="hero-subtitle">
                    Review this restaurant's full menu, pick your quantities, and add items directly
                    to your cart.
                </p>
                <p className="restaurant-back-link-wrap">
                    <Link to="/" className="restaurant-back-link">
                        Back to Home
                    </Link>
                </p>
            </section>

            {restaurantState.error ? <p className="status-error">{restaurantState.error}</p> : null}

            {restaurant && !restaurantState.loading ? (
                <section className="restaurant-overview-card">
                    <div className="restaurant-overview-main">
                        <p>
                            <strong>Cuisine:</strong> {restaurant.cuisine}
                        </p>
                        <p>
                            <strong>Location:</strong> {restaurant.location}
                        </p>
                        <p>
                            <strong>Delivery fee:</strong> ${restaurant.delivery_fee.toFixed(2)}
                        </p>
                    </div>
                    <span
                        className={`availability-pill ${
                            restaurant.is_available ? "is-open" : "is-closed"
                        }`}
                    >
                        {restaurant.is_available ? "Open" : "Closed"}
                    </span>
                </section>
            ) : null}

            <section className="restaurant-section">
                <div className="section-heading">
                    <h2>Menu items</h2>
                    <p>
                        {isSearchingMenu
                            ? `Showing results for "${menuSearchQuery}" in this restaurant.`
                            : "Browse the complete menu and add items to your cart."}
                    </p>
                </div>

                {menuState.loading ? (
                    <div className="section-placeholder">Loading menu items...</div>
                ) : displayedMenuItems.length === 0 ? (
                    <div className="section-placeholder">
                        {isSearchingMenu
                            ? "No menu items match your search."
                            : "No menu items are available for this restaurant yet."}
                    </div>
                ) : (
                    <div className="menu-item-grid">
                        {displayedMenuItems.map((item) => (
                            <MenuItemCard
                                key={item.id}
                                item={item}
                                quantity={quantityByItemId[item.id] ?? 1}
                                onQuantityChange={handleQuantityChange}
                                onAddToCart={handleAddToCart}
                                isSubmitting={cartState.pendingMenuItemId === item.id}
                                isHighlighted={item.id === highlightedMenuItemId}
                            />
                        ))}
                    </div>
                )}
            </section>

            {cartState.success ? <p className="status-success">{cartState.success}</p> : null}
            {cartState.error ? <p className="status-error">{cartState.error}</p> : null}
            {menuState.error ? <p className="status-error">{menuState.error}</p> : null}

            <section className="restaurant-section">
                <div className="section-heading">
                    <h2>Customer reviews</h2>
                    <p>See what other customers are saying about this restaurant.</p>
                </div>

                {reviewsState.error ? (
                    <p className="status-error">{reviewsState.error}</p>
                ) : reviewsState.loading ? (
                    <div className="section-placeholder">Loading reviews...</div>
                ) : reviewsState.items.length === 0 ? (
                    <div className="section-placeholder">No reviews yet for this restaurant.</div>
                ) : (
                    <>
                        <div className="rd-review-list">
                            {reviewsState.items.map((rev) => (
                                <div key={rev.id} className="rd-review-card">
                                    <div className="rd-review-header">
                                        <StarsDisplay rating={rev.rating} />
                                        <span className="rd-review-title">{rev.title}</span>
                                        {rev.created_at && (
                                            <span className="rd-review-date">
                                                {new Date(rev.created_at).toLocaleDateString()}
                                            </span>
                                        )}
                                    </div>
                                    {rev.comment && (
                                        <p className="rd-review-comment">{rev.comment}</p>
                                    )}
                                </div>
                            ))}
                        </div>

                        {reviewsState.totalPages > 1 && (
                            <div className="rd-reviews-pagination">
                                <button
                                    type="button"
                                    className="rd-page-btn"
                                    disabled={!reviewsState.hasPrev || reviewsState.loading}
                                    onClick={() => loadReviewsPage(reviewsState.page - 1)}
                                >
                                    ← Previous
                                </button>
                                <span className="rd-page-info">
                                    Page {reviewsState.page} of {reviewsState.totalPages}
                                </span>
                                <button
                                    type="button"
                                    className="rd-page-btn"
                                    disabled={!reviewsState.hasNext || reviewsState.loading}
                                    onClick={() => loadReviewsPage(reviewsState.page + 1)}
                                >
                                    Next →
                                </button>
                            </div>
                        )}
                    </>
                )}
            </section>
        </main>
    );
}
