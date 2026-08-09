const BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8081/api/v1";

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
    return fetchClient("/auth/login", {
      method: "POST",
      body: params,
      isFormUrlEncoded: true,
    });
  },
  register: (email, username, password) =>
    fetchClient("/auth/register", {
      method: "POST",
      body: { email, username, password },
    }),
  verifyAccount: (token) =>
    fetchClient("/auth/verify", {
      method: "POST",
      body: { token },
    }),
  forgotPassword: (email) =>
    fetchClient("/auth/password/forgot", {
      method: "POST",
      body: { email },
    }),
  resetPassword: (token, newPassword) =>
    fetchClient("/auth/password/reset", {
      method: "POST",
      body: { token, new_password: newPassword },
    }),
  testToken: () => fetchClient("/auth/test-token"),
};

export const userApi = {
  getMe: () => fetchClient("/users/my-profile"),
  updateMe: (data) =>
    fetchClient("/users/my-profile", { method: "PATCH", body: data }),
  updatePassword: (currentPassword, newPassword) =>
    fetchClient("/users/my/password", {
      method: "PATCH",
      body: { current_password: currentPassword, new_password: newPassword },
    }),
  listUsers: (skip = 0, limit = 100) =>
    fetchClient(`/users/?skip=${skip}&limit=${limit}`),
  createUser: (data) => fetchClient("/users/", { method: "POST", body: data }),
  getUser: (userId) => fetchClient(`/users/${userId}`),
  updateUser: (userId, data) =>
    fetchClient(`/users/${userId}`, { method: "PATCH", body: data }),
  deleteUser: (userId) => fetchClient(`/users/${userId}`, { method: "DELETE" }),
};

export const profileApi = {
  getProfile: () => fetchClient("/users/my-profile/"),
  updateProfile: (data) =>
    fetchClient("/users/my-profile/", { method: "PATCH", body: data }),
};

export const cvApi = {
  getCV: () => fetchClient("/users/my-cv/"),
  updateCV: (data) =>
    fetchClient("/users/my-cv/", {
      method: "PUT",
      body: data,
    }),
  uploadCVAttachment: (filename) =>
    fetchClient("/users/my-cv/attachment", {
      method: "POST",
      body: { filename },
    }),
  uploadAttachment: (file) => {
    return fetchClient("/users/my-cv/attachment", {
      method: "POST",
      body: { filename: typeof file === "string" ? file : file.name },
    });
  },
  createProject: (project) =>
    fetchClient("/users/my-cv/projects", { method: "POST", body: project }),
  updateProject: (projectId, project) =>
    fetchClient(`/users/my-cv/projects/${projectId}`, {
      method: "PATCH",
      body: project,
    }),
  deleteProject: (projectId) =>
    fetchClient(`/users/my-cv/projects/${projectId}`, { method: "DELETE" }),
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
};

export const consultantApi = {
  processChatbotIntent: (intent, userInput) =>
    fetchClient("/consultants/chatbot/process-intent", {
      method: "POST",
      body: { intent, user_input: userInput },
    }),
  processAgentIntent: (intent, actionType) =>
    fetchClient("/consultants/agents/process-intent", {
      method: "POST",
      body: { intent, action_type: actionType },
    }),
  getHistory: () => fetchClient("/consultants/history"),
  clearHistory: () => fetchClient("/consultants/history", { method: "DELETE" }),
};

export const companyApi = {
  getCompanyDetails: (id) => fetchClient(`/companies/${id}`),
};
