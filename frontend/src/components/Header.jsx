import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getCurrentUser } from "../api";

function Header() {
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      getCurrentUser(token)
        .then((data) => setUser(data))
        .catch(() => setUser(null));
    }
  }, []);

  const handleLoginClick = () => {
    navigate("/login");
  };

  return (
    <header
      style={{
        background: "#282c34",
        color: "white",
        padding: "1rem 2rem",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
      }}
    >
      {/* Left side: App title */}
      <h2 style={{ margin: 0 }}>Smart Finance Tracker</h2>

      {/* Right side: user status or login button */}
      <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
        {user ? (
          <p style={{ margin: 0 }}>Welcome, {user.username} 👋</p>
        ) : (
          <>
            <p style={{ margin: 0 }}>Not logged in</p>
            <button
              onClick={handleLoginClick}
              style={{
                backgroundColor: "#007bff",
                color: "white",
                border: "none",
                borderRadius: "6px",
                padding: "8px 16px",
                cursor: "pointer",
                fontSize: "1rem",
              }}
            >
              Login
            </button>
          </>
        )}
      </div>
    </header>
  );
}

export default Header;
