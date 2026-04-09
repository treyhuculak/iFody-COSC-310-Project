const API_URL = import.meta.env.VITE_API_URL || "/api";

function buildUserHeaders(userId) {
    return {
        "x-user-id": String(userId),
        "Content-Type": "application/json",
    };
}

export async function getReview(orderId) {
    const res = await fetch(`${API_URL}/orders/${orderId}/review`);
    if (res.status === 404) return null;
    if (!res.ok) return null;
    return res.json().catch(() => null);
}

export async function createReview(orderId, { rating, title, comment }, userId) {
    const res = await fetch(`${API_URL}/orders/${orderId}/review`, {
        method: "POST",
        headers: buildUserHeaders(userId),
        body: JSON.stringify({ rating, title, comment: comment || null }),
    });
    const payload = await res.json().catch(() => null);
    if (!res.ok) throw new Error(payload?.detail || "Failed to submit review");
    return payload;
}

export async function updateReview(orderId, { rating, title, comment }, userId) {
    const res = await fetch(`${API_URL}/orders/${orderId}/review`, {
        method: "PUT",
        headers: buildUserHeaders(userId),
        body: JSON.stringify({ rating, title, comment: comment || null }),
    });
    const payload = await res.json().catch(() => null);
    if (!res.ok) throw new Error(payload?.detail || "Failed to update review");
    return payload;
}

export async function deleteReview(orderId, userId) {
    const res = await fetch(`${API_URL}/orders/${orderId}/review`, {
        method: "DELETE",
        headers: buildUserHeaders(userId),
    });
    const payload = await res.json().catch(() => null);
    if (!res.ok) throw new Error(payload?.detail || "Failed to delete review");
    return payload;
}
