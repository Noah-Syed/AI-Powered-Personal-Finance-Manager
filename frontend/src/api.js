// src/api.js

const API_URL = "http://127.0.0.1:8000"; // your FastAPI backend

// Helper to include JWT token
export async function getCurrentUser(token) {
  const response = await fetch(`${API_URL}/me`, {
    headers: {
      "Authorization": `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error("Failed to fetch user");
  }

  return await response.json();
}

export async function login({ username, password }) {
  const res = await fetch(`${API_URL}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) throw new Error("Incorrect username or password");
  return res.json();
}

export async function getMe(token) {
  const res = await fetch(`${API_URL}/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Not authenticated");
  return res.json();
}

export async function logout(token) {
  await fetch(`${API_URL}/logout`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token }),
  });
}
