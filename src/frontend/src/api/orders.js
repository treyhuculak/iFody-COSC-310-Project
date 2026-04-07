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

function emitCartUpdated() {
    if (typeof window !== "undefined") {
        window.dispatchEvent(new CustomEvent("cart:updated"));
    }
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
    if (!Number.isInteger(Number(restaurantId)) || Number(restaurantId) <= 0) {
        return;
    }

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

function parseRestaurantIdFromOrderMapKey(orderMapKey) {
    const [, restaurantIdSegment] = String(orderMapKey).split(":");
    const restaurantId = Number(restaurantIdSegment);

    if (!Number.isInteger(restaurantId) || restaurantId <= 0) {
        return null;
    }

    return restaurantId;
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

async function decrementOrderItemFromOrder({ orderId, userId, itemId, signal } = {}) {
    return request(`/orders/${orderId}/items/${itemId}`, {
        signal,
        method: "DELETE",
        headers: buildUserHeaders(userId),
    });
}

export async function fetchActiveCartOrders({ userId, signal } = {}) {
    if (!userId) {
        return [];
    }

    const orderMap = readActiveOrderMap();
    const keys = Object.keys(orderMap).filter((key) => key.startsWith(`${userId}:`));

    if (keys.length === 0) {
        return [];
    }

    const settledOrders = await Promise.allSettled(
        keys.map(async (key) => {
            const orderId = Number(orderMap[key]);
            if (!Number.isInteger(orderId) || orderId <= 0) {
                clearStoredActiveOrderId(userId, parseRestaurantIdFromOrderMapKey(key));
                return null;
            }

            const order = await fetchOrderById(orderId, userId, { signal });
            if (
                order?.customer_id !== userId ||
                !isModifiableOrderStatus(order?.status) ||
                !Array.isArray(order?.order_items)
            ) {
                clearStoredActiveOrderId(userId, order?.restaurant_id ?? parseRestaurantIdFromOrderMapKey(key));
                return null;
            }

            if (order.order_items.length === 0) {
                clearStoredActiveOrderId(userId, order.restaurant_id);
                return null;
            }

            return order;
        })
    );

    return settledOrders
        .filter((entry) => entry.status === "fulfilled")
        .map((entry) => entry.value)
        .filter(Boolean)
        .sort((a, b) => String(b.timestamp || "").localeCompare(String(a.timestamp || "")));
}

export function countItemsInOrders(orders = []) {
    return orders.reduce((total, order) => {
        const orderQuantity = (order.order_items || []).reduce(
            (sum, item) => sum + Number(item.quantity || 0),
            0
        );
        return total + orderQuantity;
    }, 0);
}

export async function getCartItemCount(userId, { signal } = {}) {
    const orders = await fetchActiveCartOrders({ userId, signal });
    return countItemsInOrders(orders);
}

export async function setCartItemQuantity({
    orderId,
    userId,
    menuItem,
    itemId,
    currentQuantity,
    targetQuantity,
    signal,
} = {}) {
    const normalizedCurrent = Number(currentQuantity);
    const normalizedTarget = Number(targetQuantity);

    if (!Number.isInteger(normalizedCurrent) || normalizedCurrent < 0) {
        throw new Error("Current quantity must be a whole number.");
    }

    if (!Number.isInteger(normalizedTarget) || normalizedTarget < 0) {
        throw new Error("Quantity must be zero or a positive whole number.");
    }

    if (normalizedTarget === normalizedCurrent) {
        return fetchOrderById(orderId, userId, { signal });
    }

    if (normalizedTarget > normalizedCurrent) {
        const increment = normalizedTarget - normalizedCurrent;

        if (!menuItem || !Number.isFinite(Number(menuItem.price))) {
            throw new Error("Menu item details are required to increase quantity.");
        }

        await addItemToOrder({
            orderId,
            userId,
            menuItem,
            quantity: increment,
            signal,
        });
    } else {
        const decrement = normalizedCurrent - normalizedTarget;
        const safeItemId = itemId ?? menuItem?.id;

        if (!Number.isInteger(Number(safeItemId)) || Number(safeItemId) <= 0) {
            throw new Error("A valid item id is required to decrease quantity.");
        }

        for (let i = 0; i < decrement; i += 1) {
            await decrementOrderItemFromOrder({
                orderId,
                userId,
                itemId: Number(safeItemId),
                signal,
            });
        }
    }

    emitCartUpdated();
    return fetchOrderById(orderId, userId, { signal });
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

        emitCartUpdated();
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

            emitCartUpdated();
            return { orderId, item };
        }

        throw error;
    }
}
