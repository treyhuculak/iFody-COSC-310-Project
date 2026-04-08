const API_URL = import.meta.env.VITE_API_URL || "/api";

async function request(path, { signal, headers, ...options } = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    signal,
    headers,
    ...options,
  });

  const payload = await response.json().catch(() => null);

  if (!response.ok) {
    const error = new Error(payload?.detail || payload?.message || `Request failed (${response.status})`);
    error.status = response.status;
    error.payload = payload;
    throw error;
  }

  return payload;
}

function authHeaders() {
  const token = localStorage.getItem("auth_token") || localStorage.getItem("token");
  const headers = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  return headers;
}

// fetchOfferSuggestions implemented below with optional per-user cache

function _userKey(userId) {
  return `weekly_offers_user_${userId}`;
}

export async function fetchOfferSuggestions({ signal, userId = null, forceRefresh = false } = {}) {
  // If user-scoped cache exists and not forcing, return it
  if (userId && !forceRefresh) {
    try {
      const cached = localStorage.getItem(_userKey(userId));
      if (cached) {
        return JSON.parse(cached);
      }
    } catch {
      // ignore parse errors
    }
  }

  const offers = await request(`/offers/suggestions`, { signal, headers: authHeaders() });

  if (userId) {
    try {
      localStorage.setItem(_userKey(userId), JSON.stringify(offers));
    } catch {
      // ignore storage errors
    }
  }

  return offers;
}

export async function activateOffer(offerId) {
  return request(`/offers/activate/${encodeURIComponent(String(offerId))}`, {
    method: "POST",
    headers: authHeaders(),
  });
}

export async function deactivateOffer(offerId) {
  return request(`/offers/deactivate/${encodeURIComponent(String(offerId))}`, {
    method: "POST",
    headers: authHeaders(),
  });
}

export async function fetchActiveOffer({ signal } = {}) {
  return request(`/offers/active`, { signal, headers: authHeaders() });
}
