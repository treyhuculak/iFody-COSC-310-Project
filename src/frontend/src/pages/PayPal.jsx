import { useCallback, useEffect, useMemo, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { fetchPaymentMethodsByUser, getPaymentLabel } from "../api/payments";
import { parseUserIdFromStorage } from "../api/restaurants";
import {
  capturePaypalTransaction,
  fetchPaypalTransaction,
  getPendingPaypalTransactionByProviderOrderId,
  getPendingPaypalTransactions,
  startPaypalTransaction,
} from "../api/transactions";
import "../styles/paypal.css";

function formatMoney(value) {
  return `$${Number(value ?? 0).toFixed(2)}`;
}

function normalizeOrdersFromState(state) {
  const ids = Array.isArray(state?.orderIds) ? state.orderIds : [];
  const totals = state?.orderTotals && typeof state.orderTotals === "object" ? state.orderTotals : {};

  return ids
    .map((id) => ({
      id: Number(id),
      total: Number(totals[id] ?? totals[String(id)] ?? 0),
    }))
    .filter((order) => Number.isInteger(order.id) && order.id > 0);
}

export default function PayPalPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const userId = parseUserIdFromStorage();

  const checkoutOrders = useMemo(() => normalizeOrdersFromState(location.state), [location.state]);
  const preferredPaymentMethodId = location.state?.preferredPaymentMethodId || "";

  const [paypalPayments, setPaypalPayments] = useState([]);
  const [pendingTransactions, setPendingTransactions] = useState([]);
  const [selectedTransaction, setSelectedTransaction] = useState(null);
  const [loading, setLoading] = useState(true);
  const [busyAction, setBusyAction] = useState("");
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [form, setForm] = useState({
    order_id: checkoutOrders[0]?.id ?? "",
    amount: checkoutOrders[0]?.total ?? "",
    payment_method_id: "",
  });

  const redirectToLogin = useCallback(() => {
    const redirectPath = `${location.pathname}${location.search}`;
    const query = new URLSearchParams({ redirect: redirectPath }).toString();
    navigate(`/login?${query}`);
  }, [location.pathname, location.search, navigate]);

  const loadPageData = useCallback(async () => {
    if (!userId) return;

    setLoading(true);
    setError("");

    try {
      const methods = await fetchPaymentMethodsByUser(userId);
      const paypalOnly = methods.filter((payment) => payment.method === "paypal");
      setPaypalPayments(paypalOnly);
      setPendingTransactions(getPendingPaypalTransactions());
      setForm((prev) => ({
        order_id: prev.order_id || checkoutOrders[0]?.id || "",
        amount: prev.amount || checkoutOrders[0]?.total || "",
        payment_method_id: prev.payment_method_id || preferredPaymentMethodId || paypalOnly[0]?.id || "",
      }));
    } catch (err) {
      if (err?.status === 401) {
        redirectToLogin();
        return;
      }
      setError(err.message || "Failed to load PayPal page.");
    } finally {
      setLoading(false);
    }
  }, [checkoutOrders, preferredPaymentMethodId, redirectToLogin, userId]);

  useEffect(() => {
    if (!userId) {
      redirectToLogin();
      return;
    }

    loadPageData();
  }, [loadPageData, redirectToLogin, userId]);

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const token = params.get("token");
    const status = params.get("paypal_status");

    if (!token) return;

    const match = getPendingPaypalTransactionByProviderOrderId(token);
    if (match) {
      setSelectedTransaction((prev) => prev || match);
      if (status === "approved") {
        setSuccessMessage(
          `PayPal approval completed for transaction #${match.id}. You can capture it below.`
        );
      }
    }
  }, [location.search]);

  const clearMessages = () => {
    setError("");
    setSuccessMessage("");
  };

  const handleFormChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleStartPaypal = async (event) => {
    event.preventDefault();
    clearMessages();
    setBusyAction("start-paypal");

    try {
      const transaction = await startPaypalTransaction({
        order_id: Number(form.order_id),
        amount: Number(form.amount),
        payment_method_id: Number(form.payment_method_id),
      });
      setSelectedTransaction(transaction);
      setPendingTransactions(getPendingPaypalTransactions());
      setSuccessMessage(`PayPal transaction #${transaction.id} started successfully.`);
    } catch (err) {
      setError(err.message || "Failed to start PayPal transaction.");
    } finally {
      setBusyAction("");
    }
  };

  const handleInspectPending = async (transactionId) => {
    clearMessages();
    setBusyAction(`inspect-${transactionId}`);

    try {
      const details = await fetchPaypalTransaction(transactionId);
      setSelectedTransaction(details);
    } catch (err) {
      setError(err.message || "Failed to load PayPal transaction.");
    } finally {
      setBusyAction("");
    }
  };

  const handleCapture = async (transactionId) => {
    clearMessages();
    setBusyAction(`capture-${transactionId}`);

    try {
      const captured = await capturePaypalTransaction(transactionId);
      setSelectedTransaction(captured);
      setPendingTransactions(getPendingPaypalTransactions());
      setSuccessMessage(`PayPal transaction #${captured.id} captured successfully.`);
    } catch (err) {
      setError(err.message || "Failed to capture PayPal transaction.");
    } finally {
      setBusyAction("");
    }
  };

  const selectedTransactionId = Number(selectedTransaction?.id) || null;

  return (
    <main className="home-page paypal-page">
      <section className="hero-banner">
        <p className="hero-kicker">PayPal</p>
        <h1>Start a PayPal transaction and capture it after approval.</h1>
        <p className="hero-subtitle">
          This page starts the PayPal flow, shows the approval URL, and lets you capture the transaction after the approval step.
        </p>
      </section>

      {error ? <p className="status-error">{error}</p> : null}
      {successMessage ? <p className="status-success">{successMessage}</p> : null}

      <section className="transactions-grid paypal-grid">
        <article className="transaction-form-card">
          <div className="section-heading">
            <h2>Start PayPal transaction</h2>
            <p>Uses <code>POST /transaction/paypal/start</code></p>
          </div>

          {loading ? (
            <div className="section-placeholder">Loading PayPal methods...</div>
          ) : paypalPayments.length === 0 ? (
            <div className="section-placeholder">
              <p>You do not have a PayPal payment method yet.</p>
              <Link to="/payment" className="paypal-inline-link">Go to Payments</Link>
            </div>
          ) : (
            <form className="transaction-form" onSubmit={handleStartPaypal}>
              <label>
                Order
                <select name="order_id" value={form.order_id} onChange={handleFormChange} required>
                  <option value="">Select an order</option>
                  {checkoutOrders.map((order) => (
                    <option key={order.id} value={order.id}>
                      Order #{order.id} — {formatMoney(order.total)}
                    </option>
                  ))}
                  {!checkoutOrders.some((order) => String(order.id) === String(form.order_id)) && form.order_id ? (
                    <option value={form.order_id}>Order #{form.order_id}</option>
                  ) : null}
                </select>
              </label>

              <label>
                PayPal payment method
                <select
                  name="payment_method_id"
                  value={form.payment_method_id}
                  onChange={handleFormChange}
                  required
                >
                  <option value="">Select PayPal method</option>
                  {paypalPayments.map((payment) => (
                    <option key={payment.id} value={payment.id}>
                      #{payment.id} — {getPaymentLabel(payment.method)}
                      {payment.is_active ? " (active)" : ""}
                    </option>
                  ))}
                </select>
              </label>

              <label>
                Amount
                <input
                  name="amount"
                  type="number"
                  min="0.01"
                  step="0.01"
                  value={form.amount}
                  onChange={handleFormChange}
                  required
                />
              </label>

              <div className="transaction-form-actions">
                <button type="submit" disabled={busyAction === "start-paypal"}>
                  {busyAction === "start-paypal" ? "Starting..." : "Start PayPal checkout"}
                </button>
              </div>
            </form>
          )}
        </article>

        <article className="transaction-list-card">
          <div className="section-heading">
            <h2>Pending PayPal transactions</h2>
            <p>Saved locally after you start them.</p>
          </div>

          {pendingTransactions.length === 0 ? (
            <div className="section-placeholder">No pending PayPal transactions.</div>
          ) : (
            <div className="transaction-list">
              {pendingTransactions.map((transaction) => (
                <article key={transaction.id} className="transaction-row-card">
                  <div>
                    <h3>Transaction #{transaction.id}</h3>
                    <p>
                      Order #{transaction.order_id} · Provider status: {transaction.provider_status || "CREATED"}
                    </p>
                  </div>
                  <div className="transaction-row-actions">
                    <button
                      type="button"
                      onClick={() => handleInspectPending(transaction.id)}
                      disabled={busyAction === `inspect-${transaction.id}`}
                    >
                      {busyAction === `inspect-${transaction.id}` ? "Loading..." : "Inspect"}
                    </button>
                    <button
                      type="button"
                      onClick={() => handleCapture(transaction.id)}
                      disabled={busyAction === `capture-${transaction.id}`}
                    >
                      {busyAction === `capture-${transaction.id}` ? "Capturing..." : "Capture"}
                    </button>
                  </div>
                </article>
              ))}
            </div>
          )}
        </article>
      </section>

      <section className="restaurant-section transaction-inspect-card">
        <div className="section-heading">
          <h2>Selected PayPal transaction</h2>
          <p>Uses <code>GET /transaction/paypal/{`{transaction_id}`}</code> and <code>POST /transaction/paypal/capture/{`{transaction_id}`}</code></p>
        </div>

        {!selectedTransaction ? (
          <div className="section-placeholder">Start or inspect a PayPal transaction to see its details.</div>
        ) : (
          <div className="paypal-detail-stack">
            <div className="transaction-detail-grid">
              <p><strong>ID:</strong> {selectedTransaction.id}</p>
              <p><strong>Order ID:</strong> {selectedTransaction.order_id}</p>
              <p><strong>Payment method ID:</strong> {selectedTransaction.payment_method_id}</p>
              <p><strong>Amount:</strong> {formatMoney(selectedTransaction.amount)}</p>
              <p><strong>Provider order ID:</strong> {selectedTransaction.provider_order_id || "—"}</p>
              <p><strong>Provider status:</strong> {selectedTransaction.provider_status || "—"}</p>
              <p><strong>Captured:</strong> {selectedTransaction.is_successful ? "Yes" : "No"}</p>
            </div>

            <div className="paypal-approval-card">
              <h3>Approval URL</h3>
              {selectedTransaction.approve_url ? (
                <>
                  <a
                    href={selectedTransaction.approve_url}
                    target="_blank"
                    rel="noreferrer"
                    className="paypal-approve-link"
                  >
                    Open PayPal approval page
                  </a>
                  <p className="paypal-helper-text">
                    After approval, PayPal returns you to Home with a message. Then come back here and capture transaction #{selectedTransactionId}.
                  </p>
                </>
              ) : (
                <p className="section-placeholder">No approval URL available.</p>
              )}

              <div className="transaction-form-actions">
                <button
                  type="button"
                  onClick={() => handleCapture(selectedTransaction.id)}
                  disabled={busyAction === `capture-${selectedTransaction.id}` || selectedTransaction.is_successful}
                >
                  {selectedTransaction.is_successful
                    ? "Already captured"
                    : busyAction === `capture-${selectedTransaction.id}`
                    ? "Capturing..."
                    : "Capture now"}
                </button>
              </div>
            </div>
          </div>
        )}
      </section>
    </main>
  );
}
