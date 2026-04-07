const API_URL = import.meta.env.VITE_API_URL || "/api";

async function request(path, { signal, headers, ...options } = {}) {
    const response = await fetch(`${API_URL}${path}`, {
        signal,
        headers,
        ...options,
    });

    const payload = await response.json().catch(() => null);

    if (!response.ok) {
        const error = new Error(
            payload?.detail || payload?.message || `Request failed (${response.status})`
        );
        error.status = response.status;
        throw error;
    }

    return payload;
}

export async function fetchOrder(orderId, { signal } = {}) {
    return request(`/orders/${orderId}`, { signal });
}

export async function deleteOrderItem(orderId, itemId, userId) {
    return request(`/orders/${orderId}/items/${itemId}`, {
        method: "DELETE",
        headers: {
            "Content-Type": "application/json",
            "X-User-Id": String(userId),
        },
    });
}

export async function updateOrderItemQuantity(orderId, itemId, menuItem, quantity, userId) {
    // Delete old item then re-add with new quantity
    await deleteOrderItem(orderId, itemId, userId);
    return request(`/orders/${orderId}/items?quantity=${quantity}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-User-Id": String(userId),
        },
        body: JSON.stringify(menuItem),
    });
}