"use client";

import { useRef } from "react";
import { motion, useScroll, useTransform } from "motion/react";
import { BrainCircuit, TrendingUp, FileUser } from "lucide-react";
import { useTranslations } from "next-intl";
import Image from "next/image";
import { getPlatformsList, getFeaturesList } from "@/utils/homepage_utils";

export default function Introduction() {
  const t = useTranslations("Introduction");
  const platformsList = getPlatformsList(t);
  const featuresList = getFeaturesList(t, {
    TrendingUp,
    BrainCircuit,
    FileUser,
  });
  const containerRef = useRef(null);
  const { scrollYProgress } = useScroll({ target: containerRef });
  const yHero = useTransform(scrollYProgress, [0, 1], [0, 400]);
  const opacityHero = useTransform(scrollYProgress, [0, 0.3], [1, 0]);

  return (
    <div
      ref={containerRef}
      className="relative w-full bg-slate-50 dark:bg-slate-950 overflow-hidden"
    >
      <section
        id="hero"
        className="relative min-h-screen flex items-center justify-start px-6 md:px-12 overflow-hidden bg-slate-50 dark:bg-slate-950"
      >
        <motion.div
          style={{ y: yHero, opacity: opacityHero }}
          className="relative z-10 w-full max-w-7xl mx-auto flex flex-col items-start text-left"
        >
          <h1 className="text-[10vw] sm:text-[11vw] md:text-[10vw] leading-[1.15] font-black tracking-tighter text-slate-900 dark:text-white uppercase mb-3 flex flex-col w-full break-words">
            <span className="overflow-hidden">
              <motion.span
                initial={{ y: "100%" }}
                animate={{ y: 0 }}
                transition={{
                  duration: 1.2,
                  ease: [0.16, 1, 0.3, 1],
                  delay: 0.1,
                }}
                className="block"
              >
                {t("hero_heading_1")}
              </motion.span>
            </span>
            <span className="overflow-hidden pt-5">
              <motion.span
                initial={{ y: "100%" }}
                animate={{ y: 0 }}
                transition={{
                  duration: 1.2,
                  ease: [0.16, 1, 0.3, 1],
                  delay: 0.25,
                }}
                className="block text-[#285872] dark:text-sky-400"
              >
                {t("hero_heading_2")}
              </motion.span>
            </span>
          </h1>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1.2, ease: [0.16, 1, 0.3, 1], delay: 0.4 }}
          >
            <p className="text-lg md:text-xl lg:text-2xl text-slate-600 dark:text-slate-400 font-medium max-w-3xl leading-relaxed tracking-tight">
              <q>{t("hero_heading_text")}</q>
            </p>
          </motion.div>
        </motion.div>
      </section>

      <section
        id="platforms"
        className="relative min-h-screen flex items-center justify-center px-6 py-24 bg-slate-100 dark:bg-slate-900 z-20"
      >
        <div className="w-full max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-10 gap-12 lg:gap-16 items-start lg:items-center">
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: "-10%" }}
              transition={{ duration: 0.8, ease: "easeOut" }}
              className="lg:col-span-4 lg:sticky lg:top-32"
            >
              <h2 className="text-4xl md:text-5xl font-extrabold tracking-tight text-slate-900 dark:text-white mb-6">
                {t("platforms_title")}
              </h2>
              <p className="text-lg md:text-xl text-slate-600 dark:text-slate-400 leading-relaxed  text-justify">
                {t("platforms_desc")}
              </p>
            </motion.div>

            <div className="lg:col-span-6 flex flex-col divide-y divide-slate-200 dark:divide-slate-800">
              {platformsList.map((platform, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, margin: "-10%" }}
                  transition={{
                    duration: 0.6,
                    delay: platform.delay,
                    ease: [0.16, 1, 0.3, 1],
                  }}
                  className="py-8 first:pt-0 last:pb-0 flex flex-col sm:flex-row items-start gap-6 text-left group"
                >
                  <div className="w-14 h-14 shrink-0 bg-white rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm flex items-center justify-center p-2 group-hover:scale-105 transition-transform duration-300">
                    <Image
                      src={platform.image}
                      alt={platform.name}
                      className="w-full h-full object-contain"
                      width={48}
                      height={48}
                    />
                  </div>
                  <div className="flex-1 space-y-2">
                    <h3 className="text-xl font-bold tracking-tight text-slate-900 dark:text-white group-hover:text-[#285872] dark:group-hover:text-sky-400 transition-colors">
                      {platform.name}
                    </h3>
                    <p className="text-slate-600 dark:text-slate-400 leading-relaxed text-sm md:text-base text-justify">
                      {platform.desc}
                    </p>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section
        id="features"
        className="relative min-h-screen flex items-center justify-center px-6 py-24 bg-white dark:bg-slate-950 z-20 rounded-t-[3rem] border-t border-slate-200 dark:border-slate-800 shadow-[0_-20px_50px_-20px_rgba(0,0,0,0.1)] -mt-10"
      >
        <div className="w-full max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-20%" }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="mb-16 md:mb-24 flex flex-col md:flex-row md:items-end justify-between gap-8"
          >
            <h2 className="text-4xl md:text-5xl font-extrabold tracking-tight text-slate-900 dark:text-white leading-tight">
              {t("features_title_1")} <br /> {t("features_title_2")}
            </h2>
            <p className="text-lg md:text-xl text-slate-600 dark:text-slate-400 max-w-md pb-2 text-left md:text-right">
              {t("features_subtitle")}
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-8">
            {featuresList.map((feature, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 50 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-10%" }}
                transition={{
                  duration: 0.8,
                  delay: i * 0.15,
                  ease: [0.16, 1, 0.3, 1],
                }}
                whileHover={{ y: -12, scale: 1.02 }}
                className="p-8 md:p-10 rounded-[2.5rem] flex flex-col items-center text-center gap-4 group transition-transform duration-500 border border-slate-200 dark:border-slate-800"
              >
                <div className="w-14 h-14 rounded-full bg-white dark:bg-slate-950 flex items-center justify-center shadow-sm border border-slate-100 dark:border-slate-800">
                  <feature.icon className="w-8 h-8 text-[#285872] dark:text-sky-400" />
                </div>
                <div className="space-y-3">
                  <h3 className="text-xl md:text-2xl font-bold text-slate-900 dark:text-white group-hover:text-[#285872] dark:group-hover:text-sky-400 transition-colors">
                    {feature.title}
                  </h3>
                  <p className="text-slate-600 dark:text-slate-400 text-sm md:text-base leading-relaxed text-justify">
                    {feature.desc}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
