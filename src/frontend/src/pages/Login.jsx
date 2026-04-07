import { useState } from "react";
import { useLocation } from "react-router-dom";
import { login } from "../api/auth";

export default function Login() {
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  const redirectTarget = (() => {
    const query = new URLSearchParams(location.search);
    const candidate = query.get("redirect") || "/";

    if (!candidate.startsWith("/")) {
      return "/";
    }

    return candidate;
  })();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const data = await login(email, password);
      // Persist minimal session info so the app can show username + use recent endpoints
      if (data?.username) {
        localStorage.setItem("username", String(data.username));
      }

      if (data?.role) {
        localStorage.setItem("userRole", String(data.role));
      }

      // Try common id/token keys returned by backend
      const candidateIdKeys = ["id", "user_id", "userId"];
      for (const k of candidateIdKeys) {
        if (data && data[k] !== undefined && data[k] !== null) {
          localStorage.setItem("userId", String(data[k]));
          break;
        }
      }

      if (data?.access_token) {
        localStorage.setItem("auth_token", String(data.access_token));
      } else if (data?.token) {
        localStorage.setItem("auth_token", String(data.token));
      }

      // Use full reload so app-shell auth state rehydrates from localStorage.
      window.location.href = redirectTarget;
    } catch (err) {
      setMessage(err.message);
    }
  };

  return (
    <div style={styles.container}>
      <h2>Login</h2>
      <form onSubmit={handleLogin} style={styles.form}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          style={styles.input}
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          style={styles.input}
        />

        <button type="submit" style={styles.button}>Login</button>
      </form>

      {message && <p>{message}</p>}
    </div>
  );
}

const styles = {
  container: { maxWidth: 400, margin: "auto", padding: 20 },
  form: { display: "flex", flexDirection: "column", gap: 10 },
  input: { padding: 10, fontSize: 16 },
  button: { padding: 10, fontSize: 16, cursor: "pointer" }
};