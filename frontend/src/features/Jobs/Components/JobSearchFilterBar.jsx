"use client";

import { Search } from "lucide-react";
import { useTranslations } from "next-intl";

export default function JobSearchFilterBar({
  searchTitle,
  setSearchTitle,
  searchSeniority,
  setSearchSeniority,
  searchWorkingModel,
  setSearchWorkingModel,
  searchMinSalary,
  setSearchMinSalary,
  onSearch,
}) {
  const t = useTranslations("Counselee.Explorer");

  return (
    <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2.5rem] p-6 backdrop-blur-md shadow-sm">
      <form onSubmit={onSearch} className="flex flex-col gap-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              placeholder={t("search_placeholder")}
              value={searchTitle}
              onChange={(e) => setSearchTitle(e.target.value)}
              className="w-full bg-slate-50 dark:bg-slate-955 border border-slate-200 dark:border-slate-850 rounded-2xl pl-11 pr-4 py-3.5 text-xs font-bold text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-[#285872] transition-all"
            />
          </div>

          <div>
            <select
              value={searchSeniority}
              onChange={(e) => setSearchSeniority(e.target.value)}
              className="w-full bg-slate-50 dark:bg-slate-955 border border-slate-200 dark:border-slate-850 rounded-2xl px-4 py-3.5 text-xs font-bold text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-[#285872] transition-all"
            >
              <option value="">{t("all_seniorities")}</option>
              <option value="Intern">Intern</option>
              <option value="Fresher">Fresher</option>
              <option value="Junior">Junior</option>
              <option value="Mid">Middle</option>
              <option value="Senior">Senior</option>
              <option value="Lead">Lead</option>
              <option value="Manager">Manager</option>
            </select>
          </div>

          <div>
            <select
              value={searchWorkingModel}
              onChange={(e) => setSearchWorkingModel(e.target.value)}
              className="w-full bg-slate-50 dark:bg-slate-955 border border-slate-200 dark:border-slate-850 rounded-2xl px-4 py-3.5 text-xs font-bold text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-[#285872] transition-all"
            >
              <option value="">{t("all_working_models")}</option>
              <option value="Onsite">At Office</option>
              <option value="Hybrid">Hybrid</option>
              <option value="Remote">Remote</option>
            </select>
          </div>

          <div>
            <input
              type="number"
              placeholder={t("min_salary_placeholder")}
              value={searchMinSalary}
              onChange={(e) => setSearchMinSalary(e.target.value)}
              className="w-full bg-slate-50 dark:bg-slate-955 border border-slate-200 dark:border-slate-850 rounded-2xl px-4 py-3.5 text-xs font-bold text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-[#285872] transition-all"
            />
          </div>
        </div>

        <div className="flex justify-end">
          <button
            type="submit"
            className="bg-[#285872] hover:bg-[#1c3f52] text-white rounded-2xl px-8 py-3.5 text-xs font-black tracking-wide shadow-lg shadow-[#285872]/20 transition-all hover:scale-105 cursor-pointer"
          >
            {t("search_button")}
          </button>
        </div>
      </form>
    </div>
  );
}
