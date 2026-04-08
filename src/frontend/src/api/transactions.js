const API_URL = import.meta.env.VITE_API_URL || "/api";
const PAYPAL_PENDING_STORAGE_KEY = "pending_paypal_transactions";

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

function normalizeTransaction(raw = {}) {
  return {
    id: Number(raw.id),
    payment_method_id: Number(raw.payment_method_id),
    order_id: Number(raw.order_id),
    amount: Number(raw.amount ?? 0),
    is_successful: Boolean(raw.is_successful),
    user_id: Number(raw.user_id),
    provider_order_id: raw.provider_order_id ?? "",
    provider_status: raw.provider_status ?? "",
    approve_url: raw.approve_url ?? "",
    links: Array.isArray(raw.links) ? raw.links : [],
  };
}

export async function createTransaction({ payment_method_id, order_id, amount, signal } = {}) {
  const payload = await request(`/transaction/`, {
    signal,
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      payment_method_id: Number(payment_method_id),
      order_id: Number(order_id),
      amount: Number(amount),
    }),
  });

  return normalizeTransaction(payload);
}

export async function fetchTransaction(transactionId, { signal } = {}) {
  const payload = await request(`/transaction/${transactionId}`, { signal });
  return normalizeTransaction(payload);
}

export async function fetchUserTransactions(userId, { signal } = {}) {
  const payload = await request(`/transaction/user_transactions/${userId}`, { signal });
  return Array.isArray(payload) ? payload.map(normalizeTransaction) : [];
}

export async function deleteTransaction(transactionId, { signal } = {}) {
  const payload = await request(`/transaction/${transactionId}`, {
    signal,
    method: "DELETE",
  });
  return normalizeTransaction(payload);
}

export async function startPaypalTransaction({ payment_method_id, order_id, amount, signal } = {}) {
  const payload = await request(`/transaction/paypal/start`, {
    signal,
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      payment_method_id: Number(payment_method_id),
      order_id: Number(order_id),
      amount: Number(amount),
    }),
  });

  const normalized = normalizeTransaction(payload);
  rememberPendingPaypalTransaction(normalized);
  return normalized;
}

export async function fetchPaypalTransaction(transactionId, { signal } = {}) {
  const payload = await request(`/transaction/paypal/${transactionId}`, { signal });
  return normalizeTransaction(payload);
}

export async function capturePaypalTransaction(transactionId, { signal } = {}) {
  const payload = await request(`/transaction/paypal/capture/${transactionId}`, {
    signal,
    method: "POST",
  });

  const normalized = normalizeTransaction(payload);
  forgetPendingPaypalTransactionById(normalized.id);
  return normalized;
}

function readPendingPaypalTransactions() {
  try {
    const raw = localStorage.getItem(PAYPAL_PENDING_STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function writePendingPaypalTransactions(entries) {
  try {
    localStorage.setItem(PAYPAL_PENDING_STORAGE_KEY, JSON.stringify(entries));
  } catch {
    // ignore storage failures
  }
}

export function rememberPendingPaypalTransaction(transaction) {
  if (!transaction?.id) return;

  const current = readPendingPaypalTransactions().filter(
    (entry) => Number(entry.id) !== Number(transaction.id)
  );

  current.unshift({
    id: Number(transaction.id),
    order_id: Number(transaction.order_id),
    payment_method_id: Number(transaction.payment_method_id),
    provider_order_id: transaction.provider_order_id || "",
    approve_url: transaction.approve_url || "",
    provider_status: transaction.provider_status || "",
  });

  writePendingPaypalTransactions(current.slice(0, 10));
}

export function getPendingPaypalTransactions() {
  return readPendingPaypalTransactions();
}

export function getPendingPaypalTransactionByProviderOrderId(providerOrderId) {
  return readPendingPaypalTransactions().find(
    (entry) => entry.provider_order_id && entry.provider_order_id === providerOrderId
  ) || null;
}

export function forgetPendingPaypalTransactionById(transactionId) {
  const next = readPendingPaypalTransactions().filter(
    (entry) => Number(entry.id) !== Number(transactionId)
  );
  writePendingPaypalTransactions(next);
}
