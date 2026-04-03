const API_URL = import.meta.env.VITE_API_URL || "/api";

export async function login(email, password) {
  const res = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  });

  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || "Login failed");
  }

  return res.json();
}

export async function register(username, email, password, role) {
  const res = await fetch(`${API_URL}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, email, password, role })
  });

  // Try to parse JSON safely
  const data = await res.json().catch(() => ({}));

  // Handle FastAPI validation errors (422)
  if (!res.ok) {
    if (Array.isArray(data.detail)) {
      const friendly = data.detail
        .map((err) => {
          const msg = err.msg.toLowerCase();

          if (msg.includes("email")) return "Please enter a valid email address.";
          if (msg.includes("regex")) return "Password is not in the correct format.";
          if (msg.includes("field required")) return "All fields are required.";
          return err.msg;
        })
        .join(" ");

      throw new Error(friendly);
    }

    // Handle backend exceptions (AccountExistsException, etc.)
    throw new Error(data.detail || "Registration failed.");
  }

  return data;
}