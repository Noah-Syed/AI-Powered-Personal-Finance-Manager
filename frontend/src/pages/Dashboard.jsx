import React from "react";
import Header from "../components/Header";

export default function Dashboard() {
  return (
    <div>
      <Header />
      <main style={{ padding: "2rem" }}>
        <h2>Your Dashboard</h2>
        <p>Welcome back!</p>
      </main>
    </div>
  );
}