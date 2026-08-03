"use client";

import { motion, AnimatePresence } from "motion/react";
import { Menu, X, Bot, ChevronDown } from "lucide-react";
import { Button, buttonVariants } from "@/components/ui/button";
import { Link } from "@/i18n/routing";
import { useHeader } from "@/components/shared/hooks/useHeader";
import { useAuth } from "@/context/AuthProvider";
import { cn } from "@/lib/utils";

export default function Header() {
  const { isAuthenticated, user } = useAuth();
  const {
    t,
    locale,
    isScrolled,
    mobileMenuOpen,
    setMobileMenuOpen,
    langMenuOpen,
    setLangMenuOpen,
    langMenuRef,
    navLinks,
    switchLanguage,
    pathname,
  } = useHeader();

  return (
    <motion.header
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ type: "spring", stiffness: 300, damping: 30 }}
      className={`fixed top-0 left-0 right-0 z-50 transition-colors duration-300 ${
        isScrolled
          ? "bg-white/80 dark:bg-slate-950/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 shadow-sm"
          : "bg-transparent"
      }`}
    >
      <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2 group">
          <motion.div
            whileHover={{ rotate: 10 }}
            whileTap={{ scale: 0.95 }}
            className="w-10 h-10 bg-blue-600 dark:bg-blue-500 rounded-xl flex items-center justify-center text-white"
          >
            <Bot className="w-6 h-6" />
          </motion.div>
          <span className="text-xl font-bold text-slate-900 dark:text-white tracking-tight">
            AIJMC
          </span>
        </Link>

        <nav className="hidden md:flex items-center gap-8">
          {navLinks.map((link) => {
            const isActive = pathname === link.href;

            return (
              <Link
                key={link.name}
                href={link.href}
                className={`text-sm font-medium transition-colors relative group ${
                  isActive
                    ? "text-blue-600 dark:text-blue-400"
                    : "text-slate-600 dark:text-slate-300 hover:text-blue-600 dark:hover:text-blue-400"
                }`}
              >
                {link.name}
                <motion.span
                  className={`absolute -bottom-1 left-0 h-0.5 bg-blue-600 dark:bg-blue-400 transition-all ${
                    isActive ? "w-full" : "w-0 group-hover:w-full"
                  }`}
                />
              </Link>
            );
          })}
        </nav>

        <div className="hidden md:flex items-center gap-2">
          <Link
            href={isAuthenticated ? "/counselee/overview" : "/counselee/login"}
            className={cn(
              buttonVariants({ variant: "ghost" }),
              "text-slate-900 dark:text-white font-bold",
            )}
          >
            {isAuthenticated ? user?.username || "Dashboard" : t("login")}
          </Link>
          <Link
            href={isAuthenticated ? "/counselee/overview" : "/counselee/login"}
            className={cn(
              buttonVariants({ variant: "default" }),
              "bg-blue-600 hover:bg-blue-700 text-white rounded-full px-6",
            )}
          >
            {isAuthenticated ? "Market Dashboard" : t("get_started")}
          </Link>

          <div className="relative ml-2" ref={langMenuRef}>
            <button
              onClick={() => setLangMenuOpen(!langMenuOpen)}
              className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-slate-700 dark:text-slate-200 bg-slate-100 dark:bg-slate-800 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900 transition-colors"
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
                          ? "bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 font-medium"
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
                          ? "bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 font-medium"
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
        </div>

        <button
          className="md:hidden p-2 text-slate-900 dark:text-white"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          aria-label="Toggle menu"
        >
          {mobileMenuOpen ? (
            <X className="w-6 h-6" />
          ) : (
            <Menu className="w-6 h-6" />
          )}
        </button>
      </div>

      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden bg-white dark:bg-slate-950 border-b border-slate-200 dark:border-slate-800 overflow-hidden"
          >
            <div className="flex flex-col px-6 py-4 gap-3">
              {navLinks.map((link) => {
                const isActive = pathname === link.href;
                return (
                  <Link
                    key={link.name}
                    href={link.href}
                    className={`text-lg font-medium transition-colors ${
                      isActive
                        ? "text-blue-600 dark:text-blue-400"
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
                      ? "border-blue-600 text-blue-600 bg-blue-50 dark:bg-blue-900/20"
                      : "border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300"
                  }`}
                >
                  {t("lang_en")}
                </button>
                <button
                  onClick={() => switchLanguage("vi")}
                  className={`flex-1 py-2 text-sm rounded-lg border ${
                    locale === "vi"
                      ? "border-blue-600 text-blue-600 bg-blue-50 dark:bg-blue-900/20"
                      : "border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300"
                  }`}
                >
                  {t("lang_vi")}
                </button>
              </div>

              <div className="h-px bg-slate-200 dark:bg-slate-800 my-2" />
              <div className="flex flex-col gap-3">
                <Link
                  href={
                    isAuthenticated ? "/counselee/overview" : "/counselee/login"
                  }
                  onClick={() => setMobileMenuOpen(false)}
                  className={cn(
                    buttonVariants({ variant: "outline" }),
                    "w-full justify-center",
                  )}
                >
                  {isAuthenticated ? user?.username || "Dashboard" : t("login")}
                </Link>
                <Link
                  href={
                    isAuthenticated ? "/counselee/overview" : "/counselee/login"
                  }
                  onClick={() => setMobileMenuOpen(false)}
                  className={cn(
                    buttonVariants({ variant: "default" }),
                    "w-full justify-center bg-blue-600 hover:bg-blue-700 text-white",
                  )}
                >
                  {isAuthenticated ? "Market Dashboard" : t("get_started")}
                </Link>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.header>
  );
}
