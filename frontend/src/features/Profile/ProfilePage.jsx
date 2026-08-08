"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";
import {
  User,
  Calendar,
  Goal,
  Loader2,
  CheckCircle,
  AlertCircle,
  Save,
  ChevronLeft,
} from "lucide-react";
import { useAuth } from "@/context/AuthProvider";
import { profileApi } from "@/configs/apis";
import { Link, useRouter } from "@/i18n/routing";
import { useLocale, useTranslations } from "next-intl";
import Header from "@/components/shared/Header";

export default function ProfilePage() {
  const { user, authLoading } = useAuth();
  const router = useRouter();
  const locale = useLocale();
  const t = useTranslations("Counselee.Profile");

  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [birthday, setBirthday] = useState("");
  const [biography, setBiography] = useState("");
  const [goal, setGoal] = useState("");

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    if (!authLoading && !user) {
      router.replace("/counselee/login");
    }
  }, [user, authLoading, router]);

  useEffect(() => {
    async function fetchProfile() {
      if (!user) return;
      try {
        const data = await profileApi.getProfile();
        if (data) {
          setFirstName(data.first_name || "");
          setLastName(data.last_name || "");
          if (data.birthday) {
            setBirthday(data.birthday.split("T")[0]);
          }
          setBiography(data.biography || "");
          setGoal(data.goal || "");
        }
      } catch (err) {
        setError(t("error"));
      } finally {
        setLoading(false);
      }
    }
    fetchProfile();
  }, [user, t]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError("");
    setSuccess("");

    try {
      await profileApi.updateProfile({
        first_name: firstName,
        last_name: lastName,
        birthday: birthday ? `${birthday}T00:00:00` : null,
        biography,
        goal,
      });
      setSuccess(t("success"));
      setTimeout(() => setSuccess(""), 4000);
    } catch (err) {
      setError(t("error"));
    } finally {
      setSaving(false);
    }
  };

  if (authLoading || loading) {
    return (
      <div className="min-h-screen w-full flex items-center justify-center bg-slate-50 dark:bg-slate-955 text-slate-900 dark:text-white transition-colors duration-300">
        <Loader2 className="w-8 h-8 animate-spin text-[#285872]" />
      </div>
    );
  }

  return (
    <div className="relative min-h-screen bg-slate-50 dark:bg-slate-955 text-slate-900 dark:text-slate-100 font-sans transition-colors duration-300 pb-20">
      <div className="pointer-events-none absolute inset-0 z-0 opacity-[0.03] dark:opacity-[0.05] mix-blend-overlay">
        <svg className="w-full h-full">
          <filter id="noiseFilter">
            <feTurbulence
              type="fractalNoise"
              baseFrequency="0.75"
              numOctaves="3"
              stitchTiles="stitch"
            />
          </filter>
          <rect width="100%" height="100%" filter="url(#noiseFilter)" />
        </svg>
      </div>

      <motion.div
        animate={{
          x: [0, 15, -20, 0],
          y: [0, -25, 15, 0],
          scale: [1, 1.05, 0.98, 1],
        }}
        transition={{ duration: 20, repeat: Infinity, ease: "easeInOut" }}
        className="absolute top-0 left-0 w-[45vw] h-[45vw] bg-[#285872]/5 dark:bg-[#285872]/10 rounded-full blur-[130px] pointer-events-none z-0"
      />

      <Header />

      <main className="relative z-10 max-w-2xl mx-auto px-6 pt-28 flex flex-col gap-6">
        <button
          onClick={() => router.back()}
          className="self-start flex items-center gap-2 text-sm font-bold text-slate-500 hover:text-slate-900 dark:hover:text-white transition-colors cursor-pointer group"
        >
          <ChevronLeft className="w-4 h-4 transition-transform group-hover:-translate-x-1" />
          {t("go_back")}
        </button>

        <div className="flex flex-col gap-2">
          <h1 className="text-2xl font-black text-[#285872] dark:text-[#407c9c]">
            {t("title")}
          </h1>
          <p className="text-xs text-slate-500 font-medium">{t("subtitle")}</p>
        </div>

        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="bg-red-500/10 border border-red-500/20 text-red-500 dark:text-red-400 rounded-2xl p-4 text-xs font-bold flex items-center gap-2"
            >
              <AlertCircle className="w-4 h-4 shrink-0" />
              {error}
            </motion.div>
          )}
          {success && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 dark:text-emerald-400 rounded-2xl p-4 text-xs font-bold flex items-center gap-2"
            >
              <CheckCircle className="w-4 h-4 shrink-0" />
              {success}
            </motion.div>
          )}
        </AnimatePresence>

        <form
          onSubmit={handleSubmit}
          className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-8 backdrop-blur-md shadow-sm flex flex-col gap-6"
        >
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <div className="flex flex-col gap-2">
              <label className="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest flex items-center gap-1.5">
                <User className="w-3.5 h-3.5" />
                {t("first_name")}
              </label>
              <input
                type="text"
                required
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                className="bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-850 rounded-2xl px-4 py-3 text-sm font-semibold outline-none focus:ring-1 focus:ring-[#285872] text-slate-900 dark:text-white"
              />
            </div>
            <div className="flex flex-col gap-2">
              <label className="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest flex items-center gap-1.5">
                <User className="w-3.5 h-3.5" />
                {t("last_name")}
              </label>
              <input
                type="text"
                required
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                className="bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-850 rounded-2xl px-4 py-3 text-sm font-semibold outline-none focus:ring-1 focus:ring-[#285872] text-slate-900 dark:text-white"
              />
            </div>
          </div>

          <div className="flex flex-col gap-2">
            <label className="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest flex items-center gap-1.5">
              <Calendar className="w-3.5 h-3.5" />
              {t("birthday")}
            </label>
            <input
              type="date"
              value={birthday}
              onChange={(e) => setBirthday(e.target.value)}
              className="bg-slate-50 dark:bg-slate-955 border border-slate-200 dark:border-slate-850 rounded-2xl px-4 py-3 text-sm font-semibold outline-none focus:ring-1 focus:ring-[#285872] text-slate-900 dark:text-white"
            />
          </div>

          <div className="flex flex-col gap-2">
            <label className="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest flex items-center gap-1.5">
              <User className="w-3.5 h-3.5" />
              {t("biography")}
            </label>
            <textarea
              rows={4}
              value={biography}
              onChange={(e) => setBiography(e.target.value)}
              placeholder={t("biography_placeholder")}
              className="bg-slate-50 dark:bg-slate-955 border border-slate-200 dark:border-slate-850 rounded-2xl px-4 py-3 text-sm font-medium outline-none focus:ring-1 focus:ring-[#285872] text-slate-900 dark:text-white resize-none"
            />
          </div>

          <div className="flex flex-col gap-2">
            <label className="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest flex items-center gap-1.5">
              <Goal className="w-3.5 h-3.5" />
              {t("goal")}
            </label>
            <textarea
              rows={3}
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
              placeholder={t("goal_placeholder")}
              className="bg-slate-50 dark:bg-slate-955 border border-slate-200 dark:border-slate-850 rounded-2xl px-4 py-3 text-sm font-medium outline-none focus:ring-1 focus:ring-[#285872] text-slate-900 dark:text-white resize-none"
            />
          </div>

          <button
            type="submit"
            disabled={saving}
            className="w-full bg-[#285872] hover:bg-[#1c3f52] disabled:opacity-40 text-white rounded-2xl py-3.5 text-sm font-bold flex items-center justify-center gap-2 cursor-pointer shadow-md transition-colors mt-2"
          >
            {saving ? (
              <Loader2 className="w-4.5 h-4.5 animate-spin" />
            ) : (
              <Save className="w-4.5 h-4.5" />
            )}
            {t("btn_save")}
          </button>
        </form>
      </main>
    </div>
  );
}
