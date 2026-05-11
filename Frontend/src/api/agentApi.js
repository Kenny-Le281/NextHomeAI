const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export async function sendAgentMessage(message, sessionId) {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message,
      session_id: sessionId,
    }),
  });

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const detail = data?.detail || "Failed to contact backend.";
    throw new Error(detail);
  }

  return data;
}