export const BASE_URL =
  process.env.NEXT_PUBLIC_BASE_URL || "http://localhost:8081/api/v2";

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
      "ngrok-skip-browser-warning": "true",
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
    let data;
    const response = await fetch(`${BASE_URL}${endpoint}`, config);
    const contentType = response.headers.get("content-type");
    if (contentType && contentType.includes("application/json")) {
      data = await response.json();
    } else {
      data = await response.text();
    }

    if (!response.ok) {
      let msg = "An error occurred";
      if (typeof data?.detail === "string") {
        msg = data.detail;
      } else if (Array.isArray(data?.detail)) {
        msg = data.detail.map((e) => e?.msg || String(e)).join(", ");
      } else if (data?.message) {
        msg = data.message;
      }
      const error = new Error(msg);
      error.status = response.status;
      error.data = data;
      throw error;
    }

    return data;
  } catch (error) {
    if (
      typeof window !== "undefined" &&
      (error.message === "Failed to fetch" || error.name === "TypeError")
    ) {
      const currentPath = window.location.pathname;
      const pathParts = currentPath.split("/");
      const locale = pathParts[1] || "en";
      if (!currentPath.includes("/unavailable")) {
        window.location.replace(
          `${window.location.origin}/${locale}/unavailable`,
        );
      }
    }
    throw error;
  }
}

export const APIS = {
  register: (payload) =>
    fetchClient("/accounts/", {
      method: "POST",
      body: payload,
    }),
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
  resetPassword: (payload) =>
    fetchClient("/accounts/password/", {
      method: "PATCH",
      body: payload,
    }),
  verifyEmailGet: (token) =>
    fetchClient(`/accounts/verification/?token=${encodeURIComponent(token)}`),
  verifyEmail: (payload) =>
    fetchClient("/accounts/verification/", {
      method: "POST",
      body: payload,
    }),
  sendVerificationEmail: (payload) =>
    fetchClient("/accounts/verification/email/", {
      method: "POST",
      body: payload,
    }),

  getMyProfile: () => fetchClient("/users/profile/"),
  updateMyProfile: (payload) =>
    fetchClient("/users/profile/", {
      method: "PATCH",
      body: payload,
    }),
  getMyCv: () => fetchClient("/users/profile/cv/"),
  updateMyCv: (payload) =>
    fetchClient("/users/profile/cv/", {
      method: "PATCH",
      body: payload,
    }),
  getMyCvProjects: () => fetchClient("/users/profile/cv/projects/"),
  createCvProject: (payload) =>
    fetchClient("/users/profile/cv/projects/", {
      method: "POST",
      body: payload,
    }),
  updateCvProject: (projectId, payload) =>
    fetchClient(`/users/profile/cv/projects/${projectId}/`, {
      method: "PATCH",
      body: payload,
    }),
  deleteCvProject: (projectId) =>
    fetchClient(`/users/profile/cv/projects/${projectId}/`, {
      method: "DELETE",
    }),

  getAgentHistory: (params = {}) => {
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
    return fetchClient(
      queryString
        ? `/consultants/agent-history/?${queryString}`
        : "/consultants/agent-history/",
    );
  },
  clearAgentHistory: () =>
    fetchClient("/consultants/agent-history/", {
      method: "DELETE",
    }),
  executeAgent: (payload) =>
    fetchClient("/consultants/agent/", {
      method: "POST",
      body: payload,
    }),

  getCompanies: (params = {}) => {
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
    return fetchClient(
      queryString ? `/companies/?${queryString}` : "/companies/",
    );
  },
  createCompany: (payload) =>
    fetchClient("/companies/", {
      method: "POST",
      body: payload,
    }),
  getCompanyDetails: (id) => fetchClient(`/companies/${id}/`),
  updateCompany: (id, payload) =>
    fetchClient(`/companies/${id}/`, {
      method: "PATCH",
      body: payload,
    }),
  deleteCompany: (id) =>
    fetchClient(`/companies/${id}/`, {
      method: "DELETE",
    }),

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
    return fetchClient(queryString ? `/jobs/?${queryString}` : "/jobs/");
  },
  createJob: (payload) =>
    fetchClient("/jobs/", {
      method: "POST",
      body: payload,
    }),
  getJobDetails: (id) => fetchClient(`/jobs/${id}/`),
  updateJob: (id, payload) =>
    fetchClient(`/jobs/${id}/`, {
      method: "PATCH",
      body: payload,
    }),
  deleteJob: (id) =>
    fetchClient(`/jobs/${id}/`, {
      method: "DELETE",
    }),
  hybridSearchJobs: (payload) =>
    fetchClient("/jobs/hybrid/", {
      method: "POST",
      body: payload,
    }),
};

export const authApi = {
  login: (email, password) => APIS.login(email, password),
  register: (email, username, password, confirmPassword) =>
    APIS.register({
      email,
      username,
      password,
      confirm_password: confirmPassword || password,
    }),
  resetPassword: (payload) => APIS.resetPassword(payload),
  verifyEmailGet: (token) => APIS.verifyEmailGet(token),
  verifyEmail: (payload) => APIS.verifyEmail(payload),
  sendVerificationEmail: (payload) => APIS.sendVerificationEmail(payload),
};

export const userApi = {
  getMe: () => APIS.getMyProfile(),
  updateMe: (data) => APIS.updateMyProfile(data),
};
