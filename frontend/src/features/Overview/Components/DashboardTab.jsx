"use client";

import { motion } from "motion/react";
import {
  User,
  TrendingUp,
  Award,
  Briefcase,
  Sparkles,
  Loader2,
  RefreshCw,
} from "lucide-react";
import { useTranslations } from "next-intl";

export default function DashboardTab({
  profile,
  trends,
  skillsSuggestions,
  jobPositions,
  loadingMarketData,
  hasMarketData,
  onFetchMarketAnalysis,
}) {
  const t = useTranslations("Counselee.Overview");

  return (
    <motion.div
      key="dashboard"
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -15 }}
      transition={{ duration: 0.2 }}
      className="grid grid-cols-1 lg:grid-cols-2 gap-8"
    >
      <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-8 backdrop-blur-md shadow-sm flex flex-col gap-6">
        <h2 className="text-xl font-extrabold text-slate-900 dark:text-white flex items-center gap-2.5 border-b border-slate-100 dark:border-slate-800 pb-3">
          <User className="w-5.5 h-5.5 text-[#285872]" />
          {t("profile_info")}
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          <div>
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block mb-0.5">
              {t("first_name")}
            </span>
            <p className="text-sm font-bold text-slate-800 dark:text-slate-200">
              {profile?.first_name || "—"}
            </p>
          </div>
          <div>
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block mb-0.5">
              {t("last_name")}
            </span>
            <p className="text-sm font-bold text-slate-800 dark:text-slate-200">
              {profile?.last_name || "—"}
            </p>
          </div>
          <div className="sm:col-span-2">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block mb-0.5">
              {t("birthday")}
            </span>
            <p className="text-sm font-bold text-slate-800 dark:text-slate-200">
              {profile?.birthday
                ? new Date(profile.birthday).toLocaleDateString()
                : "—"}
            </p>
          </div>
          <div className="sm:col-span-2">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block mb-0.5">
              {t("biography")}
            </span>
            <p className="text-sm font-medium text-slate-660 dark:text-slate-350 leading-relaxed whitespace-pre-line">
              {profile?.biography || t("biography_empty")}
            </p>
          </div>
          <div className="sm:col-span-2">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block mb-0.5">
              {t("career_goal")}
            </span>
            <p className="text-sm font-medium text-slate-655 dark:text-slate-300 leading-relaxed whitespace-pre-line">
              {profile?.goal || t("goal_empty")}
            </p>
          </div>
        </div>
      </div>

      <div className="flex flex-col gap-8">
        <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-8 backdrop-blur-md shadow-sm">
          <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3 mb-6">
            <h2 className="text-xl font-extrabold text-slate-900 dark:text-white flex items-center gap-2.5">
              <TrendingUp className="w-5.5 h-5.5 text-[#285872]" />
              {t("market_trend")}
            </h2>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-850 rounded-2xl p-4">
              <span className="text-[10px] font-bold text-slate-450 uppercase tracking-widest block mb-1">
                {t("target_role")}
              </span>
              <p className="text-base font-extrabold text-[#285872] line-clamp-1">
                {trends.role}
              </p>
            </div>
            <div className="bg-slate-50 dark:bg-slate-955 border border-slate-200 dark:border-slate-850 rounded-2xl p-4">
              <span className="text-[10px] font-bold text-slate-450 uppercase tracking-widest block mb-1">
                {t("active_postings")}
              </span>
              <p className="text-base font-extrabold text-slate-850 dark:text-white">
                {trends.activeJobs}
              </p>
            </div>
            <div className="bg-slate-50 dark:bg-slate-955 border border-slate-200 dark:border-slate-850 rounded-2xl p-4">
              <span className="text-[10px] font-bold text-slate-450 uppercase tracking-widest block mb-1">
                {t("avg_salary")}
              </span>
              <p className="text-base font-extrabold text-slate-850 dark:text-white">
                {trends.salaryRange}
              </p>
            </div>
            <div className="bg-slate-50 dark:bg-slate-955 border border-slate-200 dark:border-slate-850 rounded-2xl p-4">
              <span className="text-[10px] font-bold text-slate-450 uppercase tracking-widest block mb-1">
                {t("competition_rate")}
              </span>
              <p className="text-base font-extrabold text-slate-850 dark:text-white">
                {trends.difficulty}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-8 backdrop-blur-md shadow-sm flex flex-col gap-6">
          <div>
            <h2 className="text-xl font-extrabold text-slate-900 dark:text-white flex items-center gap-2.5 border-b border-slate-100 dark:border-slate-800 pb-3">
              <Award className="w-5.5 h-5.5 text-[#285872]" />
              {t("skills_positions")}
            </h2>
          </div>

          <div className="flex flex-col gap-4">
            <div>
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block mb-2">
                {t("recommended_skills")}
              </span>
              <div className="flex flex-wrap gap-2">
                {skillsSuggestions.map((skill, index) => (
                  <span
                    key={index}
                    className="bg-slate-100 dark:bg-slate-955 border border-slate-200 dark:border-slate-850 text-slate-700 dark:text-slate-355 px-3 py-1 rounded-xl text-xs font-bold"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>

            <div className="mt-2">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block mb-2">
                {t("target_job_tracks")}
              </span>
              <ul className="flex flex-col gap-2">
                {jobPositions.map((pos, index) => (
                  <li
                    key={index}
                    className="flex items-center gap-2 text-xs font-semibold text-slate-655 dark:text-slate-300"
                  >
                    <Briefcase className="w-4 h-4 text-[#285872] shrink-0" />
                    {pos}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
