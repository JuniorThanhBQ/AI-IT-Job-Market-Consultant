"use client";

import { Briefcase } from "lucide-react";
import { Link } from "@/i18n/routing";
import { useLocale, useTranslations } from "next-intl";
import { mapEnum, formatSalaryRange } from "@/utils/enumMapper";

export default function CompanyJobsList({ company, page, setPage, pageSize }) {
  const locale = useLocale();
  const t = useTranslations("Counselee.Company");

  const jobs = company.jobs || [];
  const totalPages = Math.ceil(jobs.length / pageSize);
  const displayedJobs = jobs.slice((page - 1) * pageSize, page * pageSize);

  return (
    <div className="lg:col-span-5 flex flex-col gap-6">
      <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-6 backdrop-blur-md flex flex-col gap-5">
        <h3 className="text-sm font-extrabold text-slate-900 dark:text-white pb-3 border-b border-slate-100 dark:border-slate-800 flex items-center gap-2">
          <Briefcase className="w-4.5 h-4.5 text-[#285872]" />
          {t("title", { count: jobs.length })}
        </h3>

        {jobs.length === 0 ? (
          <p className="text-xs text-slate-500 font-medium py-10 text-center">
            {t("no_jobs")}
          </p>
        ) : (
          <>
            <div className="flex flex-col gap-4">
              {displayedJobs.map((job) => (
                <div
                  key={job.id}
                  className="bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-850 rounded-2xl p-4 flex flex-col gap-2.5 hover:border-[#285872]/45 transition-colors"
                >
                  <Link
                    href={`/counselee/jobs/${job.id}`}
                    className="text-xs font-black text-[#285872] dark:text-[#407c9c] hover:underline leading-snug line-clamp-1"
                  >
                    {job.title}
                  </Link>
                  <div className="flex flex-wrap gap-1.5">
                    <span className="bg-slate-200/50 dark:bg-slate-900 text-slate-600 dark:text-slate-400 px-2 py-0.5 rounded text-[9px] font-bold uppercase">
                      {mapEnum(job.seniority, "SeniorityLevel", locale)}
                    </span>
                    <span className="bg-slate-200/50 dark:bg-slate-900 text-slate-600 dark:text-slate-400 px-2 py-0.5 rounded text-[9px] font-bold uppercase">
                      {mapEnum(job.working_model, "WorkingModel", locale)}
                    </span>
                  </div>
                  <span className="text-[10px] font-bold text-slate-450 dark:text-slate-500">
                    {formatSalaryRange(job.min_salary, job.max_salary, locale)}
                  </span>
                </div>
              ))}
            </div>

            {jobs.length > pageSize && (
              <div className="flex items-center justify-between border-t border-slate-100 dark:border-slate-800 pt-4 mt-2">
                <button
                  disabled={page === 1}
                  onClick={() => setPage((p) => p - 1)}
                  className="bg-slate-100 hover:bg-slate-200 dark:bg-slate-950 dark:hover:bg-slate-850 disabled:opacity-40 text-slate-700 dark:text-slate-300 rounded-lg px-3 py-1.5 text-[10px] font-bold transition-all cursor-pointer select-none"
                >
                  {t("prev")}
                </button>
                <span className="text-[10px] font-black text-slate-500">
                  {t("page_indicator", {
                    page: page,
                    total: totalPages,
                  })}
                </span>
                <button
                  disabled={page * pageSize >= jobs.length}
                  onClick={() => setPage((p) => p + 1)}
                  className="bg-slate-100 hover:bg-slate-200 dark:bg-slate-955 dark:hover:bg-slate-850 disabled:opacity-40 text-slate-700 dark:text-slate-300 rounded-lg px-3 py-1.5 text-[10px] font-bold transition-all cursor-pointer select-none"
                >
                  {t("next")}
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
