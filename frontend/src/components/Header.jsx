// src/components/Header.jsx
import React, { useEffect, useState } from "react";
import { getCurrentUser } from "../api";

function Header() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      getCurrentUser(token)
        .then((data) => setUser(data))
        .catch(() => setUser(null));
    }
  }, []);

  return (
    <header style={{ background: "#282c34", color: "white", padding: "1rem" }}>
      <h2>Smart Finance Tracker</h2>
      {user ? <p>Welcome, {user.username} 👋</p> : <p>Not logged in</p>}
    </header>
  );
}

export default Header;
