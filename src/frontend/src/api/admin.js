const API_URL = import.meta.env.VITE_API_URL || "/api";

function buildUserHeaders(userId) {
    return {
        "x-user-id": String(userId),
        "Content-Type": "application/json",
    };
}

export async function blockUser(username, userId) {
    const res = await fetch(`${API_URL}/auth/blocked/${encodeURIComponent(username)}`, {
        method: "POST",
        headers: buildUserHeaders(userId),
    });
    const payload = await res.json().catch(() => null);
    if (!res.ok) throw new Error(payload?.detail || "Failed to block user");
    return payload;
}

export async function unblockUser(username, userId) {
    const res = await fetch(`${API_URL}/auth/blocked/${encodeURIComponent(username)}`, {
        method: "DELETE",
        headers: buildUserHeaders(userId),
    });
    const payload = await res.json().catch(() => null);
    if (!res.ok) throw new Error(payload?.detail || "Failed to unblock user");
    return payload;
}

export async function deleteUser(username, userId) {
    const res = await fetch(`${API_URL}/auth/register/${encodeURIComponent(username)}`, {
        method: "DELETE",
        headers: buildUserHeaders(userId),
    });
    const payload = await res.json().catch(() => null);
    if (!res.ok) throw new Error(payload?.detail || "Failed to delete user");
    return payload;
}

export async function getAllOrders(userId) {
    const res = await fetch(`${API_URL}/auth/statistics/order`, {
        headers: buildUserHeaders(userId),
    });
    const payload = await res.json().catch(() => null);
    if (!res.ok) throw new Error(payload?.detail || "Failed to fetch orders");
    return payload;
}

export async function getGrossRevenue(restaurantId, userId) {
    const res = await fetch(`${API_URL}/auth/statistics/gross_revenue/${restaurantId}`, {
        headers: buildUserHeaders(userId),
    });
    const payload = await res.json().catch(() => null);
    if (!res.ok) throw new Error(payload?.detail || "Failed to fetch gross revenue");
    return payload;
}

export async function getAverageDeliveryTime(userId) {
    const res = await fetch(`${API_URL}/auth/statistics/average_delivery_time`, {
        headers: buildUserHeaders(userId),
    });
    const payload = await res.json().catch(() => null);
    if (!res.ok) throw new Error(payload?.detail || "Failed to fetch average delivery time");
    return payload;
}

export async function getMostPopularRestaurant(userId) {
    const res = await fetch(`${API_URL}/auth/statistics/most_popular_restaurant`, {
        headers: buildUserHeaders(userId),
    });
    const payload = await res.json().catch(() => null);
    if (!res.ok) throw new Error(payload?.detail || "Failed to fetch most popular restaurant");
    return payload;
}
