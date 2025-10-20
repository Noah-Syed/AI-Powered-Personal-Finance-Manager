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
