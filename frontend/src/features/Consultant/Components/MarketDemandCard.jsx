"use client";

import { TrendingUp } from "lucide-react";
import { useTranslations } from "next-intl";

export default function MarketDemandCard({ marketSummary }) {
  const t = useTranslations("Counselee.Consultant");

  return (
    <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-8 backdrop-blur-md shadow-sm">
      <h2 className="text-xl font-extrabold text-slate-900 dark:text-white flex items-center gap-2.5 mb-6 border-b border-slate-100 dark:border-slate-800 pb-3">
        <TrendingUp className="w-5 h-5 text-[#285872]" />
        {t("demand_title")}
      </h2>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
        <div className="bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-850 rounded-2xl p-4">
          <span className="text-[10px] font-bold text-slate-450 dark:text-slate-500 uppercase tracking-widest block mb-1">
            {t("active_openings")}
          </span>
          <p className="text-2xl font-black text-[#285872]">
            {marketSummary.totalOpenings}
          </p>
          <span className="text-[10px] font-bold text-emerald-600 dark:text-emerald-450">
            {marketSummary.growth} {t("active_openings_index")}
          </span>
        </div>
        <div className="bg-slate-50 dark:bg-slate-955 border border-slate-200 dark:border-slate-850 rounded-2xl p-4">
          <span className="text-[10px] font-bold text-slate-450 dark:text-slate-500 uppercase tracking-widest block mb-1">
            {t("avg_salary")}
          </span>
          <p className="text-2xl font-black text-slate-900 dark:text-white">
            {marketSummary.avgSalary}
          </p>
          <span className="text-[10px] font-medium text-slate-450">
            {t("avg_salary_median")}
          </span>
        </div>
        <div className="bg-slate-50 dark:bg-slate-955 border border-slate-200 dark:border-slate-850 rounded-2xl p-4 col-span-2">
          <span className="text-[10px] font-bold text-slate-450 dark:text-slate-500 uppercase tracking-widest block mb-1">
            {t("growth_domain")}
          </span>
          <p className="text-lg font-extrabold text-slate-900 dark:text-white mt-1.5">
            {marketSummary.topField}
          </p>
        </div>
      </div>
      <p className="text-sm font-medium text-slate-650 dark:text-slate-350 leading-relaxed">
        {marketSummary.desc}
      </p>
    </div>
  );
}
