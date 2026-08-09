"use client";

import { BookOpen, MapPin, DollarSign, ChevronRight } from "lucide-react";
import { Link } from "@/i18n/routing";
import { useTranslations } from "next-intl";

export default function ConsultantJobMatches({ recommendedJobs }) {
  const t = useTranslations("Counselee.Consultant");

  return (
    <section className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2.5rem] p-8 backdrop-blur-md shadow-sm w-full">
      <h2 className="text-xl font-extrabold text-slate-900 dark:text-white flex items-center gap-2.5 mb-6 border-b border-slate-100 dark:border-slate-800 pb-3">
        <BookOpen className="w-5 h-5 text-[#285872]" />
        {t("jobs_title")}
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {recommendedJobs.map((job) => (
          <div
            key={job.id}
            className="bg-slate-50/40 dark:bg-slate-950/20 border border-slate-200 dark:border-slate-850 rounded-[2rem] p-6 flex flex-col justify-between gap-6 hover:border-slate-350 dark:hover:border-slate-800 transition-all group"
          >
            <div className="flex flex-col gap-3">
              <div className="flex justify-between items-start gap-2">
                <span className="bg-emerald-100 dark:bg-emerald-955/40 text-emerald-600 px-3 py-1 rounded-full text-[9px] font-black tracking-wider uppercase">
                  {t("match", { matchScore: job.matchScore })}
                </span>
                <span className="text-xs font-bold text-slate-450 flex items-center gap-1">
                  <MapPin className="w-3.5 h-3.5" />
                  {job.location}
                </span>
              </div>
              <div>
                <h3 className="text-base font-extrabold text-slate-900 dark:text-white group-hover:text-[#285872] transition-colors line-clamp-1">
                  {job.title}
                </h3>
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mt-0.5">
                  {job.company}
                </p>
              </div>
              <div className="flex flex-wrap gap-1.5 mt-1">
                {job.tags.map((tag, tIndex) => (
                  <span
                    key={tIndex}
                    className="bg-slate-100 dark:bg-slate-900 text-slate-600 dark:text-slate-400 px-2.5 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>

            <div className="flex items-center justify-between border-t border-slate-200 dark:border-slate-800/80 pt-4 mt-1">
              <span className="text-xs font-extrabold text-emerald-600 flex items-center">
                <DollarSign className="w-4 h-4 shrink-0" />
                {job.salary}
              </span>
              <Link
                href="/counselee/jobs"
                className="text-[10px] text-[#285872] font-black uppercase tracking-wider flex items-center gap-0.5"
              >
                {t("view_details")}
                <ChevronRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
