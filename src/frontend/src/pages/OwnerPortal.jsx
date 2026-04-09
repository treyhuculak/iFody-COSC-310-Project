import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import {
    createRestaurant,
    createRestaurantMenuItem,
    deleteRestaurant,
    deleteRestaurantMenuItem,
    fetchOwnerRestaurants,
    fetchRestaurantMenuItems,
    parseUserIdFromStorage,
    searchOwnerRestaurantsByName,
    searchRestaurantMenuItemsPaginated,
    updateRestaurant,
    updateRestaurantMenuItem,
} from "../api/restaurants";
import "../styles/owner.css";

const OWNER_RESTAURANTS_PAGE_SIZE = 6;
const OWNER_MENU_PAGE_SIZE = 8;

const PROVINCE_OPTIONS = [
    "BC",
    "AB",
    "SK",
    "MB",
    "ON",
    "QC",
    "NB",
    "NS",
    "PE",
    "NL",
    "YT",
    "NT",
    "NU",
];

const EMPTY_RESTAURANT_FORM = {
    name: "",
    cuisine: "",
    city: "",
    province: "BC",
    delivery_fee: "",
};

const EMPTY_MENU_ITEM_FORM = {
    name: "",
    description: "",
    price: "",
};

function normalizeRole(role) {
    return String(role || "")
        .toLowerCase()
        .replace(/[^a-z]/g, "");
}

function isOwnerRole(role) {
    return normalizeRole(role) === "restaurantowner";
}

export default function OwnerPortal() {
    const [ownerId] = useState(() => parseUserIdFromStorage());
    const [userRole] = useState(() => {
        try {
            return localStorage.getItem("userRole") || "";
        } catch {
            return "";
        }
    });

    const [restaurantsPage, setRestaurantsPage] = useState(1);
    const [menuPage, setMenuPage] = useState(1);
    const [restaurantSearchQuery, setRestaurantSearchQuery] = useState("");
    const [menuSearchQuery, setMenuSearchQuery] = useState("");

    const [restaurantsRefreshKey, setRestaurantsRefreshKey] = useState(0);
    const [menuRefreshKey, setMenuRefreshKey] = useState(0);

    const [activeRestaurantId, setActiveRestaurantId] = useState(null);

    const [restaurantsState, setRestaurantsState] = useState({
        items: [],
        loading: true,
        error: "",
        totalPages: 1,
        total: 0,
    });

    const [menuState, setMenuState] = useState({
        items: [],
        loading: false,
        error: "",
        totalPages: 1,
        total: 0,
    });

    const [feedback, setFeedback] = useState({ type: "", text: "" });
    const [isSubmitting, setIsSubmitting] = useState(false);

    const [showCreateRestaurantForm, setShowCreateRestaurantForm] = useState(false);
    const [newRestaurantForm, setNewRestaurantForm] = useState(EMPTY_RESTAURANT_FORM);

    const [editingRestaurantId, setEditingRestaurantId] = useState(null);
    const [restaurantEditForm, setRestaurantEditForm] = useState({
        name: "",
        cuisine: "",
        city: "",
        delivery_fee: "",
        is_available: false,
    });

    const [showCreateMenuItemForm, setShowCreateMenuItemForm] = useState(false);
    const [newMenuItemForm, setNewMenuItemForm] = useState(EMPTY_MENU_ITEM_FORM);

    const [editingMenuItemId, setEditingMenuItemId] = useState(null);
    const [menuItemEditForm, setMenuItemEditForm] = useState(EMPTY_MENU_ITEM_FORM);

    const canManageRestaurants = Number.isInteger(ownerId) && ownerId > 0 && isOwnerRole(userRole);

    useEffect(() => {
        if (!canManageRestaurants) {
            setRestaurantsState((prev) => ({
                ...prev,
                items: [],
                loading: false,
                error: "",
                totalPages: 1,
                total: 0,
            }));
            setActiveRestaurantId(null);
            return;
        }

        let cancelled = false;

        setRestaurantsState((prev) => ({
            ...prev,
            loading: true,
            error: "",
        }));

        const loadOwnerRestaurants = restaurantSearchQuery.trim()
            ? searchOwnerRestaurantsByName({
                  ownerId,
                  name: restaurantSearchQuery,
                  skip: (restaurantsPage - 1) * OWNER_RESTAURANTS_PAGE_SIZE,
                  limit: OWNER_RESTAURANTS_PAGE_SIZE,
              })
            : fetchOwnerRestaurants({
                  ownerId,
                  skip: (restaurantsPage - 1) * OWNER_RESTAURANTS_PAGE_SIZE,
                  limit: OWNER_RESTAURANTS_PAGE_SIZE,
              });

        loadOwnerRestaurants
            .then((response) => {
                if (cancelled) {
                    return;
                }

                if (response.items.length === 0 && restaurantsPage > 1 && response.has_prev) {
                    setRestaurantsPage((prev) => Math.max(1, prev - 1));
                    return;
                }

                setRestaurantsState({
                    items: response.items,
                    loading: false,
                    error: "",
                    totalPages: response.total_pages || 1,
                    total: response.total || response.items.length,
                });

                setActiveRestaurantId((previousId) => {
                    if (previousId && response.items.some((restaurant) => restaurant.id === previousId)) {
                        return previousId;
                    }

                    return response.items[0]?.id ?? null;
                });
            })
            .catch((error) => {
                if (cancelled) {
                    return;
                }

                setRestaurantsState({
                    items: [],
                    loading: false,
                    error: error.message || "Failed to load your restaurants.",
                    totalPages: 1,
                    total: 0,
                });
                setActiveRestaurantId(null);
            });

        return () => {
            cancelled = true;
        };
    }, [
        canManageRestaurants,
        ownerId,
        restaurantsPage,
        restaurantsRefreshKey,
        restaurantSearchQuery,
    ]);

    useEffect(() => {
        if (!canManageRestaurants || !activeRestaurantId) {
            setMenuState({
                items: [],
                loading: false,
                error: "",
                totalPages: 1,
                total: 0,
            });
            return;
        }

        let cancelled = false;

        setMenuState((prev) => ({
            ...prev,
            loading: true,
            error: "",
        }));

        const loadMenuItems = menuSearchQuery.trim()
            ? searchRestaurantMenuItemsPaginated({
                  restaurantId: activeRestaurantId,
                  name: menuSearchQuery,
                  skip: (menuPage - 1) * OWNER_MENU_PAGE_SIZE,
                  limit: OWNER_MENU_PAGE_SIZE,
              })
            : fetchRestaurantMenuItems({
                  restaurantId: activeRestaurantId,
                  skip: (menuPage - 1) * OWNER_MENU_PAGE_SIZE,
                  limit: OWNER_MENU_PAGE_SIZE,
              });

        loadMenuItems
            .then((response) => {
                if (cancelled) {
                    return;
                }

                if (response.items.length === 0 && menuPage > 1 && response.has_prev) {
                    setMenuPage((prev) => Math.max(1, prev - 1));
                    return;
                }

                setMenuState({
                    items: response.items,
                    loading: false,
                    error: "",
                    totalPages: response.total_pages || 1,
                    total: response.total || response.items.length,
                });
            })
            .catch((error) => {
                if (cancelled) {
                    return;
                }

                setMenuState({
                    items: [],
                    loading: false,
                    error: error.message || "Failed to load menu items.",
                    totalPages: 1,
                    total: 0,
                });
            });

        return () => {
            cancelled = true;
        };
    }, [
        canManageRestaurants,
        activeRestaurantId,
        menuPage,
        menuRefreshKey,
        menuSearchQuery,
    ]);

    const selectedRestaurant = useMemo(() => {
        return (
            restaurantsState.items.find((restaurant) => restaurant.id === activeRestaurantId) || null
        );
    }, [restaurantsState.items, activeRestaurantId]);

    useEffect(() => {
        if (!selectedRestaurant) {
            setEditingRestaurantId(null);
            return;
        }

        if (editingRestaurantId && editingRestaurantId !== selectedRestaurant.id) {
            setEditingRestaurantId(null);
        }
    }, [selectedRestaurant, editingRestaurantId]);

    const handleRestaurantCardClick = (restaurantId) => {
        if (restaurantId === activeRestaurantId) {
            return;
        }

        setActiveRestaurantId(restaurantId);
        setMenuPage(1);
        setMenuSearchQuery("");
        setEditingMenuItemId(null);
        setShowCreateMenuItemForm(false);
        setFeedback({ type: "", text: "" });
    };

    const handleCreateRestaurant = async (event) => {
        event.preventDefault();
        if (!canManageRestaurants || isSubmitting) {
            return;
        }

        const deliveryFee = Number(newRestaurantForm.delivery_fee);
        if (Number.isNaN(deliveryFee) || deliveryFee < 0) {
            setFeedback({
                type: "error",
                text: "Delivery fee must be a number greater than or equal to 0.",
            });
            return;
        }

        setIsSubmitting(true);
        setFeedback({ type: "", text: "" });

        try {
            await createRestaurant({
                restaurant: {
                    name: newRestaurantForm.name.trim(),
                    cuisine: newRestaurantForm.cuisine.trim(),
                    city: newRestaurantForm.city.trim(),
                    province: newRestaurantForm.province,
                    delivery_fee: deliveryFee,
                },
                userId: ownerId,
            });

            setNewRestaurantForm(EMPTY_RESTAURANT_FORM);
            setShowCreateRestaurantForm(false);
            setRestaurantsPage(1);
            setRestaurantsRefreshKey((prev) => prev + 1);
            setFeedback({ type: "success", text: "Restaurant created successfully." });
        } catch (error) {
            setFeedback({
                type: "error",
                text: error.message || "Could not create restaurant.",
            });
        } finally {
            setIsSubmitting(false);
        }
    };

    const startEditRestaurant = () => {
        if (!selectedRestaurant) {
            return;
        }

        setEditingRestaurantId(selectedRestaurant.id);
        setRestaurantEditForm({
            name: selectedRestaurant.name || "",
            cuisine: selectedRestaurant.cuisine || "",
            city: selectedRestaurant.city || selectedRestaurant.location || "",
            delivery_fee: String(selectedRestaurant.delivery_fee ?? ""),
            is_available: Boolean(selectedRestaurant.is_available),
        });
        setFeedback({ type: "", text: "" });
    };

    const handleUpdateRestaurant = async (event) => {
        event.preventDefault();
        if (!selectedRestaurant || !canManageRestaurants || isSubmitting) {
            return;
        }

        const trimmedName = restaurantEditForm.name.trim();
        const trimmedCuisine = restaurantEditForm.cuisine.trim();
        const trimmedCity = restaurantEditForm.city.trim();
        const deliveryFee = Number(restaurantEditForm.delivery_fee);

        if (!trimmedName || !trimmedCuisine) {
            setFeedback({
                type: "error",
                text: "Restaurant name and cuisine are required.",
            });
            return;
        }

        if (Number.isNaN(deliveryFee) || deliveryFee < 0) {
            setFeedback({
                type: "error",
                text: "Delivery fee must be a number greater than or equal to 0.",
            });
            return;
        }

        const updates = {
            name: trimmedName,
            cuisine: trimmedCuisine,
            delivery_fee: deliveryFee,
            is_available: Boolean(restaurantEditForm.is_available),
        };

        if (trimmedCity) {
            updates.location = trimmedCity;
        }

        setIsSubmitting(true);
        setFeedback({ type: "", text: "" });

        try {
            await updateRestaurant({
                restaurantId: selectedRestaurant.id,
                updates,
                userId: ownerId,
            });

            setEditingRestaurantId(null);
            setRestaurantsRefreshKey((prev) => prev + 1);
            setFeedback({ type: "success", text: "Restaurant updated successfully." });
        } catch (error) {
            setFeedback({
                type: "error",
                text: error.message || "Could not update restaurant.",
            });
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleDeleteRestaurant = async () => {
        if (!selectedRestaurant || !canManageRestaurants || isSubmitting) {
            return;
        }

        const shouldDelete = window.confirm(
            `Delete restaurant "${selectedRestaurant.name}"? This cannot be undone.`
        );

        if (!shouldDelete) {
            return;
        }

        setIsSubmitting(true);
        setFeedback({ type: "", text: "" });

        try {
            await deleteRestaurant({
                restaurantId: selectedRestaurant.id,
                userId: ownerId,
            });

            setEditingRestaurantId(null);
            setShowCreateMenuItemForm(false);
            setEditingMenuItemId(null);

            if (restaurantsState.items.length === 1 && restaurantsPage > 1) {
                setRestaurantsPage((prev) => Math.max(1, prev - 1));
            } else {
                setRestaurantsRefreshKey((prev) => prev + 1);
            }

            setMenuPage(1);
            setMenuRefreshKey((prev) => prev + 1);
            setFeedback({ type: "success", text: "Restaurant deleted successfully." });
        } catch (error) {
            setFeedback({
                type: "error",
                text: error.message || "Could not delete restaurant.",
            });
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleCreateMenuItem = async (event) => {
        event.preventDefault();
        if (!selectedRestaurant || !canManageRestaurants || isSubmitting) {
            return;
        }

        const price = Number(newMenuItemForm.price);
        if (Number.isNaN(price) || price <= 0) {
            setFeedback({
                type: "error",
                text: "Menu item price must be greater than 0.",
            });
            return;
        }

        setIsSubmitting(true);
        setFeedback({ type: "", text: "" });

        try {
            await createRestaurantMenuItem({
                restaurantId: selectedRestaurant.id,
                menuItem: {
                    name: newMenuItemForm.name.trim(),
                    description: newMenuItemForm.description.trim(),
                    price,
                },
                userId: ownerId,
            });

            setNewMenuItemForm(EMPTY_MENU_ITEM_FORM);
            setShowCreateMenuItemForm(false);
            setMenuPage(1);
            setMenuRefreshKey((prev) => prev + 1);
            setFeedback({ type: "success", text: "Menu item created successfully." });
        } catch (error) {
            setFeedback({
                type: "error",
                text: error.message || "Could not create menu item.",
            });
        } finally {
            setIsSubmitting(false);
        }
    };

    const startEditMenuItem = (item) => {
        setEditingMenuItemId(item.id);
        setMenuItemEditForm({
            name: item.name || "",
            description: item.description || "",
            price: String(item.price ?? ""),
        });
        setFeedback({ type: "", text: "" });
    };

    const handleUpdateMenuItem = async (event, menuItemId) => {
        event.preventDefault();
        if (!selectedRestaurant || !canManageRestaurants || isSubmitting) {
            return;
        }

        const trimmedName = menuItemEditForm.name.trim();
        const price = Number(menuItemEditForm.price);

        if (!trimmedName) {
            setFeedback({ type: "error", text: "Menu item name is required." });
            return;
        }

        if (Number.isNaN(price) || price <= 0) {
            setFeedback({
                type: "error",
                text: "Menu item price must be greater than 0.",
            });
            return;
        }

        setIsSubmitting(true);
        setFeedback({ type: "", text: "" });

        try {
            await updateRestaurantMenuItem({
                restaurantId: selectedRestaurant.id,
                menuItemId,
                updates: {
                    name: trimmedName,
                    description: menuItemEditForm.description.trim(),
                    price,
                },
                userId: ownerId,
            });

            setEditingMenuItemId(null);
            setMenuRefreshKey((prev) => prev + 1);
            setFeedback({ type: "success", text: "Menu item updated successfully." });
        } catch (error) {
            setFeedback({
                type: "error",
                text: error.message || "Could not update menu item.",
            });
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleDeleteMenuItem = async (item) => {
        if (!selectedRestaurant || !canManageRestaurants || isSubmitting) {
            return;
        }

        const shouldDelete = window.confirm(
            `Delete menu item "${item.name}" from ${selectedRestaurant.name}?`
        );

        if (!shouldDelete) {
            return;
        }

        setIsSubmitting(true);
        setFeedback({ type: "", text: "" });

        try {
            await deleteRestaurantMenuItem({
                restaurantId: selectedRestaurant.id,
                menuItemId: item.id,
                userId: ownerId,
            });

            if (menuState.items.length === 1 && menuPage > 1) {
                setMenuPage((prev) => Math.max(1, prev - 1));
            } else {
                setMenuRefreshKey((prev) => prev + 1);
            }

            setEditingMenuItemId(null);
            setFeedback({ type: "success", text: "Menu item deleted successfully." });
        } catch (error) {
            setFeedback({
                type: "error",
                text: error.message || "Could not delete menu item.",
            });
        } finally {
            setIsSubmitting(false);
        }
    };

    if (!ownerId) {
        return (
            <main className="owner-page">
                <section className="owner-hero">
                    <p className="owner-kicker">Owner Portal</p>
                    <h1>Restaurant management for signed-in owners</h1>
                    <p>
                        Please log in with a restaurant owner account to access your restaurant
                        and menu management tools.
                    </p>
                    <div className="owner-hero-actions">
                        <Link to="/login?redirect=/owner" className="owner-action-link">
                            Go to Login
                        </Link>
                    </div>
                </section>
            </main>
        );
    }

    if (!canManageRestaurants) {
        return (
            <main className="owner-page">
                <section className="owner-hero">
                    <p className="owner-kicker">Owner Portal</p>
                    <h1>Access is limited to restaurant owners</h1>
                    <p>
                        This section is only available for accounts with the restaurant owner role.
                    </p>
                </section>
            </main>
        );
    }

    return (
        <main className="owner-page">
            <section className="owner-hero">
                <p className="owner-kicker">Owner Portal</p>
                <h1>Manage your restaurants and menus</h1>
                <p>
                    Select one of your restaurants to edit details, manage menu items, or remove it.
                    Use the create buttons to add new restaurants and menu items.
                </p>
            </section>

            {feedback.text ? (
                <p className={feedback.type === "error" ? "owner-status-error" : "owner-status-success"}>
                    {feedback.text}
                </p>
            ) : null}

            {restaurantsState.error ? (
                <p className="owner-status-error">{restaurantsState.error}</p>
            ) : null}

            <section className="owner-section">
                <div className="owner-section-header">
                    <div>
                        <h2>Your restaurants</h2>
                        <p>
                            Page {restaurantsPage} of {Math.max(restaurantsState.totalPages, 1)} • {restaurantsState.total} total
                            {restaurantSearchQuery.trim()
                                ? ` matching "${restaurantSearchQuery.trim()}"`
                                : ""}
                        </p>
                    </div>
                    <button
                        type="button"
                        className="owner-primary-button"
                        onClick={() => {
                            setShowCreateRestaurantForm((prev) => !prev);
                            setEditingRestaurantId(null);
                            setFeedback({ type: "", text: "" });
                        }}
                    >
                        {showCreateRestaurantForm ? "Close create form" : "Create restaurant"}
                    </button>
                </div>

                <div className="owner-search-row">
                    <label htmlFor="owner-restaurant-search">Search your restaurants by name</label>
                    <input
                        id="owner-restaurant-search"
                        type="text"
                        value={restaurantSearchQuery}
                        onChange={(event) => {
                            setRestaurantSearchQuery(event.target.value);
                            setRestaurantsPage(1);
                        }}
                        placeholder="e.g. sushi, burger, downtown"
                    />
                </div>

                {showCreateRestaurantForm ? (
                    <form className="owner-form-grid" onSubmit={handleCreateRestaurant}>
                        <label>
                            Name
                            <input
                                type="text"
                                value={newRestaurantForm.name}
                                onChange={(event) =>
                                    setNewRestaurantForm((prev) => ({
                                        ...prev,
                                        name: event.target.value,
                                    }))
                                }
                                required
                                minLength={1}
                                maxLength={100}
                            />
                        </label>

                        <label>
                            Cuisine
                            <input
                                type="text"
                                value={newRestaurantForm.cuisine}
                                onChange={(event) =>
                                    setNewRestaurantForm((prev) => ({
                                        ...prev,
                                        cuisine: event.target.value,
                                    }))
                                }
                                required
                                minLength={1}
                                maxLength={100}
                            />
                        </label>

                        <label>
                            City
                            <input
                                type="text"
                                value={newRestaurantForm.city}
                                onChange={(event) =>
                                    setNewRestaurantForm((prev) => ({
                                        ...prev,
                                        city: event.target.value,
                                    }))
                                }
                                required
                                minLength={1}
                                maxLength={100}
                            />
                        </label>

                        <label>
                            Province
                            <select
                                value={newRestaurantForm.province}
                                onChange={(event) =>
                                    setNewRestaurantForm((prev) => ({
                                        ...prev,
                                        province: event.target.value,
                                    }))
                                }
                                required
                            >
                                {PROVINCE_OPTIONS.map((provinceCode) => (
                                    <option key={provinceCode} value={provinceCode}>
                                        {provinceCode}
                                    </option>
                                ))}
                            </select>
                        </label>

                        <label>
                            Delivery fee
                            <input
                                type="number"
                                step="0.01"
                                min="0"
                                value={newRestaurantForm.delivery_fee}
                                onChange={(event) =>
                                    setNewRestaurantForm((prev) => ({
                                        ...prev,
                                        delivery_fee: event.target.value,
                                    }))
                                }
                                required
                            />
                        </label>

                        <button type="submit" className="owner-primary-button" disabled={isSubmitting}>
                            {isSubmitting ? "Saving..." : "Save restaurant"}
                        </button>
                    </form>
                ) : null}

                {restaurantsState.loading ? (
                    <div className="owner-placeholder">Loading your restaurants...</div>
                ) : restaurantsState.items.length === 0 ? (
                    <div className="owner-placeholder">No restaurants found for this owner account yet.</div>
                ) : (
                    <>
                        <div className="owner-card-grid">
                            {restaurantsState.items.map((restaurant) => (
                                <article
                                    key={restaurant.id}
                                    className={`owner-card ${restaurant.id === activeRestaurantId ? "is-selected" : ""}`}
                                >
                                    <button
                                        type="button"
                                        className="owner-card-select"
                                        onClick={() => handleRestaurantCardClick(restaurant.id)}
                                    >
                                        <h3>{restaurant.name}</h3>
                                        <p>
                                            {restaurant.cuisine} • {restaurant.city || restaurant.location || "Unknown city"}
                                        </p>
                                        <p>Delivery fee: ${Number(restaurant.delivery_fee || 0).toFixed(2)}</p>
                                        <span
                                            className={`owner-pill ${restaurant.is_available ? "is-open" : "is-closed"}`}
                                        >
                                            {restaurant.is_available ? "Available" : "Unavailable"}
                                        </span>
                                    </button>
                                </article>
                            ))}
                        </div>

                        <div className="owner-pagination-row">
                            <button
                                type="button"
                                onClick={() => setRestaurantsPage((prev) => Math.max(1, prev - 1))}
                                disabled={restaurantsPage <= 1 || restaurantsState.loading}
                            >
                                Previous
                            </button>
                            <span>Restaurant page {restaurantsPage}</span>
                            <button
                                type="button"
                                onClick={() =>
                                    setRestaurantsPage((prev) =>
                                        Math.min(restaurantsState.totalPages || 1, prev + 1)
                                    )
                                }
                                disabled={
                                    restaurantsPage >= (restaurantsState.totalPages || 1) ||
                                    restaurantsState.loading
                                }
                            >
                                Next
                            </button>
                        </div>
                    </>
                )}
            </section>

            <section className="owner-section">
                <div className="owner-section-header">
                    <div>
                        <h2>Selected restaurant</h2>
                        <p>
                            {selectedRestaurant
                                ? `Managing ${selectedRestaurant.name}`
                                : "Select a restaurant to manage details and menu items."}
                        </p>
                    </div>

                    {selectedRestaurant ? (
                        <div className="owner-inline-actions">
                            <button
                                type="button"
                                onClick={startEditRestaurant}
                                disabled={isSubmitting}
                            >
                                Edit details
                            </button>
                            <button
                                type="button"
                                onClick={handleDeleteRestaurant}
                                className="danger"
                                disabled={isSubmitting}
                            >
                                Delete restaurant
                            </button>
                        </div>
                    ) : null}
                </div>

                {selectedRestaurant ? (
                    <>
                        {editingRestaurantId === selectedRestaurant.id ? (
                            <form className="owner-form-grid" onSubmit={handleUpdateRestaurant}>
                                <label>
                                    Name
                                    <input
                                        type="text"
                                        value={restaurantEditForm.name}
                                        onChange={(event) =>
                                            setRestaurantEditForm((prev) => ({
                                                ...prev,
                                                name: event.target.value,
                                            }))
                                        }
                                        required
                                        minLength={1}
                                        maxLength={100}
                                    />
                                </label>

                                <label>
                                    Cuisine
                                    <input
                                        type="text"
                                        value={restaurantEditForm.cuisine}
                                        onChange={(event) =>
                                            setRestaurantEditForm((prev) => ({
                                                ...prev,
                                                cuisine: event.target.value,
                                            }))
                                        }
                                        required
                                        minLength={1}
                                        maxLength={100}
                                    />
                                </label>

                                <label>
                                    City
                                    <input
                                        type="text"
                                        value={restaurantEditForm.city}
                                        onChange={(event) =>
                                            setRestaurantEditForm((prev) => ({
                                                ...prev,
                                                city: event.target.value,
                                            }))
                                        }
                                        minLength={1}
                                        maxLength={100}
                                    />
                                </label>

                                <label>
                                    Delivery fee
                                    <input
                                        type="number"
                                        step="0.01"
                                        min="0"
                                        value={restaurantEditForm.delivery_fee}
                                        onChange={(event) =>
                                            setRestaurantEditForm((prev) => ({
                                                ...prev,
                                                delivery_fee: event.target.value,
                                            }))
                                        }
                                        required
                                    />
                                </label>

                                <label className="owner-checkbox-field">
                                    <input
                                        type="checkbox"
                                        checked={restaurantEditForm.is_available}
                                        onChange={(event) =>
                                            setRestaurantEditForm((prev) => ({
                                                ...prev,
                                                is_available: event.target.checked,
                                            }))
                                        }
                                    />
                                    Mark restaurant available
                                </label>

                                <div className="owner-inline-actions">
                                    <button
                                        type="submit"
                                        className="owner-primary-button"
                                        disabled={isSubmitting}
                                    >
                                        {isSubmitting ? "Saving..." : "Save changes"}
                                    </button>
                                    <button
                                        type="button"
                                        onClick={() => setEditingRestaurantId(null)}
                                        disabled={isSubmitting}
                                    >
                                        Cancel
                                    </button>
                                </div>
                            </form>
                        ) : (
                            <div className="owner-summary-grid">
                                <p>
                                    <strong>Name:</strong> {selectedRestaurant.name}
                                </p>
                                <p>
                                    <strong>Cuisine:</strong> {selectedRestaurant.cuisine}
                                </p>
                                <p>
                                    <strong>City:</strong> {selectedRestaurant.city || "N/A"}
                                </p>
                                <p>
                                    <strong>Province:</strong> {selectedRestaurant.province || "N/A"}
                                </p>
                                <p>
                                    <strong>Delivery fee:</strong> ${Number(selectedRestaurant.delivery_fee || 0).toFixed(2)}
                                </p>
                                <p>
                                    <strong>Status:</strong> {selectedRestaurant.is_available ? "Available" : "Unavailable"}
                                </p>
                            </div>
                        )}

                        <div className="owner-subsection-header">
                            <div>
                                <h3>Menu items</h3>
                                <p>
                                    Page {menuPage} of {Math.max(menuState.totalPages, 1)} • {menuState.total} total
                                    {menuSearchQuery.trim()
                                        ? ` matching "${menuSearchQuery.trim()}"`
                                        : ""}
                                </p>
                            </div>
                            <button
                                type="button"
                                className="owner-primary-button"
                                onClick={() => {
                                    setShowCreateMenuItemForm((prev) => !prev);
                                    setEditingMenuItemId(null);
                                    setFeedback({ type: "", text: "" });
                                }}
                            >
                                {showCreateMenuItemForm ? "Close menu form" : "Create menu item"}
                            </button>
                        </div>

                        <div className="owner-search-row compact">
                            <label htmlFor="owner-menu-search">Search menu items by name</label>
                            <input
                                id="owner-menu-search"
                                type="text"
                                value={menuSearchQuery}
                                onChange={(event) => {
                                    setMenuSearchQuery(event.target.value);
                                    setMenuPage(1);
                                }}
                                placeholder="e.g. poutine, burger, latte"
                            />
                        </div>

                        {showCreateMenuItemForm ? (
                            <form className="owner-form-grid" onSubmit={handleCreateMenuItem}>
                                <label>
                                    Name
                                    <input
                                        type="text"
                                        value={newMenuItemForm.name}
                                        onChange={(event) =>
                                            setNewMenuItemForm((prev) => ({
                                                ...prev,
                                                name: event.target.value,
                                            }))
                                        }
                                        required
                                        minLength={1}
                                    />
                                </label>

                                <label>
                                    Description
                                    <textarea
                                        value={newMenuItemForm.description}
                                        onChange={(event) =>
                                            setNewMenuItemForm((prev) => ({
                                                ...prev,
                                                description: event.target.value,
                                            }))
                                        }
                                        rows={3}
                                        required
                                    />
                                </label>

                                <label>
                                    Price
                                    <input
                                        type="number"
                                        step="0.01"
                                        min="0.01"
                                        value={newMenuItemForm.price}
                                        onChange={(event) =>
                                            setNewMenuItemForm((prev) => ({
                                                ...prev,
                                                price: event.target.value,
                                            }))
                                        }
                                        required
                                    />
                                </label>

                                <button type="submit" className="owner-primary-button" disabled={isSubmitting}>
                                    {isSubmitting ? "Saving..." : "Save menu item"}
                                </button>
                            </form>
                        ) : null}

                        {menuState.error ? <p className="owner-status-error">{menuState.error}</p> : null}

                        {menuState.loading ? (
                            <div className="owner-placeholder">Loading menu items...</div>
                        ) : menuState.items.length === 0 ? (
                            <div className="owner-placeholder">No menu items found for this restaurant.</div>
                        ) : (
                            <>
                                <div className="owner-menu-grid">
                                    {menuState.items.map((item) => (
                                        <article key={item.id} className="owner-menu-card">
                                            {editingMenuItemId === item.id ? (
                                                <form
                                                    className="owner-form-grid compact"
                                                    onSubmit={(event) => handleUpdateMenuItem(event, item.id)}
                                                >
                                                    <label>
                                                        Name
                                                        <input
                                                            type="text"
                                                            value={menuItemEditForm.name}
                                                            onChange={(event) =>
                                                                setMenuItemEditForm((prev) => ({
                                                                    ...prev,
                                                                    name: event.target.value,
                                                                }))
                                                            }
                                                            required
                                                        />
                                                    </label>

                                                    <label>
                                                        Description
                                                        <textarea
                                                            value={menuItemEditForm.description}
                                                            onChange={(event) =>
                                                                setMenuItemEditForm((prev) => ({
                                                                    ...prev,
                                                                    description: event.target.value,
                                                                }))
                                                            }
                                                            rows={2}
                                                            required
                                                        />
                                                    </label>

                                                    <label>
                                                        Price
                                                        <input
                                                            type="number"
                                                            step="0.01"
                                                            min="0.01"
                                                            value={menuItemEditForm.price}
                                                            onChange={(event) =>
                                                                setMenuItemEditForm((prev) => ({
                                                                    ...prev,
                                                                    price: event.target.value,
                                                                }))
                                                            }
                                                            required
                                                        />
                                                    </label>

                                                    <div className="owner-inline-actions">
                                                        <button
                                                            type="submit"
                                                            className="owner-primary-button"
                                                            disabled={isSubmitting}
                                                        >
                                                            {isSubmitting ? "Saving..." : "Save"}
                                                        </button>
                                                        <button
                                                            type="button"
                                                            onClick={() => setEditingMenuItemId(null)}
                                                            disabled={isSubmitting}
                                                        >
                                                            Cancel
                                                        </button>
                                                    </div>
                                                </form>
                                            ) : (
                                                <>
                                                    <div className="owner-menu-heading">
                                                        <h4>{item.name}</h4>
                                                        <span>${Number(item.price || 0).toFixed(2)}</span>
                                                    </div>
                                                    <p>{item.description}</p>
                                                    <div className="owner-inline-actions">
                                                        <button
                                                            type="button"
                                                            onClick={() => startEditMenuItem(item)}
                                                            disabled={isSubmitting}
                                                        >
                                                            Edit
                                                        </button>
                                                        <button
                                                            type="button"
                                                            className="danger"
                                                            onClick={() => handleDeleteMenuItem(item)}
                                                            disabled={isSubmitting}
                                                        >
                                                            Delete
                                                        </button>
                                                    </div>
                                                </>
                                            )}
                                        </article>
                                    ))}
                                </div>

                                <div className="owner-pagination-row">
                                    <button
                                        type="button"
                                        onClick={() => setMenuPage((prev) => Math.max(1, prev - 1))}
                                        disabled={menuPage <= 1 || menuState.loading}
                                    >
                                        Previous
                                    </button>
                                    <span>Menu page {menuPage}</span>
                                    <button
                                        type="button"
                                        onClick={() =>
                                            setMenuPage((prev) =>
                                                Math.min(menuState.totalPages || 1, prev + 1)
                                            )
                                        }
                                        disabled={menuPage >= (menuState.totalPages || 1) || menuState.loading}
                                    >
                                        Next
                                    </button>
                                </div>
                            </>
                        )}
                    </>
                ) : (
                    <div className="owner-placeholder">
                        Select one of your restaurants above to manage details and menu items.
                    </div>
                )}
            </section>
        </main>
    );
}
