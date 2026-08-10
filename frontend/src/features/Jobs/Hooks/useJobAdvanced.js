"use client";

import { useState } from "react";
import { jobApi } from "@/configs/apis";

export function useJobAdvanced() {
  const [query, setQuery] = useState("");
  const [filters, setFilters] = useState({
    seniority: "",
    working_model: "",
    min_salary: "",
    limit: 15,
  });
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [error, setError] = useState("");
  const [selectedJobId, setSelectedJobId] = useState(null);
  const [selectedJobDetail, setSelectedJobDetail] = useState(null);

  const handleSearch = async (overrideQuery) => {
    const q = overrideQuery ?? query;
    if (!q.trim()) return;
    setLoading(true);
    setHasSearched(true);
    setError("");
    setSelectedJobId(null);
    setSelectedJobDetail(null);
    try {
      const payload = {
        query: q,
        limit: filters.limit,
        ...(filters.seniority && { seniority: filters.seniority }),
        ...(filters.working_model && { working_model: filters.working_model }),
        ...(filters.min_salary && { min_salary: Number(filters.min_salary) }),
      };
      const data = await jobApi.semanticSearch(payload);
      setResults(data);
    } catch (err) {
      setError("Search failed. Please try again.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectJob = (job) => {
    setSelectedJobId(job.id);
    setSelectedJobDetail(job);
  };

  return {
    query,
    setQuery,
    filters,
    setFilters,
    results,
    loading,
    hasSearched,
    error,
    selectedJobId,
    selectedJobDetail,
    handleSearch,
    handleSelectJob,
  };
}
