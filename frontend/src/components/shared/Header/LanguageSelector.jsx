"use client";

import React from "react";
import { ChevronDown } from "lucide-react";
import { motion, AnimatePresence } from "motion/react";
import { useTranslations } from "next-intl";

export function LanguageSelector({
  locale,
  langMenuOpen,
  setLangMenuOpen,
  langMenuRef,
  switchLanguage,
}) {
  const t = useTranslations("Header");

  return (
    <div className="relative ml-2" ref={langMenuRef}>
      <button
        onClick={() => setLangMenuOpen(!langMenuOpen)}
        className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-slate-700 dark:text-slate-200 bg-slate-100 dark:bg-slate-800 rounded-lg hover:bg-[#285872]/10 dark:hover:bg-[#285872]/20 transition-colors"
        aria-haspopup="listbox"
        aria-expanded={langMenuOpen}
      >
        {locale === "vi" ? t("lang_vi") : t("lang_en")}
        <ChevronDown className="w-4 h-4 opacity-50" />
      </button>

      <AnimatePresence>
        {langMenuOpen && (
          <motion.div
            initial={{ opacity: 0, y: 10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 10, scale: 0.95 }}
            transition={{ duration: 0.15 }}
            className="absolute right-0 mt-2 w-36 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-lg overflow-hidden z-50"
          >
            <ul role="listbox" className="py-1">
              <li
                role="option"
                aria-selected={locale === "en"}
                onClick={() => switchLanguage("en")}
                className={`px-4 py-2.5 text-sm cursor-pointer transition-colors ${
                  locale === "en"
                    ? "bg-[#285872]/10 dark:bg-[#285872]/20 text-[#285872] dark:text-[#407c9c] font-medium"
                    : "text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800"
                }`}
              >
                {t("lang_en")}
              </li>
              <li
                role="option"
                aria-selected={locale === "vi"}
                onClick={() => switchLanguage("vi")}
                className={`px-4 py-2.5 text-sm cursor-pointer transition-colors ${
                  locale === "vi"
                    ? "bg-[#285872]/10 dark:bg-[#285872]/20 text-[#285872] dark:text-[#407c9c] font-medium"
                    : "text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800"
                }`}
              >
                {t("lang_vi")}
              </li>
            </ul>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
