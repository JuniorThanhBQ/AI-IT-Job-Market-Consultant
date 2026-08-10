"use client";

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "motion/react";
import { Menu, X, ChevronDown } from "lucide-react";
import { Button, buttonVariants } from "@/components/ui/button";
import { Link } from "@/i18n/routing";
import { useHeader } from "@/components/shared/hooks/useHeader";
import { useAuth } from "@/context/AuthProvider";
import { cn } from "@/lib/utils";
import Image from "next/image";
import { LOGO } from "@/assets/CloudinaryAssetsUrl";
import ChatbotPopup from "@/components/shared/ChatbotPopup";

export default function Header() {
  const { isAuthenticated, user, logout } = useAuth();
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

  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const userMenuRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target)) {
        setUserMenuOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const getHeaderCTA = () => {
    if (!isAuthenticated) {
      return {
        label: t("get_started"),
        href: "/counselee/login",
      };
    }
    if (pathname.includes("/counselee/jobs")) {
      return {
        label: t("cta_overview"),
        href: "/counselee/overview",
      };
    }
    if (pathname.includes("/counselee/jobs")) {
      return {
        label: t("cta_dashboard"),
        href: "/counselee/overview",
      };
    }
    return {
      label: t("cta_dashboard"),
      href: "/counselee/jobs",
    };
  };

  const cta = getHeaderCTA();

  return (
    <>
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
          <Link
            href={isAuthenticated ? "/counselee/overview" : "/"}
            className="flex items-center gap-2 group"
          >
            <Image
              src={LOGO.AIJMC_LOGO}
              alt="AIJMC Logo"
              width={320}
              height={320}
              className="h-44 w-auto object-contain"
              loading="eager"
            />
          </Link>

          <nav className="hidden md:flex items-center gap-8">
            {!isAuthenticated &&
              navLinks.map((link) => {
                const isActive = pathname === link.href;

                return (
                  <Link
                    key={link.name}
                    href={link.href}
                    className={`text-sm font-medium transition-colors relative group ${
                      isActive
                        ? "text-[#285872] dark:text-[#407c9c]"
                        : "text-slate-600 dark:text-slate-300 hover:text-[#285872] dark:hover:text-[#407c9c]"
                    }`}
                  >
                    {link.name}
                    <motion.span
                      className={`absolute -bottom-1 left-0 h-0.5 bg-[#285872] dark:bg-[#407c9c] transition-all ${
                        isActive ? "w-full" : "w-0 group-hover:w-full"
                      }`}
                    />
                  </Link>
                );
              })}
          </nav>

          <div className="hidden md:flex items-center gap-2">
            {isAuthenticated ? (
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
            ) : (
              <Link
                href="/counselee/login"
                className={cn(
                  buttonVariants({ variant: "ghost" }),
                  "text-slate-900 dark:text-white font-bold",
                )}
              >
                {t("login")}
              </Link>
            )}

            <Link
              href={cta.href}
              className={cn(
                buttonVariants({ variant: "default" }),
                "bg-[#285872] hover:bg-[#1c3f52] text-white rounded-full px-6",
              )}
            >
              {cta.label}
            </Link>

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
                    <Link
                      href="/counselee/login"
                      onClick={() => setMobileMenuOpen(false)}
                      className={cn(
                        buttonVariants({ variant: "outline" }),
                        "w-full justify-center",
                      )}
                    >
                      {t("login")}
                    </Link>
                  )}
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
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.header>
      {isAuthenticated && pathname.includes("/counselee/") && <ChatbotPopup />}
    </>
  );
}
