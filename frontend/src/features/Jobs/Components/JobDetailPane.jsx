"use client";

import {
  Building,
  Loader2,
  Calendar,
  Clock,
  ExternalLink,
  Briefcase,
} from "lucide-react";
import { Link } from "@/i18n/routing";
import { useLocale, useTranslations } from "next-intl";
import {
  mapEnum,
  mapWorkingHours,
  formatSalaryRange,
} from "@/utils/enumMapper";
import { LOGO } from "@/assets/CloudinaryAssetsUrl";
import Image from "next/image";

export default function JobDetailPane({
  selectedJobId,
  selectedJobDetail,
  selectedJobLoading,
  stickyTop = "top-28",
}) {
  const locale = useLocale();
  const t = useTranslations("Counselee.Explorer");

  if (!selectedJobId) {
    return (
      <div
        className={`lg:w-3/5 ${stickyTop} flex flex-col gap-6 lg:sticky self-start`}
      >
        <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2.5rem] p-12 text-center backdrop-blur-md h-full min-h-[400px] flex flex-col justify-center items-center">
          <Briefcase className="w-12 h-12 text-slate-300 dark:text-slate-600 mb-4" />
          <h3 className="text-base font-extrabold text-slate-900 dark:text-white mb-1">
            {t("select_job_title")}
          </h3>
          <p className="text-xs text-slate-500 max-w-sm leading-relaxed">
            {t("select_job_desc")}
          </p>
        </div>
      </div>
    );
  }

  if (selectedJobLoading) {
    return (
      <div
        className={`lg:w-3/5 ${stickyTop} flex flex-col gap-6 lg:sticky self-start`}
      >
        <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2.5rem] p-12 text-center backdrop-blur-md h-full min-h-[400px] flex flex-col justify-center items-center">
          <Loader2 className="w-10 h-10 animate-spin text-[#285872]" />
        </div>
      </div>
    );
  }

  if (!selectedJobDetail) return null;

  const detailSource = selectedJobDetail.source || "ITViec";
  const detailLogoUrl = LOGO[detailSource.toUpperCase()] || LOGO.AIJMC_LOGO;

  return (
    <div
      className={`lg:w-3/5 flex flex-col gap-6 lg:sticky ${stickyTop} self-start`}
    >
      <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2.5rem] p-8 backdrop-blur-md shadow-sm flex flex-col gap-6">
        <div className="flex items-start justify-between gap-4 border-b border-slate-100 dark:border-slate-800 pb-6">
          <div className="flex items-start gap-4">
            <div className="w-16 h-16 bg-white border border-slate-200 dark:border-slate-800 rounded-2xl flex items-center justify-center p-2 shrink-0">
              <Image
                src={detailLogoUrl}
                alt={detailSource}
                width={64}
                height={64}
                className="w-full h-full object-contain"
              />
            </div>
            <div>
              <h2 className="text-xl font-extrabold text-slate-900 dark:text-white leading-tight max-w-[80%]">
                {selectedJobDetail.title}
              </h2>
              {selectedJobDetail.company ? (
                <Link
                  href={`/counselee/companies/${selectedJobDetail.company.id}`}
                  className="text-xs font-black text-[#285872] dark:text-[#407c9c] hover:underline flex items-center gap-1.5 mt-1"
                >
                  <Building className="w-3.5 h-3.5" />
                  {selectedJobDetail.company.name}
                </Link>
              ) : (
                <p className="text-xs font-bold text-slate-500 mt-1">
                  Company Confidential
                </p>
              )}
            </div>
          </div>

          <div className="flex flex-col items-end gap-2">
            <span className="text-base font-black text-emerald-600 dark:text-emerald-450">
              {formatSalaryRange(
                selectedJobDetail.min_salary,
                selectedJobDetail.max_salary,
                locale,
              )}
            </span>
            {selectedJobDetail.url && (
              <a
                href={selectedJobDetail.url}
                target="_blank"
                rel="noreferrer"
                className="bg-[#285872] hover:bg-[#1c3f52] text-white rounded-full px-5 py-2 text-xs font-black tracking-wide shadow-lg shadow-[#285872]/20 transition-all hover:scale-105 inline-flex items-center gap-1.5"
              >
                {t("apply_now")}
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
            )}
          </div>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-850 rounded-2xl p-4 text-xs font-bold">
          <div>
            <span className="text-[10px] text-slate-400 dark:text-slate-500 uppercase tracking-widest block mb-0.5">
              Seniority
            </span>
            <span className="text-slate-700 dark:text-slate-300">
              {mapEnum(selectedJobDetail.seniority, "SeniorityLevel", locale)}
            </span>
          </div>
          <div>
            <span className="text-[10px] text-slate-400 dark:text-slate-500 uppercase tracking-widest block mb-0.5">
              Work Model
            </span>
            <span className="text-slate-700 dark:text-slate-300">
              {mapEnum(selectedJobDetail.working_model, "WorkingModel", locale)}
            </span>
          </div>
          <div>
            <span className="text-[10px] text-slate-400 dark:text-slate-500 uppercase tracking-widest block mb-0.5">
              Working Hours
            </span>
            <span className="text-slate-700 dark:text-slate-300 flex items-center gap-1">
              <Clock className="w-3 h-3 text-slate-400" />
              {mapWorkingHours(selectedJobDetail.working_hours, locale)}
            </span>
          </div>
          <div>
            <span className="text-[10px] text-slate-400 dark:text-slate-500 uppercase tracking-widest block mb-0.5">
              Expired time
            </span>
            <span className="text-slate-700 dark:text-slate-300 flex items-center gap-1">
              <Calendar className="w-3 h-3 text-slate-400" />
              {selectedJobDetail.expired_date
                ? new Date(selectedJobDetail.expired_date).toLocaleDateString()
                : "N/A"}
            </span>
          </div>
        </div>

        {selectedJobDetail.skills && selectedJobDetail.skills.length > 0 && (
          <div className="flex flex-col gap-2.5">
            <h4 className="text-xs font-black uppercase tracking-widest text-slate-450 dark:text-slate-500">
              Required Skills & Technologies
            </h4>
            <div className="flex flex-wrap gap-2">
              {selectedJobDetail.skills.map((skill, sIdx) => (
                <span
                  key={sIdx}
                  className="bg-[#285872]/10 dark:bg-[#285872]/20 border border-[#285872]/30 text-[#285872] dark:text-[#52a0cc] px-3 py-1 rounded-xl text-xs font-extrabold"
                >
                  {skill.name}
                </span>
              ))}
            </div>
          </div>
        )}

        <div className="flex flex-col gap-3">
          <h4 className="text-xs font-black uppercase tracking-widest text-slate-450 dark:text-slate-500">
            Job Description & Responsibilities
          </h4>
          <div className="text-xs font-medium text-slate-650 dark:text-slate-350 leading-relaxed space-y-4 max-h-[380px] overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-slate-200 dark:scrollbar-thumb-slate-800">
            {selectedJobDetail.job_description ? (
              <p className="whitespace-pre-line text-justify">
                {selectedJobDetail.job_description}
              </p>
            ) : (
              <p className="italic text-slate-400">
                No description provided by the recruiter.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
