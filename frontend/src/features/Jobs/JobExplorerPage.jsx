"use client";

import { motion } from "motion/react";
import { useJobExplorer } from "./Hooks/useJobExplorer";
import JobExplorerHeader from "./Components/JobExplorerHeader";
import JobSearchFilterBar from "./Components/JobSearchFilterBar";
import JobListSidebar from "./Components/JobListSidebar";
import JobDetailPane from "./Components/JobDetailPane";

export default function JobExplorerPage() {
  const {
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
  } = useJobExplorer();

  return (
    <div className="relative min-h-screen bg-slate-50 dark:bg-slate-955 text-slate-900 dark:text-slate-100 font-sans transition-colors duration-300 pb-20">
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
          x: [0, 30, -20, 0],
          y: [0, -40, 30, 0],
          scale: [1, 1.15, 0.95, 1],
        }}
        transition={{ duration: 25, repeat: Infinity, ease: "easeInOut" }}
        className="absolute top-0 right-0 w-[50vw] h-[50vw] bg-[#285872]/10 dark:bg-[#285872]/15 rounded-full blur-[140px] pointer-events-none z-0"
      />
      <motion.div
        animate={{
          x: [0, -30, 20, 0],
          y: [0, 35, -20, 0],
          scale: [1, 1.1, 0.9, 1],
        }}
        transition={{ duration: 30, repeat: Infinity, ease: "easeInOut" }}
        className="absolute bottom-0 left-0 w-[45vw] h-[45vw] bg-[#285872]/10 dark:bg-[#285872]/10 rounded-full blur-[140px] pointer-events-none z-0"
      />

      <main className="relative z-10 max-w-[90vw] mx-auto px-4 sm:px-6 pt-28 flex flex-col gap-8">
        <JobExplorerHeader />
        <JobSearchFilterBar
          searchTitle={searchTitle}
          setSearchTitle={setSearchTitle}
          searchSeniority={searchSeniority}
          setSearchSeniority={setSearchSeniority}
          searchWorkingModel={searchWorkingModel}
          setSearchWorkingModel={setSearchWorkingModel}
          onSearch={handleSearch}
        />

        {error && (
          <p className="text-red-500 text-xs font-semibold text-center bg-red-500/10 border border-red-500/20 py-2.5 rounded-xl">
            {error}
          </p>
        )}

        <div className="flex flex-col lg:flex-row gap-8 items-start">
          <JobListSidebar
            jobs={jobs}
            jobsLoading={jobsLoading}
            selectedJobId={selectedJobId}
            onSelectJob={setSelectedJobId}
            page={page}
            setPage={setPage}
            pageSize={pageSize}
          />
          <JobDetailPane
            selectedJobId={selectedJobId}
            selectedJobDetail={selectedJobDetail}
            selectedJobLoading={selectedJobLoading}
          />
        </div>
      </main>
    </div>
  );
}
