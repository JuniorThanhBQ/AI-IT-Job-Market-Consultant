"use client";

import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "motion/react";
import {
  Building,
  User,
  Briefcase,
  DollarSign,
  Loader2,
  Calendar,
  Clock,
  Search,
  Globe,
  LogOut,
  ArrowRight,
  ExternalLink,
  ChevronRight,
  Sparkles,
} from "lucide-react";
import { useAuth } from "@/context/AuthProvider";
import { jobApi } from "@/configs/apis";
import { Link, useRouter } from "@/i18n/routing";
import { useLocale, useTranslations } from "next-intl";
import {
  mapEnum,
  mapWorkingHours,
  formatSalaryRange,
} from "@/utils/enumMapper";
import Header from "@/components/shared/Header";
import { LOGO } from "@/assets/CloudinaryAssetsUrl";

export default function JobExplorerPage() {
  const { user, logout, loading: authLoading } = useAuth();
  const router = useRouter();
  const locale = useLocale();
  const t = useTranslations("Counselee.Explorer");

  const [jobs, setJobs] = useState([]);
  const [jobsLoading, setJobsLoading] = useState(false);
  const [selectedJobId, setSelectedJobId] = useState(null);
  const [selectedJobDetail, setSelectedJobDetail] = useState(null);
  const [selectedJobLoading, setSelectedJobLoading] = useState(false);

  const [searchTitle, setSearchTitle] = useState("");
  const [searchSeniority, setSearchSeniority] = useState("");
  const [searchWorkingModel, setSearchWorkingModel] = useState("");
  const [searchMinSalary, setSearchMinSalary] = useState("");
  const [page, setPage] = useState(1);
  const pageSize = 10;

  useEffect(() => {
    if (!authLoading && !user) {
      router.replace("/counselee/login");
    }
  }, [user, authLoading, router]);

  const fetchJobs = useCallback(
    async (resetPage = false) => {
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
        if (searchMinSalary) params.min_salary = searchMinSalary;

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
    [
      page,
      searchTitle,
      searchSeniority,
      searchWorkingModel,
      searchMinSalary,
      selectedJobId,
    ],
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
    const fetchSelectedDetails = async () => {
      if (!selectedJobId) {
        setSelectedJobDetail(null);
        return;
      }
      setSelectedJobLoading(true);
      try {
        const detail = await jobApi.getJobDetails(selectedJobId);
        setSelectedJobDetail(detail);
      } catch (err) {
        console.error("Failed to load job details:", err);
      } finally {
        setSelectedJobLoading(false);
      }
    };
    fetchSelectedDetails();
  }, [selectedJobId]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchJobs(true);
  };

  const handleClearFilters = () => {
    setSearchTitle("");
    setSearchSeniority("");
    setSearchWorkingModel("");
    setSearchMinSalary("");
    setPage(1);
    setSelectedJobId(null);
    setSelectedJobDetail(null);
    setTimeout(() => {
      setJobsLoading(true);
      jobApi
        .getJobs({ skip: 0, limit: pageSize })
        .then((data) => {
          setJobs(data || []);
          if (data && data.length > 0) {
            setSelectedJobId(data[0].id);
          }
        })
        .catch((err) => console.error(err))
        .finally(() => setJobsLoading(false));
    }, 50);
  };

  if (authLoading || !user) {
    return (
      <div className="min-h-screen w-full flex items-center justify-center bg-slate-50 dark:bg-slate-955 text-slate-900 dark:text-white transition-colors duration-300">
        <Loader2 className="w-8 h-8 animate-spin text-[#285872]" />
      </div>
    );
  }

  return (
    <div className="relative min-h-screen bg-slate-50 dark:bg-slate-955 text-slate-900 dark:text-slate-100 font-sans transition-colors duration-300 pb-16">
      <div className="pointer-events-none absolute inset-0 z-0 opacity-[0.03] dark:opacity-[0.05] mix-blend-overlay">
        <svg className="w-full h-full">
          <filter id="noiseFilter">
            <feTurbulence
              type="fractalNoise"
              baseFrequency="0.75"
              numOctaves="3"
              stitchTiles="stitch"
            />
          </filter>
          <rect width="100%" height="100%" filter="url(#noiseFilter)" />
        </svg>
      </div>

      <motion.div
        animate={{
          x: [0, 20, -10, 0],
          y: [0, -30, 20, 0],
          scale: [1, 1.1, 0.95, 1],
        }}
        transition={{ duration: 20, repeat: Infinity, ease: "easeInOut" }}
        className="absolute top-0 right-0 w-[45vw] h-[45vw] bg-[#285872]/10 dark:bg-[#285872]/15 rounded-full blur-[130px] pointer-events-none z-0"
      />
      <motion.div
        animate={{
          x: [0, -20, 15, 0],
          y: [0, 25, -15, 0],
          scale: [1, 1.05, 0.9, 1],
        }}
        transition={{ duration: 25, repeat: Infinity, ease: "easeInOut" }}
        className="absolute bottom-0 left-0 w-[40vw] h-[40vw] bg-[#285872]/10 dark:bg-[#285872]/10 rounded-full blur-[130px] pointer-events-none z-0"
      />

      <Header />

      <main className="relative z-10 max-w-7xl mx-auto px-6 pt-28">
        <div className="flex flex-col gap-6">
          <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-4">
            <div>
              <h1 className="text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white">
                {t("title")}
              </h1>
              <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                {t("subtitle")}
              </p>
            </div>
            <div className="flex items-center gap-4">
              <Link
                href="/counselee/consultant"
                className="bg-[#285872] hover:bg-[#1c3f52] text-white rounded-full px-5 py-2.5 font-bold text-xs tracking-wide shadow-lg flex items-center gap-1.5 transition-all hover:scale-105"
              >
                <Sparkles className="w-3.5 h-3.5 animate-pulse" />
                {t("btn_consultant")}
              </Link>
            </div>
          </div>

          <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-6 backdrop-blur-md shadow-sm">
            <form
              onSubmit={handleSearchSubmit}
              className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end"
            >
              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider pl-1">
                  {t("label_search")}
                </label>
                <div className="relative">
                  <Search className="absolute left-3 top-3.5 w-4 h-4 text-slate-400" />
                  <input
                    type="text"
                    value={searchTitle}
                    onChange={(e) => setSearchTitle(e.target.value)}
                    placeholder={t("placeholder_search")}
                    className="w-full bg-slate-50 dark:bg-slate-955 border border-slate-200 dark:border-slate-850 rounded-xl pl-9 pr-4 py-3 outline-none focus:ring-1 focus:ring-[#285872] text-sm text-slate-900 dark:text-white font-medium"
                  />
                </div>
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider pl-1">
                  {t("label_seniority")}
                </label>
                <select
                  value={searchSeniority}
                  onChange={(e) => setSearchSeniority(e.target.value)}
                  className="w-full bg-slate-50 dark:bg-slate-955 border border-slate-200 dark:border-slate-850 rounded-xl p-3 outline-none focus:ring-1 focus:ring-[#285872] text-sm text-slate-900 dark:text-white font-medium cursor-pointer"
                >
                  <option value="">{t("all_seniorities")}</option>
                  <option value="Intern">
                    {mapEnum("Intern", "SeniorityLevel", locale)}
                  </option>
                  <option value="Junior">
                    {mapEnum("Junior", "SeniorityLevel", locale)}
                  </option>
                  <option value="Mid">
                    {mapEnum("Mid", "SeniorityLevel", locale)}
                  </option>
                  <option value="Senior">
                    {mapEnum("Senior", "SeniorityLevel", locale)}
                  </option>
                  <option value="Lead">
                    {mapEnum("Lead", "SeniorityLevel", locale)}
                  </option>
                </select>
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider pl-1">
                  {t("label_model")}
                </label>
                <select
                  value={searchWorkingModel}
                  onChange={(e) => setSearchWorkingModel(e.target.value)}
                  className="w-full bg-slate-50 dark:bg-slate-955 border border-slate-200 dark:border-slate-850 rounded-xl p-3 outline-none focus:ring-1 focus:ring-[#285872] text-sm text-slate-900 dark:text-white font-medium cursor-pointer"
                >
                  <option value="">{t("all_models")}</option>
                  <option value="Remote">
                    {mapEnum("Remote", "WorkingModel", locale)}
                  </option>
                  <option value="Hybrid">
                    {mapEnum("Hybrid", "WorkingModel", locale)}
                  </option>
                  <option value="Onsite">
                    {mapEnum("Onsite", "WorkingModel", locale)}
                  </option>
                </select>
              </div>

              <div className="flex gap-3">
                <button
                  type="submit"
                  className="flex-1 bg-[#285872] hover:bg-[#1c3f52] text-white rounded-xl py-3 font-bold text-sm shadow-md transition-colors cursor-pointer"
                >
                  {t("btn_search")}
                </button>
                <button
                  type="button"
                  onClick={handleClearFilters}
                  className="border border-slate-200 dark:border-slate-800 text-slate-555 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white rounded-xl px-4 py-3 font-bold text-sm transition-colors cursor-pointer"
                >
                  {t("btn_clear")}
                </button>
              </div>
            </form>
          </div>

          <div className="flex flex-col lg:flex-row gap-6 items-start">
            <div className="w-full lg:w-[35%] flex flex-col gap-4 shrink-0">
              {jobsLoading ? (
                <div className="w-full py-20 flex items-center justify-center bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] backdrop-blur-md">
                  <Loader2 className="w-8 h-8 animate-spin text-[#285872]" />
                </div>
              ) : jobs.length > 0 ? (
                <div className="flex flex-col gap-4 w-full">
                  <div className="flex flex-col gap-3 w-full">
                    {jobs.map((job) => {
                      const isSelected = selectedJobId === job.id;
                      return (
                        <div
                          key={job.id}
                          onClick={() => setSelectedJobId(job.id)}
                          className={`cursor-pointer p-5 rounded-2xl border transition-all flex flex-col justify-between gap-4 bg-white/80 dark:bg-slate-900/40 ${
                            isSelected
                              ? "border-l-4 border-l-[#285872] border-slate-350 dark:border-slate-700 bg-slate-100/50 dark:bg-slate-800/40"
                              : "border-slate-250 dark:border-slate-900 hover:border-slate-350 dark:hover:border-slate-800"
                          }`}
                        >
                          <div className="flex flex-col gap-2">
                            <h3 className="text-sm font-extrabold text-slate-900 dark:text-white line-clamp-2">
                              {job.title}
                            </h3>
                            <p className="text-xs text-slate-500 dark:text-slate-400 font-semibold uppercase tracking-wider">
                              {job.company_name || t("company_profile")}
                            </p>
                          </div>

                          <div className="flex flex-wrap gap-1.5">
                            <span className="bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 px-2 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider">
                              {mapEnum(job.seniority, "SeniorityLevel", locale)}
                            </span>
                            <span className="bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 px-2 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider">
                              {mapEnum(
                                job.working_model,
                                "WorkingModel",
                                locale,
                              )}
                            </span>
                          </div>

                          <div className="flex items-center justify-between border-t border-slate-150 dark:border-slate-800/50 pt-3">
                            <p className="text-xs font-bold text-emerald-600 dark:text-emerald-450 flex items-center">
                              <DollarSign className="w-3.5 h-3.5 shrink-0" />
                              {formatSalaryRange(
                                job.min_salary,
                                job.max_salary,
                                locale,
                              )}
                            </p>
                            <ChevronRight className="w-4 h-4 text-slate-400" />
                          </div>
                        </div>
                      );
                    })}
                  </div>

                  <div className="flex items-center justify-between bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-2xl p-4 backdrop-blur-md shadow-sm">
                    <button
                      disabled={page === 1 || jobsLoading}
                      onClick={() => setPage((prev) => Math.max(prev - 1, 1))}
                      className="px-3 py-2 rounded-xl border border-slate-250 dark:border-slate-800 text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 disabled:opacity-50 disabled:hover:bg-transparent font-bold text-xs transition-colors cursor-pointer"
                    >
                      {t("prev")}
                    </button>
                    <span className="text-xs font-bold text-slate-500">
                      {t("page_indicator", { page })}
                    </span>
                    <button
                      disabled={jobs.length < pageSize || jobsLoading}
                      onClick={() => setPage((prev) => prev + 1)}
                      className="px-3 py-2 rounded-xl border border-slate-250 dark:border-slate-800 text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 disabled:opacity-50 disabled:hover:bg-transparent font-bold text-xs transition-colors cursor-pointer"
                    >
                      {t("next")}
                    </button>
                  </div>
                </div>
              ) : (
                <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-2xl p-8 text-center backdrop-blur-md w-full">
                  <p className="text-sm font-bold text-slate-500">
                    {t("no_jobs_found")}
                  </p>
                </div>
              )}
            </div>

            <div className="w-full lg:w-[65%] sticky top-24 max-h-[calc(100vh-140px)] bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2.5rem] backdrop-blur-md shadow-sm flex flex-col overflow-hidden">
              <div className="flex-1 overflow-y-auto p-8">
                {selectedJobLoading ? (
                  <div className="w-full py-32 flex items-center justify-center">
                    <Loader2 className="w-8 h-8 animate-spin text-[#285872]" />
                  </div>
                ) : selectedJobDetail ? (
                  <div className="flex flex-col gap-6">
                    <div className="flex items-start gap-4">
                      <div className="w-14 h-14 bg-white border border-slate-200 dark:border-slate-800 rounded-2xl flex items-center justify-center shrink-0 overflow-hidden p-1.5">
                        {(() => {
                          const source = selectedJobDetail.source || "ITViec";
                          const logoUrl =
                            LOGO[source.toUpperCase()] || LOGO.AIJMC_LOGO;
                          return (
                            <img
                              src={logoUrl}
                              alt={source}
                              className="w-full h-full object-contain"
                            />
                          );
                        })()}
                      </div>
                      <div>
                        <h2 className="text-xl font-extrabold text-slate-900 dark:text-white">
                          {selectedJobDetail.title}
                        </h2>
                        <p className="text-sm text-slate-550 dark:text-slate-400 font-bold mt-1">
                          {selectedJobDetail.company?.name ||
                            selectedJobDetail.company_name ||
                            t("company_profile")}
                        </p>
                      </div>
                    </div>

                    <div className="flex flex-wrap gap-4 mt-2">
                      {selectedJobDetail.company_id && (
                        <button
                          onClick={() =>
                            router.push(
                              `/counselee/companies/${selectedJobDetail.company_id}`,
                            )
                          }
                          className="bg-[#285872] hover:bg-[#1c3f52] text-white rounded-full px-5 py-2.5 font-bold text-xs tracking-wide shadow-lg transition-all hover:scale-105 flex items-center gap-1.5 cursor-pointer border-0"
                        >
                          <Building className="w-3.5 h-3.5" />
                          {t("btn_company_info")}
                        </button>
                      )}
                      {selectedJobDetail.url && (
                        <a
                          href={selectedJobDetail.url}
                          target="_blank"
                          rel="noreferrer"
                          className="border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-850 rounded-full px-5 py-2.5 font-bold text-xs transition-all hover:scale-105 flex items-center gap-1.5 cursor-pointer select-none"
                        >
                          <Globe className="w-3.5 h-3.5" />
                          {t("btn_original_link")}
                        </a>
                      )}
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 border-t border-b border-slate-100 dark:border-slate-800 py-4 mt-2">
                      <div>
                        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block mb-0.5">
                          {t("salary")}
                        </span>
                        <p className="text-xs font-bold text-emerald-600 dark:text-emerald-450 flex items-center">
                          <DollarSign className="w-3.5 h-3.5 shrink-0" />
                          {formatSalaryRange(
                            selectedJobDetail.min_salary,
                            selectedJobDetail.max_salary,
                            locale,
                          )}
                        </p>
                      </div>
                      <div>
                        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block mb-0.5">
                          {t("seniority")}
                        </span>
                        <p className="text-xs font-bold text-slate-700 dark:text-slate-350 uppercase">
                          {mapEnum(
                            selectedJobDetail.seniority,
                            "SeniorityLevel",
                            locale,
                          )}
                        </p>
                      </div>
                      <div>
                        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block mb-0.5">
                          {t("working_model")}
                        </span>
                        <p className="text-xs font-bold text-slate-700 dark:text-slate-350 uppercase">
                          {mapEnum(
                            selectedJobDetail.working_model,
                            "WorkingModel",
                            locale,
                          )}
                        </p>
                      </div>
                      <div>
                        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block mb-0.5">
                          {t("working_hours")}
                        </span>
                        <p className="text-xs font-bold text-slate-700 dark:text-slate-350">
                          {mapWorkingHours(
                            selectedJobDetail.working_hours,
                            locale,
                          )}
                        </p>
                      </div>
                    </div>

                    <div className="flex flex-col gap-5 mt-2">
                      <div>
                        <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest block mb-2 border-b border-slate-100 dark:border-slate-800 pb-1.5">
                          {t("job_description")}
                        </h3>
                        <p className="text-sm font-medium text-slate-700 dark:text-slate-300 leading-relaxed whitespace-pre-line">
                          {selectedJobDetail.job_description ||
                            selectedJobDetail.description ||
                            t("no_description")}
                        </p>
                      </div>

                      {selectedJobDetail.requirements && (
                        <div>
                          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest block mb-2 border-b border-slate-100 dark:border-slate-800 pb-1.5">
                            {t("requirements")}
                          </h3>
                          <p className="text-sm font-medium text-slate-700 dark:text-slate-300 leading-relaxed whitespace-pre-line">
                            {selectedJobDetail.requirements}
                          </p>
                        </div>
                      )}

                      {selectedJobDetail.skills &&
                        selectedJobDetail.skills.length > 0 && (
                          <div>
                            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest block mb-3 border-b border-slate-100 dark:border-slate-800 pb-1.5">
                              {t("key_skills")}
                            </h3>
                            <div className="flex flex-wrap gap-2">
                              {selectedJobDetail.skills.map((skill) => (
                                <span
                                  key={skill.id}
                                  className="bg-slate-100 dark:bg-slate-955 border border-slate-200 dark:border-slate-850 text-[#285872] dark:text-[#407c9c] px-3 py-1 rounded-xl text-xs font-bold uppercase tracking-wider"
                                >
                                  {skill.name}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}

                      <div className="flex items-center gap-2 text-xs font-semibold text-slate-500 border-t border-slate-100 dark:border-slate-800 pt-4">
                        <Calendar className="w-4 h-4 text-[#285872]" />
                        <span>{t("expiration_date")}</span>
                        <span>
                          {selectedJobDetail.expired_date
                            ? new Date(
                                selectedJobDetail.expired_date,
                              ).toLocaleDateString()
                            : t("no_deadline")}
                        </span>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="w-full py-32 flex flex-col items-center justify-center text-center">
                    <Briefcase className="w-12 h-12 text-slate-300 dark:text-slate-700 mb-4" />
                    <p className="text-sm font-bold text-slate-500">
                      {t("placeholder_select")}
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
