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
    const rawDetail = data?.detail;
    const detail = typeof rawDetail === "string"
      ? rawDetail
      : rawDetail
        ? JSON.stringify(rawDetail)
        : `Backend request failed with HTTP ${response.status} ${response.statusText}.`;
    const requestId = response.headers.get("X-Request-ID");
    throw new Error(requestId ? `${detail} (request ID: ${requestId})` : detail);
  }

  return data;
}
