"use client";

import {
  Building,
  Loader2,
  Calendar,
  Clock,
  ExternalLink,
  Briefcase,
} from "lucide-react";
import { Link, useRouter } from "@/i18n/routing";
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
  fullPage = false,
}) {
  const locale = useLocale();
  const router = useRouter();
  const t = useTranslations("Counselee.Explorer");
  const tJob = useTranslations("Counselee.Job");
  const tCompany = useTranslations("Counselee.Company");
  const tExplorer = useTranslations("Explorer");

  if (!selectedJobId) {
    return (
      <div
        className={`hidden lg:flex lg:w-3/5 ${stickyTop} flex-col gap-6 lg:sticky self-start`}
      >
        <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-2xl p-12 text-center backdrop-blur-md h-full min-h-[400px] flex flex-col justify-center items-center">
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
        className={`hidden lg:flex lg:w-3/5 ${stickyTop} flex-col gap-6 lg:sticky self-start`}
      >
        <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-2xl p-12 text-center backdrop-blur-md h-full min-h-[400px] flex flex-col justify-center items-center">
          <Loader2 className="w-10 h-10 animate-spin text-[#285872]" />
        </div>
      </div>
    );
  }

  if (!selectedJobDetail) return null;

  if (fullPage) {
    const detailSource = selectedJobDetail.source || "ITViec";
    const detailLogoUrl = LOGO[detailSource.toUpperCase()] || LOGO.AIJMC_LOGO;

    return (
      <div className="flex flex-col gap-8">
        <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2.5rem] p-8 backdrop-blur-md shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
          <div className="flex items-center gap-6">
            <div className="w-20 h-20 bg-white border border-slate-200 dark:border-slate-800 rounded-[1.5rem] flex items-center justify-center overflow-hidden p-2.5 shrink-0 shadow-sm">
              <Image
                src={detailLogoUrl}
                alt={detailSource}
                width={80}
                height={80}
                className="w-full h-full object-contain"
              />
            </div>
            <div className="min-w-0">
              <h1 className="text-2xl md:text-3xl lg:text-4xl font-black text-slate-900 dark:text-white tracking-tighter leading-tight break-words mb-3">
                {selectedJobDetail.title}
              </h1>
              <div className="flex flex-wrap items-center gap-3">
                <span className="text-sm font-bold text-slate-550 dark:text-slate-400">
                  {selectedJobDetail.company?.name ||
                    selectedJobDetail.company_name ||
                    tCompany("confidential")}
                </span>
                {selectedJobDetail.company_id && (
                  <>
                    <span className="w-1.5 h-1.5 rounded-full bg-slate-300 dark:bg-slate-700" />
                    <button
                      onClick={() =>
                        router.push(
                          `/counselee/companies/${selectedJobDetail.company_id}`,
                        )
                      }
                      className="text-xs font-black text-[#285872] dark:text-[#407c9c] hover:underline cursor-pointer"
                    >
                      {tJob("view_profile")}
                    </button>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-6 backdrop-blur-md shadow-sm grid grid-cols-2 md:grid-cols-4 gap-6 text-sm font-sans">
          <div className="flex flex-col gap-1">
            <span className="text-[10px] font-bold text-slate-400 dark:text-slate-550 uppercase tracking-widest">
              {tJob("salary_range")}
            </span>
            <span className="font-black text-[#285872] dark:text-[#407c9c]">
              {formatSalaryRange(
                selectedJobDetail.min_salary,
                selectedJobDetail.max_salary,
                locale,
              )}
            </span>
          </div>
          <div className="flex flex-col gap-1">
            <span className="text-[10px] font-bold text-slate-400 dark:text-slate-550 uppercase tracking-widest">
              {tJob("seniority")}
            </span>
            <span className="font-black text-slate-850 dark:text-slate-100 uppercase">
              {mapEnum(selectedJobDetail.seniority, "SeniorityLevel", locale)}
            </span>
          </div>
          <div className="flex flex-col gap-1">
            <span className="text-[10px] font-bold text-slate-400 dark:text-slate-550 uppercase tracking-widest">
              {tJob("model")}
            </span>
            <span className="font-black text-slate-850 dark:text-slate-100 uppercase">
              {mapEnum(selectedJobDetail.working_model, "WorkingModel", locale)}
            </span>
          </div>
          <div className="flex flex-col gap-1">
            <span className="text-[10px] font-bold text-slate-400 dark:text-slate-555 uppercase tracking-widest">
              {tJob("hours")}
            </span>
            <span className="font-black text-slate-850 dark:text-slate-100">
              {mapWorkingHours(selectedJobDetail.working_hours, locale)}
            </span>
          </div>
        </div>

        <div className="flex flex-col lg:flex-row gap-8">
          <div className="w-full lg:w-4/5 bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-8 backdrop-blur-md shadow-sm">
            <div className="flex flex-col gap-8">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="flex flex-col gap-4">
                  <h2 className="text-xs font-black text-[#285872] dark:text-[#407c9c] uppercase tracking-widest pb-2 border-b border-slate-100 dark:border-slate-800/60">
                    <span>02</span>
                    <span className="ml-1.5">{tJob("description")}</span>
                  </h2>
                  <p className="text-xs font-medium text-slate-700 dark:text-slate-300 leading-relaxed whitespace-pre-line text-justify">
                    {selectedJobDetail.job_description ||
                      selectedJobDetail.description ||
                      "No description provided."}
                  </p>
                </div>

                <div className="flex flex-col gap-4">
                  <h2 className="text-xs font-black text-[#285872] dark:text-[#407c9c] uppercase tracking-widest pb-2 border-b border-slate-100 dark:border-slate-800/60">
                    <span>03</span>
                    <span className="ml-1.5">{tJob("responsibilities")}</span>
                  </h2>
                  {selectedJobDetail.responsibilities &&
                  selectedJobDetail.responsibilities.length > 0 ? (
                    <ul className="flex flex-col gap-3 pl-0 text-xs text-slate-700 dark:text-slate-300 font-bold">
                      {selectedJobDetail.responsibilities.map((resp, index) => (
                        <li
                          key={index}
                          className="flex items-start gap-2 leading-relaxed"
                        >
                          <span className="text-[9px] font-bold text-slate-400 dark:text-slate-600 mt-0.5">
                            {(index + 1).toString().padStart(2, "0")}.
                          </span>
                          <span>{resp}</span>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-xs text-slate-405 dark:text-slate-500 italic">
                      No responsibilities specified.
                    </p>
                  )}
                </div>
              </div>

              {(selectedJobDetail.required_qualifications?.length > 0 ||
                selectedJobDetail.nice_to_have?.length > 0 ||
                selectedJobDetail.requirements) && (
                <div className="flex flex-col gap-6 border-t border-slate-150 dark:border-slate-800/60 pt-6">
                  {selectedJobDetail.required_qualifications &&
                    selectedJobDetail.required_qualifications.length > 0 && (
                      <div className="flex flex-col gap-4">
                        <h2 className="text-xs font-black text-[#285872] dark:text-[#407c9c] uppercase tracking-widest pb-2 border-b border-slate-100 dark:border-slate-800/60">
                          <span>04</span>
                          <span className="ml-1.5">{tJob("required")}</span>
                        </h2>
                        <ul className="flex flex-col gap-3 pl-0 text-xs text-slate-700 dark:text-slate-300 font-bold">
                          {selectedJobDetail.required_qualifications.map(
                            (qual, index) => (
                              <li
                                key={index}
                                className="flex items-start gap-2 leading-relaxed"
                              >
                                <span className="text-[9px] font-bold text-slate-400 dark:text-slate-600 mt-0.5">
                                  {(index + 1).toString().padStart(2, "0")}.
                                </span>
                                <span>{qual}</span>
                              </li>
                            ),
                          )}
                        </ul>
                      </div>
                    )}

                  {(selectedJobDetail.nice_to_have?.length > 0 ||
                    selectedJobDetail.requirements) && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 border-t border-slate-100 dark:border-slate-800/60 pt-6">
                      <div className="flex flex-col gap-4">
                        {selectedJobDetail.nice_to_have &&
                          selectedJobDetail.nice_to_have.length > 0 && (
                            <>
                              <h2 className="text-xs font-black text-[#285872] dark:text-[#407c9c] uppercase tracking-widest pb-2 border-b border-slate-100 dark:border-slate-800/60">
                                <span>05</span>
                                <span className="ml-1.5">
                                  {tJob("nice_to_have")}
                                </span>
                              </h2>
                              <ul className="flex flex-col gap-3 pl-0 text-xs text-slate-700 dark:text-slate-300 font-black">
                                {selectedJobDetail.nice_to_have.map(
                                  (nth, index) => (
                                    <li
                                      key={index}
                                      className="flex items-start gap-2 leading-relaxed"
                                    >
                                      <span className="text-[9px] font-bold text-[#285872] dark:text-[#407c9c] mt-0.5">
                                        {(index + 1)
                                          .toString()
                                          .padStart(2, "0")}
                                        .
                                      </span>
                                      <span>{nth}</span>
                                    </li>
                                  ),
                                )}
                              </ul>
                            </>
                          )}
                      </div>

                      <div className="flex flex-col gap-4">
                        {selectedJobDetail.requirements && (
                          <>
                            <h2 className="text-xs font-black text-[#285872] dark:text-[#407c9c] uppercase tracking-widest pb-2 border-b border-slate-100 dark:border-slate-800/60">
                              <span>06</span>
                              <span className="ml-1.5">
                                {tJob("additional")}
                              </span>
                            </h2>
                            <p className="text-xs font-medium text-slate-700 dark:text-slate-300 leading-relaxed whitespace-pre-line">
                              {selectedJobDetail.requirements}
                            </p>
                          </>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          <div className="w-full lg:w-1/5 flex flex-col gap-8 lg:sticky lg:top-28 self-start">
            {selectedJobDetail.skills &&
              selectedJobDetail.skills.length > 0 && (
                <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-6 backdrop-blur-md shadow-sm flex flex-col gap-4">
                  <h3 className="text-xs font-black text-[#285872] dark:text-[#407c9c] uppercase tracking-widest flex items-center gap-2 pb-2 border-b border-slate-100 dark:border-slate-800/60">
                    <span>07</span>
                    <span>{tJob("skills")}</span>
                  </h3>
                  <div className="flex flex-wrap gap-2 pt-2">
                    {selectedJobDetail.skills.map((skill) => (
                      <span
                        key={skill.id}
                        className="bg-[#285872]/10 dark:bg-[#285872]/20 border border-[#285872]/30 text-[#285872] dark:text-[#52a0cc] px-3 py-1.5 rounded-xl text-xs font-extrabold"
                      >
                        {skill.name}
                      </span>
                    ))}
                  </div>
                </div>
              )}

            {selectedJobDetail.domains &&
              selectedJobDetail.domains.length > 0 && (
                <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-6 backdrop-blur-md shadow-sm flex flex-col gap-4">
                  <h3 className="text-xs font-black text-[#285872] dark:text-[#407c9c] uppercase tracking-widest flex items-center gap-2 pb-2 border-b border-slate-100 dark:border-slate-800/60">
                    <span>08</span>
                    <span>{tJob("domains")}</span>
                  </h3>
                  <div className="flex flex-wrap gap-2 pt-2">
                    {selectedJobDetail.domains.map((dom, index) => (
                      <span
                        key={index}
                        className="bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 px-3 py-1.5 rounded-xl text-xs font-extrabold border border-slate-200 dark:border-slate-700"
                      >
                        {dom}
                      </span>
                    ))}
                  </div>
                </div>
              )}

            <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-6 backdrop-blur-md shadow-sm flex flex-col gap-4 text-sm font-semibold">
              <div className="flex items-center gap-3 text-slate-600 dark:text-slate-300 py-4 border-y border-slate-100 dark:border-slate-800/60">
                <Calendar className="w-5 h-5 text-[#285872] shrink-0" />
                <div>
                  <span className="text-[10px] font-bold text-slate-400 dark:text-slate-550 uppercase tracking-widest block">
                    {tJob("expiration")}
                  </span>
                  <span className="font-black text-slate-850 dark:text-slate-100">
                    {selectedJobDetail.expired_date
                      ? new Date(
                          selectedJobDetail.expired_date,
                        ).toLocaleDateString()
                      : tExplorer("no_deadline")}
                  </span>
                </div>
              </div>

              {selectedJobDetail.url && (
                <a
                  href={selectedJobDetail.url}
                  target="_blank"
                  rel="noreferrer"
                  className="w-full text-center bg-[#285872] hover:bg-[#1c3f52] text-white rounded-full py-3 font-bold text-sm shadow-md transition-colors cursor-pointer block"
                >
                  {tJob("apply_external")}
                </a>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!selectedJobDetail) return null;

  const detailSource = selectedJobDetail.source || "ITViec";
  const detailLogoUrl = LOGO[detailSource.toUpperCase()] || LOGO.AIJMC_LOGO;

  const topOffset = stickyTop === "top-36" ? 144 : 112;
  const maxCardHeight = `calc(100vh - ${topOffset + 36}px)`;

  return (
    <div
      className={`hidden lg:flex lg:w-3/5 flex-col gap-6 lg:sticky ${stickyTop} self-start`}
    >
      <div
        style={{ maxHeight: maxCardHeight }}
        className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-2xl p-8 backdrop-blur-md shadow-sm flex flex-col gap-6 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-200 dark:scrollbar-thumb-slate-800"
      >
        <div className="flex items-start justify-between gap-4 border-b border-slate-100 dark:border-slate-800 pb-6">
          <div className="flex items-start gap-4 min-w-0">
            <div className="w-16 h-16 bg-white border border-slate-200 dark:border-slate-800 rounded-2xl flex items-center justify-center p-2 shrink-0">
              <Image
                src={detailLogoUrl}
                alt={detailSource}
                width={64}
                height={64}
                className="w-full h-full object-contain"
              />
            </div>
            <div className="min-w-0">
              <h2 className="text-xl font-extrabold text-slate-900 dark:text-white leading-tight max-w-full break-words">
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
            <span className="text-base font-black text-[#285872] dark:text-[#407c9c]">
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

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-0 bg-transparent border border-slate-200 dark:border-slate-900 rounded-2xl p-0 text-xs font-bold divide-x divide-y sm:divide-y-0 divide-slate-200 dark:divide-slate-800 overflow-hidden">
          <div className="p-4 sm:p-5 flex flex-col justify-center">
            <span className="text-[10px] text-slate-400 dark:text-slate-500 uppercase tracking-widest block mb-0.5">
              Seniority
            </span>
            <span className="text-slate-700 dark:text-slate-350">
              {mapEnum(selectedJobDetail.seniority, "SeniorityLevel", locale)}
            </span>
          </div>
          <div className="p-4 sm:p-5 flex flex-col justify-center">
            <span className="text-[10px] text-slate-400 dark:text-slate-500 uppercase tracking-widest block mb-0.5">
              Work Model
            </span>
            <span className="text-slate-700 dark:text-slate-350">
              {mapEnum(selectedJobDetail.working_model, "WorkingModel", locale)}
            </span>
          </div>
          <div className="p-4 sm:p-5 flex flex-col justify-center">
            <span className="text-[10px] text-slate-400 dark:text-slate-500 uppercase tracking-widest block mb-0.5">
              Working Hours
            </span>
            <span className="text-slate-700 dark:text-slate-350">
              {mapWorkingHours(selectedJobDetail.working_hours, locale)}
            </span>
          </div>
          <div className="p-4 sm:p-5 flex flex-col justify-center">
            <span className="text-[10px] text-slate-400 dark:text-slate-500 uppercase tracking-widest block mb-0.5">
              Expired time
            </span>
            <span className="text-slate-700 dark:text-slate-350">
              {selectedJobDetail.expired_date
                ? new Date(selectedJobDetail.expired_date).toLocaleDateString()
                : "N/A"}
            </span>
          </div>
        </div>

        {selectedJobDetail.skills && selectedJobDetail.skills.length > 0 && (
          <div className="flex flex-col gap-2.5">
            <h4 className="text-[10px] font-black uppercase tracking-widest text-[#285872] dark:text-[#407c9c] border-b border-slate-100 dark:border-slate-800 pb-1.5 mb-1">
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
          <h4 className="text-[10px] font-black uppercase tracking-widest text-[#285872] dark:text-[#407c9c] border-b border-slate-100 dark:border-slate-800 pb-1.5 mb-1">
            Job Description & Responsibilities
          </h4>
          <div className="text-xs font-medium text-slate-655 dark:text-slate-350 leading-relaxed space-y-4">
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

        {selectedJobDetail.responsibilities &&
          selectedJobDetail.responsibilities.length > 0 && (
            <div className="flex flex-col gap-2.5">
              <h4 className="text-[10px] font-black uppercase tracking-widest text-[#285872] dark:text-[#407c9c] border-b border-slate-100 dark:border-slate-800 pb-1.5 mb-1">
                Key Responsibilities
              </h4>
              <ul className="list-disc pl-5 text-xs font-medium text-slate-655 dark:text-slate-350 leading-relaxed flex flex-col gap-1.5">
                {selectedJobDetail.responsibilities.map((resp, index) => (
                  <li key={index}>{resp}</li>
                ))}
              </ul>
            </div>
          )}

        {selectedJobDetail.required_qualifications &&
          selectedJobDetail.required_qualifications.length > 0 && (
            <div className="flex flex-col gap-2.5">
              <h4 className="text-[10px] font-black uppercase tracking-widest text-[#285872] dark:text-[#407c9c] border-b border-slate-100 dark:border-slate-800 pb-1.5 mb-1">
                Required Qualifications
              </h4>
              <ul className="list-disc pl-5 text-xs font-medium text-slate-655 dark:text-slate-350 leading-relaxed flex flex-col gap-1.5">
                {selectedJobDetail.required_qualifications.map(
                  (qual, index) => (
                    <li key={index}>{qual}</li>
                  ),
                )}
              </ul>
            </div>
          )}

        {selectedJobDetail.nice_to_have &&
          selectedJobDetail.nice_to_have.length > 0 && (
            <div className="flex flex-col gap-2.5">
              <h4 className="text-[10px] font-black uppercase tracking-widest text-[#285872] dark:text-[#407c9c] border-b border-slate-100 dark:border-slate-800 pb-1.5 mb-1">
                Nice to Have
              </h4>
              <ul className="list-disc pl-5 text-xs font-medium text-slate-655 dark:text-slate-355 leading-relaxed flex flex-col gap-1.5">
                {selectedJobDetail.nice_to_have.map((nth, index) => (
                  <li key={index}>{nth}</li>
                ))}
              </ul>
            </div>
          )}

        {selectedJobDetail.domains && selectedJobDetail.domains.length > 0 && (
          <div className="flex flex-col gap-2.5">
            <h4 className="text-[10px] font-black uppercase tracking-widest text-[#285872] dark:text-[#407c9c] border-b border-slate-100 dark:border-slate-800 pb-1.5 mb-1">
              Business Domains
            </h4>
            <div className="flex flex-wrap gap-2">
              {selectedJobDetail.domains.map((dom, index) => (
                <span
                  key={index}
                  className="bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 px-3 py-1.5 rounded-xl text-xs font-extrabold border border-slate-200 dark:border-slate-700"
                >
                  {dom}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
