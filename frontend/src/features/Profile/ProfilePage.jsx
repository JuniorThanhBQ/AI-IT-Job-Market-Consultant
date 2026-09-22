"use client";

import React from "react";
import { motion, AnimatePresence } from "motion/react";
import { Loader2, Save } from "lucide-react";
import { useProfile } from "./hooks/useProfile";
import { ProfileFormField } from "./components/ProfileFormField";

export default function ProfilePage() {
  const {
    authLoading,
    router,
    locale,
    t,
    firstName,
    setFirstName,
    lastName,
    setLastName,
    birthday,
    setBirthday,
    biography,
    setBiography,
    goal,
    setGoal,
    loading,
    saving,
    error,
    success,
    isMissingName,
    handleSubmit,
  } = useProfile();

  if (authLoading || loading) {
    return (
      <div className="min-h-screen w-full flex items-center justify-center bg-white dark:bg-slate-955 text-slate-900 dark:text-white transition-colors duration-300">
        <Loader2 className="w-8 h-8 animate-spin text-slate-900 dark:text-white" />
      </div>
    );
  }

  return (
    <div className="relative min-h-screen bg-slate-50 dark:bg-slate-955 text-slate-900 dark:text-slate-100 font-sans transition-colors duration-300 pb-24">
      <div className="pointer-events-none absolute inset-0 z-0 opacity-[0.02] dark:opacity-[0.03] mix-blend-overlay">
        <svg className="w-full h-full">
          <filter id="noiseFilter">
            <feTurbulence
              type="fractalNoise"
              baseFrequency="0.85"
              numOctaves="3"
              stitchTiles="stitch"
            />
          </filter>
          <rect width="100%" height="100%" filter="url(#noiseFilter)" />
        </svg>
      </div>

      <main className="relative z-10 w-full max-w-full px-4 sm:px-6 md:px-12 pt-32 flex flex-col">
        <div className="flex flex-col gap-4 border-b border-slate-900 dark:border-white pb-8 mb-12">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl md:text-4xl font-black tracking-tighter uppercase leading-none">
              {t("title")}
            </h1>
          </div>
          <p className="text-base text-slate-500 font-bold max-w-full md:max-w-[80%] uppercase tracking-wider font-mono">
            {t("subtitle")}
          </p>
        </div>

        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="border border-red-500/30 bg-red-500/5 text-red-500 dark:text-red-400 p-4 text-base font-mono mb-8 flex items-center gap-2"
            >
              {error}
            </motion.div>
          )}
          {success && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="border border-emerald-500/30 bg-emerald-500/5 text-emerald-600 dark:text-emerald-450 p-4 text-base font-mono mb-8 flex items-center gap-2"
            >
              {success}
            </motion.div>
          )}
        </AnimatePresence>

        {isMissingName && (
          <div className="border border-slate-900 dark:border-white p-6 mb-12 flex flex-col gap-2 font-mono">
            <p className="text-base font-bold leading-relaxed text-slate-700 dark:text-slate-355">
              {locale === "vi"
                ? "Hãy hoàn thành hồ sơ của bạn để AIJMC định hướng theo đúng mong muốn và mục tiêu nhé."
                : "Providing your information to enables custom AI recommendations, optimized career path consulting and matching."}
            </p>
          </div>
        )}

        <form
          onSubmit={handleSubmit}
          className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-5 sm:p-8 md:p-12 backdrop-blur-md shadow-sm flex flex-col gap-8 md:gap-12"
        >
          <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
            <ProfileFormField
              index={1}
              label={t("first_name")}
              required
              value={firstName}
              onChange={(e) => setFirstName(e.target.value)}
            />
            <ProfileFormField
              index={2}
              label={t("last_name")}
              required
              value={lastName}
              onChange={(e) => setLastName(e.target.value)}
            />
          </div>

          <ProfileFormField
            index={3}
            label={t("birthday")}
            type="date"
            value={birthday}
            onChange={(e) => setBirthday(e.target.value)}
          />

          <ProfileFormField
            index={4}
            label={t("biography")}
            isTextArea
            rows={4}
            value={biography}
            onChange={(e) => setBiography(e.target.value)}
            placeholder={t("biography_placeholder")}
          />

          <ProfileFormField
            index={5}
            label={t("goal")}
            isTextArea
            rows={3}
            value={goal}
            onChange={(e) => setGoal(e.target.value)}
            placeholder={t("goal_placeholder")}
          />

          <div className="flex flex-col gap-4 mt-8">
            <button
              type="submit"
              disabled={saving}
              className="w-full bg-[#285872] hover:bg-[#1c3f52] disabled:opacity-40 text-white rounded-2xl py-4 text-[11px] font-black uppercase tracking-widest transition-all cursor-pointer flex items-center justify-center gap-2 shadow-lg shadow-[#285872]/20 hover:scale-[1.01]"
            >
              {saving ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Save className="w-4 h-4" />
              )}
              {t("btn_save")}
            </button>

            <button
              type="button"
              onClick={() => router.back()}
              className="w-full border border-slate-200 dark:border-slate-800 hover:border-slate-900 dark:hover:border-white rounded-2xl py-4 text-[11px] font-black uppercase tracking-widest transition-colors cursor-pointer text-slate-500 hover:text-slate-900 dark:hover:text-white"
            >
              {t("go_back")}
            </button>
          </div>
        </form>
      </main>
    </div>
  );
}
