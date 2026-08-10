import { useState, useEffect, useCallback } from "react";
import { useAuth } from "@/context/AuthProvider";
import { profileApi, consultantApi } from "@/configs/apis";
import { useRouter } from "@/i18n/routing";

export function useOverviewData() {
  const { user, authLoading } = useAuth();
  const router = useRouter();

  const [activeTab, setActiveTab] = useState("dashboard");
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadingMarketData, setLoadingMarketData] = useState(false);
  const [error, setError] = useState("");
  const [marketAgentData, setMarketAgentData] = useState(null);

  useEffect(() => {
    if (!authLoading && !user) {
      router.replace("/counselee/login");
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

  const fetchMarketAnalysis = async () => {
    setLoadingMarketData(true);
    try {
      const marketData = await consultantApi.processAgentIntent(
        "MARKET_ANALYSIS",
        "DEMAND_TREND",
      );
      setMarketAgentData(marketData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingMarketData(false);
    }
  };

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
    loadingMarketData,
    error,
    marketAgentData,
    fetchProfile,
    fetchMarketAnalysis,
  };
}
