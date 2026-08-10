"use client";

import { motion } from "motion/react";
import { BarChart2 } from "lucide-react";
import { useTranslations } from "next-intl";

export default function ConsultantSkillsChart({ skillsData }) {
  const t = useTranslations("Counselee.Consultant");

  return (
    <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-8 backdrop-blur-md shadow-sm">
      <h2 className="text-xl font-extrabold text-slate-900 dark:text-white flex items-center gap-2.5 mb-6 border-b border-slate-100 dark:border-slate-800 pb-3">
        <BarChart2 className="w-5 h-5 text-[#285872]" />
        {t("skills_chart")}
      </h2>
      <div className="flex flex-col gap-5">
        {skillsData.map((skill, index) => (
          <div key={index} className="flex flex-col gap-1.5">
            <div className="flex justify-between items-center text-xs font-bold">
              <span className="text-slate-700 dark:text-slate-300">
                {skill.name}
              </span>
              <span className="text-[#285872]">
                {t("skills_postings", { percentage: skill.percentage })}
              </span>
            </div>
            <div className="w-full h-3 bg-slate-100 dark:bg-slate-955 border border-slate-200 dark:border-slate-850/80 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${skill.percentage}%` }}
                transition={{ duration: 1, delay: index * 0.1 }}
                className={`h-full ${skill.color} rounded-full`}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
