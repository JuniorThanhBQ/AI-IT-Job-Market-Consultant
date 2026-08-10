"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { motion, AnimatePresence } from "motion/react";
import {
  Search,
  SlidersHorizontal,
  ArrowLeft,
  Briefcase,
  Sparkles,
  Loader2,
  ChevronDown,
  Building,
  ExternalLink,
} from "lucide-react";
import Header from "@/components/shared/Header";
import { Button } from "@/components/ui/button";
import { Link, useRouter } from "@/i18n/routing";
import { useJobAdvanced } from "./Hooks/useJobAdvanced";
import JobDetailPane from "./Components/JobDetailPane";
import { useLocale } from "next-intl";
import { formatSalaryRange, mapEnum } from "@/utils/enumMapper";
import { LOGO } from "@/assets/CloudinaryAssetsUrl";
import Image from "next/image";

const SENIORITY_OPTIONS = [
  { value: "", label: "All Levels" },
  { value: "INTERN", label: "Intern" },
  { value: "FRESHER", label: "Fresher" },
  { value: "JUNIOR", label: "Junior" },
  { value: "MIDDLE", label: "Middle" },
  { value: "SENIOR", label: "Senior" },
  { value: "LEAD", label: "Lead" },
  { value: "MANAGER", label: "Manager" },
];

const MODEL_OPTIONS = [
  { value: "", label: "All Models" },
  { value: "OFFICE", label: "Office" },
  { value: "REMOTE", label: "Remote" },
  { value: "HYBRID", label: "Hybrid" },
];

function ScoreBar({ score }) {
  const pct = Math.round(score * 100);
  const color =
    pct >= 70
      ? "bg-emerald-500"
      : pct >= 45
        ? "bg-[#285872]"
        : "bg-slate-300 dark:bg-slate-700";
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500 ${color}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-[10px] font-black text-slate-400 dark:text-slate-500 w-8 text-right">
        {pct}%
      </span>
    </div>
  );
}

function SerpCard({ job, isSelected, onSelect, locale }) {
  const logoUrl = LOGO[job.source?.toUpperCase()] || LOGO.AIJMC_LOGO;
  const snippet = job.job_description?.slice(0, 180).replace(/\n/g, " ") + "…";

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      onClick={() => onSelect(job)}
      className={`cursor-pointer rounded-[1.5rem] border p-5 flex flex-col gap-3 transition-all duration-200 ${
        isSelected
          ? "border-[#285872] bg-[#285872]/5 dark:bg-[#285872]/10 shadow-md shadow-[#285872]/10"
          : "border-slate-200 dark:border-slate-800 bg-white/70 dark:bg-slate-900/40 hover:border-[#285872]/40 hover:shadow-sm"
      } backdrop-blur-md`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3 min-w-0">
          <div className="w-10 h-10 shrink-0 bg-white border border-slate-200 dark:border-slate-800 rounded-xl flex items-center justify-center overflow-hidden p-1">
            <Image
              src={logoUrl}
              alt={job.source || ""}
              width={40}
              height={40}
              className="w-full h-full object-contain"
            />
          </div>
          <div className="min-w-0">
            <h3 className="text-sm font-black text-slate-900 dark:text-white leading-tight line-clamp-2">
              {job.title}
            </h3>
            {job.company ? (
              <div className="flex items-center gap-1 mt-0.5">
                <Building className="w-3 h-3 text-[#285872] dark:text-[#407c9c] shrink-0" />
                <span className="text-xs font-bold text-[#285872] dark:text-[#407c9c] truncate">
                  {job.company.name}
                </span>
              </div>
            ) : (
              <span className="text-xs font-bold text-slate-400">
                Company Confidential
              </span>
            )}
          </div>
        </div>
        <span className="text-xs font-black text-emerald-600 dark:text-emerald-450 shrink-0">
          {formatSalaryRange(job.min_salary, job.max_salary, locale)}
        </span>
      </div>

      <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed line-clamp-2">
        {snippet}
      </p>

      {job.skills && job.skills.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {job.skills.slice(0, 4).map((s, i) => (
            <span
              key={i}
              className="bg-[#285872]/8 dark:bg-[#285872]/15 border border-[#285872]/20 text-[#285872] dark:text-[#52a0cc] px-2 py-0.5 rounded-lg text-[10px] font-extrabold"
            >
              {s.name}
            </span>
          ))}
          {job.skills.length > 4 && (
            <span className="text-[10px] font-bold text-slate-400">
              +{job.skills.length - 4}
            </span>
          )}
        </div>
      )}

      <ScoreBar score={job.score ?? 0} />
    </motion.div>
  );
}

export default function JobAdvancedPage() {
  const t = useTranslations("Counselee.Explorer");
  const locale = useLocale();
  const router = useRouter();
  const [isFiltersOpen, setIsFiltersOpen] = useState(false);

  const {
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
  } = useJobAdvanced();

  const onSubmit = (e) => {
    e?.preventDefault();
    handleSearch();
  };

  return (
    <div className="relative min-h-screen bg-slate-50 dark:bg-slate-955 text-slate-900 dark:text-slate-100 font-sans transition-colors duration-300 pb-12 overflow-x-hidden">
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
          scale: [1, 1.05, 0.98, 1],
        }}
        transition={{ duration: 25, repeat: Infinity, ease: "easeInOut" }}
        className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[60vw] h-[60vw] bg-[#285872]/5 dark:bg-[#285872]/8 rounded-full blur-[140px] pointer-events-none z-0"
      />

      <Header />

      <AnimatePresence mode="wait">
        {!hasSearched ? (
          /* ─── PHASE 1: Google-style centered search ─── */
          <motion.div
            key="phase1"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.2 }}
            className="relative z-10 max-w-3xl mx-auto pt-24 px-4"
          >
            <button
              onClick={() => router.back()}
              className="flex items-center gap-2 text-xs font-black text-slate-500 hover:text-[#285872] dark:hover:text-[#407c9c] transition-colors group mb-10 cursor-pointer"
            >
              <ArrowLeft className="w-4 h-4 transition-transform group-hover:-translate-x-1" />
              Back to Explorer
            </button>

            <div className="text-center mb-10 flex flex-col items-center select-none">
              <div className="flex items-center gap-3 mb-2">
                <span className="p-3 bg-[#285872] text-white rounded-3xl shadow-lg shadow-[#285872]/30">
                  <Briefcase className="w-8 h-8" />
                </span>
                <span className="text-4xl font-black tracking-tight">
                  <span className="text-[#285872] dark:text-[#407c9c]">AI</span>
                  JMC
                </span>
              </div>
              <p className="text-sm mt-3 font-bold text-slate-500 dark:text-slate-400">
                {t("sub_advanced_title")}
              </p>
            </div>

            <form onSubmit={onSubmit} className="w-full flex flex-col gap-5">
              <div className="relative group">
                <div className="absolute inset-y-0 left-5 flex items-center pointer-events-none">
                  <Search className="w-5 h-5 text-slate-400 group-focus-within:text-[#285872] transition-colors" />
                </div>
                <input
                  autoFocus
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder={t("placeholder_search")}
                  className="w-full pl-14 pr-14 py-4 rounded-full border border-slate-200 dark:border-slate-800 bg-white/70 dark:bg-slate-900/60 backdrop-blur-md text-sm font-semibold outline-none focus:border-[#285872] dark:focus:border-[#407c9c] focus:ring-4 focus:ring-[#285872]/10 shadow-sm transition-all"
                />
                <button
                  type="button"
                  onClick={() => setIsFiltersOpen(!isFiltersOpen)}
                  className={`absolute inset-y-0 right-4 flex items-center px-2 cursor-pointer transition-colors ${
                    isFiltersOpen
                      ? "text-[#285872] dark:text-[#407c9c]"
                      : "text-slate-400"
                  }`}
                >
                  <SlidersHorizontal className="w-4 h-4" />
                </button>
              </div>

              <AnimatePresence>
                {isFiltersOpen && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.2 }}
                    className="overflow-hidden"
                  >
                    <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-800 rounded-[2rem] p-6 backdrop-blur-md grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="flex flex-col gap-1.5">
                        <label className="text-[10px] font-black uppercase tracking-widest text-slate-400">
                          {t("label_seniority")}
                        </label>
                        <div className="relative">
                          <select
                            value={filters.seniority}
                            onChange={(e) =>
                              setFilters((f) => ({
                                ...f,
                                seniority: e.target.value,
                              }))
                            }
                            className="w-full px-4 py-3 rounded-2xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 text-xs font-bold outline-none appearance-none cursor-pointer focus:border-[#285872]"
                          >
                            {SENIORITY_OPTIONS.map((o) => (
                              <option key={o.value} value={o.value}>
                                {o.label}
                              </option>
                            ))}
                          </select>
                          <ChevronDown className="w-3.5 h-3.5 text-slate-400 absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none" />
                        </div>
                      </div>

                      <div className="flex flex-col gap-1.5">
                        <label className="text-[10px] font-black uppercase tracking-widest text-slate-400">
                          {t("label_model")}
                        </label>
                        <div className="relative">
                          <select
                            value={filters.working_model}
                            onChange={(e) =>
                              setFilters((f) => ({
                                ...f,
                                working_model: e.target.value,
                              }))
                            }
                            className="w-full px-4 py-3 rounded-2xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 text-xs font-bold outline-none appearance-none cursor-pointer focus:border-[#285872]"
                          >
                            {MODEL_OPTIONS.map((o) => (
                              <option key={o.value} value={o.value}>
                                {o.label}
                              </option>
                            ))}
                          </select>
                          <ChevronDown className="w-3.5 h-3.5 text-slate-400 absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none" />
                        </div>
                      </div>

                      <div className="flex flex-col gap-1.5">
                        <label className="text-[10px] font-black uppercase tracking-widest text-slate-400">
                          Min Salary (USD)
                        </label>
                        <input
                          type="number"
                          value={filters.min_salary}
                          onChange={(e) =>
                            setFilters((f) => ({
                              ...f,
                              min_salary: e.target.value,
                            }))
                          }
                          placeholder="e.g. 1000"
                          className="w-full px-4 py-3 rounded-2xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 text-xs font-bold outline-none focus:border-[#285872]"
                        />
                      </div>

                      <div className="md:col-span-3 flex flex-col gap-1.5">
                        <label className="text-[10px] font-black uppercase tracking-widest text-slate-400">
                          Results:{" "}
                          <span className="text-[#285872]">
                            {filters.limit}
                          </span>
                        </label>
                        <input
                          type="range"
                          min={5}
                          max={30}
                          step={5}
                          value={filters.limit}
                          onChange={(e) =>
                            setFilters((f) => ({
                              ...f,
                              limit: Number(e.target.value),
                            }))
                          }
                          className="accent-[#285872] cursor-pointer"
                        />
                        <div className="flex justify-between text-[10px] text-slate-400 font-bold">
                          <span>5</span>
                          <span>15</span>
                          <span>30</span>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              <div className="flex items-center justify-center gap-3">
                <Button
                  type="submit"
                  disabled={!query.trim()}
                  className="bg-[#285872] hover:bg-[#1c3f52] text-white rounded-full px-6 py-5 text-xs font-black tracking-wide shadow-lg shadow-[#285872]/20 transition-all hover:scale-105 disabled:opacity-50 disabled:pointer-events-none"
                >
                  {t("btn_search")}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    const samples = [
                      "React Senior",
                      "Node.js Backend",
                      "Python AI",
                      "DevOps Kubernetes",
                      "Golang Microservices",
                    ];
                    const q =
                      samples[Math.floor(Math.random() * samples.length)];
                    setQuery(q);
                    handleSearch(q);
                  }}
                  className="border-slate-200 dark:border-slate-800 rounded-full px-6 py-5 text-xs font-black text-slate-600 dark:text-slate-350 hover:bg-slate-100 dark:hover:bg-slate-900 flex items-center gap-1.5 cursor-pointer"
                >
                  Hãy thử chức năng tư vấn chi tiết
                </Button>
              </div>
            </form>
          </motion.div>
        ) : (
          /* ─── PHASE 2: Results split-pane ─── */
          <motion.div
            key="phase2"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.25 }}
            className="relative z-10 max-w-[90vw] mx-auto pt-24 px-4 flex flex-col gap-6"
          >
            {/* Compact sticky search bar */}
            <div className="sticky top-20 z-20">
              <form
                onSubmit={onSubmit}
                className="flex items-center gap-3 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border border-slate-200 dark:border-slate-800 rounded-full px-4 py-2 shadow-sm"
              >
                <Search className="w-4 h-4 text-slate-400 shrink-0" />
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder={t("placeholder_search")}
                  className="flex-1 text-sm font-semibold bg-transparent outline-none placeholder:text-slate-400"
                />
                <button
                  type="button"
                  onClick={() => setIsFiltersOpen(!isFiltersOpen)}
                  className={`cursor-pointer p-1.5 rounded-full transition-colors ${
                    isFiltersOpen
                      ? "text-[#285872] bg-[#285872]/10"
                      : "text-slate-400 hover:text-slate-655"
                  }`}
                >
                  <SlidersHorizontal className="w-4 h-4" />
                </button>
                <Button
                  type="submit"
                  size="sm"
                  className="bg-[#285872] hover:bg-[#1c3f52] text-white rounded-full px-4 py-1.5 text-xs font-black"
                >
                  {t("btn_search")}
                </Button>
              </form>

              <AnimatePresence>
                {isFiltersOpen && (
                  <motion.div
                    initial={{ opacity: 0, y: -8 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -8 }}
                    className="mt-2 bg-white/90 dark:bg-slate-900/90 backdrop-blur-md border border-slate-200 dark:border-slate-800 rounded-[1.5rem] p-4 shadow-lg grid grid-cols-2 md:grid-cols-4 gap-3"
                  >
                    <div className="relative">
                      <select
                        value={filters.seniority}
                        onChange={(e) =>
                          setFilters((f) => ({
                            ...f,
                            seniority: e.target.value,
                          }))
                        }
                        className="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 text-xs font-bold outline-none appearance-none cursor-pointer"
                      >
                        {SENIORITY_OPTIONS.map((o) => (
                          <option key={o.value} value={o.value}>
                            {o.label}
                          </option>
                        ))}
                      </select>
                      <ChevronDown className="w-3 h-3 text-slate-400 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none" />
                    </div>
                    <div className="relative">
                      <select
                        value={filters.working_model}
                        onChange={(e) =>
                          setFilters((f) => ({
                            ...f,
                            working_model: e.target.value,
                          }))
                        }
                        className="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 text-xs font-bold outline-none appearance-none cursor-pointer"
                      >
                        {MODEL_OPTIONS.map((o) => (
                          <option key={o.value} value={o.value}>
                            {o.label}
                          </option>
                        ))}
                      </select>
                      <ChevronDown className="w-3 h-3 text-slate-400 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none" />
                    </div>
                    <input
                      type="number"
                      value={filters.min_salary}
                      onChange={(e) =>
                        setFilters((f) => ({
                          ...f,
                          min_salary: e.target.value,
                        }))
                      }
                      placeholder="Min salary USD"
                      className="px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 text-xs font-bold outline-none"
                    />
                    <div className="flex flex-col gap-1">
                      <span className="text-[10px] font-black text-slate-400">
                        Results:{" "}
                        <span className="text-[#285872]">{filters.limit}</span>
                      </span>
                      <input
                        type="range"
                        min={5}
                        max={30}
                        step={5}
                        value={filters.limit}
                        onChange={(e) =>
                          setFilters((f) => ({
                            ...f,
                            limit: Number(e.target.value),
                          }))
                        }
                        className="accent-[#285872] cursor-pointer"
                      />
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Split pane */}
            <div className="flex flex-col lg:flex-row gap-6 items-start">
              {/* LEFT: SERP results list 2/5 */}
              <div className="lg:w-2/5 flex flex-col gap-3">
                {loading && (
                  <div className="flex items-center justify-center py-20">
                    <Loader2 className="w-8 h-8 animate-spin text-[#285872]" />
                  </div>
                )}
                {!loading && error && (
                  <p className="text-xs font-bold text-red-500 text-center py-8">
                    {error}
                  </p>
                )}
                {!loading && !error && results.length === 0 && (
                  <div className="text-center py-16 text-slate-400">
                    <Search className="w-10 h-10 mx-auto mb-3 opacity-40" />
                    <p className="text-sm font-bold">No results found.</p>
                    <p className="text-xs mt-1">
                      Try a different query or adjust filters.
                    </p>
                  </div>
                )}
                {!loading &&
                  results.map((job) => (
                    <SerpCard
                      key={job.id}
                      job={job}
                      isSelected={selectedJobId === job.id}
                      onSelect={handleSelectJob}
                      locale={locale}
                    />
                  ))}
              </div>

              {/* RIGHT: JobDetailPane 3/5 */}
              <JobDetailPane
                selectedJobId={selectedJobId}
                selectedJobDetail={selectedJobDetail}
                selectedJobLoading={false}
                stickyTop="top-36"
              />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
