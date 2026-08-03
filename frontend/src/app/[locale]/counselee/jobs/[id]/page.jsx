"use client";

import { use, useState, useEffect, useCallback } from "react";
import {
  Building,
  User,
  Briefcase,
  DollarSign,
  Loader2,
  ChevronLeft,
  Calendar,
  Clock,
} from "lucide-react";
import { useAuth } from "@/context/AuthProvider";
import { jobApi } from "@/configs/apis";
import Header from "@/components/shared/Header";
import { useRouter } from "@/i18n/routing";

export default function JobDetailPage({ params }) {
  const { id } = use(params);
  const router = useRouter();
  const { user, authLoading } = useAuth();
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Redirect if not logged in
  useEffect(() => {
    if (!authLoading && !user) {
      router.replace("/counselee/login");
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
      // eslint-disable-next-line react-hooks/set-state-in-effect
      fetchJobDetails();
    }
  }, [user, id, fetchJobDetails]);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-955 relative overflow-hidden font-sans pb-16">
      {/* Organic noise background overlay */}
      <div
        className="absolute inset-0 pointer-events-none opacity-40 dark:opacity-[0.12] mix-blend-overlay z-0"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E")`,
        }}
      />

      {/* Moving blurred gradient background circles */}
      <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-blue-500/10 dark:bg-blue-500/5 rounded-full blur-[120px] pointer-events-none z-0" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-indigo-500/10 dark:bg-indigo-500/5 rounded-full blur-[120px] pointer-events-none z-0" />

      <Header />

      <main className="max-w-4xl mx-auto px-4 sm:px-6 pt-24 pb-12 relative z-10 flex flex-col gap-6">
        {/* Back Link */}
        <button
          onClick={() => router.push("/counselee/overview")}
          className="self-start flex items-center gap-2 text-sm font-bold text-slate-550 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors cursor-pointer group"
        >
          <ChevronLeft className="w-4 h-4 transition-transform group-hover:-translate-x-1" />
          Back to Dashboard
        </button>

        {loading ? (
          <div className="w-full py-32 flex items-center justify-center">
            <Loader2 className="w-10 h-10 animate-spin text-blue-600 dark:text-blue-500" />
          </div>
        ) : error ? (
          <div className="bg-white/80 dark:bg-slate-900/40 border border-red-250 dark:border-red-900 rounded-[2rem] p-12 text-center backdrop-blur-md">
            <p className="text-red-600 dark:text-red-400 font-bold mb-4">
              {error}
            </p>
            <button
              onClick={fetchJobDetails}
              className="bg-blue-600 hover:bg-blue-500 text-white rounded-full px-6 py-2.5 font-bold text-sm transition-colors cursor-pointer"
            >
              Try Again
            </button>
          </div>
        ) : (
          <div className="flex flex-col gap-8">
            {/* Header Box */}
            <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2.5rem] p-8 backdrop-blur-md flex flex-col md:flex-row justify-between items-start md:items-center gap-6 shadow-sm">
              <div className="flex items-center gap-5">
                <div className="w-16 h-16 bg-slate-100 dark:bg-slate-950 border border-slate-200 dark:border-slate-850 rounded-2xl flex items-center justify-center text-slate-400">
                  <Building className="w-8 h-8 text-blue-600 dark:text-blue-500" />
                </div>
                <div>
                  <h1 className="text-2xl md:text-3xl font-extrabold text-slate-900 dark:text-white mb-2">
                    {job.title}
                  </h1>
                  <div className="flex flex-wrap items-center gap-x-3 gap-y-1.5">
                    <span className="text-base font-bold text-slate-500 dark:text-slate-400">
                      {job.company?.name ||
                        job.company_name ||
                        "Company Profile"}
                    </span>
                    {job.company_id && (
                      <button
                        onClick={() =>
                          router.push(`/counselee/companies/${job.company_id}`)
                        }
                        className="text-xs bg-blue-50 hover:bg-blue-100 dark:bg-slate-800 dark:hover:bg-blue-900/50 text-blue-600 dark:text-blue-400 border border-slate-200 dark:border-slate-700 rounded-lg px-2.5 py-1 font-extrabold transition-all cursor-pointer"
                      >
                        View Company Profile →
                      </button>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Quick Stats Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-2xl p-5 backdrop-blur-md">
                <span className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest block mb-1">
                  Salary range
                </span>
                <p className="text-sm font-bold text-emerald-600 dark:text-emerald-450 flex items-center gap-0.5">
                  <DollarSign className="w-4 h-4 shrink-0 text-emerald-500" />
                  {job.min_salary
                    ? `${Number(job.min_salary).toLocaleString()} - ${Number(
                        job.max_salary || 0,
                      ).toLocaleString()} USD`
                    : "Competitive"}
                </p>
              </div>

              <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-2xl p-5 backdrop-blur-md">
                <span className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest block mb-1">
                  Seniority Level
                </span>
                <p className="text-sm font-bold text-slate-700 dark:text-slate-200 flex items-center gap-1.5 uppercase">
                  <User className="w-4 h-4 text-blue-600 dark:text-blue-500" />
                  {job.seniority}
                </p>
              </div>

              <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-2xl p-5 backdrop-blur-md">
                <span className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest block mb-1">
                  Working Model
                </span>
                <p className="text-sm font-bold text-slate-700 dark:text-slate-200 flex items-center gap-1.5 uppercase">
                  <Briefcase className="w-4 h-4 text-blue-600 dark:text-blue-500" />
                  {job.working_model}
                </p>
              </div>

              <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-2xl p-5 backdrop-blur-md">
                <span className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest block mb-1">
                  Hours / Day
                </span>
                <p className="text-sm font-bold text-slate-700 dark:text-slate-200 flex items-center gap-1.5">
                  <Clock className="w-4 h-4 text-blue-600 dark:text-blue-500" />
                  {job.working_hours || "Full-time"}
                </p>
              </div>
            </div>

            {/* Main Content Layout */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Left Column: Description & Details */}
              <div className="lg:col-span-2 flex flex-col gap-6">
                <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-8 backdrop-blur-md flex flex-col gap-6">
                  <div>
                    <h2 className="text-lg font-extrabold text-slate-900 dark:text-white border-b border-slate-150 dark:border-slate-800 pb-3 mb-4">
                      Job Description
                    </h2>
                    <p className="text-sm font-medium text-slate-650 dark:text-slate-350 leading-relaxed whitespace-pre-line">
                      {job.job_description ||
                        job.description ||
                        "No description provided."}
                    </p>
                  </div>

                  {job.requirements && (
                    <div>
                      <h2 className="text-lg font-extrabold text-slate-900 dark:text-white border-b border-slate-150 dark:border-slate-800 pb-3 mb-4">
                        Requirements & Qualifications
                      </h2>
                      <p className="text-sm font-medium text-slate-655 dark:text-slate-350 leading-relaxed whitespace-pre-line">
                        {job.requirements}
                      </p>
                    </div>
                  )}
                </div>
              </div>

              {/* Right Column: Skills & Dates */}
              <div className="lg:col-span-1 flex flex-col gap-6">
                {/* Skills Card */}
                {job.skills && job.skills.length > 0 && (
                  <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-6 backdrop-blur-md">
                    <h3 className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-4">
                      Key Technical Skills
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {job.skills.map((skill) => (
                        <span
                          key={skill.id}
                          className="bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-850 text-blue-600 dark:text-blue-400 px-3 py-1.5 rounded-xl text-xs font-bold uppercase tracking-wider"
                        >
                          {skill.name}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Deadlines Card */}
                <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-6 backdrop-blur-md flex flex-col gap-4 text-sm font-semibold">
                  <div className="flex items-center gap-3 text-slate-600 dark:text-slate-300">
                    <Calendar className="w-5 h-5 text-blue-500 shrink-0" />
                    <div>
                      <span className="text-[10px] font-bold text-slate-400 dark:text-slate-550 uppercase tracking-widest block">
                        Expiration Date
                      </span>
                      <span>
                        {job.expired_date
                          ? new Date(job.expired_date).toLocaleDateString()
                          : "No deadline"}
                      </span>
                    </div>
                  </div>

                  {job.url && (
                    <a
                      href={job.url}
                      target="_blank"
                      rel="noreferrer"
                      className="w-full text-center bg-blue-600 hover:bg-blue-500 text-white rounded-full py-3 font-bold text-sm shadow-md transition-colors cursor-pointer block"
                    >
                      Apply via External Link ↗
                    </a>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
