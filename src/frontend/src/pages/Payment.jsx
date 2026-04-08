import { useCallback, useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import {
  createCardPayment,
  createCashPayment,
  createPaypalPayment,
  deletePaymentMethod,
  fetchActivePaymentMethod,
  fetchPaymentDetails,
  fetchPaymentMethodsByUser,
  getPaymentLabel,
  setActivePaymentMethod,
} from "../api/payments";
import { parseUserIdFromStorage } from "../api/restaurants";
import "../styles/payments.css";

const initialCardForm = {
  method: "credit_card",
  card_digits: "",
  expiration_month: "",
  expiration_year: "",
  CVV: "",
  name_on_card: "",
  active: false,
};

const initialSimpleForm = {
  active: false,
};

export default function Payments() {
  const navigate = useNavigate();
  const location = useLocation();
  const userId = parseUserIdFromStorage();

  const [payments, setPayments] = useState([]);
  const [activePayment, setActivePayment] = useState(null);
  const [selectedPayment, setSelectedPayment] = useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [busyAction, setBusyAction] = useState("");

  const [cardForm, setCardForm] = useState(initialCardForm);
  const [cashForm, setCashForm] = useState(initialSimpleForm);
  const [paypalForm, setPaypalForm] = useState(initialSimpleForm);

  const redirectToLogin = useCallback(() => {
    const redirectPath = `${location.pathname}${location.search}`;
    const query = new URLSearchParams({ redirect: redirectPath }).toString();
    navigate(`/login?${query}`);
  }, [location.pathname, location.search, navigate]);

  const clearMessages = () => {
    setError("");
    setSuccessMessage("");
  };

  const loadPayments = useCallback(async () => {
    if (!userId) {
      return;
    }

    setLoading(true);
    setError("");

    try {
      const methods = await fetchPaymentMethodsByUser(userId);
      setPayments(methods);

      if (methods.length > 0) {
        try {
          const active = await fetchActivePaymentMethod(userId);
          setActivePayment(active);
        } catch {
          setActivePayment(methods.find((item) => item.is_active) || null);
        }
      } else {
        setActivePayment(null);
      }
    } catch (err) {
      if (err?.status === 401) {
        redirectToLogin();
        return;
      }
      setError(err.message || "Failed to load payment methods.");
      setPayments([]);
      setActivePayment(null);
    } finally {
      setLoading(false);
    }
  }, [redirectToLogin, userId]);

  useEffect(() => {
    if (!userId) {
      redirectToLogin();
      return;
    }

    loadPayments();
  }, [loadPayments, redirectToLogin, userId]);

  const sortedPayments = useMemo(() => {
    return [...payments].sort((a, b) => {
      if (a.is_active && !b.is_active) return -1;
      if (!a.is_active && b.is_active) return 1;
      return Number(a.id) - Number(b.id);
    });
  }, [payments]);

  const handleCardInputChange = (event) => {
    const { name, value, type, checked } = event.target;
    setCardForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleCashInputChange = (event) => {
    const { checked } = event.target;
    setCashForm({ active: checked });
  };

  const handlePaypalInputChange = (event) => {
    const { checked } = event.target;
    setPaypalForm({ active: checked });
  };

  const handleCreateCash = async (event) => {
    event.preventDefault();
    if (!userId) return;

    clearMessages();
    setBusyAction("create-cash");

    try {
      await createCashPayment({
        userId,
        active: cashForm.active,
      });

      setCashForm(initialSimpleForm);
      setSelectedPayment(null);
      setSuccessMessage("Cash payment method added.");
      await loadPayments();
    } catch (err) {
      setError(err.message || "Failed to add cash payment method.");
    } finally {
      setBusyAction("");
    }
  };

  const handleCreatePaypal = async (event) => {
    event.preventDefault();
    if (!userId) return;

    clearMessages();
    setBusyAction("create-paypal");

    try {
      await createPaypalPayment({
        userId,
        active: paypalForm.active,
      });

      setPaypalForm(initialSimpleForm);
      setSelectedPayment(null);
      setSuccessMessage("PayPal payment method added.");
      await loadPayments();
    } catch (err) {
      setError(err.message || "Failed to add PayPal payment method.");
    } finally {
      setBusyAction("");
    }
  };

  const handleCreateCard = async (event) => {
    event.preventDefault();
    if (!userId) return;

    clearMessages();
    setBusyAction("create-card");

    try {
      await createCardPayment({
        userId,
        active: cardForm.active,
        method: cardForm.method,
        card_digits: cardForm.card_digits,
        expiration_month: cardForm.expiration_month,
        expiration_year: cardForm.expiration_year,
        CVV: cardForm.CVV,
        name_on_card: cardForm.name_on_card,
      });

      setCardForm(initialCardForm);
      setSelectedPayment(null);
      setSuccessMessage("Card payment method added.");
      await loadPayments();
    } catch (err) {
      setError(err.message || "Failed to add card payment method.");
    } finally {
      setBusyAction("");
    }
  };

  const handleInspectPayment = async (payment) => {
    clearMessages();
    setBusyAction(`inspect-${payment.id}`);

    try {
      const details = await fetchPaymentDetails(payment.id, payment.method);
      setSelectedPayment(details);
    } catch (err) {
      setError(err.message || "Failed to inspect payment method.");
    } finally {
      setBusyAction("");
    }
  };

  const handleActivatePayment = async (payment) => {
    clearMessages();
    setBusyAction(`activate-${payment.id}`);

    try {
      await setActivePaymentMethod(userId, payment.id);
      setSuccessMessage(`Payment method #${payment.id} is now active.`);
      await loadPayments();

      try {
        const details = await fetchPaymentDetails(payment.id, payment.method);
        setSelectedPayment(details);
      } catch {
        setSelectedPayment(null);
      }
    } catch (err) {
      setError(err.message || "Failed to activate payment method.");
    } finally {
      setBusyAction("");
    }
  };

  const handleDeletePayment = async (payment) => {
    clearMessages();
    setBusyAction(`delete-${payment.id}`);

    try {
      await deletePaymentMethod(payment.id, payment.method, userId);

      if (selectedPayment?.id === payment.id) {
        setSelectedPayment(null);
      }

      setSuccessMessage(`Payment method #${payment.id} was deleted.`);
      await loadPayments();
    } catch (err) {
      setError(err.message || "Failed to delete payment method.");
    } finally {
      setBusyAction("");
    }
  };

  return (
    <main className="home-page payments-page">
      <section className="hero-banner">
        <p className="hero-kicker">Payments</p>
        <h1>Manage your saved payment methods.</h1>
        <p className="hero-subtitle">
          Add card, cash, or PayPal methods, inspect them, and choose which one is active.
        </p>
      </section>

      {error ? <p className="status-error">{error}</p> : null}
      {successMessage ? <p className="status-success">{successMessage}</p> : null}

      <section className="payments-grid">
        <article className="payment-form-card">
          <div className="section-heading">
            <h2>Add card</h2>
            <p>Uses <code>POST /payment/card</code></p>
          </div>

          <form className="payment-form" onSubmit={handleCreateCard}>
            <label>
              Card type
              <select
                name="method"
                value={cardForm.method}
                onChange={handleCardInputChange}
              >
                <option value="credit_card">Credit Card</option>
                <option value="debit_card">Debit Card</option>
              </select>
            </label>

            <label>
              Card digits
              <input
                name="card_digits"
                type="text"
                value={cardForm.card_digits}
                onChange={handleCardInputChange}
                placeholder="4111111111111111"
                required
              />
            </label>

            <div className="payment-form-row">
              <label>
                Exp. month
                <input
                  name="expiration_month"
                  type="number"
                  min="1"
                  max="12"
                  value={cardForm.expiration_month}
                  onChange={handleCardInputChange}
                  required
                />
              </label>

              <label>
                Exp. year
                <input
                  name="expiration_year"
                  type="number"
                  min="2024"
                  value={cardForm.expiration_year}
                  onChange={handleCardInputChange}
                  required
                />
              </label>
            </div>

            <label>
              CVV
              <input
                name="CVV"
                type="text"
                value={cardForm.CVV}
                onChange={handleCardInputChange}
                placeholder="123"
                required
              />
            </label>

            <label>
              Name on card
              <input
                name="name_on_card"
                type="text"
                value={cardForm.name_on_card}
                onChange={handleCardInputChange}
                placeholder="John Doe"
                required
              />
            </label>

            <label className="payment-checkbox">
              <input
                name="active"
                type="checkbox"
                checked={cardForm.active}
                onChange={handleCardInputChange}
              />
              Make active immediately
            </label>

            <button type="submit" disabled={busyAction === "create-card"}>
              {busyAction === "create-card" ? "Adding..." : "Add card"}
            </button>
          </form>
        </article>

        <article className="payment-form-card">
          <div className="section-heading">
            <h2>Add cash</h2>
            <p>Uses <code>POST /payment/cash</code></p>
          </div>

          <form className="payment-form" onSubmit={handleCreateCash}>
            <label className="payment-checkbox">
              <input
                type="checkbox"
                checked={cashForm.active}
                onChange={handleCashInputChange}
              />
              Make active immediately
            </label>

            <button type="submit" disabled={busyAction === "create-cash"}>
              {busyAction === "create-cash" ? "Adding..." : "Add cash"}
            </button>
          </form>
        </article>

        <article className="payment-form-card">
          <div className="section-heading">
            <h2>Add PayPal</h2>
            <p>Uses <code>POST /payment/paypal</code></p>
          </div>

          <form className="payment-form" onSubmit={handleCreatePaypal}>
            <label className="payment-checkbox">
              <input
                type="checkbox"
                checked={paypalForm.active}
                onChange={handlePaypalInputChange}
              />
              Make active immediately
            </label>

            <button type="submit" disabled={busyAction === "create-paypal"}>
              {busyAction === "create-paypal" ? "Adding..." : "Add PayPal"}
            </button>
          </form>
        </article>
      </section>

      <section className="restaurant-section">
        <div className="section-heading">
          <h2>Saved payment methods</h2>
          <p>
            Uses <code>GET /payment/{userId}</code> and <code>GET /payment/active/{userId}</code>
          </p>
        </div>

        {loading ? (
          <div className="section-placeholder">Loading payment methods...</div>
        ) : sortedPayments.length === 0 ? (
          <div className="section-placeholder">
            No payment methods found for this user yet.
          </div>
        ) : (
          <div className="payment-method-list">
            {sortedPayments.map((payment) => {
              const isBusy =
                busyAction === `inspect-${payment.id}` ||
                busyAction === `activate-${payment.id}` ||
                busyAction === `delete-${payment.id}`;

              const isSelected = selectedPayment?.id === payment.id;
              const isActive =
                activePayment?.id === payment.id || payment.is_active === true;

              return (
                <article
                  key={payment.id}
                  className={`payment-method-card ${isActive ? "active" : ""} ${
                    isSelected ? "selected" : ""
                  }`}
                >
                  <div className="payment-method-main">
                    <div>
                      <p className="payment-method-title">
                        {getPaymentLabel(payment.method)}
                      </p>
                      <p className="payment-method-meta">
                        ID #{payment.id} • User #{payment.user_id}
                      </p>
                      {payment.last4 ? (
                        <p className="payment-method-meta">
                          {payment.card_brand || "Card"} ending in {payment.last4}
                        </p>
                      ) : null}
                    </div>

                    <span className={`payment-badge ${isActive ? "active" : ""}`}>
                      {isActive ? "Active" : "Inactive"}
                    </span>
                  </div>

                  <div className="payment-method-actions">
                    <button
                      type="button"
                      onClick={() => handleInspectPayment(payment)}
                      disabled={isBusy}
                    >
                      Inspect
                    </button>

                    <button
                      type="button"
                      onClick={() => handleActivatePayment(payment)}
                      disabled={isBusy || isActive}
                    >
                      {isBusy && busyAction === `activate-${payment.id}`
                        ? "Updating..."
                        : "Make active"}
                    </button>

                    <button
                      type="button"
                      className="danger-button"
                      onClick={() => handleDeletePayment(payment)}
                      disabled={isBusy}
                    >
                      {isBusy && busyAction === `delete-${payment.id}`
                        ? "Deleting..."
                        : "Delete"}
                    </button>
                  </div>
                </article>
              );
            })}
          </div>
        )}
      </section>

      <section className="restaurant-section">
        <div className="section-heading">
          <h2>Selected payment details</h2>
          <p>
            Uses type-specific inspect endpoints like <code>GET /payment/card/{"{id}"}</code>
          </p>
        </div>

        {!selectedPayment ? (
          <div className="section-placeholder">
            Select <strong>Inspect</strong> on a payment method to view its details.
          </div>
        ) : (
          <article className="payment-details-card">
            <div className="payment-details-grid">
              <div>
                <span className="details-label">Payment ID</span>
                <p>{selectedPayment.id}</p>
              </div>
              <div>
                <span className="details-label">User ID</span>
                <p>{selectedPayment.user_id}</p>
              </div>
              <div>
                <span className="details-label">Method</span>
                <p>{getPaymentLabel(selectedPayment.method)}</p>
              </div>
              <div>
                <span className="details-label">Active</span>
                <p>{selectedPayment.is_active ? "Yes" : "No"}</p>
              </div>

              {selectedPayment.last4 ? (
                <>
                  <div>
                    <span className="details-label">Last 4</span>
                    <p>{selectedPayment.last4}</p>
                  </div>
                  <div>
                    <span className="details-label">Brand</span>
                    <p>{selectedPayment.card_brand || "Unknown"}</p>
                  </div>
                  <div>
                    <span className="details-label">Name on card</span>
                    <p>{selectedPayment.name_on_card || "-"}</p>
                  </div>
                  <div>
                    <span className="details-label">Expiration</span>
                    <p>
                      {selectedPayment.expiration_month || "-"} /{" "}
                      {selectedPayment.expiration_year || "-"}
                    </p>
                  </div>
                </>
              ) : null}
            </div>
          </article>
        )}
      </section>
    </main>
  );
}