import { useCallback, useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import {
    addMenuItem,
    addRestaurant,
    deleteMenuItem,
    deleteRestaurant,
    getMyRestaurants,
    updateMenuItem,
    updateRestaurant,
} from "../api/restaurantManager";
import { parseUserIdFromStorage } from "../api/restaurants";
import "../styles/restaurant-manager.css";

const emptyRestaurantForm = { name: "", cuisine: "", location: "", rating: "" };
const emptyMenuItemForm = { name: "", description: "", price: "" };

export default function RestaurantManager() {
    const location = useLocation();
    const navigate = useNavigate();
    const userId = parseUserIdFromStorage();
    const userRole =
        typeof localStorage !== "undefined" ? localStorage.getItem("userRole") || "" : "";

    const redirectToLogin = useCallback(() => {
        const redirectPath = `${location.pathname}${location.search}`;
        navigate(`/login?${new URLSearchParams({ redirect: redirectPath })}`);
    }, [location.pathname, location.search, navigate]);

    const [restaurants, setRestaurants] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [successMessage, setSuccessMessage] = useState("");

    const [addForm, setAddForm] = useState(emptyRestaurantForm);
    const [addBusy, setAddBusy] = useState(false);

    const [editId, setEditId] = useState(null);
    const [editForm, setEditForm] = useState(emptyRestaurantForm);
    const [editBusy, setEditBusy] = useState(false);

    const [selectedRestaurantId, setSelectedRestaurantId] = useState(null);
    const [menuItemForm, setMenuItemForm] = useState(emptyMenuItemForm);
    const [menuBusy, setMenuBusy] = useState(false);

    const [editMenuItemId, setEditMenuItemId] = useState(null);
    const [editMenuItemForm, setEditMenuItemForm] = useState(emptyMenuItemForm);

    const loadRestaurants = useCallback(async () => {
        if (!userId) return;
        try {
            setLoading(true);
            const data = await getMyRestaurants(userId, userId);
            setRestaurants(data || []);
            setError("");
        } catch (err) {
            setError(err.message || "Failed to load your restaurants.");
        } finally {
            setLoading(false);
        }
    }, [userId]);

    useEffect(() => {
        if (!userId || userRole !== "restaurant owner") {
            redirectToLogin();
            return;
        }
        loadRestaurants();
    }, [loadRestaurants, redirectToLogin, userId, userRole]);

    const clearMessages = () => {
        setError("");
        setSuccessMessage("");
    };

    const handleAddRestaurant = async (e) => {
        e.preventDefault();
        clearMessages();
        setAddBusy(true);
        try {
            await addRestaurant(
                {
                    name: addForm.name,
                    cuisine: addForm.cuisine,
                    location: addForm.location,
                    rating: addForm.rating ? Number(addForm.rating) : undefined,
                    owner_id: userId,
                },
                userId
            );
            setAddForm(emptyRestaurantForm);
            setSuccessMessage("Restaurant added.");
            await loadRestaurants();
        } catch (err) {
            setError(err.message || "Failed to add restaurant.");
        } finally {
            setAddBusy(false);
        }
    };

    const handleEditSubmit = async (e) => {
        e.preventDefault();
        if (!editId) return;
        clearMessages();
        setEditBusy(true);
        try {
            await updateRestaurant(editId, editForm, userId);
            setEditId(null);
            setSuccessMessage("Restaurant updated.");
            await loadRestaurants();
        } catch (err) {
            setError(err.message || "Failed to update restaurant.");
        } finally {
            setEditBusy(false);
        }
    };

    const handleDeleteRestaurant = async (restaurantId) => {
        clearMessages();
        try {
            await deleteRestaurant(restaurantId, userId);
            if (selectedRestaurantId === restaurantId) setSelectedRestaurantId(null);
            setSuccessMessage("Restaurant deleted.");
            await loadRestaurants();
        } catch (err) {
            setError(err.message || "Failed to delete restaurant.");
        }
    };

    const handleAddMenuItem = async (e) => {
        e.preventDefault();
        if (!selectedRestaurantId) return;
        clearMessages();
        setMenuBusy(true);
        try {
            await addMenuItem(
                selectedRestaurantId,
                {
                    name: menuItemForm.name,
                    description: menuItemForm.description,
                    price: Number(menuItemForm.price),
                },
                userId
            );
            setMenuItemForm(emptyMenuItemForm);
            setSuccessMessage("Menu item added.");
            await loadRestaurants();
        } catch (err) {
            setError(err.message || "Failed to add menu item.");
        } finally {
            setMenuBusy(false);
        }
    };

    const handleUpdateMenuItem = async (e) => {
        e.preventDefault();
        if (!selectedRestaurantId || !editMenuItemId) return;
        clearMessages();
        setMenuBusy(true);
        try {
            await updateMenuItem(
                selectedRestaurantId,
                editMenuItemId,
                {
                    name: editMenuItemForm.name,
                    description: editMenuItemForm.description,
                    price: Number(editMenuItemForm.price),
                },
                userId
            );
            setEditMenuItemId(null);
            setEditMenuItemForm(emptyMenuItemForm);
            setSuccessMessage("Menu item updated.");
            await loadRestaurants();
        } catch (err) {
            setError(err.message || "Failed to update menu item.");
        } finally {
            setMenuBusy(false);
        }
    };

    const handleDeleteMenuItem = async (menuItemId) => {
        if (!selectedRestaurantId) return;
        clearMessages();
        try {
            await deleteMenuItem(selectedRestaurantId, menuItemId, userId);
            setSuccessMessage("Menu item deleted.");
            await loadRestaurants();
        } catch (err) {
            setError(err.message || "Failed to delete menu item.");
        }
    };

    const selectedRestaurant = restaurants.find((r) => r.id === selectedRestaurantId);

    return (
        <main className="home-page">
            <section className="hero-banner">
                <p className="hero-kicker">Management</p>
                <h1>My Restaurants</h1>
                <p className="hero-subtitle">Add, update, or remove your restaurants and their menus.</p>
            </section>

            {error && <p className="status-error">{error}</p>}
            {successMessage && <p className="status-success">{successMessage}</p>}

            {/* Add restaurant form */}
            <section className="restaurant-section">
                <div className="rm-form-card">
                    <h2>Add a new restaurant</h2>
                    <form className="rm-form" onSubmit={handleAddRestaurant}>
                        <label>
                            Name
                            <input
                                type="text"
                                value={addForm.name}
                                onChange={(e) => setAddForm((p) => ({ ...p, name: e.target.value }))}
                                required
                                placeholder="Restaurant name"
                            />
                        </label>
                        <label>
                            Cuisine
                            <input
                                type="text"
                                value={addForm.cuisine}
                                onChange={(e) => setAddForm((p) => ({ ...p, cuisine: e.target.value }))}
                                placeholder="e.g. Italian"
                            />
                        </label>
                        <label>
                            Location
                            <input
                                type="text"
                                value={addForm.location}
                                onChange={(e) => setAddForm((p) => ({ ...p, location: e.target.value }))}
                                placeholder="City or address"
                            />
                        </label>
                        <label>
                            Rating (0–5)
                            <input
                                type="number"
                                min="0"
                                max="5"
                                step="0.1"
                                value={addForm.rating}
                                onChange={(e) => setAddForm((p) => ({ ...p, rating: e.target.value }))}
                                placeholder="4.5"
                            />
                        </label>
                        <button type="submit" disabled={addBusy}>
                            {addBusy ? "Adding…" : "Add restaurant"}
                        </button>
                    </form>
                </div>
            </section>

            {/* Restaurant list */}
            <section className="restaurant-section">
                <h2 className="section-title">Your restaurants</h2>
                {loading ? (
                    <div className="section-placeholder">Loading your restaurants…</div>
                ) : restaurants.length === 0 ? (
                    <div className="section-placeholder">You have no restaurants yet.</div>
                ) : (
                    <div className="rm-restaurant-list">
                        {restaurants.map((r) => (
                            <article key={r.id} className="rm-restaurant-card">
                                {editId === r.id ? (
                                    <form className="rm-form" onSubmit={handleEditSubmit}>
                                        <label>
                                            Name
                                            <input
                                                value={editForm.name}
                                                onChange={(e) =>
                                                    setEditForm((p) => ({ ...p, name: e.target.value }))
                                                }
                                                required
                                            />
                                        </label>
                                        <label>
                                            Cuisine
                                            <input
                                                value={editForm.cuisine}
                                                onChange={(e) =>
                                                    setEditForm((p) => ({ ...p, cuisine: e.target.value }))
                                                }
                                            />
                                        </label>
                                        <label>
                                            Location
                                            <input
                                                value={editForm.location}
                                                onChange={(e) =>
                                                    setEditForm((p) => ({ ...p, location: e.target.value }))
                                                }
                                            />
                                        </label>
                                        <div className="rm-card-actions">
                                            <button type="submit" className="rm-btn primary" disabled={editBusy}>
                                                {editBusy ? "Saving…" : "Save"}
                                            </button>
                                            <button
                                                type="button"
                                                className="rm-btn secondary"
                                                onClick={() => setEditId(null)}
                                            >
                                                Cancel
                                            </button>
                                        </div>
                                    </form>
                                ) : (
                                    <>
                                        <div className="rm-restaurant-header">
                                            <div>
                                                <h3>{r.name}</h3>
                                                <p className="rm-restaurant-meta">
                                                    {r.cuisine} &mdash; {r.location} &mdash; ★{" "}
                                                    {Number(r.rating ?? 0).toFixed(1)}
                                                </p>
                                            </div>
                                            <div className="rm-card-actions">
                                                <button
                                                    type="button"
                                                    className="rm-btn secondary"
                                                    onClick={() => {
                                                        setEditId(r.id);
                                                        setEditForm({
                                                            name: r.name || "",
                                                            cuisine: r.cuisine || "",
                                                            location: r.location || "",
                                                            rating: r.rating ?? "",
                                                        });
                                                    }}
                                                >
                                                    Edit
                                                </button>
                                                <button
                                                    type="button"
                                                    className="rm-btn primary"
                                                    onClick={() =>
                                                        setSelectedRestaurantId(
                                                            selectedRestaurantId === r.id ? null : r.id
                                                        )
                                                    }
                                                >
                                                    {selectedRestaurantId === r.id
                                                        ? "Close menu"
                                                        : "Manage menu"}
                                                </button>
                                                <button
                                                    type="button"
                                                    className="rm-btn danger"
                                                    onClick={() => handleDeleteRestaurant(r.id)}
                                                >
                                                    Delete
                                                </button>
                                            </div>
                                        </div>

                                        {selectedRestaurantId === r.id && (
                                            <div className="rm-menu-section">
                                                <h4>Menu items</h4>

                                                {(r.menu_items || []).length === 0 ? (
                                                    <p style={{ fontSize: "0.85rem", color: "#7a5540" }}>
                                                        No items yet.
                                                    </p>
                                                ) : (
                                                    <div className="rm-menu-list">
                                                        {(r.menu_items || []).map((item) => (
                                                            <div key={item.id} className="rm-menu-item-row">
                                                                {editMenuItemId === item.id ? (
                                                                    <form
                                                                        className="rm-form"
                                                                        style={{ flex: 1 }}
                                                                        onSubmit={handleUpdateMenuItem}
                                                                    >
                                                                        <label>
                                                                            Name
                                                                            <input
                                                                                value={editMenuItemForm.name}
                                                                                onChange={(e) =>
                                                                                    setEditMenuItemForm((p) => ({
                                                                                        ...p,
                                                                                        name: e.target.value,
                                                                                    }))
                                                                                }
                                                                                required
                                                                            />
                                                                        </label>
                                                                        <label>
                                                                            Price
                                                                            <input
                                                                                type="number"
                                                                                min="0"
                                                                                step="0.01"
                                                                                value={editMenuItemForm.price}
                                                                                onChange={(e) =>
                                                                                    setEditMenuItemForm((p) => ({
                                                                                        ...p,
                                                                                        price: e.target.value,
                                                                                    }))
                                                                                }
                                                                                required
                                                                            />
                                                                        </label>
                                                                        <div className="rm-card-actions">
                                                                            <button
                                                                                type="submit"
                                                                                className="rm-btn primary"
                                                                                disabled={menuBusy}
                                                                            >
                                                                                {menuBusy ? "Saving…" : "Save"}
                                                                            </button>
                                                                            <button
                                                                                type="button"
                                                                                className="rm-btn secondary"
                                                                                onClick={() =>
                                                                                    setEditMenuItemId(null)
                                                                                }
                                                                            >
                                                                                Cancel
                                                                            </button>
                                                                        </div>
                                                                    </form>
                                                                ) : (
                                                                    <>
                                                                        <div className="rm-menu-item-info">
                                                                            <p className="rm-menu-item-name">
                                                                                {item.name}
                                                                            </p>
                                                                            <p className="rm-menu-item-price">
                                                                                ${Number(item.price ?? 0).toFixed(2)}
                                                                            </p>
                                                                        </div>
                                                                        <div className="rm-card-actions">
                                                                            <button
                                                                                type="button"
                                                                                className="rm-btn secondary"
                                                                                onClick={() => {
                                                                                    setEditMenuItemId(item.id);
                                                                                    setEditMenuItemForm({
                                                                                        name: item.name || "",
                                                                                        description:
                                                                                            item.description || "",
                                                                                        price: item.price ?? "",
                                                                                    });
                                                                                }}
                                                                            >
                                                                                Edit
                                                                            </button>
                                                                            <button
                                                                                type="button"
                                                                                className="rm-btn danger"
                                                                                onClick={() =>
                                                                                    handleDeleteMenuItem(item.id)
                                                                                }
                                                                            >
                                                                                Delete
                                                                            </button>
                                                                        </div>
                                                                    </>
                                                                )}
                                                            </div>
                                                        ))}
                                                    </div>
                                                )}

                                                <h4 style={{ marginTop: "0.8rem" }}>Add menu item</h4>
                                                <form className="rm-form" onSubmit={handleAddMenuItem}>
                                                    <label>
                                                        Name
                                                        <input
                                                            value={menuItemForm.name}
                                                            onChange={(e) =>
                                                                setMenuItemForm((p) => ({
                                                                    ...p,
                                                                    name: e.target.value,
                                                                }))
                                                            }
                                                            required
                                                            placeholder="Item name"
                                                        />
                                                    </label>
                                                    <label>
                                                        Description
                                                        <input
                                                            value={menuItemForm.description}
                                                            onChange={(e) =>
                                                                setMenuItemForm((p) => ({
                                                                    ...p,
                                                                    description: e.target.value,
                                                                }))
                                                            }
                                                            placeholder="Optional"
                                                        />
                                                    </label>
                                                    <label>
                                                        Price
                                                        <input
                                                            type="number"
                                                            min="0"
                                                            step="0.01"
                                                            value={menuItemForm.price}
                                                            onChange={(e) =>
                                                                setMenuItemForm((p) => ({
                                                                    ...p,
                                                                    price: e.target.value,
                                                                }))
                                                            }
                                                            required
                                                            placeholder="9.99"
                                                        />
                                                    </label>
                                                    <button
                                                        type="submit"
                                                        className="rm-btn primary"
                                                        disabled={menuBusy}
                                                    >
                                                        {menuBusy ? "Adding…" : "Add item"}
                                                    </button>
                                                </form>
                                            </div>
                                        )}
                                    </>
                                )}
                            </article>
                        ))}
                    </div>
                )}
            </section>
        </main>
    );
}
