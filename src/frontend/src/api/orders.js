const API_URL = import.meta.env.VITE_API_URL || "/api";
const ACTIVE_ORDER_STORAGE_KEY = "active_order_ids_by_restaurant";

function toQueryString(params) {
    const query = new URLSearchParams();

    Object.entries(params).forEach(([key, value]) => {
        if (value === undefined || value === null || value === "") {
            return;
        }

        query.set(key, String(value));
    });

    return query.toString();
}

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
        error.payload = payload;
        throw error;
    }

    return payload;
}

function readActiveOrderMap() {
    try {
        const raw = localStorage.getItem(ACTIVE_ORDER_STORAGE_KEY);
        if (!raw) {
            return {};
        }

        const parsed = JSON.parse(raw);
        return parsed && typeof parsed === "object" ? parsed : {};
    } catch {
        return {};
    }
}

function writeActiveOrderMap(orderMap) {
    try {
        localStorage.setItem(ACTIVE_ORDER_STORAGE_KEY, JSON.stringify(orderMap));
    } catch {
        // Intentionally ignore storage write failures.
    }
}

function buildOrderMapKey(userId, restaurantId) {
    return `${userId}:${restaurantId}`;
}

function clearStoredActiveOrderId(userId, restaurantId) {
    const key = buildOrderMapKey(userId, restaurantId);
    const orderMap = readActiveOrderMap();
    if (!(key in orderMap)) {
        return;
    }

    delete orderMap[key];
    writeActiveOrderMap(orderMap);
}

function getStoredActiveOrderId(userId, restaurantId) {
    const key = buildOrderMapKey(userId, restaurantId);
    const orderMap = readActiveOrderMap();
    const orderId = Number(orderMap[key]);

    if (!Number.isInteger(orderId) || orderId <= 0) {
        return null;
    }

    return orderId;
}

function setStoredActiveOrderId(userId, restaurantId, orderId) {
    const key = buildOrderMapKey(userId, restaurantId);
    const orderMap = readActiveOrderMap();
    orderMap[key] = Number(orderId);
    writeActiveOrderMap(orderMap);
}

function buildUserHeaders(userId) {
    return {
        "x-user-id": String(userId),
        "Content-Type": "application/json",
    };
}

function isModifiableOrderStatus(status) {
    return status !== "out for delivery" && status !== "delivered";
}

async function fetchOrderById(orderId, userId, { signal } = {}) {
    return request(`/orders/${orderId}`, {
        signal,
        headers: buildUserHeaders(userId),
    });
}

async function createOrder({ restaurantId, userId, location = "BC", signal } = {}) {
    return request(`/orders/`, {
        signal,
        method: "POST",
        headers: buildUserHeaders(userId),
        body: JSON.stringify({
            customer_id: userId,
            restaurant_id: Number(restaurantId),
            location,
            order_items: [],
        }),
    });
}

async function addItemToOrder({ orderId, userId, menuItem, quantity, signal } = {}) {
    const query = toQueryString({ quantity });
    return request(`/orders/${orderId}/items?${query}`, {
        signal,
        method: "POST",
        headers: buildUserHeaders(userId),
        body: JSON.stringify({
            id: menuItem.id,
            name: menuItem.name,
            description: menuItem.description || "",
            price: Number(menuItem.price),
        }),
    });
}

async function resolveActiveOrderId({ restaurantId, userId, signal } = {}) {
    const storedOrderId = getStoredActiveOrderId(userId, restaurantId);

    if (storedOrderId) {
        try {
            const existingOrder = await fetchOrderById(storedOrderId, userId, { signal });
            if (
                existingOrder?.customer_id === userId &&
                existingOrder?.restaurant_id === Number(restaurantId) &&
                isModifiableOrderStatus(existingOrder?.status)
            ) {
                return storedOrderId;
            }
        } catch (error) {
            if (error.name === "AbortError") {
                throw error;
            }
        }

        clearStoredActiveOrderId(userId, restaurantId);
    }

    const newOrder = await createOrder({ restaurantId, userId, signal });
    setStoredActiveOrderId(userId, restaurantId, newOrder.id);
    return newOrder.id;
}

export async function addMenuItemToCart({
    restaurantId,
    userId,
    menuItem,
    quantity,
    signal,
} = {}) {
    const parsedQuantity = Number(quantity);
    if (!Number.isInteger(parsedQuantity) || parsedQuantity <= 0) {
        throw new Error("Quantity must be a positive whole number.");
    }

    let orderId = await resolveActiveOrderId({ restaurantId, userId, signal });

    try {
        const item = await addItemToOrder({
            orderId,
            userId,
            menuItem,
            quantity: parsedQuantity,
            signal,
        });

        return { orderId, item };
    } catch (error) {
        if (error.name === "AbortError") {
            throw error;
        }

        if (error.status === 404) {
            clearStoredActiveOrderId(userId, restaurantId);
            orderId = await resolveActiveOrderId({ restaurantId, userId, signal });

            const item = await addItemToOrder({
                orderId,
                userId,
                menuItem,
                quantity: parsedQuantity,
                signal,
            });

            return { orderId, item };
        }

        throw error;
    }
}
