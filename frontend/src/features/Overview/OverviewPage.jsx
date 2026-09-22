"use client";

import React from "react";
import OverviewHeaderBanner from "./Components/OverviewHeaderBanner";
import DashboardTab from "./Components/DashboardTab";
import { motion, AnimatePresence } from "motion/react";
import { Loader2, Sparkles } from "lucide-react";
import { useLocale, useTranslations } from "next-intl";
import { useOverviewData } from "./Hooks/useOverviewData";

export default function OverviewPage() {
  const t = useTranslations("Counselee.Overview");
  const locale = useLocale();

  const {
    user,
    authLoading,
    activeTab,
    setActiveTab,
    profile,
    loading,
    error,
  } = useOverviewData();

  if (authLoading || loading) {
    return (
      <div className="min-h-screen w-full flex items-center justify-center bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-white transition-colors duration-300">
        <Loader2 className="w-8 h-8 animate-spin text-[#285872]" />
      </div>
    );
  }

  return (
    <div className="relative min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 font-sans transition-colors duration-300 pb-20">
      <main className="relative z-10 max-w-7xl mx-auto px-6 pt-28 flex flex-col gap-8">
        <OverviewHeaderBanner
          name={profile?.first_name || user?.username}
          activeTab={activeTab}
          setActiveTab={setActiveTab}
        />

        {error && (
          <div className="bg-red-500/10 border border-red-500/20 text-red-500 dark:text-red-400 rounded-[2rem] p-6 text-sm font-semibold">
            {error}
          </div>
        )}

        <AnimatePresence mode="wait">
          {activeTab === "dashboard" ? (
            <DashboardTab profile={profile} />
          ) : (
            <motion.div
              key="cv_analysis"
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -15 }}
              transition={{ duration: 0.2 }}
              className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-12 backdrop-blur-md shadow-sm flex flex-col items-center justify-center min-h-[350px] text-center w-full"
            >
              <Sparkles className="w-12 h-12 text-[#285872] mb-4 animate-pulse" />
              <h2 className="text-xl font-extrabold text-slate-900 dark:text-white mb-2">
                {t("tab_cv_analysis")}
              </h2>
              <p className="text-sm font-semibold text-slate-500 max-w-sm leading-relaxed">
                {locale === "vi"
                  ? "Tính năng phân tích CV sẽ sớm ra mắt!"
                  : "CV Analysis feature is coming soon!"}
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}
