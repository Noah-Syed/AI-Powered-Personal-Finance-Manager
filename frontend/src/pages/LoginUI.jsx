import React, { useState } from "react";

export default function LoginUI() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    setError("");

    if (!email || !password) {
      setError("Both fields are required");
      return;
    }

    console.log("Logging in:", { email, password });
  };

  return (
    <div style={{ padding: "40px", textAlign: "center" }}>
      <h2>Login</h2>
      <form onSubmit={handleSubmit} style={{ maxWidth: 320, margin: "auto" }}>
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
    </div>
  );
}