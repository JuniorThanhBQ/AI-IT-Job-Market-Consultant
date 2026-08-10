"use client";

import { useTranslations } from "next-intl";

export default function OverviewHeaderBanner({
  name,
  activeTab,
  setActiveTab,
}) {
  const t = useTranslations("Counselee.Overview");

  return (
    <div className="flex flex-col md:flex-row md:items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-6 gap-4">
      <div>
        <h1 className="text-3xl font-black tracking-tight text-[#285872] dark:text-[#407c9c] flex items-center gap-2">
          {t("welcome_back", { name })}
        </h1>
        <p className="text-sm text-slate-555 mt-1">{t("subtitle")}</p>
      </div>
      <div className="flex bg-slate-100 dark:bg-slate-950 p-1 rounded-2xl border border-slate-200 dark:border-slate-850">
        <button
          onClick={() => setActiveTab("dashboard")}
          className={`px-5 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
            activeTab === "dashboard"
              ? "bg-[#285872] text-white shadow-md"
              : "text-slate-555 hover:text-slate-855 dark:hover:text-slate-200"
          }`}
        >
          {t("tab_dashboard")}
        </button>
        <button
          onClick={() => setActiveTab("cv_analysis")}
          className={`px-5 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
            activeTab === "cv_analysis"
              ? "bg-[#285872] text-white shadow-md"
              : "text-slate-555 hover:text-slate-855 dark:hover:text-slate-200"
          }`}
        >
          {t("tab_cv_analysis")}
        </button>
      </div>
    </div>
  );
}
