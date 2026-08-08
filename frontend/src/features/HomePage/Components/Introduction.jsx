"use client";

import { useRef, useState, useEffect } from "react";
import { motion, useScroll, useTransform, useInView } from "motion/react";
import {
  ArrowUpRight,
  BrainCircuit,
  TrendingUp,
  FileUser,
  Database,
  Network,
  Server,
} from "lucide-react";
import VerticalScrollbar from "@/components/shared/VerticalScrollbar";
import { useTranslations } from "next-intl";
import { LOGO } from "@/assets/CloudinaryAssetsUrl";
import Image from "next/image";

function BlinkingStat({ targetValue, label }) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <div
      ref={ref}
      className="flex flex-col items-center justify-center p-6 md:p-8 bg-white/80 dark:bg-slate-900/40 backdrop-blur-md rounded-[2.5rem] border border-slate-200 dark:border-slate-800 shadow-2xl transition-all duration-500 hover:scale-105 hover:bg-white/90 dark:hover:bg-slate-900/50"
    >
      <motion.span
        animate={
          isInView
            ? {
                opacity: [1, 0, 1, 0, 1, 0, 1],
              }
            : {
                opacity: 0,
              }
        }
        transition={{
          duration: 1.5,
          times: [0, 0.16, 0.33, 0.5, 0.66, 0.83, 1],
          ease: "easeInOut",
        }}
        className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-black tracking-tight mb-4 min-h-[1.2em] font-mono text-transparent bg-clip-text bg-gradient-to-r from-blue-600 via-indigo-500 to-blue-600 dark:from-white dark:via-blue-100 dark:to-white"
      >
        {targetValue}
      </motion.span>
      <span className="text-sm md:text-base font-bold uppercase tracking-widest text-slate-500 dark:text-blue-200 text-center">
        {label}
      </span>
    </div>
  );
}

export default function Introduction() {
  const t = useTranslations("Introduction");
  const containerRef = useRef(null);
  const { scrollYProgress } = useScroll({ target: containerRef });

  const yHero = useTransform(scrollYProgress, [0, 1], [0, 400]);
  const opacityHero = useTransform(scrollYProgress, [0, 0.3], [1, 0]);

  const sections = [
    { id: "hero", label: t("nav_hero") },
    { id: "platforms", label: t("nav_platforms") },
    { id: "features", label: t("nav_features") },
    { id: "cta", label: t("nav_cta") },
  ];

  return (
    <div
      ref={containerRef}
      className="relative w-full bg-slate-50 dark:bg-slate-950 overflow-hidden"
    >
      <VerticalScrollbar sections={sections} />

      <section
        id="hero"
        className="relative min-h-screen flex items-center justify-start px-6 md:px-12 overflow-hidden bg-slate-50 dark:bg-slate-950"
      >
        <div className="pointer-events-none absolute inset-0 z-0 opacity-[0.04] dark:opacity-[0.06] mix-blend-overlay">
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
            x: [0, 40, -30, 0],
            y: [0, -40, 50, 0],
            scale: [1, 1.15, 0.9, 1],
          }}
          transition={{ duration: 18, repeat: Infinity, ease: "easeInOut" }}
          className="absolute -top-[10%] -left-[10%] w-[55vw] h-[55vw] bg-blue-500/20 dark:bg-blue-600/20 rounded-full blur-[120px] pointer-events-none z-0"
        />

        <motion.div
          animate={{
            x: [0, -50, 30, 0],
            y: [0, 40, -30, 0],
            scale: [1, 1.2, 0.85, 1],
          }}
          transition={{ duration: 22, repeat: Infinity, ease: "easeInOut" }}
          className="absolute top-[30%] -right-[10%] w-[45vw] h-[45vw] bg-purple-500/20 dark:bg-purple-600/20 rounded-full blur-[120px] pointer-events-none z-0"
        />

        <motion.div
          style={{ y: yHero, opacity: opacityHero }}
          className="relative z-10 w-full max-w-7xl mx-auto flex flex-col items-start text-left pt-20"
        >
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 1.2, ease: [0.16, 1, 0.3, 1] }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md mb-8 shadow-sm"
          >
            <FileUser className="w-4 h-4 text-blue-600" />
            <span className="text-sm font-medium text-slate-900 dark:text-slate-200 uppercase tracking-widest">
              {t("hero_badge")}
            </span>
          </motion.div>

          <h1 className="text-[14vw] md:text-[10vw] leading-[1.1] font-black tracking-tighter text-slate-900 dark:text-white uppercase mb-3 flex flex-col">
            <span className="overflow-hidden pt-12 -mt-6 mb-2">
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
            <span className="overflow-hidden pb-3">
              <motion.span
                initial={{ y: "100%" }}
                animate={{ y: 0 }}
                transition={{
                  duration: 1.2,
                  ease: [0.16, 1, 0.3, 1],
                  delay: 0.25,
                }}
                className="block text-transparent bg-clip-text bg-gradient-to-r from-blue-600 via-indigo-500 to-purple-600"
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

            <div className="lg:col-span-6 grid grid-cols-1 sm:grid-cols-2 gap-6 md:gap-8">
              {[
                {
                  name: t("platforms_itviec"),
                  desc: t("platforms_itviec_desc"),
                  image: LOGO.ITVIEC,
                  delay: 0,
                },
                {
                  name: t("platforms_topdev"),
                  desc: t("platforms_topdev_desc"),
                  image: LOGO.TOPDEV,
                  delay: 0.1,
                },
                {
                  name: t("platforms_itjobs"),
                  desc: t("platforms_itjobs_desc"),
                  image: LOGO.ITJOBS,
                  delay: 0.2,
                },
                {
                  name: t("platforms_vietnamworks"),
                  desc: t("platforms_vietnamworks_desc"),
                  image: LOGO.VIETNAMWORKS,
                  delay: 0.3,
                },
              ].map((platform, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 50 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, margin: "-10%" }}
                  transition={{
                    duration: 0.8,
                    delay: platform.delay,
                    ease: [0.16, 1, 0.3, 1],
                  }}
                  whileHover={{ y: -10 }}
                  className="bg-white dark:bg-slate-950 p-8 md:p-10 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-xl group text-left"
                >
                  <div className="w-14 h-14 bg-white dark:bg-slate-800 rounded-2xl flex items-center justify-center mb-8 group-hover:scale-110 transition-transform duration-500 shadow-sm p-2 border border-slate-100 dark:border-slate-700">
                    <Image
                      src={platform.image}
                      alt={platform.name}
                      className="w-full h-full object-contain"
                      width={112}
                      height={112}
                    />
                  </div>
                  <h3 className="text-2xl font-black tracking-tight text-slate-900 dark:text-white mb-4">
                    {platform.name}
                  </h3>
                  <p className="text-slate-500 dark:text-slate-400 leading-relaxed text-sm md:text-base text-justify">
                    {platform.desc}
                  </p>
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
            className="mb-20 md:mb-32 flex flex-col md:flex-row md:items-end justify-between gap-8"
          >
            <h2 className="text-5xl md:text-7xl font-bold tracking-tight text-slate-900 dark:text-white leading-tight">
              {t("features_title_1")} <br /> {t("features_title_2")}
            </h2>
            <p className="text-xl text-slate-500 dark:text-slate-400 max-w-md pb-2 text-right">
              {t("features_subtitle")}
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-8">
            {[
              {
                title: t("feature_1_title"),
                desc: t("feature_1_desc"),
                icon: TrendingUp,
                color: "bg-slate-50 dark:bg-slate-900",
              },
              {
                title: t("feature_2_title"),
                desc: t("feature_2_desc"),
                icon: BrainCircuit,
                color: "bg-slate-50 dark:bg-slate-900",
              },
              {
                title: t("feature_3_title"),
                desc: t("feature_3_desc"),
                icon: FileUser,
                color: "bg-slate-50 dark:bg-slate-900",
              },
            ].map((feature, i) => (
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
                className={`p-10 md:p-12 rounded-[2.5rem] ${feature.color} flex flex-col justify-between aspect-square group transition-transform duration-500 border border-slate-100 dark:border-slate-800`}
              >
                <div className="w-16 h-16 rounded-full bg-white dark:bg-slate-950 flex items-center justify-center shadow-sm border border-slate-100 dark:border-slate-800 mx-auto my-2">
                  <feature.icon className="w-12 h-12 text-blue-600" />
                </div>
                <div>
                  <h3 className="text-3xl font-bold text-slate-900 dark:text-white mb-8 group-hover:text-blue-600 transition-colors text-center">
                    {feature.title}
                  </h3>
                  <p className="text-slate-600 dark:text-slate-400 text-lg leading-relaxed text-justify">
                    {feature.desc}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      <section className="relative overflow-hidden py-24" id="cta">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_0%,rgba(59,130,246,0.12),transparent_55%)]" />
        <div className="absolute inset-x-0 bottom-0 h-1/2 bg-[radial-gradient(circle_at_50%_100%,rgba(0,0,0,0.12),transparent_65%)]" />

        <div className="relative z-10 mx-auto w-full max-w-6xl px-6">
          <div className="mx-auto mb-12 max-w-2xl text-center">
            <p className="mb-3 text-sm font-medium uppercase tracking-[0.2em] text-blue-500">
              {t("stats_badge")}
            </p>

            <h2 className="text-3xl font-semibold tracking-tight md:text-4xl">
              {t("stats_title")}
            </h2>

            <p className="mt-4 text-base text-muted-foreground">
              {t("stats_desc")}
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 md:gap-8">
            <BlinkingStat targetValue="1500+" label={t("stats_jobs")} />

            <BlinkingStat targetValue="50+" label={t("stats_companies")} />

            <BlinkingStat targetValue="500+" label={t("stats_skills")} />

            <BlinkingStat targetValue="4+" label={t("stats_portals")} />
          </div>
        </div>
      </section>
    </div>
  );
}
