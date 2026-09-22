"use client";

import { motion } from "motion/react";
import { ArrowUpRight } from "lucide-react";
import { useTranslations } from "next-intl";
import { FOUNDER_SOCIAL_LINKS } from "@/utils/const";
import { LOGO } from "@/assets/CloudinaryAssetsUrl";
import Image from "next/image";

export default function Contact() {
  const t = useTranslations("Contact");

  return (
    <div className="relative w-full bg-slate-50 dark:bg-slate-950 min-h-screen flex items-center py-24 px-6 md:px-12">
      <div className="relative z-10 w-full max-w-7xl mx-auto flex flex-col gap-12">
        <div className="w-full text-center flex flex-col items-center">
          <motion.h1
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="text-4xl md:text-6xl font-black tracking-tighter uppercase text-slate-900 dark:text-white mb-6"
          >
            {t("hero_title")}{" "}
            <span className="text-[#285872] dark:text-sky-400 inline-block py-2">
              {t("hero_subtitle")}
            </span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.1, ease: "easeOut" }}
            className="w-full lg:w-4/5 text-base md:text-lg text-slate-600 dark:text-slate-400 font-medium leading-relaxed text-center"
          >
            {t("description")}
          </motion.p>
        </div>

        <div className="flex flex-col divide-y divide-slate-200 dark:divide-slate-800 border-t border-b border-slate-200 dark:border-slate-800">
          <a
            href={`mailto:${FOUNDER_SOCIAL_LINKS.EMAIL}`}
            className="group py-8 flex flex-col sm:flex-row sm:items-center justify-between gap-6 text-left transition-colors"
          >
            <div className="flex items-start sm:items-center gap-6">
              <div className="w-14 h-14 bg-white rounded-xl flex items-center justify-center shrink-0 border border-slate-200 dark:border-slate-800 shadow-sm group-hover:scale-105 transition-transform duration-300">
                <Image
                  src={LOGO.GMAIL_LOGO}
                  alt="Gmail"
                  width={32}
                  height={32}
                  className="w-7 h-7 object-contain"
                />
              </div>
              <div>
                <span className="block text-xs font-bold text-slate-400 dark:text-slate-500 tracking-widest uppercase mb-1">
                  {t("email_label")}
                </span>
                <span className="text-lg md:text-xl font-bold text-slate-900 dark:text-white group-hover:text-[#285872] dark:group-hover:text-sky-400 transition-colors break-all">
                  {FOUNDER_SOCIAL_LINKS.EMAIL}
                </span>
              </div>
            </div>
            <div className="flex items-center gap-2 text-sm font-semibold text-slate-400 group-hover:text-[#285872] dark:group-hover:text-sky-400 transition-colors self-end sm:self-center">
              <span>{t("email_label")}</span>
              <ArrowUpRight className="w-5 h-5 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
            </div>
          </a>

          <div className="py-8 flex flex-col sm:flex-row sm:items-center justify-between gap-6 text-left">
            <div className="flex items-start sm:items-center gap-6">
              <div className="w-14 h-14 bg-white rounded-xl flex items-center justify-center shrink-0 border border-slate-200 dark:border-slate-800 shadow-sm">
                <Image
                  src={LOGO.OUHCMC}
                  alt="OUHCMC"
                  width={32}
                  height={32}
                  className="w-7 h-7 object-contain"
                />
              </div>
              <div>
                <span className="block text-xs font-bold text-slate-400 dark:text-slate-500 tracking-widest uppercase mb-1">
                  {t("address_title")}
                </span>
                <span className="text-lg md:text-xl font-bold text-slate-900 dark:text-white leading-snug">
                  {t("address_value")}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
