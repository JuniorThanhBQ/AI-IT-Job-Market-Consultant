const BASE_URL = "/api/v1";

async function fetchClient(
  endpoint,
  {
    method = "GET",
    body,
    headers = {},
    isFormUrlEncoded = false,
    ...customConfig
  } = {},
) {
  const token =
    typeof window !== "undefined" ? localStorage.getItem("token") : null;

  const config = {
    method,
    headers: {
      ...headers,
    },
    ...customConfig,
  };

  if (token) {
    config.headers["Authorization"] = `Bearer ${token}`;
  }

  if (body) {
    if (isFormUrlEncoded) {
      config.headers["Content-Type"] = "application/x-www-form-urlencoded";
      config.body = body.toString();
    } else if (body instanceof FormData) {
      config.body = body;
    } else {
      config.headers["Content-Type"] = "application/json";
      config.body = JSON.stringify(body);
    }
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
  login: (email, password) => {
    const params = new URLSearchParams();
    params.append("username", email);
    params.append("password", password);
    return fetchClient("/accounts/sessions/", {
      method: "POST",
      body: params,
      isFormUrlEncoded: true,
    });
  },
  register: (email, username, password) =>
    fetchClient("/accounts", {
      method: "POST",
      body: { email, username, password },
    }),
};

export const userApi = {
  getMe: () => fetchClient("/users/my-profile/"),
  updateMe: (data) =>
    fetchClient("/users/my-profile/", { method: "PATCH", body: data }),
};

export const profileApi = {
  getProfile: () => fetchClient("/users/my-profile/"),
  updateProfile: (data) =>
    fetchClient("/users/my-profile/", { method: "PATCH", body: data }),
};

export const jobApi = {
  getJobs: (params = {}) => {
    const cleanedParams = {};
    Object.keys(params).forEach((key) => {
      if (
        params[key] !== undefined &&
        params[key] !== null &&
        params[key] !== ""
      ) {
        cleanedParams[key] = params[key];
      }
    });
    const queryString = new URLSearchParams(cleanedParams).toString();
    return fetchClient(`/jobs?${queryString}`);
  },
  getJobDetails: (id) => fetchClient(`/jobs/${id}`),
  semanticSearch: (payload) =>
    fetchClient("/jobs/search/semantic", { method: "POST", body: payload }),
};

export const consultantApi = {
  processChatbotIntent: (intent, userInput) =>
    fetchClient("/consultants/chatbot/process-intent", {
      method: "POST",
      body: { intent, user_input: userInput },
    }),
  getHistory: () => fetchClient("/consultants/history"),
  clearHistory: () => fetchClient("/consultants/history", { method: "DELETE" }),
};

export const companyApi = {
  getCompanyDetails: (id) => fetchClient(`/companies/${id}`),
};
