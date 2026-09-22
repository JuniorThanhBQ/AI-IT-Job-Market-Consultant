"use client";

import React from "react";
import { Link } from "@/i18n/routing";
import { ChevronDown } from "lucide-react";
import { motion, AnimatePresence } from "motion/react";
import { useTranslations } from "next-intl";

export function UserMenu({
  user,
  userMenuOpen,
  setUserMenuOpen,
  userMenuRef,
  logout,
}) {
  const t = useTranslations("Header");

  return (
    <div className="relative" ref={userMenuRef}>
      <button
        onClick={() => setUserMenuOpen(!userMenuOpen)}
        className="flex items-center gap-1.5 px-3 py-2 text-sm font-bold text-slate-900 dark:text-white hover:opacity-80 transition-opacity cursor-pointer"
      >
        {user?.last_name} {user?.first_name || "Counselee"}
        <ChevronDown className="w-4 h-4 opacity-50" />
      </button>

      <AnimatePresence>
        {userMenuOpen && (
          <motion.div
            initial={{ opacity: 0, y: 10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 10, scale: 0.95 }}
            transition={{ duration: 0.15 }}
            className="absolute right-0 mt-2 w-48 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-lg overflow-hidden z-50"
          >
            <div className="py-1">
              <Link
                href="/counselee/overview"
                onClick={() => setUserMenuOpen(false)}
                className="block px-4 py-2.5 text-sm text-slate-700 dark:text-slate-350 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
              >
                {t("overview")}
              </Link>
              <Link
                href="/counselee/profile"
                onClick={() => setUserMenuOpen(false)}
                className="block px-4 py-2.5 text-sm text-slate-700 dark:text-slate-350 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
              >
                {t("my_profile")}
              </Link>

              <button
                onClick={() => {
                  setUserMenuOpen(false);
                  logout();
                }}
                className="w-full text-left block px-4 py-2.5 text-sm text-red-655 dark:text-red-400 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors cursor-pointer"
              >
                {t("logout")}
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
