import { useCallback, useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { parseUserIdFromStorage } from "../api/restaurants";
import { fetchTransaction, fetchUserTransactions } from "../api/transactions";
import "../styles/transactions.css";

function formatMoney(value) {
  return `$${Number(value ?? 0).toFixed(2)}`;
}

export default function Transactions() {
  const navigate = useNavigate();
  const location = useLocation();
  const userId = parseUserIdFromStorage();

  const [transactions, setTransactions] = useState([]);
  const [selectedTransaction, setSelectedTransaction] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [successMessage] = useState(location.state?.message || "");
  const [busyAction, setBusyAction] = useState("");

  const redirectToLogin = useCallback(() => {
    const redirectPath = `${location.pathname}${location.search}`;
    const query = new URLSearchParams({ redirect: redirectPath }).toString();
    navigate(`/login?${query}`);
  }, [location.pathname, location.search, navigate]);

  const loadData = useCallback(async () => {
    if (!userId) return;

    setLoading(true);
    setError("");

    try {
      const transactionList = await fetchUserTransactions(userId).catch((err) => {
        if (err?.status === 404) return [];
        throw err;
      });

      const sorted = transactionList.sort((a, b) => Number(b.id) - Number(a.id));
      setTransactions(sorted);
      setSelectedTransaction((prev) => {
        if (!prev?.id) return sorted[0] || null;
        return sorted.find((item) => item.id === prev.id) || sorted[0] || null;
      });
    } catch (err) {
      if (err?.status === 401) {
        redirectToLogin();
        return;
      }
      setError(err.message || "Failed to load transactions.");
      setTransactions([]);
      setSelectedTransaction(null);
    } finally {
      setLoading(false);
    }
  }, [redirectToLogin, userId]);

  useEffect(() => {
    if (!userId) {
      redirectToLogin();
      return;
    }

    loadData();
  }, [loadData, redirectToLogin, userId]);

  useEffect(() => {
    if (!location.state?.message) return;
    window.history.replaceState({}, document.title);
  }, [location.state]);

  const transactionCountLabel = useMemo(() => {
    return `${transactions.length} purchase${transactions.length === 1 ? "" : "s"}`;
  }, [transactions.length]);

  const handleInspectTransaction = async (transactionId) => {
    setError("");
    setBusyAction(`inspect-${transactionId}`);

    try {
      const details = await fetchTransaction(transactionId);
      setSelectedTransaction(details);
    } catch (err) {
      setError(err.message || "Failed to load transaction details.");
    } finally {
      setBusyAction("");
    }
  };

  return (
    <main className="home-page transactions-page">
      <section className="hero-banner">
        <p className="hero-kicker">Transactions</p>
        <h1>View your purchase history.</h1>
        <p className="hero-subtitle">
          This page is read-only and lists the transactions created when you check out your cart.
        </p>
      </section>

      {error ? <p className="status-error">{error}</p> : null}
      {successMessage ? <p className="status-success">{successMessage}</p> : null}

      <section className="transactions-grid transactions-grid-single">
        <article className="transaction-list-card">
          <div className="section-heading">
            <h2>Purchase history</h2>
            <p>{loading ? "Loading..." : transactionCountLabel}</p>
          </div>

          {loading ? (
            <div className="section-placeholder">Loading transactions...</div>
          ) : transactions.length === 0 ? (
            <div className="section-placeholder">No transactions found yet.</div>
          ) : (
            <div className="transaction-list">
              {transactions.map((transaction) => (
                <article key={transaction.id} className="transaction-row-card">
                  <div>
                    <h3>Transaction #{transaction.id}</h3>
                    <p>
                      Order #{transaction.order_id} · {formatMoney(transaction.amount)} · {transaction.is_successful ? "Successful" : "Failed"}
                    </p>
                  </div>
                  <div className="transaction-row-actions">
                    <button
                      type="button"
                      onClick={() => handleInspectTransaction(transaction.id)}
                      disabled={busyAction === `inspect-${transaction.id}`}
                    >
                      {busyAction === `inspect-${transaction.id}` ? "Loading..." : "Inspect"}
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
          <h2>Inspect one transaction</h2>
          <p>Uses <code>GET /transaction/{`{transaction_id}`}</code></p>
        </div>

        {!selectedTransaction ? (
          <div className="section-placeholder">Choose a transaction to inspect.</div>
        ) : (
          <div className="transaction-detail-grid">
            <p><strong>ID:</strong> {selectedTransaction.id}</p>
            <p><strong>Order ID:</strong> {selectedTransaction.order_id}</p>
            <p><strong>Payment method ID:</strong> {selectedTransaction.payment_method_id}</p>
            <p><strong>User ID:</strong> {selectedTransaction.user_id}</p>
            <p><strong>Amount:</strong> {formatMoney(selectedTransaction.amount)}</p>
            <p><strong>Status:</strong> {selectedTransaction.is_successful ? "Successful" : "Failed"}</p>
          </div>
        )}
      </section>
    </main>
  );
}
