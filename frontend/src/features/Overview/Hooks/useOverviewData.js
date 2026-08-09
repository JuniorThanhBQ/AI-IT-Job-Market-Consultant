import { useState, useEffect, useCallback } from "react";
import { useAuth } from "@/context/AuthProvider";
import { profileApi, cvApi, consultantApi } from "@/configs/apis";
import { useRouter } from "@/i18n/routing";

export function useOverviewData() {
  const { user, authLoading } = useAuth();
  const router = useRouter();

  const [activeTab, setActiveTab] = useState("dashboard");
  const [profile, setProfile] = useState(null);
  const [cv, setCv] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadingMarketData, setLoadingMarketData] = useState(false);
  const [loadingCVAnalysis, setLoadingCVAnalysis] = useState(false);
  const [error, setError] = useState("");
  const [cvAnalysisData, setCvAnalysisData] = useState(null);
  const [marketAgentData, setMarketAgentData] = useState(null);

  useEffect(() => {
    if (!authLoading && !user) {
      router.replace("/counselee/login");
    }
  }, [user, authLoading, router]);

  const fetchProfileAndCv = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const profileData = await profileApi.getProfile();
      setProfile(profileData);
      const cvData = await cvApi.getCV();
      setCv(cvData);
    } catch (err) {
      setError("Could not fetch profile or CV data.");
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

  const fetchCVAnalysis = async () => {
    setLoadingCVAnalysis(true);
    try {
      const cvAnalysis = await consultantApi.processAgentIntent(
        "PERSONAL_STANDARD_EVALUATION",
        "CV_SCORE",
      );
      setCvAnalysisData(cvAnalysis);
      if (
        cvAnalysis?.tool_outputs?.personalization_analysis?.score !== undefined
      ) {
        setCv((prev) => ({
          ...prev,
          score: cvAnalysis.tool_outputs.personalization_analysis.score,
        }));
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingCVAnalysis(false);
    }
  };

  useEffect(() => {
    if (user) {
      const timer = setTimeout(() => {
        fetchProfileAndCv();
      }, 0);
      return () => clearTimeout(timer);
    }
  }, [user, fetchProfileAndCv]);

  return {
    user,
    authLoading,
    activeTab,
    setActiveTab,
    profile,
    cv,
    loading,
    loadingMarketData,
    loadingCVAnalysis,
    error,
    cvAnalysisData,
    marketAgentData,
    fetchProfileAndCv,
    fetchMarketAnalysis,
    fetchCVAnalysis,
  };
}
