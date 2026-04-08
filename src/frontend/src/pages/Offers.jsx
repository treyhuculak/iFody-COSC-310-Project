import { useCallback, useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { parseUserIdFromStorage } from "../api/restaurants";
import { fetchOfferSuggestions, activateOffer, deactivateOffer } from "../api/offers";
import "../styles/offers.css";

function formatDate(iso) {
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso || "N/A";
  }
}

export default function Offers() {
  const location = useLocation();
  const navigate = useNavigate();
  const userId = parseUserIdFromStorage();

  const [state, setState] = useState({ loading: true, error: "", offers: [] });
  const [pending, setPending] = useState(null);

  const redirectToLogin = useCallback(() => {
    const redirectPath = `${location.pathname}${location.search}`;
    const query = new URLSearchParams({ redirect: redirectPath }).toString();
    navigate(`/login?${query}`);
  }, [location.pathname, location.search, navigate]);

  const loadOffers = useCallback(async (signal) => {
    setState((s) => ({ ...s, loading: true, error: "" }));
    try {
      const offers = await fetchOfferSuggestions({ signal });
      setState({ loading: false, error: "", offers: Array.isArray(offers) ? offers : [] });
    } catch (err) {
      if (err?.status === 401) {
        redirectToLogin();
        return;
      }
      setState({ loading: false, error: err.message || "Failed to load offers.", offers: [] });
    }
  }, [redirectToLogin]);

  useEffect(() => {
    if (!userId) {
      redirectToLogin();
      return;
    }

    const ac = new AbortController();
    loadOffers(ac.signal);
    return () => ac.abort();
  }, [loadOffers, redirectToLogin, userId]);

  const handleToggle = async (offer) => {
    setPending(offer.offer_id);
    setState((s) => ({ ...s, error: "" }));

    try {
      if (offer.is_active) {
        await deactivateOffer(offer.offer_id);
      } else {
        await activateOffer(offer.offer_id);
      }

      await loadOffers();
    } catch (err) {
      if (err?.status === 401) {
        redirectToLogin();
        return;
      }

      setState((s) => ({ ...s, error: err.message || "Could not update offer." }));
    } finally {
      setPending(null);
    }
  };

  return (
    <main className="offers-page">
      <section className="hero-banner">
        <p className="hero-kicker">Exclusive Offers</p>
        <h1>Special deals just for you</h1>
        <p className="hero-subtitle">Activate an offer to have it applied automatically at checkout.</p>
      </section>

      {state.error ? <p className="status-error">{state.error}</p> : null}

      <section className="offers-list">
        {state.loading ? (
          <div className="section-placeholder">Loading offers...</div>
        ) : state.offers.length === 0 ? (
          <div className="section-placeholder">No offers available right now.</div>
        ) : (
          state.offers.map((offer) => (
            <article key={offer.offer_id} className="offer-card">
              <header className="offer-card-header">
                <h3 className="offer-title">{offer.title}</h3>
                <small className="offer-dates">Ends: {formatDate(offer.end_date)}</small>
              </header>
              <p className="offer-desc">{offer.description}</p>

              <div className="offer-meta">
                <div className="offer-type">Type: {String(offer.offer_type)}</div>
                <div className="offer-actions">
                  <button
                    className={offer.is_active ? "offer-deactivate-button" : "offer-activate-button"}
                    onClick={() => handleToggle(offer)}
                    disabled={pending && pending !== offer.offer_id}
                  >
                    {offer.is_active ? "Deactivate" : "Activate"}
                  </button>
                </div>
              </div>
            </article>
          ))
        )}
      </section>
    </main>
  );
}
