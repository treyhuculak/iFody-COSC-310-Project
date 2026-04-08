const API_URL = import.meta.env.VITE_API_URL || "/api";

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

function buildUserHeaders(userId) {
  return {
    "x-user-id": String(userId),
    "Content-Type": "application/json",
  };
}

export function normalizePaymentMethod(raw = {}) {
  const method = String(raw.method || "").toLowerCase();

  return {
    id: Number(raw.id),
    user_id: Number(raw.user_id),
    method,
    is_active: Boolean(raw.is_active),
    expiration_month: raw.expiration_month ?? null,
    expiration_year: raw.expiration_year ?? null,
    name_on_card: raw.name_on_card ?? "",
    last4: raw.last4 ?? "",
    card_brand: raw.card_brand ?? null,
  };
}

export function getPaymentTypeSegment(method) {
  switch (String(method || "").toLowerCase()) {
    case "cash":
      return "cash";
    case "paypal":
      return "paypal";
    case "credit_card":
    case "debit_card":
      return "card";
    default:
      return "cash";
  }
}

export function getPaymentLabel(method) {
  switch (String(method || "").toLowerCase()) {
    case "cash":
      return "Cash";
    case "paypal":
      return "PayPal";
    case "credit_card":
      return "Credit Card";
    case "debit_card":
      return "Debit Card";
    default:
      return method || "Unknown";
  }
}

export async function fetchPaymentMethodsByUser(userId, { signal } = {}) {
  const payload = await request(`/payment/${userId}`, {
    signal,
    headers: buildUserHeaders(userId),
  });

  if (!Array.isArray(payload)) {
    return [];
  }

  return payload.map(normalizePaymentMethod);
}

export async function fetchActivePaymentMethod(userId, { signal } = {}) {
  const payload = await request(`/payment/active/${userId}`, {
    signal,
    headers: buildUserHeaders(userId),
  });
  return normalizePaymentMethod(payload);
}

export async function fetchPaymentDetails(paymentId, method, { signal } = {}) {
  const typeSegment = getPaymentTypeSegment(method);
  const payload = await request(`/payment/${typeSegment}/${paymentId}`, { signal });
  return normalizePaymentMethod(payload);
}

export async function createCashPayment({ userId, active = false, signal } = {}) {
  const query = toQueryString({ active });

  const payload = await request(`/payment/cash?${query}`, {
    signal,
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_id: Number(userId),
      method: "cash",
    }),
  });

  return normalizePaymentMethod(payload);
}

export async function createPaypalPayment({ userId, active = false, signal } = {}) {
  const query = toQueryString({ active });

  const payload = await request(`/payment/paypal?${query}`, {
    signal,
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_id: Number(userId),
      method: "paypal",
    }),
  });

  return normalizePaymentMethod(payload);
}

export async function createCardPayment({
  userId,
  active = false,
  method,
  card_digits,
  expiration_month,
  expiration_year,
  CVV,
  name_on_card,
  signal,
} = {}) {
  const query = toQueryString({ active });

  const payload = await request(`/payment/card?${query}`, {
    signal,
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_id: Number(userId),
      method,
      card_digits,
      expiration_month: Number(expiration_month),
      expiration_year: Number(expiration_year),
      CVV,
      name_on_card,
    }),
  });

  return normalizePaymentMethod(payload);
}

export async function setActivePaymentMethod(userId, paymentId, { signal } = {}) {
  return request(`/payment/active/${userId}/${paymentId}`, {
    signal,
    method: "PUT",
    headers: buildUserHeaders(userId),
  });
}

export async function deletePaymentMethod(paymentId, method, userId, { signal } = {}) {
  const typeSegment = getPaymentTypeSegment(method);
  const payload = await request(`/payment/${typeSegment}/${paymentId}`, {
    signal,
    method: "DELETE",
    headers: userId ? buildUserHeaders(userId) : { "Content-Type": "application/json" },
  });

  return normalizePaymentMethod(payload);
}

export async function updatePaymentMethod(paymentId, payload) {
    const response = await fetch(`${API_URL}/payment/${paymentId}`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
    });

    let data = null;
    try {
        data = await response.json();
    } catch {
        data = null;
    }

    if (!response.ok) {
        throw new Error(data?.detail || "Failed to update payment method.");
    }

    return data;
}