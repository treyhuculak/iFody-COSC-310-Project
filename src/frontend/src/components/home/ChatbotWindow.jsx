import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchRestaurants } from "../../api/restaurants";
import "../../styles/chatbot.css";

const API_URL = import.meta.env.VITE_API_URL || "/api";
const BOT_NAME = "AI Munchy";

async function sendMessage(message) {
    const res = await fetch(`${API_URL}/chat/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
    });
    const payload = await res.json().catch(() => null);
    if (!res.ok) throw new Error(payload?.detail || "Chat request failed.");
    return payload.response;
}

function findMentionedMenuItems(text, restaurants) {
    const lower = text.toLowerCase();
    const results = [];

    for (const r of restaurants) {
        for (const item of r.menu_items || []) {
            if (item.name && lower.includes(item.name.toLowerCase())) {
                results.push({
                    itemId: item.id,
                    itemName: item.name,
                    itemPrice: Number(item.price ?? 0),
                    restaurantId: r.id,
                    restaurantName: r.name,
                    deliveryFee: Number(r.delivery_fee ?? 0),
                });
            }
        }
    }

    return results;
}

export default function ChatbotWindow() {
    const navigate = useNavigate();
    const [open, setOpen] = useState(false);
    const [messages, setMessages] = useState([
        {
            role: "assistant",
            text: `Hi! I'm ${BOT_NAME}, your food assistant. Tell me what you're craving and I'll help you find something great.`,
            menuItems: [],
        },
    ]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const [warmedUp, setWarmedUp] = useState(false);
    const [allRestaurants, setAllRestaurants] = useState([]);
    const bottomRef = useRef(null);

    useEffect(() => {
        fetchRestaurants({ limit: 100 })
            .then((res) => setAllRestaurants(res.items))
            .catch(() => {});
    }, []);

    useEffect(() => {
        if (open) {
            bottomRef.current?.scrollIntoView({ behavior: "smooth" });
        }
    }, [messages, open]);

    const handleSend = async (e) => {
        e.preventDefault();
        const text = input.trim();
        if (!text || loading) return;

        setMessages((prev) => [...prev, { role: "user", text, menuItems: [] }]);
        setInput("");
        setLoading(true);

        try {
            const responseText = await sendMessage(text);
            const menuItems = findMentionedMenuItems(responseText, allRestaurants);
            setWarmedUp(true);
            setMessages((prev) => [
                ...prev,
                { role: "assistant", text: responseText, menuItems },
            ]);
        } catch {
            setMessages((prev) => [
                ...prev,
                { role: "assistant", text: "Sorry, I couldn't reach the server. Please try again.", menuItems: [] },
            ]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="chatbot-root">
            {open && (
                <div className="chatbot-window">
                    <div className="chatbot-header">
                        <div className="chatbot-header-left">
                            <span className="chatbot-title">{BOT_NAME}</span>
                            {!warmedUp && (
                                <span className="chatbot-warming-badge">Warming up...</span>
                            )}
                        </div>
                        <button className="chatbot-close" onClick={() => setOpen(false)} aria-label="Close chat">✕</button>
                    </div>

                    {!warmedUp && (
                        <div className="chatbot-warmup-notice">
                            The first response may take a moment while the AI warms up. Hang tight!
                        </div>
                    )}

                    <div className="chatbot-messages">
                        {messages.map((msg, i) => (
                            <div key={i}>
                                <div className={`chatbot-bubble chatbot-bubble--${msg.role}`}>
                                    {msg.text}
                                </div>
                                {msg.menuItems && msg.menuItems.length > 0 && (
                                    <div className="chatbot-menu-cards">
                                        {msg.menuItems.map((item) => (
                                            <button
                                                key={`${item.restaurantId}-${item.itemId}`}
                                                className="chatbot-menu-card"
                                                onClick={() => navigate(`/restaurants/${item.restaurantId}`)}
                                            >
                                                <span className="chatbot-card-item-name">{item.itemName}</span>
                                                <span className="chatbot-card-restaurant">{item.restaurantName}</span>
                                                <div className="chatbot-card-prices">
                                                    <span className="chatbot-card-item-price">${item.itemPrice.toFixed(2)}</span>
                                                    <span className="chatbot-card-delivery">+${item.deliveryFee.toFixed(2)} delivery</span>
                                                </div>
                                            </button>
                                        ))}
                                    </div>
                                )}
                            </div>
                        ))}
                        {loading && (
                            <div className="chatbot-bubble chatbot-bubble--assistant chatbot-bubble--typing">
                                <span /><span /><span />
                            </div>
                        )}
                        <div ref={bottomRef} />
                    </div>

                    <form className="chatbot-input-row" onSubmit={handleSend}>
                        <input
                            className="chatbot-input"
                            type="text"
                            placeholder="What are you craving?"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            disabled={loading}
                            autoFocus
                        />
                        <button className="chatbot-send" type="submit" disabled={loading || !input.trim()}>
                            Send
                        </button>
                    </form>
                </div>
            )}

            <button className="chatbot-fab" onClick={() => setOpen((prev) => !prev)} aria-label="Toggle chat">
                {open ? "✕" : "💬"}
            </button>
        </div>
    );
}
