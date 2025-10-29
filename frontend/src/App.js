import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import LoginUI from "./pages/LoginUI";
import SignupUI from "./pages/SignupUI";
import "./App.css";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<LoginUI />} />
        <Route path="/signup" element={<SignupUI />}/>
      </Routes>
    </Router>
  );
}

export default App;
