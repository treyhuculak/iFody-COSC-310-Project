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
import {
    deleteNotification,
    getNotifications,
    markAllAsRead,
    markAsRead,
} from "../api/notifications";
import { getRestaurantReviews } from "../api/restaurantManager";
import "../styles/owner.css";

const OWNER_RESTAURANTS_PAGE_SIZE = 6;
const OWNER_MENU_PAGE_SIZE = 8;
const OWNER_NOTIF_PAGE_SIZE = 8;
const OWNER_REVIEWS_PAGE_SIZE = 10;

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

const TOAST_DURATION_MS = 3200;

const EMPTY_CONFIRMATION_STATE = {
    open: false,
    action: "",
    title: "",
    message: "",
    confirmLabel: "Confirm",
    payload: null,
};

function normalizeRole(role) {
    return String(role || "")
        .toLowerCase()
        .replace(/[^a-z]/g, "");
}

function isOwnerRole(role) {
    return normalizeRole(role) === "restaurantowner";
}

function StarsDisplay({ rating }) {
    const filled = Math.round(Number(rating ?? 0));
    return (
        <span className="owner-stars" aria-label={`${filled} out of 5 stars`}>
            {[1, 2, 3, 4, 5].map((n) => (
                <span key={n} className={n <= filled ? "owner-star filled" : "owner-star"}>★</span>
            ))}
        </span>
    );
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

    const [toasts, setToasts] = useState([]);
    const [confirmationState, setConfirmationState] = useState(EMPTY_CONFIRMATION_STATE);
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

    // ── Notifications ────────────────────────────────────────────────────────
    const [notifItems, setNotifItems] = useState([]);
    const [notifLoading, setNotifLoading] = useState(true);
    const [notifError, setNotifError] = useState("");
    const [notifPage, setNotifPage] = useState(1);

    // ── Reviews (for active restaurant) ──────────────────────────────────────
    const [reviewItems, setReviewItems] = useState([]);
    const [reviewLoading, setReviewLoading] = useState(false);
    const [reviewError, setReviewError] = useState("");
    const [reviewPage, setReviewPage] = useState(1);
    const [reviewTotalPages, setReviewTotalPages] = useState(1);
    const [reviewHasNext, setReviewHasNext] = useState(false);
    const [reviewHasPrev, setReviewHasPrev] = useState(false);

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

    // Load notifications on mount / when owner changes
    useEffect(() => {
        if (!canManageRestaurants || !ownerId) return;
        let cancelled = false;
        setNotifLoading(true);
        setNotifError("");
        getNotifications(ownerId)
            .then((data) => {
                if (cancelled) return;
                const sorted = [...(Array.isArray(data) ? data : [])].sort(
                    (a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0)
                );
                setNotifItems(sorted);
                setNotifLoading(false);
            })
            .catch((err) => {
                if (cancelled) return;
                setNotifError(err.message || "Failed to load notifications.");
                setNotifLoading(false);
            });
        return () => { cancelled = true; };
    }, [canManageRestaurants, ownerId]);

    // Load reviews when active restaurant changes
    useEffect(() => {
        if (!canManageRestaurants || !activeRestaurantId) {
            setReviewItems([]);
            setReviewTotalPages(1);
            setReviewHasNext(false);
            setReviewHasPrev(false);
            setReviewPage(1);
            return;
        }
        let cancelled = false;
        setReviewLoading(true);
        setReviewError("");
        setReviewPage(1);
        getRestaurantReviews(activeRestaurantId, { skip: 0, limit: OWNER_REVIEWS_PAGE_SIZE })
            .then((data) => {
                if (cancelled) return;
                setReviewItems(data.items ?? []);
                setReviewTotalPages(data.total_pages ?? 1);
                setReviewHasNext(data.has_next ?? false);
                setReviewHasPrev(data.has_prev ?? false);
                setReviewLoading(false);
            })
            .catch((err) => {
                if (cancelled) return;
                setReviewError(err.message || "Failed to load reviews.");
                setReviewItems([]);
                setReviewLoading(false);
            });
        return () => { cancelled = true; };
    }, [canManageRestaurants, activeRestaurantId]);

    const selectedRestaurant = useMemo(() => {
        return (
            restaurantsState.items.find((restaurant) => restaurant.id === activeRestaurantId) || null
        );
    }, [restaurantsState.items, activeRestaurantId]);

    const selectedMenuItem = useMemo(() => {
        if (!editingMenuItemId) {
            return null;
        }

        return menuState.items.find((item) => item.id === editingMenuItemId) || null;
    }, [menuState.items, editingMenuItemId]);

    const isCreateRestaurantModalOpen = showCreateRestaurantForm;
    const isEditRestaurantModalOpen =
        Boolean(selectedRestaurant) && editingRestaurantId === selectedRestaurant?.id;
    const isCreateMenuModalOpen = showCreateMenuItemForm;
    const isEditMenuModalOpen = Boolean(selectedMenuItem);
    const isConfirmModalOpen = confirmationState.open;

    const dismissToast = (toastId) => {
        setToasts((previousToasts) =>
            previousToasts.filter((toast) => toast.id !== toastId)
        );
    };

    const pushToast = (type, text) => {
        const toastId = `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
        setToasts((previousToasts) => [...previousToasts, { id: toastId, type, text }]);

        window.setTimeout(() => {
            dismissToast(toastId);
        }, TOAST_DURATION_MS);
    };

    useEffect(() => {
        if (!selectedRestaurant) {
            setEditingRestaurantId(null);
            return;
        }

        if (editingRestaurantId && editingRestaurantId !== selectedRestaurant.id) {
            setEditingRestaurantId(null);
        }
    }, [selectedRestaurant, editingRestaurantId]);

    useEffect(() => {
        const hasOpenModal =
            isCreateRestaurantModalOpen ||
            isEditRestaurantModalOpen ||
            isCreateMenuModalOpen ||
            isEditMenuModalOpen ||
            isConfirmModalOpen;

        if (!hasOpenModal) {
            return undefined;
        }

        const handleEscape = (event) => {
            if (event.key !== "Escape" || isSubmitting) {
                return;
            }

            setShowCreateRestaurantForm(false);
            setEditingRestaurantId(null);
            setShowCreateMenuItemForm(false);
            setEditingMenuItemId(null);
            setConfirmationState(EMPTY_CONFIRMATION_STATE);
        };

        const previousOverflow = document.body.style.overflow;
        document.body.style.overflow = "hidden";

        window.addEventListener("keydown", handleEscape);
        return () => {
            document.body.style.overflow = previousOverflow;
            window.removeEventListener("keydown", handleEscape);
        };
    }, [
        isCreateRestaurantModalOpen,
        isEditRestaurantModalOpen,
        isCreateMenuModalOpen,
        isEditMenuModalOpen,
        isConfirmModalOpen,
        isSubmitting,
    ]);

    const handleRestaurantCardClick = (restaurantId) => {
        if (restaurantId === activeRestaurantId) {
            return;
        }

        setActiveRestaurantId(restaurantId);
        setMenuPage(1);
        setMenuSearchQuery("");
        setEditingMenuItemId(null);
        setShowCreateMenuItemForm(false);
        setConfirmationState(EMPTY_CONFIRMATION_STATE);
    };

    const handleCreateRestaurant = async (event) => {
        event.preventDefault();
        if (!canManageRestaurants || isSubmitting) {
            return;
        }

        const deliveryFee = Number(newRestaurantForm.delivery_fee);
        if (Number.isNaN(deliveryFee) || deliveryFee < 0) {
            pushToast("error", "Delivery fee must be a number greater than or equal to 0.");
            return;
        }

        setIsSubmitting(true);

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
            pushToast("success", "Restaurant created successfully.");
        } catch (error) {
            pushToast("error", error.message || "Could not create restaurant.");
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
            pushToast("error", "Restaurant name and cuisine are required.");
            return;
        }

        if (Number.isNaN(deliveryFee) || deliveryFee < 0) {
            pushToast("error", "Delivery fee must be a number greater than or equal to 0.");
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

        try {
            await updateRestaurant({
                restaurantId: selectedRestaurant.id,
                updates,
                userId: ownerId,
            });

            setEditingRestaurantId(null);
            setRestaurantsRefreshKey((prev) => prev + 1);
            pushToast("success", "Restaurant updated successfully.");
        } catch (error) {
            pushToast("error", error.message || "Could not update restaurant.");
        } finally {
            setIsSubmitting(false);
        }
    };

    const requestDeleteRestaurant = () => {
        if (!selectedRestaurant || !canManageRestaurants || isSubmitting) {
            return;
        }

        setConfirmationState({
            open: true,
            action: "deleteRestaurant",
            title: "Delete restaurant?",
            message: `Delete "${selectedRestaurant.name}"? This action cannot be undone.`,
            confirmLabel: "Delete restaurant",
            payload: selectedRestaurant,
        });
    };

    const handleCreateMenuItem = async (event) => {
        event.preventDefault();
        if (!selectedRestaurant || !canManageRestaurants || isSubmitting) {
            return;
        }

        const price = Number(newMenuItemForm.price);
        if (Number.isNaN(price) || price <= 0) {
            pushToast("error", "Menu item price must be greater than 0.");
            return;
        }

        setIsSubmitting(true);

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
            pushToast("success", "Menu item created successfully.");
        } catch (error) {
            pushToast("error", error.message || "Could not create menu item.");
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
    };

    const handleUpdateMenuItem = async (event, menuItemId) => {
        event.preventDefault();
        if (!selectedRestaurant || !canManageRestaurants || isSubmitting) {
            return;
        }

        const trimmedName = menuItemEditForm.name.trim();
        const price = Number(menuItemEditForm.price);

        if (!trimmedName) {
            pushToast("error", "Menu item name is required.");
            return;
        }

        if (Number.isNaN(price) || price <= 0) {
            pushToast("error", "Menu item price must be greater than 0.");
            return;
        }

        setIsSubmitting(true);

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
            pushToast("success", "Menu item updated successfully.");
        } catch (error) {
            pushToast("error", error.message || "Could not update menu item.");
        } finally {
            setIsSubmitting(false);
        }
    };

    const requestDeleteMenuItem = (item) => {
        if (!selectedRestaurant || !canManageRestaurants || isSubmitting) {
            return;
        }

        if (!item) {
            return;
        }

        setConfirmationState({
            open: true,
            action: "deleteMenuItem",
            title: "Delete menu item?",
            message: `Delete "${item.name}" from ${selectedRestaurant.name}?`,
            confirmLabel: "Delete menu item",
            payload: {
                item,
                restaurantId: selectedRestaurant.id,
            },
        });
    };

    const closeConfirmation = () => {
        if (isSubmitting) {
            return;
        }

        setConfirmationState(EMPTY_CONFIRMATION_STATE);
    };

    const handleConfirmAction = async () => {
        if (!confirmationState.open || isSubmitting || !canManageRestaurants) {
            return;
        }

        setIsSubmitting(true);

        try {
            if (confirmationState.action === "deleteRestaurant") {
                const restaurant = confirmationState.payload;
                if (!restaurant?.id) {
                    throw new Error("Restaurant information is missing.");
                }

                await deleteRestaurant({
                    restaurantId: restaurant.id,
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
                pushToast("success", "Restaurant deleted successfully.");
            }

            if (confirmationState.action === "deleteMenuItem") {
                const payload = confirmationState.payload;
                if (!payload?.restaurantId || !payload?.item?.id) {
                    throw new Error("Menu item information is missing.");
                }

                await deleteRestaurantMenuItem({
                    restaurantId: payload.restaurantId,
                    menuItemId: payload.item.id,
                    userId: ownerId,
                });

                if (menuState.items.length === 1 && menuPage > 1) {
                    setMenuPage((prev) => Math.max(1, prev - 1));
                } else {
                    setMenuRefreshKey((prev) => prev + 1);
                }

                setEditingMenuItemId((previousId) =>
                    previousId === payload.item.id ? null : previousId
                );
                pushToast("success", "Menu item deleted successfully.");
            }

            setConfirmationState(EMPTY_CONFIRMATION_STATE);
        } catch (error) {
            pushToast("error", error.message || "Unable to complete this action.");
        } finally {
            setIsSubmitting(false);
        }
    };

    // ── Notification handlers ─────────────────────────────────────────────────
    const handleMarkNotifRead = async (notifId) => {
        try {
            await markAsRead(notifId, ownerId);
            setNotifItems((prev) => prev.map((n) => n.id === notifId ? { ...n, is_read: true } : n));
        } catch { /* silent */ }
    };

    const handleMarkAllNotifRead = async () => {
        try {
            await markAllAsRead(ownerId);
            setNotifItems((prev) => prev.map((n) => ({ ...n, is_read: true })));
        } catch { /* silent */ }
    };

    const handleDeleteNotif = async (notifId) => {
        try {
            await deleteNotification(notifId, ownerId);
            setNotifItems((prev) => {
                const updated = prev.filter((n) => n.id !== notifId);
                const maxPage = Math.max(1, Math.ceil(updated.length / OWNER_NOTIF_PAGE_SIZE));
                if (notifPage > maxPage) setNotifPage(maxPage);
                return updated;
            });
        } catch { /* silent */ }
    };

    // ── Reviews pagination handler ─────────────────────────────────────────
    const loadReviewsPage = (page) => {
        if (!activeRestaurantId) return;
        setReviewLoading(true);
        setReviewError("");
        const skip = (page - 1) * OWNER_REVIEWS_PAGE_SIZE;
        getRestaurantReviews(activeRestaurantId, { skip, limit: OWNER_REVIEWS_PAGE_SIZE })
            .then((data) => {
                setReviewPage(page);
                setReviewItems(data.items ?? []);
                setReviewTotalPages(data.total_pages ?? 1);
                setReviewHasNext(data.has_next ?? false);
                setReviewHasPrev(data.has_prev ?? false);
                setReviewLoading(false);
            })
            .catch((err) => {
                setReviewError(err.message || "Failed to load reviews.");
                setReviewLoading(false);
            });
    };

    // ── Derived notification values ────────────────────────────────────────
    const notifTotalPages = Math.max(1, Math.ceil(notifItems.length / OWNER_NOTIF_PAGE_SIZE));
    const notifSlice = notifItems.slice(
        (notifPage - 1) * OWNER_NOTIF_PAGE_SIZE,
        notifPage * OWNER_NOTIF_PAGE_SIZE
    );
    const unreadNotifCount = notifItems.filter((n) => !n.is_read).length;

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
            <div className="owner-toast-stack" aria-live="polite" aria-atomic="true">
                {toasts.map((toast) => (
                    <div key={toast.id} className={`owner-toast is-${toast.type || "info"}`}>
                        <p>{toast.text}</p>
                        <button
                            type="button"
                            className="owner-toast-close"
                            onClick={() => dismissToast(toast.id)}
                            aria-label="Dismiss notification"
                        >
                            x
                        </button>
                    </div>
                ))}
            </div>

            <section className="owner-hero">
                <p className="owner-kicker">Owner Portal</p>
                <h1>Manage your restaurants and menus</h1>
                <p>
                    Select one of your restaurants to edit details, manage menu items, or remove it.
                    Use the create buttons to add new restaurants and menu items.
                </p>
            </section>

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
                            setShowCreateRestaurantForm(true);
                            setEditingRestaurantId(null);
                        }}
                    >
                        Create restaurant
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
                                onClick={requestDeleteRestaurant}
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
                                    setShowCreateMenuItemForm(true);
                                    setEditingMenuItemId(null);
                                }}
                            >
                                Create menu item
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
                                                        onClick={() => requestDeleteMenuItem(item)}
                                                        disabled={isSubmitting}
                                                    >
                                                        Delete
                                                    </button>
                                                </div>
                                            </>
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

                        {/* ── Customer reviews subsection ────────────────── */}
                        <div className="owner-subsection-header">
                            <div>
                                <h3>Customer reviews</h3>
                                <p>
                                    {reviewLoading
                                        ? "Loading…"
                                        : `Page ${reviewPage} of ${Math.max(reviewTotalPages, 1)}`}
                                </p>
                            </div>
                        </div>

                        {reviewError ? (
                            <p className="owner-status-error">{reviewError}</p>
                        ) : reviewLoading ? (
                            <div className="owner-placeholder">Loading reviews...</div>
                        ) : reviewItems.length === 0 ? (
                            <div className="owner-placeholder">No reviews yet for this restaurant.</div>
                        ) : (
                            <>
                                <div className="owner-review-list">
                                    {reviewItems.map((rev) => (
                                        <div key={rev.id} className="owner-review-card">
                                            <div className="owner-review-header">
                                                <StarsDisplay rating={rev.rating} />
                                                <span className="owner-review-title">{rev.title}</span>
                                                {rev.created_at && (
                                                    <span className="owner-review-date">
                                                        {new Date(rev.created_at).toLocaleDateString()}
                                                    </span>
                                                )}
                                            </div>
                                            {rev.comment && (
                                                <p className="owner-review-comment">{rev.comment}</p>
                                            )}
                                        </div>
                                    ))}
                                </div>

                                {reviewTotalPages > 1 && (
                                    <div className="owner-pagination-row">
                                        <button
                                            type="button"
                                            disabled={!reviewHasPrev || reviewLoading}
                                            onClick={() => loadReviewsPage(reviewPage - 1)}
                                        >
                                            Previous
                                        </button>
                                        <span>Reviews page {reviewPage}</span>
                                        <button
                                            type="button"
                                            disabled={!reviewHasNext || reviewLoading}
                                            onClick={() => loadReviewsPage(reviewPage + 1)}
                                        >
                                            Next
                                        </button>
                                    </div>
                                )}
                            </>
                        )}
                    </>
                ) : (
                    <div className="owner-placeholder">
                        Select one of your restaurants above to manage details and menu items.
                    </div>
                )}
            </section>

            {/* ── Notifications section ──────────────────────────────────── */}
            <section className="owner-section">
                <div className="owner-section-header">
                    <div>
                        <h2>
                            Notifications
                            {unreadNotifCount > 0 && (
                                <span className="owner-notif-badge">{unreadNotifCount}</span>
                            )}
                        </h2>
                        <p>Your recent order alerts and activity updates</p>
                    </div>
                    {notifItems.length > 0 && (
                        <button type="button" onClick={handleMarkAllNotifRead}>
                            Mark all as read
                        </button>
                    )}
                </div>

                {notifLoading ? (
                    <div className="owner-placeholder">Loading notifications...</div>
                ) : notifError ? (
                    <p className="owner-status-error">{notifError}</p>
                ) : notifItems.length === 0 ? (
                    <div className="owner-placeholder">No notifications yet.</div>
                ) : (
                    <>
                        <div className="owner-notif-list">
                            {notifSlice.map((n) => (
                                <div key={n.id} className={`owner-notif-row${n.is_read ? "" : " is-unread"}`}>
                                    <div className="owner-notif-body">
                                        {!n.is_read && <span className="owner-notif-dot" />}
                                        <p className="owner-notif-message">
                                            {n.message ?? n.title ?? "Notification"}
                                        </p>
                                        {n.created_at && (
                                            <p className="owner-notif-time">
                                                {new Date(n.created_at).toLocaleString()}
                                            </p>
                                        )}
                                    </div>
                                    <div className="owner-inline-actions" style={{ marginTop: 0, flexShrink: 0 }}>
                                        {!n.is_read && (
                                            <button type="button" onClick={() => handleMarkNotifRead(n.id)}>
                                                Mark read
                                            </button>
                                        )}
                                        <button
                                            type="button"
                                            className="danger"
                                            onClick={() => handleDeleteNotif(n.id)}
                                        >
                                            Delete
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>

                        {notifTotalPages > 1 && (
                            <div className="owner-pagination-row">
                                <button
                                    type="button"
                                    disabled={notifPage <= 1}
                                    onClick={() => setNotifPage((p) => p - 1)}
                                >
                                    Previous
                                </button>
                                <span>Page {notifPage} of {notifTotalPages}</span>
                                <button
                                    type="button"
                                    disabled={notifPage >= notifTotalPages}
                                    onClick={() => setNotifPage((p) => p + 1)}
                                >
                                    Next
                                </button>
                            </div>
                        )}
                    </>
                )}
            </section>

            {isConfirmModalOpen ? (
                <div className="owner-modal-backdrop" onClick={closeConfirmation}>
                    <div
                        className="owner-modal owner-confirm-modal"
                        onClick={(event) => event.stopPropagation()}
                    >
                        <div className="owner-modal-header">
                            <h3>{confirmationState.title || "Please confirm"}</h3>
                            <button
                                type="button"
                                className="owner-modal-close"
                                onClick={closeConfirmation}
                                disabled={isSubmitting}
                                aria-label="Close confirmation dialog"
                            >
                                x
                            </button>
                        </div>

                        <p className="owner-confirm-message">{confirmationState.message}</p>

                        <div className="owner-inline-actions owner-confirm-actions">
                            <button
                                type="button"
                                className="danger"
                                onClick={handleConfirmAction}
                                disabled={isSubmitting}
                            >
                                {isSubmitting ? "Working..." : confirmationState.confirmLabel || "Confirm"}
                            </button>
                            <button
                                type="button"
                                onClick={closeConfirmation}
                                disabled={isSubmitting}
                            >
                                Cancel
                            </button>
                        </div>
                    </div>
                </div>
            ) : null}

            {isCreateRestaurantModalOpen ? (
                <div
                    className="owner-modal-backdrop"
                    onClick={() => {
                        if (!isSubmitting) {
                            setShowCreateRestaurantForm(false);
                        }
                    }}
                >
                    <div className="owner-modal" onClick={(event) => event.stopPropagation()}>
                        <div className="owner-modal-header">
                            <h3>Create restaurant</h3>
                            <button
                                type="button"
                                className="owner-modal-close"
                                onClick={() => setShowCreateRestaurantForm(false)}
                                disabled={isSubmitting}
                                aria-label="Close create restaurant form"
                            >
                                x
                            </button>
                        </div>
                        <form className="owner-form-grid owner-modal-form" onSubmit={handleCreateRestaurant}>
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

                            <div className="owner-inline-actions owner-modal-actions">
                                <button
                                    type="submit"
                                    className="owner-primary-button"
                                    disabled={isSubmitting}
                                >
                                    {isSubmitting ? "Saving..." : "Save restaurant"}
                                </button>
                                <button
                                    type="button"
                                    onClick={() => setShowCreateRestaurantForm(false)}
                                    disabled={isSubmitting}
                                >
                                    Cancel
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            ) : null}

            {isEditRestaurantModalOpen ? (
                <div
                    className="owner-modal-backdrop"
                    onClick={() => {
                        if (!isSubmitting) {
                            setEditingRestaurantId(null);
                        }
                    }}
                >
                    <div className="owner-modal" onClick={(event) => event.stopPropagation()}>
                        <div className="owner-modal-header">
                            <h3>Edit restaurant</h3>
                            <button
                                type="button"
                                className="owner-modal-close"
                                onClick={() => setEditingRestaurantId(null)}
                                disabled={isSubmitting}
                                aria-label="Close edit restaurant form"
                            >
                                x
                            </button>
                        </div>
                        <form className="owner-form-grid owner-modal-form" onSubmit={handleUpdateRestaurant}>
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

                            <label className="owner-checkbox-field owner-modal-checkbox-field">
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

                            <div className="owner-inline-actions owner-modal-actions">
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
                    </div>
                </div>
            ) : null}

            {isCreateMenuModalOpen ? (
                <div
                    className="owner-modal-backdrop"
                    onClick={() => {
                        if (!isSubmitting) {
                            setShowCreateMenuItemForm(false);
                        }
                    }}
                >
                    <div className="owner-modal" onClick={(event) => event.stopPropagation()}>
                        <div className="owner-modal-header">
                            <h3>Create menu item</h3>
                            <button
                                type="button"
                                className="owner-modal-close"
                                onClick={() => setShowCreateMenuItemForm(false)}
                                disabled={isSubmitting}
                                aria-label="Close create menu item form"
                            >
                                x
                            </button>
                        </div>
                        <form className="owner-form-grid owner-modal-form" onSubmit={handleCreateMenuItem}>
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

                            <label className="owner-modal-field-full">
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

                            <div className="owner-inline-actions owner-modal-actions">
                                <button
                                    type="submit"
                                    className="owner-primary-button"
                                    disabled={isSubmitting}
                                >
                                    {isSubmitting ? "Saving..." : "Save menu item"}
                                </button>
                                <button
                                    type="button"
                                    onClick={() => setShowCreateMenuItemForm(false)}
                                    disabled={isSubmitting}
                                >
                                    Cancel
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            ) : null}

            {isEditMenuModalOpen ? (
                <div
                    className="owner-modal-backdrop"
                    onClick={() => {
                        if (!isSubmitting) {
                            setEditingMenuItemId(null);
                        }
                    }}
                >
                    <div className="owner-modal" onClick={(event) => event.stopPropagation()}>
                        <div className="owner-modal-header">
                            <h3>Edit menu item</h3>
                            <button
                                type="button"
                                className="owner-modal-close"
                                onClick={() => setEditingMenuItemId(null)}
                                disabled={isSubmitting}
                                aria-label="Close edit menu item form"
                            >
                                x
                            </button>
                        </div>
                        <form
                            className="owner-form-grid owner-modal-form"
                            onSubmit={(event) => handleUpdateMenuItem(event, selectedMenuItem.id)}
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

                            <label className="owner-modal-field-full">
                                Description
                                <textarea
                                    value={menuItemEditForm.description}
                                    onChange={(event) =>
                                        setMenuItemEditForm((prev) => ({
                                            ...prev,
                                            description: event.target.value,
                                        }))
                                    }
                                    rows={3}
                                    required
                                />
                            </label>

                            <div className="owner-inline-actions owner-modal-actions">
                                <button
                                    type="submit"
                                    className="owner-primary-button"
                                    disabled={isSubmitting}
                                >
                                    {isSubmitting ? "Saving..." : "Save changes"}
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
                    </div>
                </div>
            ) : null}
        </main>
    );
}
