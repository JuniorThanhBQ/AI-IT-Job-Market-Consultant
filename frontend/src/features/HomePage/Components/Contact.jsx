"use client";

import { useRef } from "react";
import { motion, useScroll, useTransform } from "motion/react";
import { Mail, MapPin, Info, ArrowUpRight } from "lucide-react";
import VerticalScrollbar from "@/components/shared/VerticalScrollbar";
import { useTranslations } from "next-intl";
import { FOUNDER_SOCIAL_LINKS } from "@/utils/const";
import { LOGO } from "@/assets/CloudinaryAssetsUrl";
import Image from "next/image";

export default function Contact() {
  const t = useTranslations("Contact");
  const containerRef = useRef(null);
  const { scrollYProgress } = useScroll({ target: containerRef });

  const yParallax = useTransform(scrollYProgress, [0, 1], [0, 200]);

  const sections = [
    { id: "reach-out", label: t("nav_reach_out") },
    { id: "connect", label: t("nav_connect") },
  ];

  return (
    <div
      ref={containerRef}
      className="relative w-full bg-slate-50 dark:bg-slate-950 overflow-hidden"
    >
      <VerticalScrollbar sections={sections} />

      <section
        id="reach-out"
        className="relative min-h-screen flex items-center pt-32 pb-24 px-6 md:px-12 overflow-hidden bg-slate-50 dark:bg-slate-950 border-b border-slate-200 dark:border-slate-800"
      >
        <div className="absolute inset-0 bg-[radial-gradient(#e5e7eb_1px,transparent_1px)] dark:bg-[radial-gradient(#1f2937_1px,transparent_1px)] [background-size:40px_40px] opacity-50 z-0" />

        <motion.div
          animate={{
            rotate: [0, 90, 0],
            scale: [1, 1.2, 1],
          }}
          transition={{ duration: 25, repeat: Infinity, ease: "linear" }}
          className="absolute top-0 right-0 w-[50vw] h-[50vw] bg-blue-500/10 dark:bg-blue-600/10 rounded-full blur-[120px] pointer-events-none -translate-y-1/4 translate-x-1/4 z-0"
        />

        <div className="relative z-10 w-full max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-16 items-center">
            <motion.div
              style={{ y: yParallax }}
              className="flex flex-col justify-center text-left"
            >
              <motion.h1
                initial={{ opacity: 0, x: -30 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.8, ease: "easeOut" }}
                className="text-6xl md:text-8xl lg:text-[7rem] leading-[1.5] font-black tracking-tighter uppercase text-slate-900 dark:text-white mb-6"
              >
                {t("hero_title")}
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-500 pb-2 inline-block mt-2">
                  {t("hero_subtitle")}
                </span>
              </motion.h1>

              <motion.p
                initial={{ opacity: 0, x: -30 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.8, delay: 0.1, ease: "easeOut" }}
                className="text-lg md:text-xl text-slate-600 dark:text-slate-400 font-medium leading-relaxed mb-10 text-justify max-w-xl"
              >
                {t("description")}
              </motion.p>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.2, ease: "easeOut" }}
                className="w-full max-w-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 md:p-8 flex items-start gap-5 shadow-sm"
              >
                <div className="mt-1 w-12 h-12 bg-blue-50 dark:bg-blue-900/30 rounded-2xl flex items-center justify-center shrink-0">
                  <Info className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                </div>
                <div>
                  <h4 className="text-xl font-bold text-slate-900 dark:text-white mb-2">
                    {t("note_title")}
                  </h4>
                  <p className="text-slate-600 dark:text-slate-400 leading-relaxed font-medium text-justify">
                    {t("note_desc")}
                  </p>
                </div>
              </motion.div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.8, delay: 0.3, ease: "easeOut" }}
              className="w-full flex justify-end"
            >
              <a
                href={`mailto:${FOUNDER_SOCIAL_LINKS.EMAIL}`}
                className="group relative w-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-[3rem] p-10 lg:p-14 flex flex-col items-start gap-12 lg:gap-16 shadow-sm hover:shadow-2xl hover:border-blue-500/50 transition-all duration-500 overflow-hidden"
              >
                <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

                <div className="relative z-10 w-20 h-20 bg-blue-50 dark:bg-blue-900/20 rounded-full flex items-center justify-center group-hover:scale-110 group-hover:bg-blue-600 transition-all duration-500">
                  <Mail className="w-8 h-8 text-blue-600 dark:text-blue-400 group-hover:text-white transition-colors" />
                </div>

                <div className="relative z-10 w-full pr-12">
                  <span className="block text-sm font-bold text-slate-400 dark:text-slate-500 tracking-widest uppercase mb-4">
                    {t("email_label")}
                  </span>
                  <span className="block text-2xl md:text-4xl lg:text-[2.75rem] font-black text-slate-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors break-words leading-[1.2]">
                    {FOUNDER_SOCIAL_LINKS.EMAIL}
                  </span>
                </div>

                <div className="absolute top-10 right-10 lg:top-14 lg:right-14 w-14 h-14 rounded-full border border-slate-200 dark:border-slate-700 flex items-center justify-center opacity-0 -translate-y-8 group-hover:opacity-100 group-hover:translate-y-0 transition-all duration-500 bg-white dark:bg-slate-800">
                  <ArrowUpRight className="w-7 h-7 text-slate-900 dark:text-white" />
                </div>
              </a>
            </motion.div>
          </div>
        </div>
      </section>

      <section
        id="connect"
        className="relative min-h-screen flex items-center justify-center px-6 py-24 bg-slate-100 dark:bg-slate-950 z-20"
      >
        <div className="w-full max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12">
            <motion.div
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-10%" }}
              transition={{ duration: 0.8, ease: "easeOut" }}
              className="bg-white dark:bg-slate-900 p-10 md:p-16 rounded-[3rem] border border-slate-200 dark:border-slate-800 flex flex-col justify-between aspect-square lg:aspect-auto shadow-sm"
            >
              <div className="w-20 h-20 bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 rounded-3xl flex items-center justify-center mb-12">
                <MapPin className="w-10 h-10" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-6">
                  {t("address_title")}
                </h3>
                <p className="text-4xl md:text-5xl lg:text-6xl font-black text-slate-900 dark:text-white leading-[1.15] tracking-tight">
                  {t("address_value")}
                </p>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-10%" }}
              transition={{ duration: 0.8, delay: 0.2, ease: "easeOut" }}
              className="bg-slate-950 dark:bg-black p-10 md:p-16 rounded-[3rem] border border-slate-800 flex flex-col justify-between aspect-square lg:aspect-auto text-white shadow-xl"
            >
              <div className="flex flex-col gap-6 w-full h-full justify-center">
                <h3 className="text-xl font-bold text-slate-500 uppercase tracking-widest mb-4">
                  {t("socials_title")}
                </h3>

                <a
                  href={FOUNDER_SOCIAL_LINKS.GITHUB}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="group flex items-center justify-between p-6 md:p-8 bg-slate-900 rounded-[2rem] border border-slate-800 hover:border-slate-600 transition-colors"
                >
                  <div className="flex items-center gap-6 md:gap-8">
                    <div className="w-16 h-16 bg-white rounded-2xl flex items-center justify-center shrink-0">
                      <Image
                        src={LOGO.GITHUB}
                        alt="GitHub"
                        width={64}
                        height={64}
                        className="w-9 h-9 object-contain"
                      />
                    </div>
                    <span className="text-2xl md:text-4xl font-bold">
                      {t("social_github")}
                    </span>
                  </div>
                  <ArrowUpRight className="w-8 h-8 text-slate-500 group-hover:text-white transition-colors shrink-0" />
                </a>

                <a
                  href={FOUNDER_SOCIAL_LINKS.LINKEDIN}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="group flex items-center justify-between p-6 md:p-8 bg-slate-900 rounded-[2rem] border border-slate-800 hover:border-slate-600 transition-colors"
                >
                  <div className="flex items-center gap-6 md:gap-8">
                    <div className="w-16 h-16 bg-white rounded-2xl flex items-center justify-center shrink-0">
                      <Image
                        src={LOGO.LINKEDIN}
                        alt="LinkedIn"
                        width={64}
                        height={64}
                        className="w-9 h-9 object-contain"
                      />
                    </div>
                    <span className="text-2xl md:text-4xl font-bold">
                      {t("social_linkedin")}
                    </span>
                  </div>
                  <ArrowUpRight className="w-8 h-8 text-slate-500 group-hover:text-white transition-colors shrink-0" />
                </a>
              </div>
            </motion.div>
          </div>
        </div>
      </section>
    </div>
  );
}
