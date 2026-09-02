const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

async function request(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });
  if (response.status === 204) return null;
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = Array.isArray(data.detail)
      ? data.detail.map((item) => item.msg).join(" ")
      : data.detail;
    throw new Error(detail || "The request could not be completed.");
  }
  return data;
}

export const api = {
  register: (payload) => request("/auth/register", { method: "POST", body: JSON.stringify(payload) }),
  login: (payload) => request("/auth/login", { method: "POST", body: JSON.stringify(payload) }),
  logout: (refreshToken) =>
    request("/auth/logout", { method: "POST", body: JSON.stringify({ refresh_token: refreshToken }) }),
  profile: (accessToken) =>
    request("/patients/me", { headers: { Authorization: `Bearer ${accessToken}` } }),
  updateProfile: (accessToken, payload) =>
    request("/patients/me", {
      method: "PATCH",
      headers: { Authorization: `Bearer ${accessToken}` },
      body: JSON.stringify(payload),
    }),
  facilities: (query = "") => request(`/facilities${query}`),
  providers: (query = "") => request(`/providers${query}`),
};
