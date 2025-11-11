import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { login } from "../api";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!username || !password) {
      setError("Both fields are required");
      return;
    }

    try {
      const data = await login({ username, password });
      localStorage.setItem("token", data.access_token);
      navigate("/");
    } catch (err) {
      console.error("Login failed:", err);
      setError("Incorrect username or password");
    }
  };

  return (
    <div style={{ padding: "40px", textAlign: "center" }}>
      <h2>Login</h2>
      <form onSubmit={handleSubmit} style={{ maxWidth: 320, margin: "auto" }}>
        <div>
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            style={{
              width: "100%",
              margin: "8px 0",
              padding: "8px",
              border: "1px solid #ccc",
              borderRadius: "4px",
            }}
          />
        </div>

        <div style={{ position: "relative" }}>
          <input
            type={showPassword ? "text" : "password"}
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{
              width: "100%",
              margin: "8px 0",
              padding: "8px",
              border: "1px solid #ccc",
              borderRadius: "4px",
            }}
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            style={{
              position: "absolute",
              right: 8,
              top: 8,
              background: "none",
              border: "none",
              cursor: "pointer",
              color: "#2196F3",
            }}
          >
            {showPassword ? "Hide" : "Show"}
          </button>
        </div>

        {error && <div style={{ color: "red", marginTop: 4 }}>{error}</div>}

        <button
          type="submit"
          style={{
            marginTop: 12,
            padding: "8px 16px",
            backgroundColor: "#2196F3",
            color: "white",
            border: "none",
            borderRadius: 4,
            cursor: "pointer",
          }}
        >
          Log In
        </button>
      </form>

      <p style={{ marginTop: 16 }}>
        Don’t have an account?{" "}
        <Link to="/signup" style={{ color: "#2196F3", textDecoration: "none" }}>
          Sign up
        </Link>
      </p>
    </div>
  );
}
