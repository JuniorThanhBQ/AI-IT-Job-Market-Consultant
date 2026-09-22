"use client";

import React from "react";
import Image from "next/image";
import ChatbotPopup from "@/components/shared/ChatbotPopup";
import { motion } from "motion/react";
import { Menu, X } from "lucide-react";
import { buttonVariants } from "@/components/ui/button";
import { Link } from "@/i18n/routing";
import { useHeader } from "@/components/shared/hooks/useHeader";
import { useAuth } from "@/context/AuthProvider";
import { cn } from "@/lib/utils";
import { LOGO } from "@/assets/CloudinaryAssetsUrl";
import { UserMenu } from "./Header/UserMenu";
import { LanguageSelector } from "./Header/LanguageSelector";
import { MobileMenu } from "./Header/MobileMenu";
import { getHeaderCTA } from "@/utils/navigation";

export default function Header() {
  const {
    t,
    locale,
    isScrolled,
    mobileMenuOpen,
    setMobileMenuOpen,
    langMenuOpen,
    setLangMenuOpen,
    langMenuRef,
    userMenuOpen,
    setUserMenuOpen,
    userMenuRef,
    navLinks,
    switchLanguage,
    pathname,
  } = useHeader();
  const { user, isAuthenticated, logout } = useAuth();
  const cta = getHeaderCTA(isAuthenticated, pathname, t);

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
              <UserMenu
                user={user}
                userMenuOpen={userMenuOpen}
                setUserMenuOpen={setUserMenuOpen}
                userMenuRef={userMenuRef}
                logout={logout}
              />
            ) : (
              <Link
                href="/counselee/auth"
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

            <LanguageSelector
              locale={locale}
              langMenuOpen={langMenuOpen}
              setLangMenuOpen={setLangMenuOpen}
              langMenuRef={langMenuRef}
              switchLanguage={switchLanguage}
            />
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

        <MobileMenu
          mobileMenuOpen={mobileMenuOpen}
          setMobileMenuOpen={setMobileMenuOpen}
          navLinks={navLinks}
          pathname={pathname}
          locale={locale}
          switchLanguage={switchLanguage}
          isAuthenticated={isAuthenticated}
          cta={cta}
          logout={logout}
        />
      </motion.header>
      {isAuthenticated &&
        pathname.includes("/counselee/") &&
        !pathname.includes("/counselee/chatbot") && <ChatbotPopup />}
    </>
  );
}
