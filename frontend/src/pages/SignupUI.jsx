// src/pages/SignupUI.jsx
import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { signup } from "../api";

export default function SignupUI() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    if (!username || !email || !password) {
      setError("All fields are required");
      return;
    }

    try {
      const data = await signup({ username, email, password });
      console.log("Signup success:", data);
      setSuccess("Account created successfully! Redirecting...");
      setTimeout(() => navigate("/login"), 1500);
    } catch (err) {
      setError(err.message || "Signup failed");
    }
  };

  return (
    <div style={{ padding: "40px", textAlign: "center" }}>
      <h2>Sign Up</h2>
      <form onSubmit={handleSubmit} style={{ maxWidth: 320, margin: "auto" }}>
        <div>
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            style={{ width: "100%", margin: "8px 0", padding: "8px" }}
          />
        </div>
        <div>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            style={{ width: "100%", margin: "8px 0", padding: "8px" }}
          />
        </div>
        <div style={{ position: "relative" }}>
          <input
            type={showPassword ? "text" : "password"}
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{ width: "100%", margin: "8px 0", padding: "8px" }}
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
            }}
          >
            {showPassword ? "Hide" : "Show"}
          </button>
        </div>

        {error && <div style={{ color: "red", marginTop: 4 }}>{error}</div>}
        {success && <div style={{ color: "green", marginTop: 4 }}>{success}</div>}

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
          Sign Up
        </button>
      </form>

      <p style={{ marginTop: 16 }}>
        Already have an account?{" "}
        <Link to="/login" style={{ color: "#2196F3", textDecoration: "none" }}>
          Log in
        </Link>
      </p>
    </div>
  );
}
