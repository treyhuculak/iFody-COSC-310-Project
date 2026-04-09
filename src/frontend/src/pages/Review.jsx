import { useCallback, useEffect, useState } from "react";
import { Link, useLocation, useNavigate, useParams } from "react-router-dom";
import { createReview, deleteReview, getReview, updateReview } from "../api/reviews";
import { parseUserIdFromStorage } from "../api/restaurants";
import "../styles/review.css";

const API_URL = import.meta.env.VITE_API_URL || "/api";
const MAX_TITLE = 50;
const MAX_COMMENT = 500;

const STAR_LABELS = ["", "Poor", "Fair", "Good", "Very good", "Excellent"];

function StarSelector({ value, onChange }) {
    const [hovered, setHovered] = useState(0);
    const display = hovered || value;

    return (
        <div>
            <div className="review-stars-row">
                {[1, 2, 3, 4, 5].map((star) => (
                    <button
                        key={star}
                        type="button"
                        className={`review-star-btn ${display >= star ? "filled" : ""}`}
                        onClick={() => onChange(star)}
                        onMouseEnter={() => setHovered(star)}
                        onMouseLeave={() => setHovered(0)}
                        aria-label={`${star} star${star > 1 ? "s" : ""}`}
                    >
                        ★
                    </button>
                ))}
            </div>
            <p className="review-star-label">
                {display ? STAR_LABELS[display] : "Select a rating"}
            </p>
        </div>
    );
}

function StarsDisplay({ rating }) {
    return (
        <span className="review-stars-display">
            {"★".repeat(rating)}{"☆".repeat(5 - rating)}
        </span>
    );
}

function formatTime(ts) {
    if (!ts) return "";
    try { return new Date(ts).toLocaleString(); } catch { return String(ts); }
}

async function fetchOrderInfo(orderId) {
    const res = await fetch(`${API_URL}/orders/${orderId}`);
    if (!res.ok) return null;
    return res.json().catch(() => null);
}

async function fetchRestaurantName(restaurantId) {
    const res = await fetch(`${API_URL}/restaurants/${restaurantId}`);
    if (!res.ok) return null;
    const data = await res.json().catch(() => null);
    return data?.name ?? null;
}

export default function Review() {
    const { orderId } = useParams();
    const location = useLocation();
    const navigate = useNavigate();
    const userId = parseUserIdFromStorage();

    const [order, setOrder] = useState(null);
    const [restaurantName, setRestaurantName] = useState(null);
    const [existingReview, setExistingReview] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [successMessage, setSuccessMessage] = useState("");

    // Form state
    const [isEditing, setIsEditing] = useState(false);
    const [rating, setRating] = useState(0);
    const [title, setTitle] = useState("");
    const [comment, setComment] = useState("");
    const [busy, setBusy] = useState(false);

    const redirectToLogin = useCallback(() => {
        const redirectPath = `${location.pathname}${location.search}`;
        navigate(`/login?${new URLSearchParams({ redirect: redirectPath })}`);
    }, [location.pathname, location.search, navigate]);

    const loadAll = useCallback(async () => {
        if (!userId || !orderId) return;
        try {
            const [orderData, reviewData] = await Promise.all([
                fetchOrderInfo(orderId),
                getReview(orderId),
            ]);

            if (!orderData) {
                setError("Order not found.");
                setLoading(false);
                return;
            }

            // Only delivered orders can be reviewed
            if (orderData.status !== "delivered") {
                setError("Reviews can only be left for delivered orders.");
                setLoading(false);
                return;
            }

            setOrder(orderData);
            setExistingReview(reviewData);

            if (orderData.restaurant_id) {
                fetchRestaurantName(orderData.restaurant_id).then(setRestaurantName);
            }
        } catch (err) {
            setError(err.message || "Failed to load review data.");
        } finally {
            setLoading(false);
        }
    }, [orderId, userId]);

    useEffect(() => {
        if (!userId) {
            redirectToLogin();
            return;
        }
        loadAll();
    }, [loadAll, redirectToLogin, userId]);

    const openCreateForm = () => {
        setRating(0);
        setTitle("");
        setComment("");
        setIsEditing(true);
        setSuccessMessage("");
        setError("");
    };

    const openEditForm = () => {
        if (!existingReview) return;
        setRating(existingReview.rating);
        setTitle(existingReview.title);
        setComment(existingReview.comment || "");
        setIsEditing(true);
        setSuccessMessage("");
        setError("");
    };

    const handleCancel = () => {
        setIsEditing(false);
        setError("");
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (rating === 0) {
            setError("Please select a star rating.");
            return;
        }
        if (!title.trim()) {
            setError("Please enter a title.");
            return;
        }
        if (title.length > MAX_TITLE) {
            setError(`Title must be ${MAX_TITLE} characters or fewer.`);
            return;
        }
        if (comment.length > MAX_COMMENT) {
            setError(`Comment must be ${MAX_COMMENT} characters or fewer.`);
            return;
        }

        setBusy(true);
        setError("");
        try {
            if (existingReview) {
                await updateReview(orderId, { rating, title: title.trim(), comment: comment.trim() }, userId);
                setSuccessMessage("Review updated successfully.");
            } else {
                await createReview(orderId, { rating, title: title.trim(), comment: comment.trim() }, userId);
                setSuccessMessage("Review submitted successfully.");
            }
            setIsEditing(false);
            await loadAll();
        } catch (err) {
            setError(err.message || "Failed to save review.");
        } finally {
            setBusy(false);
        }
    };

    const handleDelete = async () => {
        if (!window.confirm("Delete this review?")) return;
        setBusy(true);
        setError("");
        setSuccessMessage("");
        try {
            await deleteReview(orderId, userId);
            setExistingReview(null);
            setSuccessMessage("Review deleted.");
        } catch (err) {
            setError(err.message || "Failed to delete review.");
        } finally {
            setBusy(false);
        }
    };

    return (
        <main className="home-page">
            <section className="hero-banner">
                <p className="hero-kicker">Reviews</p>
                <h1>{existingReview ? "Your Review" : "Leave a Review"}</h1>
                <p className="hero-subtitle">Share your experience for this order.</p>
            </section>

            <section className="restaurant-section">
                <p style={{ marginBottom: "1.2rem" }}>
                    <Link to="/orders" className="restaurant-back-link">
                        ← Back to Order History
                    </Link>
                </p>

                {error && <p className="status-error">{error}</p>}
                {successMessage && <p className="status-success">{successMessage}</p>}

                {loading ? (
                    <div className="section-placeholder">Loading…</div>
                ) : !order ? null : (
                    <>
                        {/* Order summary */}
                        <div className="review-order-summary">
                            <div>
                                <p className="review-order-label">Order</p>
                                <p className="review-order-title">
                                    #{order.id} — {restaurantName || `Restaurant #${order.restaurant_id}`}
                                </p>
                                <p className="review-order-meta">
                                    {formatTime(order.created_at || order.timestamp)}
                                </p>
                            </div>
                            <span className="order-status-badge status-delivered">delivered</span>
                        </div>

                        {/* Existing review */}
                        {existingReview && !isEditing && (
                            <div className="review-existing-card">
                                <div className="review-existing-header">
                                    <div>
                                        <StarsDisplay rating={existingReview.rating} />
                                        <p className="review-existing-title">{existingReview.title}</p>
                                        <p className="review-existing-meta">
                                            Submitted {formatTime(existingReview.created_at)}
                                            {existingReview.updated_at !== existingReview.created_at &&
                                                ` · Updated ${formatTime(existingReview.updated_at)}`}
                                        </p>
                                    </div>
                                    <div className="review-existing-actions">
                                        <button
                                            type="button"
                                            className="review-action-btn edit"
                                            onClick={openEditForm}
                                            disabled={busy}
                                        >
                                            Edit
                                        </button>
                                        <button
                                            type="button"
                                            className="review-action-btn delete"
                                            onClick={handleDelete}
                                            disabled={busy}
                                        >
                                            Delete
                                        </button>
                                    </div>
                                </div>
                                {existingReview.comment && (
                                    <p className="review-existing-comment">{existingReview.comment}</p>
                                )}
                            </div>
                        )}

                        {/* No review yet — prompt */}
                        {!existingReview && !isEditing && (
                            <div className="section-placeholder" style={{ flexDirection: "column", gap: "0.9rem" }}>
                                <p>You haven't reviewed this order yet.</p>
                                <button
                                    type="button"
                                    className="review-submit-btn"
                                    onClick={openCreateForm}
                                >
                                    Write a review
                                </button>
                            </div>
                        )}

                        {/* Create / edit form */}
                        {isEditing && (
                            <form className="review-form" onSubmit={handleSubmit}>
                                <h2>{existingReview ? "Edit your review" : "Write a review"}</h2>

                                <div className="review-field">
                                    <label>Rating</label>
                                    <StarSelector value={rating} onChange={setRating} />
                                </div>

                                <div className="review-field">
                                    <label htmlFor="review-title">Title</label>
                                    <input
                                        id="review-title"
                                        type="text"
                                        value={title}
                                        onChange={(e) => setTitle(e.target.value)}
                                        placeholder="Summarise your experience"
                                        maxLength={MAX_TITLE + 10}
                                        required
                                    />
                                    <span className={`review-char-count ${title.length > MAX_TITLE ? "over" : ""}`}>
                                        {title.length}/{MAX_TITLE}
                                    </span>
                                </div>

                                <div className="review-field">
                                    <label htmlFor="review-comment">Comment <span style={{ fontWeight: 400, color: "#9a7560" }}>(optional)</span></label>
                                    <textarea
                                        id="review-comment"
                                        value={comment}
                                        onChange={(e) => setComment(e.target.value)}
                                        placeholder="Tell us more about your order…"
                                        maxLength={MAX_COMMENT + 10}
                                    />
                                    <span className={`review-char-count ${comment.length > MAX_COMMENT ? "over" : ""}`}>
                                        {comment.length}/{MAX_COMMENT}
                                    </span>
                                </div>

                                <div className="review-form-actions">
                                    <button type="submit" className="review-submit-btn" disabled={busy}>
                                        {busy ? "Saving…" : existingReview ? "Update review" : "Submit review"}
                                    </button>
                                    <button
                                        type="button"
                                        className="review-cancel-btn"
                                        onClick={handleCancel}
                                        disabled={busy}
                                    >
                                        Cancel
                                    </button>
                                </div>
                            </form>
                        )}
                    </>
                )}
            </section>
        </main>
    );
}
