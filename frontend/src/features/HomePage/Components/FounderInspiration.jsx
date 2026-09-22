"use client";

import { motion } from "motion/react";
import { Mail } from "lucide-react";
import { useTranslations } from "next-intl";
import { FOUNDER_SOCIAL_LINKS, LINKS } from "@/utils/const";
import { LOGO } from "@/assets/CloudinaryAssetsUrl";
import Image from "next/image";

export default function FounderInspiration() {
  const t = useTranslations("FounderInspiration");

  return (
    <div className="relative w-full bg-slate-50 dark:bg-slate-950 overflow-hidden">
      <section
        id="founder"
        className="relative min-h-screen flex items-center pt-32 pb-20 px-6 md:px-12 bg-slate-50 dark:bg-slate-950"
      >
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:32px_32px] z-0" />
        <div className="relative z-10 w-full max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-center">
          <div className="lg:col-span-7 flex flex-col items-start text-left w-full">
            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.1, ease: "easeOut" }}
              className="text-2xl md:text-3xl text-slate-500 dark:text-slate-400 font-medium mb-2"
            >
              {t("greeting")}
            </motion.h2>

            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2, ease: "easeOut" }}
              className="text-4xl md:text-5xl lg:text-6xl leading-[1.1] font-black tracking-tighter text-slate-900 dark:text-white uppercase mb-6"
            >
              {t("name")}
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.3, ease: "easeOut" }}
              className="text-lg md:text-xl text-slate-600 dark:text-slate-400 leading-relaxed max-w-2xl mb-10 text-justify"
            >
              {t("bio_1")}
              <a href={LINKS.OUHCMC} target="_blank" rel="noopener noreferrer">
                <span className="font-bold text-[#285872] dark:text-sky-400 hover:underline">
                  {" "}
                  {t("bio_school")}{" "}
                </span>
              </a>
              {t("bio_2")}
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4, ease: "easeOut" }}
              className="flex items-center gap-4"
            >
              <a
                href={FOUNDER_SOCIAL_LINKS.GITHUB}
                target="_blank"
                rel="noopener noreferrer"
                className="w-14 h-14 flex items-center justify-center bg-white border border-slate-200 shadow-sm rounded-2xl hover:scale-105 hover:shadow-lg transition-all duration-300"
              >
                <Image
                  src={LOGO.GITHUB}
                  alt="GitHub"
                  width={56}
                  height={56}
                  className="w-7 h-7 object-contain"
                />
              </a>
              <a
                href={FOUNDER_SOCIAL_LINKS.LINKEDIN}
                target="_blank"
                rel="noopener noreferrer"
                className="w-14 h-14 flex items-center justify-center bg-white border border-slate-200 shadow-sm rounded-2xl hover:scale-105 hover:shadow-lg transition-all duration-300"
              >
                <Image
                  src={LOGO.LINKEDIN}
                  alt="LinkedIn"
                  width={56}
                  height={56}
                  className="w-7 h-7 object-contain"
                />
              </a>
              <a
                href={`mailto:${FOUNDER_SOCIAL_LINKS.EMAIL}`}
                className="w-14 h-14 flex items-center justify-center bg-white dark:bg-slate-900 text-slate-900 dark:text-white border border-slate-200 dark:border-slate-800 shadow-sm rounded-2xl hover:scale-105 hover:shadow-lg transition-all duration-300"
              >
                <Mail className="w-6 h-6" />
              </a>
            </motion.div>
          </div>

          <motion.div
            initial={{ opacity: 0, scale: 0.8, rotate: -5 }}
            animate={{ opacity: 1, scale: 1, rotate: 0 }}
            transition={{ duration: 1, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
            className="hidden lg:block lg:col-span-5 relative w-full aspect-[4/5] md:aspect-square lg:aspect-[4/5] rounded-[3rem] overflow-hidden shadow-2xl border border-slate-200 dark:border-slate-800"
          >
            <Image
              src={LOGO.FOUNDER_AVATAR}
              alt={t("name")}
              fill
              priority
              sizes="160px"
              className="object-cover object-center"
            />
          </motion.div>
        </div>
      </section>
    </div>
  );
}
