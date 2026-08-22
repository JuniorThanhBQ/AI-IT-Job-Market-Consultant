"use client";

import { useRef, useEffect } from "react";
import { useTranslations } from "next-intl";
import { motion, AnimatePresence } from "motion/react";
import { Search, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useRouter } from "@/i18n/routing";
import { useJobAdvanced } from "./Hooks/useJobAdvanced";
import JobDetailPane from "./Components/JobDetailPane";
import JobListSidebar from "./Components/JobListSidebar";

export default function JobAdvancedPage() {
  const t = useTranslations("Counselee.Explorer");
  const router = useRouter();

  const {
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
  } = useJobAdvanced();

  const onSubmit = (e) => {
    e?.preventDefault();
    handleSearch();
  };

  const textareaRef1 = useRef(null);
  const textareaRef2 = useRef(null);

  const adjustHeight = (ref) => {
    if (ref.current) {
      ref.current.style.height = "auto";
      ref.current.style.height = `${ref.current.scrollHeight}px`;
    }
  };

  useEffect(() => {
    if (!query) {
      if (textareaRef1.current) {
        textareaRef1.current.style.height = "auto";
      }
      if (textareaRef2.current) {
        textareaRef2.current.style.height = "auto";
      }
    }
  }, [query]);

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onSubmit(e);
    }
  };

  return (
    <div className="relative min-h-screen bg-slate-50 dark:bg-slate-955 text-slate-900 dark:text-slate-100 font-sans transition-colors duration-300 pb-12">
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

      <AnimatePresence mode="wait">
        {!hasSearched ? (
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
                <textarea
                  ref={textareaRef1}
                  autoFocus
                  rows={1}
                  maxLength={500}
                  value={query}
                  onChange={(e) => {
                    setQuery(e.target.value);
                    adjustHeight(textareaRef1);
                  }}
                  onKeyDown={handleKeyDown}
                  placeholder={t("placeholder_search")}
                  className="w-full pl-14 pr-6 py-4 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white/70 dark:bg-slate-900/60 backdrop-blur-md text-sm font-semibold outline-none focus:border-[#285872] dark:focus:border-[#407c9c] focus:ring-4 focus:ring-[#285872]/10 shadow-sm transition-all resize-none overflow-hidden"
                />
              </div>

              {error && (
                <p className="text-red-500 text-xs font-semibold text-center bg-red-500/10 border border-red-500/20 py-2 rounded-xl">
                  {error}
                </p>
              )}

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
                  {t("semantic_search_example")}
                </Button>
              </div>
            </form>
          </motion.div>
        ) : (
          <motion.div
            key="phase2"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.25 }}
            className="relative z-10 max-w-[90vw] mx-auto pt-24 px-4 flex flex-col gap-6"
          >
            <button
              onClick={() => router.back()}
              className="flex items-center gap-2 text-xs font-black text-slate-500 hover:text-[#285872] dark:hover:text-[#407c9c] transition-colors group cursor-pointer self-start"
            >
              <ArrowLeft className="w-4 h-4 transition-transform group-hover:-translate-x-1" />
              Back to Explorer
            </button>

            <div className="sticky top-22 z-20">
              <form
                onSubmit={onSubmit}
                className="flex items-center gap-3 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border border-slate-200 dark:border-slate-800 rounded-full px-4 py-2 shadow-sm"
              >
                <Search className="w-4 h-4 text-slate-400 shrink-0" />
                <textarea
                  ref={textareaRef2}
                  rows={1}
                  maxLength={500}
                  value={query}
                  onChange={(e) => {
                    setQuery(e.target.value);
                    adjustHeight(textareaRef2);
                  }}
                  onKeyDown={handleKeyDown}
                  placeholder={t("placeholder_search")}
                  className="flex-1 text-sm font-semibold bg-transparent outline-none placeholder:text-slate-400 resize-none overflow-hidden"
                />
                <Button
                  type="submit"
                  size="sm"
                  className="bg-[#285872] hover:bg-[#1c3f52] text-white rounded-full px-4 py-1.5 text-xs font-black"
                >
                  {t("btn_search")}
                </Button>
              </form>
              {error && (
                <p className="text-red-500 text-xs font-semibold mt-2 px-4 bg-red-500/10 border border-red-500/20 py-2 rounded-xl text-center">
                  {error}
                </p>
              )}
            </div>

            <div className="flex flex-col lg:flex-row gap-6 items-start">
              <JobListSidebar
                jobs={results}
                jobsLoading={loading}
                selectedJobId={selectedJobId}
                onSelectJob={(jobId) => {
                  const jobObj = results.find((r) => r.id === jobId);
                  if (jobObj) handleSelectJob(jobObj);
                }}
              />

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
