"use client";

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
      <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-8 backdrop-blur-md shadow-sm flex flex-col gap-4">
        <h3 className="text-xs font-black text-[#285872] dark:text-[#407c9c] uppercase tracking-widest flex items-center gap-2 pb-2 border-b border-slate-100 dark:border-slate-800/60">
          <span>05</span>
          <span>{t("title", { count: jobs.length })}</span>
        </h3>

        {jobs.length === 0 ? (
          <p className="text-xs text-slate-500 font-medium py-10 text-center">
            {t("no_jobs")}
          </p>
        ) : (
          <>
            <div className="flex flex-col divide-y divide-slate-150 dark:divide-slate-850">
              {displayedJobs.map((job) => (
                <div
                  key={job.id}
                  className="py-4 flex flex-col gap-2 hover:bg-slate-50/50 dark:hover:bg-slate-900/10 transition-colors"
                >
                  <Link
                    href={`/counselee/jobs/${job.id}`}
                    className="text-sm font-black text-slate-900 dark:text-slate-100 hover:text-[#285872] dark:hover:text-[#407c9c] transition-colors leading-snug line-clamp-1"
                  >
                    {job.title}
                  </Link>
                  <div className="flex flex-wrap gap-2 items-center">
                    <span className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
                      {mapEnum(job.seniority, "SeniorityLevel", locale)}
                    </span>
                    <span className="w-1.5 h-1.5 rounded-full bg-slate-300 dark:bg-slate-700" />
                    <span className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
                      {mapEnum(job.working_model, "WorkingModel", locale)}
                    </span>
                    <span className="w-1.5 h-1.5 rounded-full bg-slate-300 dark:bg-slate-700" />
                    <span className="text-[10px] font-extrabold text-[#285872] dark:text-[#407c9c]">
                      {formatSalaryRange(
                        job.min_salary,
                        job.max_salary,
                        locale,
                      )}
                    </span>
                  </div>
                </div>
              ))}
            </div>

            {jobs.length > pageSize && (
              <div className="flex items-center justify-between pt-4 mt-2">
                <button
                  disabled={page === 1}
                  onClick={() => setPage((p) => p - 1)}
                  className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-850 disabled:opacity-40 text-slate-700 dark:text-slate-300 rounded-xl px-4 py-2 text-xs font-bold transition-all cursor-pointer select-none"
                >
                  {t("prev")}
                </button>
                <span className="text-xs font-black text-slate-500">
                  {t("page_indicator", {
                    page: page,
                    total: totalPages,
                  })}
                </span>
                <button
                  disabled={page * pageSize >= jobs.length}
                  onClick={() => setPage((p) => p + 1)}
                  className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-850 disabled:opacity-40 text-slate-700 dark:text-slate-300 rounded-xl px-4 py-2 text-xs font-bold transition-all cursor-pointer select-none"
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
