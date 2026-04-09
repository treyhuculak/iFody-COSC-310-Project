const API_URL = import.meta.env.VITE_API_URL || "/api";

function buildUserHeaders(userId) {
    return {
        "x-user-id": String(userId),
        "Content-Type": "application/json",
    };
}

export async function getNotifications(userId) {
    const res = await fetch(`${API_URL}/notif/${userId}`, {
        headers: buildUserHeaders(userId),
    });
    if (!res.ok) return [];
    return res.json().catch(() => []);
}

export async function getUnreadCount(userId) {
    const res = await fetch(`${API_URL}/notif/${userId}/unread-count`, {
        headers: buildUserHeaders(userId),
    });
    if (!res.ok) return 0;
    const data = await res.json().catch(() => null);
    return Number(data?.count ?? data ?? 0);
}

export async function markAsRead(notifId, userId) {
    const res = await fetch(`${API_URL}/notif/${notifId}/read`, {
        method: "PUT",
        headers: buildUserHeaders(userId),
    });
    if (!res.ok) throw new Error("Failed to mark notification as read");
    return res.json().catch(() => null);
}

export async function markAllAsRead(userId) {
    const res = await fetch(`${API_URL}/notif/${userId}/read-all`, {
        method: "PUT",
        headers: buildUserHeaders(userId),
    });
    if (!res.ok) throw new Error("Failed to mark all notifications as read");
    return res.json().catch(() => null);
}

export async function deleteNotification(notifId, userId) {
    const res = await fetch(`${API_URL}/notif/${notifId}`, {
        method: "DELETE",
        headers: buildUserHeaders(userId),
    });
    if (!res.ok) throw new Error("Failed to delete notification");
    return res.json().catch(() => null);
}
