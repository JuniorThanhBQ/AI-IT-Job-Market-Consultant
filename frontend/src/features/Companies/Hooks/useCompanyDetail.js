import { useState, useEffect, useCallback } from "react";
import { useAuth } from "@/context/AuthProvider";
import { companyApi } from "@/configs/apis";
import { useRouter } from "@/i18n/routing";

export function useCompanyDetail(id) {
  const router = useRouter();
  const { user, authLoading } = useAuth();
  const [company, setCompany] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [page, setPage] = useState(1);
  const pageSize = 5;

  useEffect(() => {
    if (!authLoading && !user) {
      router.replace("/counselee/login");
    }
  }, [user, authLoading, router]);

  const fetchCompanyDetails = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    setError("");
    try {
      const data = await companyApi.getCompanyDetails(id);
      setCompany(data);
    } catch (err) {
      console.error("Failed to fetch company details:", err);
      setError(
        "Could not load company profile. It may have been removed or is currently unavailable.",
      );
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    if (user && id) {
      const timer = setTimeout(() => {
        fetchCompanyDetails();
      }, 0);
      return () => clearTimeout(timer);
    }
  }, [user, id, fetchCompanyDetails]);

  return {
    company,
    loading,
    error,
    page,
    setPage,
    pageSize,
    fetchCompanyDetails,
  };
}
