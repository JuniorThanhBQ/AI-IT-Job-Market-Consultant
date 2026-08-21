"use client";

import { Loader2, DollarSign, ChevronRight } from "lucide-react";
import { useLocale, useTranslations } from "next-intl";
import { mapEnum, formatSalaryRange } from "@/utils/enumMapper";
import { LOGO } from "@/assets/CloudinaryAssetsUrl";
import Image from "next/image";
import { Link } from "@/i18n/routing";

export default function JobListSidebar({
  jobs,
  jobsLoading,
  selectedJobId,
  onSelectJob,
  page,
  setPage,
  pageSize,
}) {
  const locale = useLocale();
  const t = useTranslations("Counselee.Explorer");

  return (
    <div className="lg:w-2/5 w-full max-w-full min-w-0 flex flex-col gap-4">
      {jobsLoading ? (
        <div className="py-20 flex justify-center items-center">
          <Loader2 className="w-8 h-8 animate-spin text-[#285872]" />
        </div>
      ) : jobs.length === 0 ? (
        <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-12 text-center backdrop-blur-md">
          <p className="text-xs font-bold text-slate-450 dark:text-slate-500">
            {t("no_jobs_found")}
          </p>
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {jobs.map((job) => {
            const isSelected = selectedJobId === job.id;
            const source = job.source || "ITViec";
            const logoUrl = LOGO[source.toUpperCase()] || LOGO.AIJMC_LOGO;

            return (
              <div
                key={job.id}
                onClick={() => onSelectJob(job.id)}
                className={`p-5 rounded-[2rem] border transition-all cursor-pointer flex flex-col gap-3 group relative ${
                  isSelected
                    ? "bg-white dark:bg-slate-900 border-[#285872] dark:border-[#407c9c] shadow-lg shadow-[#285872]/5 ring-2 ring-[#285872]/20"
                    : "bg-white/80 dark:bg-slate-900/40 border-slate-200 dark:border-slate-900 hover:border-slate-350 dark:hover:border-slate-800"
                }`}
              >
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 bg-white border border-slate-200 dark:border-slate-800 rounded-2xl flex items-center justify-center overflow-hidden p-1.5 shrink-0">
                    <Image
                      src={logoUrl}
                      alt={source}
                      width={48}
                      height={48}
                      className="w-full h-full object-contain"
                    />
                  </div>

                  <div className="flex-1 min-w-0">
                    <h3
                      className={`text-sm font-black leading-snug line-clamp-1 group-hover:text-[#285872] transition-colors ${
                        isSelected
                          ? "text-[#285872] dark:text-[#407c9c]"
                          : "text-slate-900 dark:text-white"
                      }`}
                    >
                      {job.title}
                    </h3>
                    <p className="text-xs font-bold text-slate-500 dark:text-slate-400 truncate mt-0.5">
                      {job.company_name || "Company Confidential"}
                    </p>
                  </div>
                </div>

                <div className="flex flex-wrap gap-1.5 mt-1.5">
                  <span className="bg-slate-100/50 dark:bg-slate-950/60 text-slate-600 dark:text-slate-400 px-2 py-0.5 rounded-lg text-[9px] font-bold uppercase tracking-wider border border-slate-200/60 dark:border-slate-800">
                    {mapEnum(job.seniority, "SeniorityLevel", locale)}
                  </span>
                  <span className="bg-slate-100/50 dark:bg-slate-955/60 text-slate-600 dark:text-slate-400 px-2 py-0.5 rounded-lg text-[9px] font-bold uppercase tracking-wider border border-slate-200/60 dark:border-slate-800">
                    {mapEnum(job.working_model, "WorkingModel", locale)}
                  </span>
                  {job.status && (
                    <span
                      className={`inline-flex items-center gap-1 text-[9px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-lg border ${
                        job.status.toUpperCase() === "OPEN"
                          ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-600 dark:text-emerald-450"
                          : "bg-red-500/10 border-red-500/20 text-red-600 dark:text-red-400"
                      }`}
                    >
                      <span
                        className={`w-1 h-1 rounded-full ${
                          job.status.toUpperCase() === "OPEN"
                            ? "bg-emerald-500"
                            : "bg-red-500"
                        }`}
                      />
                      {locale === "vi"
                        ? job.status.toUpperCase() === "OPEN"
                          ? "Mở"
                          : "Đóng"
                        : job.status.toUpperCase() === "OPEN"
                          ? "Open"
                          : "Closed"}
                    </span>
                  )}
                </div>

                <div className="flex items-center justify-between border-t border-slate-100 dark:border-slate-850/60 pt-3 mt-1.5">
                  <div className="flex flex-col">
                    <span className="text-xs font-black text-[#285872] dark:text-[#407c9c]">
                      {formatSalaryRange(
                        job.min_salary,
                        job.max_salary,
                        locale,
                      )}
                    </span>
                    {job.score !== undefined && (
                      <span className="text-[10px] font-black text-emerald-600 dark:text-emerald-450 mt-1">
                        {locale === "vi" ? "Mức độ khớp: " : "Percent match: "}
                        {Math.round(job.score * 100)}%
                      </span>
                    )}
                  </div>
                  <Link
                    href={`/counselee/jobs/${job.id}`}
                    onClick={(e) => e.stopPropagation()}
                    className="text-[10px] font-bold text-slate-450 hover:text-[#285872] dark:hover:text-[#407c9c] flex items-center gap-0.5 group-hover:translate-x-0.5 transition-transform cursor-pointer"
                  >
                    {t("view_details")}
                    <ChevronRight className="w-3 h-3" />
                  </Link>
                </div>
              </div>
            );
          })}

          {setPage && (
            <div className="flex items-center justify-between p-2 mt-2">
              <button
                disabled={page === 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 hover:bg-slate-50 dark:hover:bg-slate-850 disabled:opacity-40 text-slate-700 dark:text-slate-300 rounded-xl px-4 py-2 text-xs font-bold transition-all cursor-pointer select-none"
              >
                {t("prev_page")}
              </button>
              <span className="text-xs font-black text-slate-500">
                {t("page_indicator", { page })}
              </span>
              <button
                disabled={jobs.length < pageSize}
                onClick={() => setPage((p) => p + 1)}
                className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 hover:bg-slate-50 dark:hover:bg-slate-850 disabled:opacity-40 text-slate-700 dark:text-slate-300 rounded-xl px-4 py-2 text-xs font-bold transition-all cursor-pointer select-none"
              >
                {t("next_page")}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
