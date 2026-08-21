"use client";

import { useState } from "react";
import { jobApi } from "@/configs/apis";
import { hasXSS, hasSQLInjection } from "@/utils/field_validator";

export function useJobAdvanced() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [error, setError] = useState("");
  const [selectedJobId, setSelectedJobId] = useState(null);
  const [selectedJobDetail, setSelectedJobDetail] = useState(null);

  const handleSearch = async (overrideQuery) => {
    const q = overrideQuery ?? query;
    if (!q.trim()) return;
    if (hasXSS(q) || hasSQLInjection(q)) {
      setError("Search query contains unsafe patterns.");
      setResults([]);
      setHasSearched(true);
      return;
    }
    setLoading(true);
    setHasSearched(true);
    setError("");
    setSelectedJobId(null);
    setSelectedJobDetail(null);
    try {
      const payload = {
        query: q,
        limit: 15,
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
