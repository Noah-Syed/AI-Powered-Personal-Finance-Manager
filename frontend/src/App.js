import React from "react";
import Header from "./components/Header";
import "./App.css";

function App() {
  return (
    <div className="App">
      <Header /> {/* ✅ Shows the username bar */}
      <main style={{ padding: "20px" }}>
        <h2>Welcome to Smart Finance Tracker</h2>
        <p>This is your dashboard area.</p>
      </main>
    </div>
  );
}

export default App;
