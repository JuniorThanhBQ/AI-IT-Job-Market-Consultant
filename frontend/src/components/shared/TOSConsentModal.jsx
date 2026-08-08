"use client";

import { useState, useEffect } from "react";
import { useTranslations } from "next-intl";
import { Link } from "@/i18n/routing";
import { motion, AnimatePresence } from "motion/react";
import { Check } from "lucide-react";

export default function TOSConsentModal() {
  const t = useTranslations("TOSConsent");
  const tTOS = useTranslations("TOS");
  const [isOpen, setIsOpen] = useState(false);
  const [agreeTOS, setAgreeTOS] = useState(false);
  const [agreePrivacy, setAgreePrivacy] = useState(false);

  useEffect(() => {
    const isAgreed = document.cookie
      .split("; ")
      .find((row) => row.startsWith("aijmc_tos_agreed="));
    if (!isAgreed) {
      const timer = setTimeout(() => {
        setIsOpen(true);
      }, 0);
      return () => clearTimeout(timer);
    }
  }, []);

  const handleAccept = () => {
    document.cookie =
      "aijmc_tos_agreed=true; max-age=31536000; path=/; SameSite=Lax";
    setIsOpen(false);
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-[99999] flex items-center justify-center p-4 overflow-y-auto bg-slate-955/65 backdrop-blur-lg">
        <motion.div
          initial={{ opacity: 0, scale: 0.9, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.9, y: 20 }}
          transition={{ type: "spring", duration: 0.5 }}
          className="relative w-[78vw] max-w-5xl max-h-[90vh] bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-[2.5rem] p-8 md:p-10 shadow-2xl flex flex-col gap-6 text-slate-900 dark:text-slate-100 overflow-hidden"
        >
          <div className="shrink-0 pb-2">
            <h2 className="text-xl md:text-2xl font-black tracking-tight leading-none text-slate-900 dark:text-white">
              {t("title")}
            </h2>
          </div>

          <p className="text-sm text-slate-505 dark:text-slate-400 leading-relaxed shrink-0">
            {t("desc")}
          </p>

          <div className="flex-1 min-h-[100px] md:min-h-[150px] overflow-y-auto pr-4 border border-slate-150 dark:border-slate-800 rounded-2xl p-6 bg-slate-50/50 dark:bg-slate-955/20 flex flex-col gap-6 text-sm leading-relaxed scrollbar-thin scrollbar-thumb-slate-200 dark:scrollbar-thumb-slate-800 text-justify">
            <div>
              <h3 className="font-bold text-slate-950 dark:text-white mb-2">
                {tTOS("intro_title")}
              </h3>
              <p className="text-slate-600 dark:text-slate-400 mb-3">
                {tTOS("intro_desc")}
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-white dark:bg-slate-900/60 p-4 rounded-xl border border-slate-100 dark:border-slate-800">
                  <span className="font-bold text-xs text-blue-605 dark:text-blue-400 uppercase">
                    {tTOS("intro_badge1")}
                  </span>
                  <p className="text-xs text-slate-500 mt-1 leading-normal">
                    {tTOS("intro_text1")}
                  </p>
                </div>
                <div className="bg-white dark:bg-slate-900/60 p-4 rounded-xl border border-slate-100 dark:border-slate-800">
                  <span className="font-bold text-xs text-purple-605 dark:text-purple-400 uppercase">
                    {tTOS("intro_badge2")}
                  </span>
                  <p className="text-xs text-slate-500 mt-1 leading-normal">
                    {tTOS("intro_text2")}
                  </p>
                </div>
              </div>
            </div>

            <div>
              <h3 className="font-bold text-slate-955 dark:text-white mb-2">
                {tTOS("ip_title")}
              </h3>
              <p className="text-slate-600 dark:text-slate-400 mb-3">
                {tTOS("ip_desc")}
              </p>
              <div className="flex flex-col gap-3">
                <div className="bg-white dark:bg-slate-900/60 p-4 rounded-xl border border-slate-100 dark:border-slate-800">
                  <h4 className="font-bold text-xs text-slate-955 dark:text-white uppercase">
                    {tTOS("ip_badge1")}
                  </h4>
                  <p className="text-xs text-slate-500 mt-1 leading-normal">
                    {tTOS("ip_text1")}
                  </p>
                </div>
                <div className="bg-white dark:bg-slate-900/60 p-4 rounded-xl border border-slate-100 dark:border-slate-800">
                  <h4 className="font-bold text-xs text-slate-955 dark:text-white uppercase">
                    {tTOS("ip_badge2")}
                  </h4>
                  <p className="text-xs text-slate-500 mt-1 leading-normal">
                    {tTOS("ip_text2")}
                  </p>
                </div>
                <div className="bg-white dark:bg-slate-900/60 p-4 rounded-xl border border-slate-100 dark:border-slate-800">
                  <h4 className="font-bold text-xs text-slate-955 dark:text-white uppercase">
                    {tTOS("ip_badge3")}
                  </h4>
                  <p className="text-xs text-slate-500 mt-1 leading-normal">
                    {tTOS("ip_text3")}
                  </p>
                </div>
              </div>
            </div>

            <div>
              <h3 className="font-bold text-slate-955 dark:text-white mb-2">
                {tTOS("redirect_title")}
              </h3>
              <p className="text-slate-600 dark:text-slate-400 mb-3">
                {tTOS("redirect_desc")}
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-white dark:bg-slate-900/60 p-4 rounded-xl border border-slate-100 dark:border-slate-800">
                  <span className="font-bold text-xs text-slate-955 dark:text-white uppercase">
                    {tTOS("redirect_badge1")}
                  </span>
                  <p className="text-xs text-slate-500 mt-1 leading-normal">
                    {tTOS("redirect_text1")}
                  </p>
                </div>
                <div className="bg-white dark:bg-slate-900/60 p-4 rounded-xl border border-slate-100 dark:border-slate-800">
                  <span className="font-bold text-xs text-slate-955 dark:text-white uppercase">
                    {tTOS("redirect_badge2")}
                  </span>
                  <p className="text-xs text-slate-500 mt-1 leading-normal">
                    {tTOS("redirect_text2")}
                  </p>
                </div>
              </div>
            </div>

            <div>
              <h3 className="font-bold text-slate-955 dark:text-white mb-2">
                {tTOS("privacy_title")}
              </h3>
              <p className="text-slate-600 dark:text-slate-400 leading-normal">
                {tTOS("privacy_desc")}
              </p>
            </div>

            <div>
              <h3 className="font-bold text-slate-955 dark:text-white mb-2">
                {tTOS("disclaimer_title")}
              </h3>
              <p className="text-slate-600 dark:text-slate-400 mb-3">
                {tTOS("disclaimer_desc")}
              </p>
              <ul className="flex flex-col gap-2.5">
                {[
                  tTOS("disclaimer_point1"),
                  tTOS("disclaimer_point2"),
                  tTOS("disclaimer_point3"),
                ].map((point, i) => (
                  <li
                    key={i}
                    className="flex gap-2.5 text-xs text-slate-500 dark:text-slate-400 leading-normal text-justify"
                  >
                    <span className="w-1.5 h-1.5 bg-blue-500 rounded-full shrink-0 mt-1.5" />
                    <span>{point}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h3 className="font-bold text-slate-955 dark:text-white mb-2">
                {tTOS("takedown_title")}
              </h3>
              <p className="text-slate-600 dark:text-slate-400 mb-3">
                {tTOS("takedown_desc")}
              </p>
              <ul className="flex flex-col gap-2.5">
                {[tTOS("takedown_point1"), tTOS("takedown_point2")].map(
                  (point, i) => (
                    <li
                      key={i}
                      className="flex gap-2.5 text-xs text-slate-500 dark:text-slate-400 leading-normal text-justify"
                    >
                      <span className="w-1.5 h-1.5 bg-blue-500 rounded-full shrink-0 mt-1.5" />
                      <span>{point}</span>
                    </li>
                  ),
                )}
              </ul>
            </div>
          </div>

          <div className="flex flex-col gap-4 shrink-0">
            <label className="flex items-start gap-4 p-4 rounded-2xl border border-slate-150 dark:border-slate-800 bg-slate-50 dark:bg-slate-955/40 hover:bg-slate-100/50 dark:hover:bg-slate-955/60 transition-all cursor-pointer">
              <div className="relative flex items-center shrink-0 mt-0.5">
                <input
                  type="checkbox"
                  checked={agreeTOS}
                  onChange={(e) => setAgreeTOS(e.target.checked)}
                  className="peer sr-only"
                />
                <div className="w-5.5 h-5.5 rounded-md border-2 border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 peer-checked:bg-blue-600 peer-checked:border-blue-600 flex items-center justify-center transition-all">
                  <Check className="w-3.5 h-3.5 text-white stroke-[3px]" />
                </div>
              </div>
              <span className="text-xs md:text-sm text-slate-655 dark:text-slate-350 leading-relaxed select-none">
                {t("checkbox_tos")}
              </span>
            </label>

            <label className="flex items-start gap-4 p-4 rounded-2xl border border-slate-150 dark:border-slate-800 bg-slate-50 dark:bg-slate-955/40 hover:bg-slate-100/50 dark:hover:bg-slate-955/60 transition-all cursor-pointer">
              <div className="relative flex items-center shrink-0 mt-0.5">
                <input
                  type="checkbox"
                  checked={agreePrivacy}
                  onChange={(e) => setAgreePrivacy(e.target.checked)}
                  className="peer sr-only"
                />
                <div className="w-5.5 h-5.5 rounded-md border-2 border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 peer-checked:bg-blue-600 peer-checked:border-blue-600 flex items-center justify-center transition-all">
                  <Check className="w-3.5 h-3.5 text-white stroke-[3px]" />
                </div>
              </div>
              <span className="text-xs md:text-sm text-slate-655 dark:text-slate-350 leading-relaxed select-none">
                {t("checkbox_privacy")}
              </span>
            </label>
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 mt-2 pt-4 border-t border-slate-150 dark:border-slate-800 shrink-0">
            <Link
              href="/tos"
              className="text-xs font-bold uppercase tracking-wider text-blue-600 dark:text-blue-400 hover:underline animate-pulse"
            >
              {t("view_tos")}
            </Link>

            <button
              disabled={!agreeTOS || !agreePrivacy}
              onClick={handleAccept}
              className="w-full sm:w-auto px-8 py-3.5 rounded-full bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-extrabold uppercase tracking-wider shadow-lg shadow-blue-500/20 transition-all hover:scale-105 active:scale-95 shrink-0 cursor-pointer"
            >
              {t("btn_accept")}
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
