"use client";

import React from "react";
import { motion } from "motion/react";
import { User, ArrowRight } from "lucide-react";
import { useTranslations } from "next-intl";
import { Link } from "@/i18n/routing";

export default function DashboardTab({ profile }) {
  const t = useTranslations("Counselee.Overview");
  const tHeader = useTranslations("Header");

  return (
    <motion.div
      key="dashboard"
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -15 }}
      transition={{ duration: 0.2 }}
      className="grid grid-cols-1 gap-8"
    >
      <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-8 backdrop-blur-md shadow-sm flex flex-col gap-6 w-full">
        <h2 className="text-2xl font-extrabold text-slate-900 dark:text-white flex items-center gap-2.5 border-b border-slate-100 dark:border-slate-800 pb-3">
          <User className="w-6 h-6 text-[#285872]" />
          {t("profile_info")}
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-8">
          <div>
            <span className="text-[11px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest block mb-1">
              {t("first_name")}
            </span>
            <p className="text-base font-bold text-slate-800 dark:text-slate-200">
              {profile?.first_name || "—"}
            </p>
          </div>
          <div>
            <span className="text-[11px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest block mb-1">
              {t("last_name")}
            </span>
            <p className="text-base font-bold text-slate-800 dark:text-slate-200">
              {profile?.last_name || "—"}
            </p>
          </div>
          <div className="sm:col-span-2">
            <span className="text-[11px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest block mb-1">
              {t("birthday")}
            </span>
            <p className="text-base font-bold text-slate-800 dark:text-slate-200">
              {profile?.birthday
                ? new Date(profile.birthday).toLocaleDateString()
                : "—"}
            </p>
          </div>
          <div className="sm:col-span-2">
            <span className="text-[11px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest block mb-1">
              {t("biography")}
            </span>
            <p className="text-base font-semibold text-slate-700 dark:text-slate-300 leading-relaxed whitespace-pre-line">
              {profile?.biography || t("biography_empty")}
            </p>
          </div>
          <div className="sm:col-span-2">
            <span className="text-[11px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest block mb-1">
              {t("career_goal")}
            </span>
            <p className="text-base font-semibold text-slate-700 dark:text-slate-300 leading-relaxed whitespace-pre-line">
              {profile?.goal || t("goal_empty")}
            </p>
          </div>
        </div>

        <div className="lg:hidden mt-8 border-t border-slate-100 dark:border-slate-850/60 pt-6">
          <Link
            href="/counselee/jobs"
            className="w-full flex items-center justify-center gap-2 bg-[#285872] hover:bg-[#1c3f52] text-white rounded-full py-3.5 px-6 font-bold text-sm shadow-md transition-colors cursor-pointer"
          >
            <span>{tHeader("cta_dashboard")}</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>
    </motion.div>
  );
}
