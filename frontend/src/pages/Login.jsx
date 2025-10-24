import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login } from "../api";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const data = await login({ username, password });
      localStorage.setItem("token", data.access_token);
      navigate("/dashboard");
    } catch (err) {
      setError("Incorrect username or password");
    }
  };

  return (
    <div style={{ padding: "40px", textAlign: "center" }}>
      <h2>Login</h2>
      <form onSubmit={handleSubmit} style={{ maxWidth: 300, margin: "auto" }}>
        <div>
          <input
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            style={{ width: "100%", margin: "8px 0" }}
          />
        </div>
        <div>
          <input
            placeholder="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{ width: "100%", margin: "8px 0" }}
          />
        </div>
        {error && <div style={{ color: "red" }}>{error}</div>}
        <button type="submit" style={{ marginTop: 12 }}>Login</button>
      </form>
    </div>
  );
}

