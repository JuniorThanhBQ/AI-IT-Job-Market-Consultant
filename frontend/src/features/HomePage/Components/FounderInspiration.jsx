"use client";

import { useRef } from "react";
import { motion, useScroll, useTransform } from "motion/react";
import { Mail, BrainCircuit, Terminal, Blocks, Flame } from "lucide-react";
import { useTranslations } from "next-intl";
import { FOUNDER_SOCIAL_LINKS } from "@/utils/const";
import { LOGO } from "@/assets/CloudinaryAssetsUrl";
import Image from "next/image";
import { LINKS } from "@/utils/const";
import { getFounderSkillsList } from "@/utils/homepage_utils";

export default function FounderInspiration() {
  const t = useTranslations("FounderInspiration");
  const skillsList = getFounderSkillsList(t, {
    BrainCircuit,
    Terminal,
    Blocks,
  });
  const containerRef = useRef(null);
  const { scrollYProgress } = useScroll({ target: containerRef });
  const yBg = useTransform(scrollYProgress, [0, 1], [0, 200]);
  const yAvatar = useTransform(scrollYProgress, [0, 0.5], [0, -100]);
  const opacityFade = useTransform(scrollYProgress, [0, 0.3], [1, 0]);

  return (
    <div
      ref={containerRef}
      className="relative w-full bg-slate-50 dark:bg-slate-950 overflow-hidden"
    >
      <section
        id="founder"
        className="relative min-h-screen flex items-center pt-32 pb-20 px-6 md:px-12 overflow-hidden border-b border-slate-200 dark:border-slate-800"
      >
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:32px_32px] z-0" />

        <div className="relative z-10 w-full max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-center">
          <motion.div
            style={{ opacity: opacityFade }}
            className="lg:col-span-7 flex flex-col items-start text-left w-full"
          >
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, ease: "easeOut" }}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md mb-8 shadow-sm"
            >
              <Terminal className="w-4 h-4 text-blue-600 dark:text-blue-400" />
              <span className="text-sm font-medium text-slate-900 dark:text-slate-200 uppercase tracking-widest">
                {t("badge_role")}
              </span>
            </motion.div>

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
              className="text-4xl md:text-5xl lg:text-6xl leading-[0.9] font-black tracking-tighter text-slate-900 dark:text-white uppercase mt-3 mb-6 pt-6 -mt-6"
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
                <span className="font-bold text-blue-600 dark:text-blue-400">
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
          </motion.div>

          <motion.div
            style={{ y: yAvatar }}
            initial={{ opacity: 0, scale: 0.8, rotate: -5 }}
            animate={{ opacity: 1, scale: 1, rotate: 0 }}
            transition={{ duration: 1, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
            className="lg:col-span-5 relative w-full aspect-[4/5] md:aspect-square lg:aspect-[4/5] rounded-[3rem] overflow-hidden shadow-2xl border border-slate-200 dark:border-slate-800"
          >
            <div className="absolute inset-0 bg-blue-600/10 mix-blend-overlay z-10" />
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

      <section
        id="expertise"
        className="relative min-h-screen flex items-center px-6 py-24 bg-white dark:bg-slate-950 border-b border-slate-200 dark:border-slate-800"
      >
        <div className="w-full max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-20%" }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="mb-16 md:mb-24 text-center md:text-left"
          >
            <h2 className="text-4xl md:text-5xl font-black tracking-tight text-slate-900 dark:text-white pt-6 -mt-6">
              {t("expertise_heading")}
            </h2>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8">
            <motion.div
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-10%" }}
              transition={{ duration: 0.8, ease: "easeOut" }}
              className="md:col-span-2 lg:col-span-3 bg-orange-50 dark:bg-orange-950/30 p-8 md:p-10 rounded-[2.5rem] border border-orange-100 dark:border-orange-900/50 shadow-sm flex flex-col sm:flex-row items-center sm:items-start gap-6"
            >
              <div className="w-16 h-16 bg-orange-100 dark:bg-orange-900/50 rounded-2xl flex items-center justify-center shrink-0">
                <Flame className="w-8 h-8 text-orange-600 dark:text-orange-400" />
              </div>
              <div className="text-center sm:text-left">
                <h3 className="text-2xl font-bold text-orange-900 dark:text-orange-300 mb-2 pt-2 -mt-2">
                  {t("quirk_title")}
                </h3>
                <p className="text-orange-800 dark:text-orange-200/80 text-lg leading-relaxed">
                  {t("quirk_desc")}
                </p>
              </div>
            </motion.div>

            {skillsList.map((skill, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 50 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-10%" }}
                transition={{ duration: 0.8, delay: i * 0.15, ease: "easeOut" }}
                whileHover={{ y: -10 }}
                className={`p-10 rounded-[2.5rem] border ${skill.border} shadow-sm flex flex-col items-start gap-6 hover:shadow-lg transition-all duration-300`}
              >
                <div
                  className={`w-14 h-14 ${skill.bg} rounded-2xl flex items-center justify-center shrink-0`}
                >
                  <skill.icon className={`w-7 h-7 ${skill.color}`} />
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-slate-900 dark:text-white mb-3 pt-2 -mt-2">
                    {skill.title}
                  </h3>
                  <p className="text-slate-600 dark:text-slate-400 leading-relaxed text-justify">
                    {skill.desc}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      <section
        id="story"
        className="relative min-h-screen flex items-center justify-center px-6 py-32 bg-slate-950 text-white z-20 overflow-hidden"
      >
        <motion.div
          style={{ y: yBg }}
          className="absolute -top-[50%] -bottom-[50%] -left-[50%] -right-[50%] opacity-20 pointer-events-none"
        >
          <svg className="w-full h-full">
            <filter id="noiseFilterStory">
              <feTurbulence
                type="fractalNoise"
                baseFrequency="0.6"
                numOctaves="3"
                stitchTiles="stitch"
              />
            </filter>
            <rect width="100%" height="100%" filter="url(#noiseFilterStory)" />
          </svg>
        </motion.div>

        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(37,99,235,0.15)_0,transparent_100%)] pointer-events-none" />

        <div className="relative z-10 w-full max-w-5xl mx-auto flex flex-col lg:flex-row gap-16 lg:gap-24 items-center lg:items-start">
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-20%" }}
            transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
            className="lg:w-1/2 flex flex-col"
          >
            <h2 className="text-6xl md:text-[5.5rem] leading-[1.2] font-black tracking-tighter uppercase mb-6 flex flex-col">
              <span className="block text-slate-500 pt-6 -mt-6">
                {t("story_heading_1")}
              </span>
              <span className="block text-transparent bg-clip-text bg-gradient-to-r from-blue-500 to-purple-500 pb-2 pt-6 -mt-6">
                {t("story_heading_2")}
              </span>
            </h2>
            <div className="w-24 h-2 bg-blue-600 rounded-full mt-4" />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-20%" }}
            transition={{ duration: 1, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
            className="lg:w-1/2 flex flex-col gap-8 text-xl md:text-2xl text-slate-300 font-medium leading-relaxed text-justify"
          >
            <p>{t("story_paragraph_1")}</p>
            <p className="text-white">{t("story_paragraph_2")}</p>
            <p className="text-blue-400">{t("story_paragraph_3")}</p>
          </motion.div>
        </div>
      </section>
    </div>
  );
}
