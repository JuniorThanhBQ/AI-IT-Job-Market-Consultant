"use client";

import React from "react";
import { Link } from "@/i18n/routing";
import { motion, AnimatePresence } from "motion/react";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useTranslations } from "next-intl";

export function MobileMenu({
  mobileMenuOpen,
  setMobileMenuOpen,
  navLinks,
  pathname,
  locale,
  switchLanguage,
  isAuthenticated,
  cta,
  logout,
}) {
  const t = useTranslations("Header");

  return (
    <AnimatePresence>
      {mobileMenuOpen && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
          exit={{ opacity: 0, height: 0 }}
          className="md:hidden bg-white dark:bg-slate-950 border-b border-slate-200 dark:border-slate-800 overflow-hidden"
        >
          <div className="flex flex-col px-6 py-4 gap-3">
            {!isAuthenticated &&
              navLinks.map((link) => {
                const isActive = pathname === link.href;
                return (
                  <Link
                    key={link.name}
                    href={link.href}
                    className={`text-lg font-medium transition-colors ${
                      isActive
                        ? "text-[#285872] dark:text-[#407c9c]"
                        : "text-slate-900 dark:text-white"
                    }`}
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    {link.name}
                  </Link>
                );
              })}

            <div className="flex gap-4 pt-2">
              <button
                onClick={() => switchLanguage("en")}
                className={`flex-1 py-2 text-sm rounded-lg border ${
                  locale === "en"
                    ? "border-[#285872] text-[#285872] bg-[#285872]/10 dark:bg-[#285872]/20"
                    : "border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300"
                }`}
              >
                {t("lang_en")}
              </button>
              <button
                onClick={() => switchLanguage("vi")}
                className={`flex-1 py-2 text-sm rounded-lg border ${
                  locale === "vi"
                    ? "border-[#285872] text-[#285872] bg-[#285872]/10 dark:bg-[#285872]/20"
                    : "border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300"
                }`}
              >
                {t("lang_vi")}
              </button>
            </div>

            <div className="h-px bg-slate-200 dark:bg-slate-800 my-2" />
            <div className="flex flex-col gap-3">
              {isAuthenticated ? (
                <>
                  <Link
                    href="/counselee/overview"
                    onClick={() => setMobileMenuOpen(false)}
                    className={cn(
                      buttonVariants({ variant: "outline" }),
                      "w-full justify-center",
                    )}
                  >
                    {t("overview")}
                  </Link>
                  <Link
                    href="/counselee/profile"
                    onClick={() => setMobileMenuOpen(false)}
                    className={cn(
                      buttonVariants({ variant: "outline" }),
                      "w-full justify-center",
                    )}
                  >
                    {t("my_profile")}
                  </Link>
                  <Link
                    href={cta.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className={cn(
                      buttonVariants({ variant: "default" }),
                      "w-full justify-center bg-[#285872] hover:bg-[#1c3f52] text-white",
                    )}
                  >
                    {cta.label}
                  </Link>
                  <button
                    onClick={() => {
                      setMobileMenuOpen(false);
                      logout();
                    }}
                    className={cn(
                      buttonVariants({ variant: "ghost" }),
                      "w-full justify-center text-red-655 dark:text-red-400 font-bold cursor-pointer",
                    )}
                  >
                    {t("logout")}
                  </button>
                </>
              ) : (
                <>
                  <Link
                    href="/counselee/auth"
                    onClick={() => setMobileMenuOpen(false)}
                    className={cn(
                      buttonVariants({ variant: "outline" }),
                      "w-full justify-center",
                    )}
                  >
                    {t("login")}
                  </Link>
                  <Link
                    href={cta.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className={cn(
                      buttonVariants({ variant: "default" }),
                      "w-full justify-center bg-[#285872] hover:bg-[#1c3f52] text-white",
                    )}
                  >
                    {cta.label}
                  </Link>
                </>
              )}
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
