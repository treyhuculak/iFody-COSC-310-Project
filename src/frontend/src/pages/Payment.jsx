import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { parseUserIdFromStorage } from "../api/restaurants";
import "../styles/payment.css";

const API_URL = import.meta.env.VITE_API_URL || "/api";

async function fetchPaymentMethods(userId) {
    const res = await fetch(`${API_URL}/payment/${userId}`);
    if (res.status === 404) return [];
    if (!res.ok) throw new Error("Failed to load payment methods.");
    return res.json();
}

async function createCardPayment(userId, cardForm, method) {
    const res = await fetch(`${API_URL}/payment/card?active=true`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            user_id: userId,
            method,
            name_on_card: cardForm.name_on_card,
            card_digits: cardForm.card_digits,
            expiration_month: Number(cardForm.expiration_month),
            expiration_year: Number(cardForm.expiration_year),
            CVV: cardForm.CVV,
        }),
    });
    const payload = await res.json().catch(() => null);
    if (!res.ok) throw new Error(payload?.detail || `Payment failed (${res.status}).`);
    return payload;
}

async function createCashPayment(userId) {
    const res = await fetch(`${API_URL}/payment/cash?active=true`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId, method: "cash" }),
    });
    const payload = await res.json().catch(() => null);
    if (!res.ok) throw new Error(payload?.detail || `Payment failed (${res.status}).`);
    return payload;
}

async function processPayment(orderId, paymentMethodId, amount) {
    const res = await fetch(`${API_URL}/transaction/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ payment_method_id: paymentMethodId, order_id: orderId, amount }),
    });
    const payload = await res.json().catch(() => null);
    if (!res.ok) throw new Error(payload?.detail || "Payment failed.");
    if (!payload.is_successful) throw new Error("Payment was declined. Please check your card details.");
    return payload;
}

function formatMethodLabel(p) {
    if (p.method === "cash") return "Cash";
    const brand = p.card_brand && p.card_brand !== "brand_not_found" ? p.card_brand : "";
    return `${brand} •••• ${p.last4}  (${p.expiration_month}/${p.expiration_year})`.trim();
}

async function deletePaymentMethod(p) {
    const endpoint = p.method === "cash"
        ? `${API_URL}/payment/cash/${p.id}`
        : `${API_URL}/payment/card/${p.id}`;
    const res = await fetch(endpoint, { method: "DELETE" });
    if (!res.ok) {
        const payload = await res.json().catch(() => null);
        throw new Error(payload?.detail || "Failed to delete payment method.");
    }
}

export default function Payment() {
    const navigate = useNavigate();
    const { state } = useLocation();
    const orderIds = state?.orderIds || [];
    const orderTotals = state?.orderTotals || {};
    const userId = parseUserIdFromStorage();

    const [savedMethods, setSavedMethods] = useState([]);
    const [loadingMethods, setLoadingMethods] = useState(true);
    const [selectedMethodId, setSelectedMethodId] = useState(null);
    const [addingNew, setAddingNew] = useState(false);
    const [newMethod, setNewMethod] = useState("credit_card");
    const [cardForm, setCardForm] = useState({
        name_on_card: "",
        card_digits: "",
        expiration_month: "",
        expiration_year: "",
        CVV: "",
    });

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [success, setSuccess] = useState(false);

    useEffect(() => {
        if (!userId) return;
        fetchPaymentMethods(userId)
            .then((methods) => {
                setSavedMethods(methods);
                const active = methods.find((m) => m.is_active);
                if (active) setSelectedMethodId(active.id);
                else if (methods.length === 0) setAddingNew(true);
            })
            .catch(() => setAddingNew(true))
            .finally(() => setLoadingMethods(false));
    }, [userId]);

    const handleCardChange = (e) => {
        setCardForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
    };

    const handleDeleteMethod = async (p) => {
        try {
            await deletePaymentMethod(p);
            const methods = await fetchPaymentMethods(userId);
            setSavedMethods(methods);
            if (selectedMethodId === p.id) {
                const active = methods.find((m) => m.is_active);
                setSelectedMethodId(active ? active.id : methods[0]?.id ?? null);
                if (methods.length === 0) setAddingNew(true);
            }
        } catch (err) {
            setError(err.message || "Failed to remove payment method.");
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");
        setSuccess(false);

        if (addingNew && (newMethod === "credit_card" || newMethod === "debit_card")) {
            const firstDigit = cardForm.card_digits.trim()[0];
            if (firstDigit !== "4" && firstDigit !== "5") {
                setError("Invalid card number. Card must start with 4 (Visa) or 5 (Mastercard).");
                return;
            }
        }

        setLoading(true);

        try {
            let paymentMethodId;
            if (addingNew) {
                if (newMethod === "cash") {
                    const existingCash = savedMethods.find((m) => m.method === "cash");
                    if (existingCash) {
                        paymentMethodId = existingCash.id;
                    } else {
                        const created = await createCashPayment(userId);
                        paymentMethodId = created.id;
                    }
                } else {
                    const created = await createCardPayment(userId, cardForm, newMethod);
                    paymentMethodId = created.id;
                }
            } else {
                paymentMethodId = selectedMethodId;
            }

            await Promise.all(orderIds.map((id) => processPayment(id, paymentMethodId, orderTotals[id] || 1)));

            localStorage.removeItem("active_order_ids_by_restaurant");
            window.dispatchEvent(new CustomEvent("cart:updated"));
            setSuccess(true);
            setTimeout(() => navigate("/orders"), 2000);
        } catch (err) {
            setError(err.message || "Payment failed. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <main className="home-page">
            <section className="hero-banner">
                <p className="hero-kicker">Checkout</p>
                <h1>Choose your payment method.</h1>
            </section>

            <section className="restaurant-section" style={{ maxWidth: 480, margin: "0 auto" }}>
                {error && <p className="status-error">{error}</p>}
                {success && <p className="status-success">Payment successful! Redirecting...</p>}

                {loadingMethods ? (
                    <div className="section-placeholder">Loading payment methods...</div>
                ) : (
                    <form onSubmit={handleSubmit} className="payment-form">
                        {savedMethods.length > 0 && (
                            <fieldset className="payment-options">
                                <legend>Saved payment methods</legend>
                                {savedMethods.map((p) => (
                                    <label
                                        key={p.id}
                                        className={`payment-option ${!addingNew && selectedMethodId === p.id ? "selected" : ""}`}
                                    >
                                        <input
                                            type="radio"
                                            name="savedMethod"
                                            checked={!addingNew && selectedMethodId === p.id}
                                            onChange={() => { setSelectedMethodId(p.id); setAddingNew(false); }}
                                        />
                                        {formatMethodLabel(p)}
                                        {p.is_active && <span className="payment-active-badge">Default</span>}
                                        <button
                                            type="button"
                                            className="payment-remove-button"
                                            onClick={(e) => { e.preventDefault(); handleDeleteMethod(p); }}
                                        >
                                            Remove
                                        </button>
                                    </label>
                                ))}
                                <label className={`payment-option ${addingNew ? "selected" : ""}`}>
                                    <input
                                        type="radio"
                                        name="savedMethod"
                                        checked={addingNew}
                                        onChange={() => setAddingNew(true)}
                                    />
                                    + Add new payment method
                                </label>
                            </fieldset>
                        )}

                        {addingNew && (
                            <>
                                <fieldset className="payment-options">
                                    <legend>Payment method</legend>
                                    <label className={`payment-option ${newMethod === "cash" ? "selected" : ""}`}>
                                        <input type="radio" name="newMethod" value="cash" checked={newMethod === "cash"} onChange={() => setNewMethod("cash")} />
                                        Cash
                                    </label>
                                    <label className={`payment-option ${newMethod === "credit_card" ? "selected" : ""}`}>
                                        <input type="radio" name="newMethod" value="credit_card" checked={newMethod === "credit_card"} onChange={() => setNewMethod("credit_card")} />
                                        Credit Card
                                    </label>
                                    <label className={`payment-option ${newMethod === "debit_card" ? "selected" : ""}`}>
                                        <input type="radio" name="newMethod" value="debit_card" checked={newMethod === "debit_card"} onChange={() => setNewMethod("debit_card")} />
                                        Debit Card
                                    </label>
                                </fieldset>

                                {(newMethod === "credit_card" || newMethod === "debit_card") && (
                                    <div className="card-fields">
                                        <label>
                                            Name on card
                                            <input type="text" name="name_on_card" value={cardForm.name_on_card} onChange={handleCardChange} placeholder="John Doe" required />
                                        </label>
                                        <label>
                                            Card number
                                            <input type="text" name="card_digits" value={cardForm.card_digits} onChange={handleCardChange} placeholder="16 digits, no spaces" maxLength={16} required />
                                        </label>
                                        <div className="card-fields-row">
                                            <label>
                                                Exp. Month
                                                <input type="number" name="expiration_month" value={cardForm.expiration_month} onChange={handleCardChange} placeholder="MM" min="1" max="12" required />
                                            </label>
                                            <label>
                                                Exp. Year
                                                <input type="number" name="expiration_year" value={cardForm.expiration_year} onChange={handleCardChange} placeholder="YYYY" min="2024" required />
                                            </label>
                                            <label>
                                                CVV
                                                <input type="text" name="CVV" value={cardForm.CVV} onChange={handleCardChange} placeholder="123" maxLength={3} required />
                                            </label>
                                        </div>
                                    </div>
                                )}
                            </>
                        )}

                        <button type="submit" className="payment-submit-button" disabled={loading || success}>
                            {loading ? "Processing..." : "Confirm Payment"}
                        </button>
                    </form>
                )}
            </section>
        </main>
    );
}
