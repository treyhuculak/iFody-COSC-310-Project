const API_URL = import.meta.env.VITE_API_URL || "/api";

function buildUserHeaders(userId) {
    return {
        "x-user-id": String(userId),
        "Content-Type": "application/json",
    };
}

export async function getMyRestaurants(ownerId, userId) {
    const res = await fetch(`${API_URL}/restaurants/owner/${ownerId}`, {
        headers: buildUserHeaders(userId),
    });
    const payload = await res.json().catch(() => null);
    if (!res.ok) throw new Error(payload?.detail || "Failed to fetch your restaurants");
    return Array.isArray(payload) ? payload : [];
}

export async function addRestaurant(data, userId) {
    const res = await fetch(`${API_URL}/restaurants`, {
        method: "POST",
        headers: buildUserHeaders(userId),
        body: JSON.stringify(data),
    });
    const payload = await res.json().catch(() => null);
    if (!res.ok) throw new Error(payload?.detail || "Failed to add restaurant");
    return payload;
}

export async function updateRestaurant(restaurantId, data, userId) {
    const query = new URLSearchParams(
        Object.fromEntries(Object.entries(data).filter(([, v]) => v !== undefined && v !== ""))
    ).toString();
    const res = await fetch(`${API_URL}/restaurants/${restaurantId}?${query}`, {
        method: "PUT",
        headers: buildUserHeaders(userId),
    });
    const payload = await res.json().catch(() => null);
    if (!res.ok) throw new Error(payload?.detail || "Failed to update restaurant");
    return payload;
}

export async function deleteRestaurant(restaurantId, userId) {
    const res = await fetch(`${API_URL}/restaurants/${restaurantId}`, {
        method: "DELETE",
        headers: buildUserHeaders(userId),
    });
    const payload = await res.json().catch(() => null);
    if (!res.ok) throw new Error(payload?.detail || "Failed to delete restaurant");
    return payload;
}

export async function addMenuItem(restaurantId, data, userId) {
    const res = await fetch(`${API_URL}/restaurants/${restaurantId}/menu`, {
        method: "POST",
        headers: buildUserHeaders(userId),
        body: JSON.stringify(data),
    });
    const payload = await res.json().catch(() => null);
    if (!res.ok) throw new Error(payload?.detail || "Failed to add menu item");
    return payload;
}

export async function updateMenuItem(restaurantId, menuItemId, data, userId) {
    const res = await fetch(`${API_URL}/restaurants/${restaurantId}/menu/${menuItemId}`, {
        method: "PUT",
        headers: buildUserHeaders(userId),
        body: JSON.stringify(data),
    });
    const payload = await res.json().catch(() => null);
    if (!res.ok) throw new Error(payload?.detail || "Failed to update menu item");
    return payload;
}

export async function deleteMenuItem(restaurantId, menuItemId, userId) {
    const res = await fetch(`${API_URL}/restaurants/${restaurantId}/menu/${menuItemId}`, {
        method: "DELETE",
        headers: buildUserHeaders(userId),
    });
    const payload = await res.json().catch(() => null);
    if (!res.ok) throw new Error(payload?.detail || "Failed to delete menu item");
    return payload;
}
