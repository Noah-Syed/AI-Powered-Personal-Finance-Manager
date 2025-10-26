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
        backgroundColor: "#282c34",
        color: "white",
        padding: "1rem 2rem",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        boxShadow: "0 2px 4px rgba(0,0,0,0.2)",
      }}
    >
      {/* Left side - app title */}
      <h2 style={{ margin: 0, fontSize: "1.5rem", letterSpacing: "0.5px" }}>
        Smart Finance Tracker
      </h2>

      {/* Right side - user or login */}
      <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
        {user ? (
          <p style={{ margin: 0 }}>Welcome, {user.username} 👋</p>
        ) : (
          <button
            onClick={handleLoginClick}
            style={{
              backgroundColor: "#61dafb",
              color: "#282c34",
              border: "none",
              borderRadius: "4px",
              padding: "8px 16px",
              fontWeight: "bold",
              cursor: "pointer",
              transition: "background-color 0.2s ease-in-out",
            }}
            onMouseOver={(e) => (e.target.style.backgroundColor = "#4fc3f7")}
            onMouseOut={(e) => (e.target.style.backgroundColor = "#61dafb")}
          >
            Login
          </button>
        )}
      </div>
    </header>
  );
}

export default Header;
