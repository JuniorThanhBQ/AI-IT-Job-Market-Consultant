import { useState, useEffect, useCallback } from "react";
import { useAuth } from "@/context/AuthProvider";
import { profileApi } from "@/features/Profile/hooks/useProfile";
import { useRouter } from "@/i18n/routing";

export function useOverviewData() {
  const { user, authLoading } = useAuth();
  const router = useRouter();
  const [activeTab, setActiveTab] = useState("dashboard");
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!authLoading && !user) {
      router.replace("/counselee/auth");
    }
  }, [user, authLoading, router]);

  const fetchProfile = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const profileData = await profileApi.getProfile();
      setProfile(profileData);
    } catch (err) {
      setError("Could not fetch profile data.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (user) {
      const timer = setTimeout(() => {
        fetchProfile();
      }, 0);
      return () => clearTimeout(timer);
    }
  }, [user, fetchProfile]);

  return {
    user,
    authLoading,
    activeTab,
    setActiveTab,
    profile,
    loading,
    error,
    fetchProfile,
  };
}
