"use client";

import { useRef } from "react";
import { motion, useScroll, useTransform } from "motion/react";
import {
  Info,
  TrendingDown,
  Target,
  Workflow,
  Network,
  BookOpen,
  Layers,
  Cpu,
  Server,
} from "lucide-react";
import VerticalScrollbar from "@/components/shared/VerticalScrollbar";
import { useTranslations } from "next-intl";

export default function AIJMCInfo() {
  const t = useTranslations("AIJMCInfo");
  const containerRef = useRef(null);
  const { scrollYProgress } = useScroll({ target: containerRef });

  const yParallax = useTransform(scrollYProgress, [0, 1], [0, 300]);

  const sections = [
    { id: "about", label: t("nav_about") },
    { id: "goals", label: t("nav_goals") },
    { id: "roadmap", label: t("nav_roadmap") },
  ];

  const aims = [
    {
      time: t("aim_1_time"),
      title: t("aim_1_title"),
      desc: t("aim_1_desc"),
      icon: BookOpen,
    },
    {
      time: t("aim_2_time"),
      title: t("aim_2_title"),
      desc: t("aim_2_desc"),
      icon: Layers,
    },
    {
      time: t("aim_3_time"),
      title: t("aim_3_title"),
      desc: t("aim_3_desc"),
      icon: Workflow,
    },
    {
      time: t("aim_4_time"),
      title: t("aim_4_title"),
      desc: t("aim_4_desc"),
      icon: Cpu,
    },
    {
      time: t("aim_5_time"),
      title: t("aim_5_title"),
      desc: t("aim_5_desc"),
      icon: Server,
    },
  ];

  return (
    <div
      ref={containerRef}
      className="relative w-full bg-white dark:bg-slate-950 overflow-hidden"
    >
      <VerticalScrollbar sections={sections} />

      <section
        id="about"
        className="relative min-h-screen flex items-center justify-center pt-32 pb-20 px-6 md:px-12 overflow-hidden bg-slate-50 dark:bg-slate-950 border-b border-slate-200 dark:border-slate-800"
      >
        <div className="absolute inset-0 bg-[radial-gradient(#e5e7eb_1px,transparent_1px)] dark:bg-[radial-gradient(#1f2937_1px,transparent_1px)] [background-size:32px_32px] opacity-40 z-0" />

        <div className="relative z-10 w-full max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-16 items-center">
          <motion.div
            style={{ y: yParallax }}
            className="flex flex-col items-start text-left w-full min-w-0"
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.8, ease: "easeOut" }}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md mb-8 shadow-sm"
            >
              <Info className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
              <span className="text-sm font-medium text-slate-900 dark:text-slate-200 uppercase tracking-widest">
                {t("hero_badge")}
              </span>
            </motion.div>

            <h1 className="text-5xl md:text-6xl lg:text-7xl leading-[1.1] font-black tracking-tighter text-slate-900 dark:text-white uppercase mb-6 w-full break-words">
              {t("hero_title")} <br />
              <span className="text-transparent leading-[1.5] bg-clip-text bg-gradient-to-r from-indigo-600 to-cyan-500 text-4xl md:text-5xl lg:text-6xl mt-4 inline-block pb-2">
                {t("hero_subtitle")}
              </span>
            </h1>
          </motion.div>

          <div className="flex flex-col gap-6 w-full min-w-0">
            {[
              {
                title: t("problem_1_title"),
                desc: t("problem_1_desc"),
                icon: TrendingDown,
              },
              {
                title: t("problem_2_title"),
                desc: t("problem_2_desc"),
                icon: Target,
              },
              {
                title: t("problem_3_title"),
                desc: t("problem_3_desc"),
                icon: Workflow,
              },
            ].map((prob, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: 50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{
                  duration: 0.8,
                  delay: 0.2 + i * 0.15,
                  ease: "easeOut",
                }}
                className="bg-white dark:bg-slate-900 p-8 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm flex items-start gap-6 group hover:shadow-md transition-shadow"
              >
                <div className="w-12 h-12 bg-indigo-50 dark:bg-indigo-900/30 rounded-xl flex items-center justify-center shrink-0">
                  <prob.icon className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-2 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                    {prob.title}
                  </h3>
                  <p className="text-slate-600 dark:text-slate-400 leading-relaxed text-sm">
                    {prob.desc}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      <section
        id="goals"
        className="relative min-h-screen flex items-center justify-center px-6 py-24 bg-white dark:bg-slate-950 z-20"
      >
        <div className="w-full max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-9">
            <motion.div
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-20%" }}
              transition={{ duration: 0.8, ease: "easeOut" }}
              className="lg:col-span-5 flex flex-col justify-center"
            >
              <h2 className="text-5xl md:text-6xl font-black tracking-tight text-slate-900 dark:text-white mb-8 leading-tight">
                {t("goals_heading")}
              </h2>
              <p className="text-xl text-slate-600 dark:text-slate-400 leading-relaxed text-justify">
                {t("goals_desc")}
              </p>
            </motion.div>

            <div className="lg:col-span-7 grid grid-cols-1 sm:grid-cols-2 gap-6">
              {[
                {
                  title: t("foundation_1_title"),
                  desc: t("foundation_1_desc"),
                  icon: Network,
                  color: "from-blue-500 to-indigo-500",
                },
                {
                  title: t("foundation_2_title"),
                  desc: t("foundation_2_desc"),
                  icon: BookOpen,
                  color: "from-emerald-500 to-teal-500",
                },
              ].map((found, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, scale: 0.9 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true, margin: "-10%" }}
                  transition={{
                    duration: 0.8,
                    delay: i * 0.2,
                    ease: "easeOut",
                  }}
                  className="bg-slate-50 dark:bg-slate-900 p-10 rounded-[2rem] border border-slate-100 dark:border-slate-800 flex flex-col justify-between aspect-square"
                >
                  <div
                    className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${found.color} flex items-center justify-center mb-8 shadow-lg`}
                  >
                    <found.icon className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-slate-900 dark:text-white mb-3">
                      {found.title}
                    </h3>
                    <p className="text-slate-500 dark:text-slate-400 leading-relaxed text-justify">
                      {found.desc}
                    </p>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section
        id="roadmap"
        className="relative min-h-screen px-6 py-24 bg-slate-50 dark:bg-slate-900 z-20 border-t border-slate-200 dark:border-slate-800"
      >
        <div className="w-full max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-20%" }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="mb-20 text-center"
          >
            <h2 className="text-5xl md:text-7xl font-black tracking-tight text-slate-900 dark:text-white">
              {t("roadmap_heading")}
            </h2>
          </motion.div>

          <div className="relative border-l-2 border-indigo-100 dark:border-indigo-900/50 ml-6 md:ml-12 space-y-12 pb-12">
            {aims.map((aim, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -50 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true, margin: "-10%" }}
                transition={{ duration: 0.7, delay: i * 0.15, ease: "easeOut" }}
                className="relative pl-8 md:pl-16 group"
              >
                <div className="absolute -left-[17px] top-1 w-8 h-8 bg-white dark:bg-slate-950 border-4 border-indigo-500 rounded-full flex items-center justify-center group-hover:scale-125 transition-transform duration-300">
                  <div className="w-2 h-2 bg-indigo-600 rounded-full" />
                </div>

                <div className="bg-white dark:bg-slate-950 p-8 md:p-10 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm hover:shadow-md transition-shadow">
                  <div className="flex items-center gap-4 mb-4">
                    <div className="px-4 py-1.5 bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 rounded-full text-sm font-bold tracking-wide">
                      {aim.time}
                    </div>
                    <aim.icon className="w-5 h-5 text-slate-400" />
                  </div>
                  <h3 className="text-2xl font-bold text-slate-900 dark:text-white mb-3">
                    {aim.title}
                  </h3>
                  <p className="text-slate-600 dark:text-slate-400 leading-relaxed">
                    {aim.desc}
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
