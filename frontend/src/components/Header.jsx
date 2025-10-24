import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { getMe, logout } from "../api";

export default function Header() {
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      getMe(token)
        .then(setUser)
        .catch(() => {
          setUser(null);
          localStorage.removeItem("token");
        });
    }
  }, []);

  const handleLogout = async () => {
    const token = localStorage.getItem("token");
    if (token) await logout(token);
    localStorage.removeItem("token");
    setUser(null);
    navigate("/");
  };

  return (
    <header style={{ display: "flex", justifyContent: "space-between", padding: "1rem" }}>
      <Link to="/">Home</Link>
      <div>
        {user ? (
          <>
            <span style={{ marginRight: 8 }}>Hi, {user.username}</span>
            <button onClick={handleLogout}>Logout</button>
          </>
        ) : (
          <Link to="/login">
            <button>Login</button>
          </Link>
        )}
      </div>
    </header>
  );
}
