import React from "react";
import Header from "../components/Header";

function Home() {
  return (
    <div className="App">
      <Header />
      <main style={{ padding: "20px" }}>
        <h2>Welcome to Smart Finance Tracker</h2>
        <p>This is your dashboard area.</p>
      </main>
    </div>
  );
}

export default Home;
