"use client";

import { useState, useEffect, useRef } from "react";
import { useTranslations, useLocale } from "next-intl";
import { usePathname, useRouter } from "@/i18n/routing";

export function useHeader() {
  const t = useTranslations("Header");
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();

  const [isScrolled, setIsScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [langMenuOpen, setLangMenuOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const langMenuRef = useRef(null);
  const userMenuRef = useRef(null);

  const navLinks = [
    { name: t("nav_aijmc"), href: "/aijmc" },
    { name: t("nav_founder"), href: "/aijmc/founder-inspiration" },
    { name: t("nav_faq"), href: "/aijmc/faq" },
    { name: t("nav_contact"), href: "/aijmc/contact" },
  ];

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 20);
    handleScroll();
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (langMenuRef.current && !langMenuRef.current.contains(event.target)) {
        setLangMenuOpen(false);
      }
      if (userMenuRef.current && !userMenuRef.current.contains(event.target)) {
        setUserMenuOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const switchLanguage = (newLocale) => {
    router.replace(pathname, { locale: newLocale });
    setLangMenuOpen(false);
  };

  return {
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
  };
}
