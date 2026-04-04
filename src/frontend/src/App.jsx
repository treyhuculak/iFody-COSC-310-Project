import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";

export default function App() {
  return (
    <BrowserRouter>
      <nav style={{ display: "flex", gap: 20, padding: 20 }}>
        <Link to="/login">Login</Link>
        <Link to="/register">Register</Link>
      </nav>

      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
      </Routes>
    </BrowserRouter>
  );
}