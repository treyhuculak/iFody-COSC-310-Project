const API_URL = import.meta.env.VITE_API_URL || "/api";

const POPULAR_RESTAURANTS_ENDPOINT =
    import.meta.env.VITE_POPULAR_RESTAURANTS_ENDPOINT ||
    "/restaurants/recommendations/popular";

const RECENT_RESTAURANTS_ENDPOINT =
    import.meta.env.VITE_RECENT_RESTAURANTS_ENDPOINT ||
    "/restaurants/recommendations/recent";

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

function normalizeRestaurant(raw = {}) {
    return {
        id: raw.id,
        name: raw.name || "Unknown restaurant",
        cuisine: raw.cuisine || "Cuisine not listed",
        location: raw.location || "Location unavailable",
        delivery_fee: Number(raw.delivery_fee ?? 0),
        is_available: Boolean(raw.is_available),
        owner_id: raw.owner_id,
        menu_items: Array.isArray(raw.menu_items) ? raw.menu_items : [],
    };
}

function normalizeRestaurantCollection(payload) {
    if (Array.isArray(payload)) {
        return payload.map(normalizeRestaurant);
    }

    if (Array.isArray(payload?.items)) {
        return payload.items.map(normalizeRestaurant);
    }

    return [];
}

function normalizePaginatedResponse(payload) {
    const items = normalizeRestaurantCollection(payload);
    const pageSize = Number(payload?.page_size ?? items.length ?? 0);
    const total = Number(payload?.total ?? items.length ?? 0);

    return {
        items,
        total,
        page: Number(payload?.page ?? 1),
        page_size: pageSize,
        total_pages:
            Number(payload?.total_pages) ||
            (pageSize > 0 ? Math.ceil(total / pageSize) : 0),
        has_next: Boolean(payload?.has_next),
        has_prev: Boolean(payload?.has_prev),
    };
}

function isNotReadyEndpoint(error) {
    return [404, 405, 501].includes(error?.status);
}

export async function fetchRestaurants({
    location = "",
    cuisine = "",
    maxFee = "",
    skip = 0,
    limit = 24,
    signal,
} = {}) {
    const hasFilters = Boolean(location || cuisine || maxFee !== "");

    if (hasFilters) {
        const query = toQueryString({
            location,
            cuisine,
            max_fee: maxFee,
            skip,
            limit,
        });

        const payload = await request(`/restaurants/filter?${query}`, { signal });
        return normalizePaginatedResponse(payload);
    }

    const query = toQueryString({ skip, limit });
    const payload = await request(`/restaurants?${query}`, { signal });
    return normalizePaginatedResponse(payload);
}

export async function searchRestaurantsByName(name, { limit = 8, signal } = {}) {
    if (!name.trim()) {
        return [];
    }

    const query = toQueryString({ name, limit, skip: 0 });
    const payload = await request(`/restaurants/search?${query}`, { signal });
    return normalizeRestaurantCollection(payload);
}

export async function fetchPopularRestaurants({
    location = "",
    limit = 6,
    signal,
} = {}) {
    const query = toQueryString({ location, limit });
    const path = query
        ? `${POPULAR_RESTAURANTS_ENDPOINT}?${query}`
        : POPULAR_RESTAURANTS_ENDPOINT;

    try {
        const payload = await request(path, { signal });
        return {
            items: normalizeRestaurantCollection(payload),
            endpointReady: true,
        };
    } catch (error) {
        if (isNotReadyEndpoint(error)) {
            return { items: [], endpointReady: false };
        }

        throw error;
    }
}

export async function fetchRecentlyOrderedRestaurants({
    userId,
    location = "",
    limit = 6,
    signal,
} = {}) {
    const query = toQueryString({ location, limit });
    const path = query
        ? `${RECENT_RESTAURANTS_ENDPOINT}?${query}`
        : RECENT_RESTAURANTS_ENDPOINT;

    const headers = {};
    if (userId !== undefined && userId !== null && userId !== "") {
        headers["x-user-id"] = String(userId);
    }

    try {
        const payload = await request(path, { signal, headers });
        return {
            items: normalizeRestaurantCollection(payload),
            endpointReady: true,
        };
    } catch (error) {
        if (isNotReadyEndpoint(error)) {
            return { items: [], endpointReady: false };
        }

        throw error;
    }
}

export function parseUserIdFromStorage() {
    const candidateKeys = [
        "userId",
        "currentUserId",
        "x-user-id",
        "auth_user_id",
    ];

    for (const key of candidateKeys) {
        const value = localStorage.getItem(key);
        if (!value) {
            continue;
        }

        const maybeId = Number(value);
        if (!Number.isNaN(maybeId) && maybeId > 0) {
            return maybeId;
        }
    }

    return null;
}

export function matchesRestaurantFilters(restaurant, filters) {
    const normalizedLocation = filters.location.trim().toLowerCase();
    const normalizedCuisine = filters.cuisine.trim().toLowerCase();

    const locationMatch =
        !normalizedLocation ||
        restaurant.location.toLowerCase().includes(normalizedLocation);

    const cuisineMatch =
        !normalizedCuisine || restaurant.cuisine.toLowerCase().includes(normalizedCuisine);

    const maxFee = Number(filters.maxFee);
    const feeMatch =
        Number.isNaN(maxFee) || maxFee <= 0 || restaurant.delivery_fee <= maxFee;

    return locationMatch && cuisineMatch && feeMatch;
}
