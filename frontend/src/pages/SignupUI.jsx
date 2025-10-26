import React, { useState } from "react";

export default function Signup() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    setError("");

    // simple frontend validation
    if (!username || !email || !password) {
      setError("All fields are required");
      return;
    }

    // backend call will be added later
    console.log("Signing up:", { username, email, password });
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
        <div>
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{ width: "100%", margin: "8px 0", padding: "8px" }}
          />
        </div>
        {error && <div style={{ color: "red", marginTop: 4 }}>{error}</div>}
        <button
          type="submit"
          style={{
            marginTop: 12,
            padding: "8px 16px",
            backgroundColor: "#4CAF50",
            color: "white",
            border: "none",
            borderRadius: 4,
            cursor: "pointer",
          }}
        >
          Sign Up
        </button>
      </form>
    </div>
  );
}