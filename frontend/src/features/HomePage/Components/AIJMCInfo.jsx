"use client";

import { motion } from "motion/react";
import { TrendingDown, Target, Workflow } from "lucide-react";
import { useTranslations } from "next-intl";

export default function AIJMCInfo() {
  const t = useTranslations("AIJMCInfo");

  return (
    <div className="relative w-full bg-slate-50 dark:bg-slate-950 overflow-hidden">
      <section
        id="about"
        className="relative min-h-screen flex items-center justify-center pt-32 pb-20 px-6 md:px-12 bg-slate-50 dark:bg-slate-950"
      >
        <div className="relative z-10 w-full max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-16 items-center">
          <div className="flex flex-col items-start text-left w-full min-w-0">
            <h1 className="text-5xl md:text-6xl lg:text-7xl leading-[1.25] font-black tracking-tighter text-slate-900 dark:text-white uppercase mb-6 w-full break-words">
              {t("hero_title")} <br />
              <span className="text-[#285872] dark:text-sky-400 text-4xl md:text-5xl lg:text-6xl leading-[1.3] mt-4 inline-block pb-2">
                {t("hero_subtitle")}
              </span>
            </h1>
          </div>

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
                className="bg-white dark:bg-slate-900 p-8 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex items-start gap-6 group hover:shadow-md transition-shadow"
              >
                <div className="w-12 h-12 bg-slate-50 dark:bg-slate-800 rounded-xl flex items-center justify-center shrink-0 border border-slate-100 dark:border-slate-700">
                  <prob.icon className="w-6 h-6 text-[#285872] dark:text-sky-400" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-2 group-hover:text-[#285872] dark:group-hover:text-sky-400 transition-colors">
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
    </div>
  );
}
