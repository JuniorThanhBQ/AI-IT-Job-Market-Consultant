"use client";

import { useState } from "react";
import { Search } from "lucide-react";
import { useTranslations } from "next-intl";

export default function JobSearchFilterBar({
  searchTitle,
  setSearchTitle,
  searchSeniority,
  setSearchSeniority,
  searchWorkingModel,
  setSearchWorkingModel,
  onSearch,
}) {
  const t = useTranslations("Counselee.Explorer");
  const [seniorityOpen, setSeniorityOpen] = useState(false);
  const [modelOpen, setModelOpen] = useState(false);

  const seniorityOptions = [
    "Intern",
    "Fresher",
    "Junior",
    "Mid",
    "Senior",
    "Lead",
    "Manager",
  ];
  const modelOptions = ["Onsite", "Hybrid", "Remote"];

  const isVi = t("all_seniorities").includes("Tất cả");

  const modelLabels = {
    Onsite: isVi ? "Tại văn phòng" : "At Office",
    Hybrid: "Hybrid",
    Remote: "Remote",
  };

  const handleSeniorityToggle = (opt) => {
    if (searchSeniority.includes(opt)) {
      setSearchSeniority(searchSeniority.filter((s) => s !== opt));
    } else {
      setSearchSeniority([...searchSeniority, opt]);
    }
  };

  const handleSeniorityReset = () => {
    setSearchSeniority([]);
  };

  const handleModelToggle = (opt) => {
    if (searchWorkingModel.includes(opt)) {
      setSearchWorkingModel(searchWorkingModel.filter((m) => m !== opt));
    } else {
      setSearchWorkingModel([...searchWorkingModel, opt]);
    }
  };

  const handleModelReset = () => {
    setSearchWorkingModel([]);
  };

  return (
    <div className="relative z-20 bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-2xl p-0 backdrop-blur-md shadow-sm">
      <form onSubmit={onSearch}>
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-0 items-stretch divide-y lg:divide-y-0 lg:divide-x divide-slate-200 dark:divide-slate-800">
          <div className="flex flex-col justify-center px-6 py-3">
            <span className="text-[10px] uppercase tracking-wider font-extrabold text-slate-400 dark:text-slate-500 mb-1">
              {t("label_search")}
            </span>
            <div className="relative flex items-center">
              <Search className="absolute left-0 w-4 h-4 text-slate-400" />
              <input
                type="text"
                placeholder={t("search_placeholder")}
                value={searchTitle}
                onChange={(e) => setSearchTitle(e.target.value)}
                className="w-full bg-transparent border-0 pl-6 pr-2 py-1 text-xs font-bold text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none transition-all"
              />
            </div>
          </div>

          <div
            onClick={() => setSeniorityOpen(!seniorityOpen)}
            className="flex flex-col justify-center px-6 py-3 relative cursor-pointer select-none h-full"
          >
            <span className="text-[10px] uppercase tracking-wider font-extrabold text-slate-400 dark:text-slate-500 mb-1">
              {t("label_seniority")}
            </span>
            <div className="flex items-center justify-between text-xs font-bold text-slate-900 dark:text-white">
              <span className="truncate pr-4">
                {searchSeniority.length > 0
                  ? searchSeniority
                      .map((s) => (s === "Mid" ? "Middle" : s))
                      .join(", ")
                  : t("all_seniorities")}
              </span>
              <span className="text-slate-400 text-[10px] transition-transform duration-200">
                ▼
              </span>
            </div>

            {seniorityOpen && (
              <>
                <div
                  className="fixed inset-0 z-40 cursor-default"
                  onClick={(e) => {
                    e.stopPropagation();
                    setSeniorityOpen(false);
                  }}
                />
                <div
                  onClick={(e) => e.stopPropagation()}
                  className="absolute top-full left-0 mt-2 w-64 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-xl z-50 overflow-hidden flex flex-col"
                >
                  <div className="max-h-48 overflow-y-auto p-3 flex flex-col gap-2">
                    {seniorityOptions.map((opt) => (
                      <label
                        key={opt}
                        className="flex items-center gap-2.5 text-xs font-bold text-slate-700 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white cursor-pointer py-1"
                      >
                        <input
                          type="checkbox"
                          checked={searchSeniority.includes(opt)}
                          onChange={() => handleSeniorityToggle(opt)}
                          className="w-4 h-4 rounded border-slate-300 text-[#285872] focus:ring-[#285872] cursor-pointer"
                        />
                        {opt === "Mid" ? "Middle" : opt}
                      </label>
                    ))}
                  </div>
                  <div className="sticky bottom-0 bg-slate-50 dark:bg-slate-900/90 border-t border-slate-200 dark:border-slate-800 p-2 flex justify-between gap-2">
                    <button
                      type="button"
                      onClick={handleSeniorityReset}
                      className="text-[10px] font-black text-slate-500 hover:text-red-500 transition-colors uppercase tracking-wider px-2 py-1.5 rounded cursor-pointer"
                    >
                      RESET ALL
                    </button>
                    <button
                      type="button"
                      onClick={() => setSeniorityOpen(false)}
                      className="bg-[#285872] text-white text-[10px] font-black hover:bg-[#1c3f52] transition-colors uppercase tracking-wider px-3 py-1.5 rounded cursor-pointer"
                    >
                      CLOSE
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>

          <div
            onClick={() => setModelOpen(!modelOpen)}
            className="flex flex-col justify-center px-6 py-3 relative cursor-pointer select-none h-full"
          >
            <span className="text-[10px] uppercase tracking-wider font-extrabold text-slate-400 dark:text-slate-500 mb-1">
              {t("label_model")}
            </span>
            <div className="flex items-center justify-between text-xs font-bold text-slate-900 dark:text-white">
              <span className="truncate pr-4">
                {searchWorkingModel.length > 0
                  ? searchWorkingModel.map((m) => modelLabels[m]).join(", ")
                  : t("all_working_models")}
              </span>
              <span className="text-slate-400 text-[10px] transition-transform duration-200">
                ▼
              </span>
            </div>

            {modelOpen && (
              <>
                <div
                  className="fixed inset-0 z-40 cursor-default"
                  onClick={(e) => {
                    e.stopPropagation();
                    setModelOpen(false);
                  }}
                />
                <div
                  onClick={(e) => e.stopPropagation()}
                  className="absolute top-full left-0 mt-2 w-64 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-xl z-50 overflow-hidden flex flex-col"
                >
                  <div className="max-h-48 overflow-y-auto p-3 flex flex-col gap-2">
                    {modelOptions.map((opt) => (
                      <label
                        key={opt}
                        className="flex items-center gap-2.5 text-xs font-bold text-slate-700 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white cursor-pointer py-1"
                      >
                        <input
                          type="checkbox"
                          checked={searchWorkingModel.includes(opt)}
                          onChange={() => handleModelToggle(opt)}
                          className="w-4 h-4 rounded border-slate-300 text-[#285872] focus:ring-[#285872] cursor-pointer"
                        />
                        {modelLabels[opt]}
                      </label>
                    ))}
                  </div>
                  <div className="sticky bottom-0 bg-slate-50 dark:bg-slate-900/90 border-t border-slate-200 dark:border-slate-800 p-2 flex justify-between gap-2">
                    <button
                      type="button"
                      onClick={handleModelReset}
                      className="text-[10px] font-black text-slate-500 hover:text-red-500 transition-colors uppercase tracking-wider px-2 py-1.5 rounded cursor-pointer"
                    >
                      RESET ALL
                    </button>
                    <button
                      type="button"
                      onClick={() => setModelOpen(false)}
                      className="bg-[#285872] text-white text-[10px] font-black hover:bg-[#1c3f52] transition-colors uppercase tracking-wider px-3 py-1.5 rounded cursor-pointer"
                    >
                      CLOSE
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>

          <div className="flex items-stretch">
            <button
              type="submit"
              className="w-full bg-[#285872] hover:bg-[#1c3f52] text-white px-8 py-5 lg:py-0 text-xs font-black tracking-wider transition-all cursor-pointer flex items-center justify-center rounded-b-2xl lg:rounded-bl-none lg:rounded-r-2xl rounded-b-2xl"
            >
              {t("search_button").toUpperCase()}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}
