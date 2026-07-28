const BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

async function fetchClient(
  endpoint,
  { method = "GET", body, headers = {}, ...customConfig } = {},
) {
  const config = {
    method,
    headers: {
      "Content-Type": "application/json",
      ...headers,
    },
    credentials: "include",
    ...customConfig,
  };

  if (body) {
    config.body = JSON.stringify(body);
  }

  try {
    const response = await fetch(`${BASE_URL}${endpoint}`, config);

    let data;
    const contentType = response.headers.get("content-type");
    if (contentType && contentType.includes("application/json")) {
      data = await response.json();
    } else {
      data = await response.text();
    }

    if (!response.ok) {
      const error = new Error(data?.detail || "An error occurred");
      error.status = response.status;
      error.data = data;
      throw error;
    }

    return data;
  } catch (error) {
    throw error;
  }
}

export const authApi = {
  login: (credentials) =>
    fetchClient("/auth/login", { method: "POST", body: credentials }),
  logout: () => fetchClient("/auth/logout", { method: "POST" }),
};

export const userApi = {
  getMe: () => fetchClient("/users/me"),
  updateProfile: (data) =>
    fetchClient("/users/profile", { method: "PUT", body: data }),
};

export const jobApi = {
  getJobs: (params) => {
    const queryString = new URLSearchParams(params).toString();
    return fetchClient(`/jobs?${queryString}`);
  },
  getJobDetails: (id) => fetchClient(`/jobs/${id}`),
};
