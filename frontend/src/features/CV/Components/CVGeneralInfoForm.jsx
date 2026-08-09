"use client";

import { FileText, Lock } from "lucide-react";
import { useTranslations } from "next-intl";

export default function CVGeneralInfoForm({
  jobPosition,
  setJobPosition,
  summary,
  setSummary,
  education,
  setEducation,
  skillsText,
  setSkillsText,
  locked = false,
}) {
  const t = useTranslations("Counselee.CV");

  return (
    <div className="relative bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-8 backdrop-blur-md shadow-sm flex flex-col gap-6">
      {locked && (
        <div className="absolute inset-0 bg-white/70 dark:bg-slate-900/70 backdrop-blur-sm rounded-[2rem] z-10 flex flex-col items-center justify-center gap-3">
          <Lock className="w-6 h-6 text-slate-400" />
          <span className="text-xs font-bold text-slate-400 text-center px-4">
            Locked — using uploaded CV for analysis
          </span>
        </div>
      )}
      <h2 className="text-xl font-extrabold text-slate-900 dark:text-white flex items-center gap-2.5 border-b border-slate-100 dark:border-slate-800 pb-3">
        <FileText className="w-5 h-5 text-[#285872]" />
        {t("general_info_title")}
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="text-xs font-bold text-slate-500 uppercase tracking-widest block mb-2">
            {t("target_position")}
          </label>
          <input
            type="text"
            value={jobPosition}
            onChange={(e) => setJobPosition(e.target.value)}
            placeholder="e.g. Senior Frontend Engineer"
            className="w-full bg-slate-50 dark:bg-slate-955 border border-slate-200 dark:border-slate-850 rounded-2xl px-4 py-3.5 text-xs font-bold text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-[#285872] transition-all"
          />
        </div>

        <div>
          <label className="text-xs font-bold text-slate-500 uppercase tracking-widest block mb-2">
            {t("skills_label")}
          </label>
          <input
            type="text"
            value={skillsText}
            onChange={(e) => setSkillsText(e.target.value)}
            placeholder="React, Next.js, TypeScript, Tailwind"
            className="w-full bg-slate-50 dark:bg-slate-955 border border-slate-200 dark:border-slate-850 rounded-2xl px-4 py-3.5 text-xs font-bold text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-[#285872] transition-all"
          />
        </div>

        <div className="md:col-span-2">
          <label className="text-xs font-bold text-slate-500 uppercase tracking-widest block mb-2">
            {t("summary_label")}
          </label>
          <textarea
            rows={3}
            value={summary}
            onChange={(e) => setSummary(e.target.value)}
            placeholder="Brief overview of your technical background..."
            className="w-full bg-slate-50 dark:bg-slate-955 border border-slate-200 dark:border-slate-850 rounded-2xl px-4 py-3 text-xs font-medium text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-[#285872] transition-all leading-relaxed"
          />
        </div>

        <div className="md:col-span-2">
          <label className="text-xs font-bold text-slate-500 uppercase tracking-widest block mb-2">
            {t("education_label")}
          </label>
          <textarea
            rows={2}
            value={education}
            onChange={(e) => setEducation(e.target.value)}
            placeholder="e.g. BS Computer Science, HCMC University"
            className="w-full bg-slate-50 dark:bg-slate-955 border border-slate-200 dark:border-slate-850 rounded-2xl px-4 py-3 text-xs font-medium text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-[#285872] transition-all leading-relaxed"
          />
        </div>
      </div>
    </div>
  );
}
