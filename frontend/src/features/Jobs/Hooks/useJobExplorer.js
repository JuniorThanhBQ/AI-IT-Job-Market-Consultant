import { useState, useEffect, useCallback } from "react";
import { useAuth } from "@/context/AuthProvider";
import { jobApi } from "@/configs/apis";
import { useRouter } from "@/i18n/routing";
import { hasXSS, hasSQLInjection } from "@/utils/field_validator";

export function useJobExplorer() {
  const { user, logout, loading: authLoading } = useAuth();
  const router = useRouter();
  const [jobs, setJobs] = useState([]);
  const [jobsLoading, setJobsLoading] = useState(false);
  const [selectedJobId, setSelectedJobId] = useState(null);
  const [selectedJobDetail, setSelectedJobDetail] = useState(null);
  const [selectedJobLoading, setSelectedJobLoading] = useState(false);
  const [searchTitle, setSearchTitle] = useState("");
  const [searchSeniority, setSearchSeniority] = useState("");
  const [searchWorkingModel, setSearchWorkingModel] = useState("");
  const [page, setPage] = useState(1);
  const [error, setError] = useState("");
  const pageSize = 10;

  useEffect(() => {
    if (!authLoading && !user) {
      router.replace("/counselee/auth");
    }
  }, [user, authLoading, router]);

  const fetchJobs = useCallback(
    async (resetPage = false) => {
      if (
        searchTitle &&
        (hasXSS(searchTitle) || hasSQLInjection(searchTitle))
      ) {
        setError("Search input contains unsafe patterns.");
        setJobs([]);
        setSelectedJobId(null);
        setSelectedJobDetail(null);
        setJobsLoading(false);
        return;
      }
      setError("");
      setJobsLoading(true);
      let currentPage = page;
      if (resetPage) {
        setPage(1);
        currentPage = 1;
      }
      try {
        const params = {
          skip: (currentPage - 1) * pageSize,
          limit: pageSize,
        };
        if (searchTitle) params.title = searchTitle;
        if (searchSeniority) params.seniority = searchSeniority;
        if (searchWorkingModel) params.working_model = searchWorkingModel;

        const data = await jobApi.getJobs(params);
        setJobs(data || []);
        if (resetPage && data && data.length > 0) {
          setSelectedJobId(data[0].id);
        } else if (data && data.length > 0 && !selectedJobId) {
          setSelectedJobId(data[0].id);
        } else if (!data || data.length === 0) {
          setSelectedJobId(null);
          setSelectedJobDetail(null);
        }
      } catch (err) {
        console.error("Failed to load jobs", err);
      } finally {
        setJobsLoading(false);
      }
    },
    [page, searchTitle, searchSeniority, searchWorkingModel, selectedJobId],
  );

  useEffect(() => {
    if (user) {
      const timer = setTimeout(() => {
        fetchJobs();
      }, 0);
      return () => clearTimeout(timer);
    }
  }, [user, page, fetchJobs]);

  useEffect(() => {
    if (!selectedJobId) return;
    const fetchDetail = async () => {
      setSelectedJobLoading(true);
      try {
        const detail = await jobApi.getJobDetails(selectedJobId);
        setSelectedJobDetail(detail);
      } catch (err) {
        console.error("Failed to get job detail", err);
      } finally {
        setSelectedJobLoading(false);
      }
    };
    fetchDetail();
  }, [selectedJobId]);

  const handleSearch = (e) => {
    if (e) e.preventDefault();
    fetchJobs(true);
  };

  return {
    user,
    logout,
    authLoading,
    jobs,
    jobsLoading,
    selectedJobId,
    setSelectedJobId,
    selectedJobDetail,
    selectedJobLoading,
    searchTitle,
    setSearchTitle,
    searchSeniority,
    setSearchSeniority,
    searchWorkingModel,
    setSearchWorkingModel,
    page,
    setPage,
    pageSize,
    handleSearch,
    error,
  };
}
