"use client";

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
    <div className="relative min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 font-sans transition-colors duration-300 pb-20">
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
