"use client";

import { use, useState, useEffect, useCallback } from "react";
import { Loader2, ChevronLeft } from "lucide-react";
import { useAuth } from "@/context/AuthProvider";
import { jobApi } from "./Hooks/useJobExplorer";
import JobDetailPane from "./Components/JobDetailPane";
import { useTranslations } from "next-intl";
import { useRouter } from "@/i18n/routing";

export default function JobDetailPage({ params }) {
  const { id } = use(params);
  const router = useRouter();
  const t = useTranslations("Counselee.Job");
  const { user, authLoading } = useAuth();
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!authLoading && !user) {
      router.replace("/counselee/auth");
    }
  }, [user, authLoading, router]);

  const fetchJobDetails = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const data = await jobApi.getJobDetails(id);
      setJob(data);
    } catch (err) {
      console.error("Failed to fetch job details:", err);
      setError(
        "Could not load job posting. It may have been removed or is currently unavailable.",
      );
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    if (user && id) {
      const timer = setTimeout(() => {
        fetchJobDetails();
      }, 0);
      return () => clearTimeout(timer);
    }
  }, [user, id, fetchJobDetails]);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 relative overflow-x-clip font-sans pb-16">
      <main className="w-full max-w-full px-4 sm:px-6 md:px-12 pt-24 pb-12 relative z-10 flex flex-col gap-6">
        <button
          onClick={() => router.back()}
          className="self-start flex items-center gap-2 text-sm font-bold text-slate-550 dark:text-slate-400 hover:text-[#285872] dark:hover:text-[#407c9c] transition-colors cursor-pointer group"
        >
          <ChevronLeft className="w-4 h-4 transition-transform group-hover:-translate-x-1" />
          {t("back_to_jobs")}
        </button>

        {loading ? (
          <div className="w-full py-32 flex items-center justify-center">
            <Loader2 className="w-10 h-10 animate-spin text-[#285872] dark:text-[#407c9c]" />
          </div>
        ) : error ? (
          <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-12 text-center backdrop-blur-md">
            <p className="text-red-600 dark:text-red-400 font-bold mb-4">
              {error}
            </p>
            <button
              onClick={fetchJobDetails}
              className="bg-[#285872] hover:bg-[#1c3f52] text-white rounded-full px-6 py-2.5 font-bold text-sm transition-colors cursor-pointer"
            >
              Try Again
            </button>
          </div>
        ) : (
          <JobDetailPane
            selectedJobId={id}
            selectedJobDetail={job}
            selectedJobLoading={loading}
            fullPage={true}
          />
        )}
      </main>
    </div>
  );
}
