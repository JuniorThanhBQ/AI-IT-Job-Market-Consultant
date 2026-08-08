"use client";

import { useRef } from "react";
import { useTranslations } from "next-intl";
import { Link } from "@/i18n/routing";
import { motion } from "motion/react";

export default function TOSPage() {
  const t = useTranslations("TOS");

  const introRef = useRef(null);
  const ipRef = useRef(null);
  const redirectRef = useRef(null);
  const privacyRef = useRef(null);
  const disclaimerRef = useRef(null);
  const takedownRef = useRef(null);

  const scrollToSection = (sectionKey) => {
    const refs = {
      intro: introRef,
      ip: ipRef,
      redirect: redirectRef,
      privacy: privacyRef,
      disclaimer: disclaimerRef,
      takedown: takedownRef,
    };
    refs[sectionKey].current?.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  };

  const navItems = [
    { key: "intro", label: t("intro_title").split(". ")[1] },
    { key: "ip", label: t("ip_title").split(". ")[1] },
    { key: "redirect", label: t("redirect_title").split(". ")[1] },
    { key: "privacy", label: t("privacy_title").split(". ")[1] },
    { key: "disclaimer", label: t("disclaimer_title").split(". ")[1] },
    { key: "takedown", label: t("takedown_title").split(". ")[1] },
  ];

  return (
    <div className="relative min-h-screen bg-slate-50 dark:bg-slate-955 text-slate-900 dark:text-slate-100 flex flex-col font-sans transition-colors duration-300">
      <div className="absolute inset-0 overflow-hidden pointer-events-none z-0">
        <div className="pointer-events-none absolute inset-0 opacity-[0.03] dark:opacity-[0.05] mix-blend-overlay">
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
            x: [0, 30, -20, 0],
            y: [0, -40, 30, 0],
            scale: [1, 1.1, 0.95, 1],
          }}
          transition={{ duration: 25, repeat: Infinity, ease: "easeInOut" }}
          className="absolute top-0 right-0 w-[50vw] h-[50vw] bg-blue-500/10 dark:bg-blue-600/15 rounded-full blur-[130px]"
        />
        <motion.div
          animate={{
            x: [0, -30, 20, 0],
            y: [0, 30, -20, 0],
            scale: [1, 1.05, 0.9, 1],
          }}
          transition={{ duration: 30, repeat: Infinity, ease: "easeInOut" }}
          className="absolute bottom-0 left-0 w-[45vw] h-[45vw] bg-purple-500/10 dark:bg-purple-600/15 rounded-full blur-[130px]"
        />
      </div>

      <header className="relative z-10 border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-955/80 backdrop-blur-md shrink-0">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <Link
            href="/"
            className="flex items-center gap-2 text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors text-sm font-bold uppercase tracking-wider"
          >
            {t("backHome")}
          </Link>
          <div className="flex items-center gap-2 text-xs font-semibold text-slate-400">
            <span>{t("lastUpdated")}</span>
          </div>
        </div>
      </header>

      <main className="relative z-10 flex-1 max-w-7xl w-full mx-auto px-6 py-12 flex flex-col lg:flex-row gap-8 min-h-0">
        <aside className="lg:w-80 shrink-0">
          <div className="lg:sticky lg:top-28 bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-6 backdrop-blur-md flex flex-col gap-4 shadow-sm">
            <h2 className="text-xs font-bold text-slate-400 dark:text-slate-505 uppercase tracking-widest">
              Navigation
            </h2>
            <nav className="flex flex-col gap-2">
              {navItems.map((item) => (
                <button
                  key={item.key}
                  onClick={() => scrollToSection(item.key)}
                  className="text-left py-2 px-3 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-850 text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 transition-all text-xs font-bold uppercase tracking-wider cursor-pointer"
                >
                  {item.label}
                </button>
              ))}
            </nav>
          </div>
        </aside>

        <section className="flex-1 flex flex-col gap-8">
          <div className="mb-4">
            <h1 className="text-4xl md:text-5xl font-black tracking-tight text-slate-900 dark:text-white mb-3">
              {t("title")}
            </h1>
            <p className="text-base text-slate-500 dark:text-slate-400 font-medium">
              {t("subtitle")} <br></br> {t("hostOrg")}
            </p>
          </div>

          <div
            ref={introRef}
            className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-8 backdrop-blur-md shadow-sm flex flex-col gap-6"
          >
            <h2 className="text-xl font-bold text-slate-900 dark:text-white">
              {t("intro_title")}
            </h2>
            <p className="text-sm md:text-base text-slate-600 dark:text-slate-350 leading-relaxed text-justify">
              {t("intro_desc")}
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-slate-50 dark:bg-slate-955 p-6 rounded-2xl border border-slate-100 dark:border-slate-900">
                <span className="inline-block px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-455 mb-3">
                  {t("intro_badge1")}
                </span>
                <p className="text-xs md:text-sm text-slate-505 dark:text-slate-400 leading-relaxed text-justify">
                  {t("intro_text1")}
                </p>
              </div>
              <div className="bg-slate-50 dark:bg-slate-955 p-6 rounded-2xl border border-slate-100 dark:border-slate-900">
                <span className="inline-block px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-455 mb-3">
                  {t("intro_badge2")}
                </span>
                <p className="text-xs md:text-sm text-slate-505 dark:text-slate-400 leading-relaxed text-justify">
                  {t("intro_text2")}
                </p>
              </div>
            </div>
          </div>

          <div
            ref={ipRef}
            className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-8 backdrop-blur-md shadow-sm flex flex-col gap-6"
          >
            <h2 className="text-xl font-bold text-slate-900 dark:text-white">
              {t("ip_title")}
            </h2>
            <p className="text-sm md:text-base text-slate-600 dark:text-slate-350 leading-relaxed text-justify">
              {t("ip_desc")}
            </p>
            <div className="flex flex-col gap-4">
              <div className="bg-slate-50 dark:bg-slate-955 p-6 rounded-2xl border border-slate-100 dark:border-slate-900">
                <h4 className="text-sm font-bold text-slate-950 dark:text-white mb-2 uppercase tracking-wide">
                  {t("ip_badge1")}
                </h4>
                <p className="text-xs md:text-sm text-slate-505 dark:text-slate-400 leading-relaxed text-justify">
                  {t("ip_text1")}
                </p>
              </div>
              <div className="bg-slate-50 dark:bg-slate-955 p-6 rounded-2xl border border-slate-100 dark:border-slate-900">
                <h4 className="text-sm font-bold text-slate-955 dark:text-white mb-2 uppercase tracking-wide">
                  {t("ip_badge2")}
                </h4>
                <p className="text-xs md:text-sm text-slate-505 dark:text-slate-400 leading-relaxed text-justify">
                  {t("ip_text2")}
                </p>
              </div>
              <div className="bg-slate-50 dark:bg-slate-955 p-6 rounded-2xl border border-slate-100 dark:border-slate-900">
                <h4 className="text-sm font-bold text-slate-955 dark:text-white mb-2 uppercase tracking-wide">
                  {t("ip_badge3")}
                </h4>
                <p className="text-xs md:text-sm text-slate-505 dark:text-slate-400 leading-relaxed text-justify">
                  {t("ip_text3")}
                </p>
              </div>
            </div>
          </div>

          <div
            ref={redirectRef}
            className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-8 backdrop-blur-md shadow-sm flex flex-col gap-6"
          >
            <h2 className="text-xl font-bold text-slate-900 dark:text-white">
              {t("redirect_title")}
            </h2>
            <p className="text-sm md:text-base text-slate-600 dark:text-slate-350 leading-relaxed text-justify">
              {t("redirect_desc")}
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-slate-50 dark:bg-slate-955 p-6 rounded-2xl border border-slate-100 dark:border-slate-900">
                <h4 className="text-sm font-bold text-slate-955 dark:text-white mb-2 uppercase tracking-wide">
                  {t("redirect_badge1")}
                </h4>
                <p className="text-xs md:text-sm text-slate-505 dark:text-slate-400 leading-relaxed text-justify">
                  {t("redirect_text1")}
                </p>
              </div>
              <div className="bg-slate-50 dark:bg-slate-955 p-6 rounded-2xl border border-slate-100 dark:border-slate-900">
                <h4 className="text-sm font-bold text-slate-955 dark:text-white mb-2 uppercase tracking-wide">
                  {t("redirect_badge2")}
                </h4>
                <p className="text-xs md:text-sm text-slate-505 dark:text-slate-400 leading-relaxed text-justify">
                  {t("redirect_text2")}
                </p>
              </div>
            </div>
          </div>

          <div
            ref={privacyRef}
            className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-8 backdrop-blur-md shadow-sm flex flex-col gap-6"
          >
            <h2 className="text-xl font-bold text-slate-900 dark:text-white">
              {t("privacy_title")}
            </h2>
            <p className="text-sm md:text-base text-slate-600 dark:text-slate-350 leading-relaxed text-justify">
              {t("privacy_desc")}
            </p>
          </div>

          <div
            ref={disclaimerRef}
            className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-8 backdrop-blur-md shadow-sm flex flex-col gap-6"
          >
            <h2 className="text-xl font-bold text-slate-900 dark:text-white">
              {t("disclaimer_title")}
            </h2>
            <p className="text-sm md:text-base text-slate-655 dark:text-slate-350 leading-relaxed mb-2">
              {t("disclaimer_desc")}
            </p>
            <ul className="flex flex-col gap-3">
              {[
                t("disclaimer_point1"),
                t("disclaimer_point2"),
                t("disclaimer_point3"),
              ].map((point, i) => (
                <li
                  key={i}
                  className="flex gap-3 text-xs md:text-sm text-slate-500 dark:text-slate-400 leading-relaxed text-justify"
                >
                  <span className="w-1.5 h-1.5 bg-blue-500 rounded-full shrink-0 mt-2" />
                  <span>{point}</span>
                </li>
              ))}
            </ul>
          </div>

          <div
            ref={takedownRef}
            className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-8 backdrop-blur-md shadow-sm flex flex-col gap-6 mb-12"
          >
            <h2 className="text-xl font-bold text-slate-900 dark:text-white">
              {t("takedown_title")}
            </h2>
            <p className="text-sm md:text-base text-slate-600 dark:text-slate-350 leading-relaxed text-justify">
              {t("takedown_desc")}
            </p>
            <ul className="flex flex-col gap-3 border-b border-slate-100 dark:border-slate-900 pb-6">
              {[t("takedown_point1"), t("takedown_point2")].map((point, i) => (
                <li
                  key={i}
                  className="flex gap-3 text-xs md:text-sm text-slate-500 dark:text-slate-400 leading-relaxed text-justify"
                >
                  <span className="w-1.5 h-1.5 bg-blue-500 rounded-full shrink-0 mt-2" />
                  <span>{point}</span>
                </li>
              ))}
            </ul>
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 mt-2 bg-slate-50 dark:bg-slate-955 p-6 rounded-2xl border border-slate-100 dark:border-slate-900">
              <div className="flex items-center gap-3">
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 dark:text-slate-505 leading-tight">
                    {t("supportEmail")}
                  </h4>
                  <p className="text-sm font-extrabold text-slate-800 dark:text-white leading-normal mt-0.5 select-all">
                    2351050164thanh@ou.edu.vn
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
