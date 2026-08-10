"use client";

import { createContext, useContext, useState, useEffect } from "react";
import { authApi, userApi } from "@/configs/apis";
import { useRouter } from "@/i18n/routing";

const AuthContext = createContext(undefined);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    let isMounted = true;

    const initializeAuth = async () => {
      const token =
        typeof window !== "undefined" ? localStorage.getItem("token") : null;
      if (!token) {
        if (isMounted) {
          setLoading(false);
        }
        return;
      }

      try {
        const userData = await userApi.getMe();
        if (isMounted) {
          setUser(userData);
        }
      } catch (error) {
        if (isMounted) {
          localStorage.removeItem("token");
          setUser(null);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    initializeAuth();

    return () => {
      isMounted = false;
    };
  }, []);

  const login = async (email, password) => {
    try {
      const data = await authApi.login(email, password);
      if (data && data.access_token) {
        localStorage.setItem("token", data.access_token);
        const userData = await userApi.getMe();
        setUser(userData);
        router.push("/counselee/overview");
      }
    } catch (error) {
      throw error;
    }
  };

  const register = async (email, username, password) => {
    try {
      await authApi.register(email, username, password);
      await login(email, password);
    } catch (error) {
      throw error;
    }
  };

  const logout = async () => {
    try {
      localStorage.removeItem("token");
    } catch (error) {
      console.error(error);
    } finally {
      setUser(null);
      router.push("/counselee/login");
    }
  };

  const value = {
    user,
    loading,
    authLoading: loading,
    login,
    register,
    logout,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
