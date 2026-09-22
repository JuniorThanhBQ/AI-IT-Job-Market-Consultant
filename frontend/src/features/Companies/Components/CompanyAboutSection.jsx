"use client";

import { useTranslations } from "next-intl";

export default function CompanyAboutSection({ company }) {
  const t = useTranslations("Counselee.Company");

  return (
    <div className="lg:col-span-7 flex flex-col gap-6">
      <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-8 backdrop-blur-md shadow-sm flex flex-col gap-4">
        <h2 className="text-xs font-black text-[#285872] dark:text-[#407c9c] uppercase tracking-widest flex items-center gap-2 pb-2 border-b border-slate-100 dark:border-slate-800/60">
          <span>02</span>
          <span>{t("about")}</span>
        </h2>
        <p className="text-sm font-medium text-slate-700 dark:text-slate-300 leading-relaxed whitespace-pre-line">
          {company.description || "No description provided."}
        </p>
      </div>

      {company.addresses && company.addresses.length > 0 && (
        <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-8 backdrop-blur-md shadow-sm flex flex-col gap-4">
          <h2 className="text-xs font-black text-[#285872] dark:text-[#407c9c] uppercase tracking-widest flex items-center gap-2 pb-2 border-b border-slate-100 dark:border-slate-800/60">
            <span>03</span>
            <span>{t("locations")}</span>
          </h2>
          <ul className="flex flex-col gap-3 pl-0 text-sm text-slate-700 dark:text-slate-300 font-bold">
            {company.addresses.map((addr, idx) => (
              <li key={idx} className="flex items-start gap-3 leading-relaxed">
                <span className="text-[10px] font-bold text-slate-400 dark:text-slate-600 mt-0.5">
                  {(idx + 1).toString().padStart(2, "0")}.
                </span>
                <span>{addr}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {company.benefits && company.benefits.length > 0 && (
        <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-8 backdrop-blur-md shadow-sm flex flex-col gap-4">
          <h2 className="text-xs font-black text-[#285872] dark:text-[#407c9c] uppercase tracking-widest flex items-center gap-2 pb-2 border-b border-slate-100 dark:border-slate-800/60">
            <span>04</span>
            <span>{t("benefits")}</span>
          </h2>
          <ul className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-3.5 text-sm text-slate-700 dark:text-slate-300 font-black">
            {company.benefits.map((benefit, idx) => (
              <li key={idx} className="flex items-start gap-3 leading-relaxed">
                <span className="text-[10px] font-bold text-[#285872] dark:text-[#407c9c] mt-0.5">
                  {(idx + 1).toString().padStart(2, "0")}.
                </span>
                <span>{benefit}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
