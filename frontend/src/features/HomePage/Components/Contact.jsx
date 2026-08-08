"use client";

import { motion } from "motion/react";
import { Info, ArrowUpRight } from "lucide-react";
import { useTranslations } from "next-intl";
import { FOUNDER_SOCIAL_LINKS } from "@/utils/const";
import { LOGO } from "@/assets/CloudinaryAssetsUrl";
import Image from "next/image";

export default function Contact() {
  const t = useTranslations("Contact");

  return (
    <div className="relative w-full bg-slate-50 dark:bg-slate-950 overflow-hidden min-h-screen flex items-center py-24 px-6 md:px-12">
      <div className="absolute inset-0 bg-[radial-gradient(#e5e7eb_1px,transparent_1px)] dark:bg-[radial-gradient(#1f2937_1px,transparent_1px)] [background-size:40px_40px] opacity-50 z-0" />

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
          rotate: [0, 90, 0],
          scale: [1, 1.2, 1],
        }}
        transition={{ duration: 25, repeat: Infinity, ease: "linear" }}
        className="absolute top-0 right-0 w-[50vw] h-[50vw] bg-blue-500/10 dark:bg-blue-600/10 rounded-full blur-[120px] pointer-events-none -translate-y-1/4 translate-x-1/4 z-0"
      />

      <div className="relative z-10 w-full max-w-7xl mx-auto flex flex-col gap-12">
        <div className="max-w-3xl text-left">
          <motion.h1
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="text-5xl md:text-7xl font-black tracking-tighter uppercase text-slate-900 dark:text-white mb-6"
          >
            {t("hero_title")}{" "}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-500 inline-block py-4">
              {t("hero_subtitle")}
            </span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.1, ease: "easeOut" }}
            className="text-base md:text-lg text-slate-600 dark:text-slate-400 font-medium leading-relaxed text-justify"
          >
            {t("description")}
          </motion.p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 md:gap-8">
          <a
            href={`mailto:${FOUNDER_SOCIAL_LINKS.EMAIL}`}
            className="group relative bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-[2.5rem] p-8 flex flex-col gap-6 shadow-sm hover:shadow-xl hover:border-blue-500/50 transition-all duration-300 overflow-hidden"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
            <div className="w-12 h-12 bg-white rounded-2xl flex items-center justify-center shrink-0 border border-slate-200 dark:border-slate-800">
              <Image
                src={LOGO.GMAIL_LOGO}
                alt="Gmail"
                width={32}
                height={32}
                className="w-7 h-7 object-contain"
              />
            </div>
            <div>
              <span className="block text-xs font-bold text-slate-400 dark:text-slate-505 tracking-widest uppercase mb-2">
                {t("email_label")}
              </span>
              <span className="block text-xl md:text-2xl font-black text-slate-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors break-all leading-snug">
                {FOUNDER_SOCIAL_LINKS.EMAIL}
              </span>
            </div>
            <div className="absolute top-8 right-8 w-10 h-10 rounded-full border border-slate-200 dark:border-slate-700 flex items-center justify-center opacity-0 -translate-y-4 group-hover:opacity-100 group-hover:translate-y-0 transition-all duration-300 bg-white dark:bg-slate-800">
              <ArrowUpRight className="w-5 h-5 text-slate-900 dark:text-white" />
            </div>
          </a>

          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-[2.5rem] p-8 flex flex-col gap-6 shadow-sm overflow-hidden">
            <div className="w-12 h-12 bg-white rounded-2xl flex items-center justify-center shrink-0 border border-slate-200 dark:border-slate-800">
              <Image
                src={LOGO.OUHCMC}
                alt="OUHCMC"
                width={32}
                height={32}
                className="w-7 h-7 object-contain"
              />
            </div>
            <div>
              <span className="block text-xs font-bold text-slate-400 dark:text-slate-550 tracking-widest uppercase mb-2">
                {t("address_title")}
              </span>
              <span className="block text-xl md:text-2xl font-black text-slate-900 dark:text-white leading-snug">
                {t("address_value")}
              </span>
            </div>
          </div>

          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-[2.5rem] p-8 flex flex-col gap-6 shadow-sm overflow-hidden">
            <div>
              <span className="block text-xs font-bold text-slate-400 dark:text-slate-550 tracking-widest uppercase mb-4">
                {t("socials_title")}
              </span>
              <div className="flex flex-col gap-3">
                <a
                  href={FOUNDER_SOCIAL_LINKS.GITHUB}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="group flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-950 rounded-2xl border border-slate-150 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center shrink-0 border border-slate-200">
                      <Image
                        src={LOGO.GITHUB}
                        alt="GitHub"
                        width={24}
                        height={24}
                        className="w-6 h-6 object-contain"
                      />
                    </div>
                    <span className="text-sm font-bold text-slate-800 dark:text-slate-200">
                      {t("social_github")}
                    </span>
                  </div>
                  <ArrowUpRight className="w-5 h-5 text-slate-400 group-hover:text-blue-500 transition-colors shrink-0" />
                </a>

                <a
                  href={FOUNDER_SOCIAL_LINKS.LINKEDIN}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="group flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-955 rounded-2xl border border-slate-150 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center shrink-0 border border-slate-200">
                      <Image
                        src={LOGO.LINKEDIN}
                        alt="LinkedIn"
                        width={24}
                        height={24}
                        className="w-6 h-6 object-contain"
                      />
                    </div>
                    <span className="text-sm font-bold text-slate-800 dark:text-slate-200">
                      {t("social_linkedin")}
                    </span>
                  </div>
                  <ArrowUpRight className="w-5 h-5 text-slate-400 group-hover:text-blue-500 transition-colors shrink-0" />
                </a>
              </div>
            </div>
          </div>

          <div className="lg:col-span-3 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-[2.5rem] p-8 flex flex-col md:flex-row items-start gap-6 shadow-sm overflow-hidden">
            <div className="w-12 h-12 bg-blue-50 dark:bg-blue-900/30 rounded-2xl flex items-center justify-center shrink-0">
              <Info className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div className="flex-1">
              <h4 className="text-lg font-bold text-slate-900 dark:text-white mb-2">
                {t("note_title")}
              </h4>
              <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed text-justify">
                {t("note_desc")}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
