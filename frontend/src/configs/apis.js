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
      // Fetch will automatically set boundary for FormData, don't set Content-Type manually
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
};

export const userApi = {
  getMe: () => fetchClient("/users/me"),
  updateMe: (data) => fetchClient("/users/me", { method: "PATCH", body: data }),
  updatePassword: (currentPassword, newPassword) =>
    fetchClient("/users/me/password", {
      method: "PATCH",
      body: { current_password: currentPassword, new_password: newPassword },
    }),
};

export const profileApi = {
  getProfile: () => fetchClient("/users/me/profile/"),
  updateProfile: (data) =>
    fetchClient("/users/me/profile/", { method: "PATCH", body: data }),
};

export const cvApi = {
  getCV: () => fetchClient("/users/me/cv/"),
  updateCV: (data) =>
    fetchClient("/users/me/cv/", {
      method: "PUT",
      body: data,
    }),
  uploadCVAttachment: (filename) =>
    fetchClient("/users/me/cv/attachment", {
      method: "POST",
      body: { filename },
    }),
  uploadAttachment: (file) => {
    // If backend expects JSON/base64 mock or file upload, we implement accordingly.
    // For now we mock it as a service upload or direct json depending on schemas.py
    // Let's assume it accepts CvAttachmentUpload schema which has fields
    return fetchClient("/users/me/cv/attachment", {
      method: "POST",
      body: { file_name: file.name, content_type: file.type },
    });
  },
  createProject: (project) =>
    fetchClient("/users/me/cv/projects", { method: "POST", body: project }),
  updateProject: (projectId, project) =>
    fetchClient(`/users/me/cv/projects/${projectId}`, {
      method: "PATCH",
      body: project,
    }),
  deleteProject: (projectId) =>
    fetchClient(`/users/me/cv/projects/${projectId}`, { method: "DELETE" }),
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
    fetchClient("/consultant/chatbot/process-intent", {
      method: "POST",
      body: { intent, user_input: userInput },
    }),
  processAgentIntent: (intent, actionType) =>
    fetchClient("/consultant/agents/process-intent", {
      method: "POST",
      body: { intent, action_type: actionType },
    }),
  getHistory: () => fetchClient("/consultant/history"),
  clearHistory: () => fetchClient("/consultant/history", { method: "DELETE" }),
};

export const companyApi = {
  getCompanyDetails: (id) => fetchClient(`/companies/${id}`),
};
