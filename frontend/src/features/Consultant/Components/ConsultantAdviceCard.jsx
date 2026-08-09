"use client";

import { Award } from "lucide-react";
import { useTranslations } from "next-intl";

export default function ConsultantAdviceCard({ recommendations }) {
  const t = useTranslations("Counselee.Consultant");

  return (
    <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-8 backdrop-blur-md shadow-sm">
      <h2 className="text-xl font-extrabold text-slate-900 dark:text-white flex items-center gap-2.5 mb-6 border-b border-slate-100 dark:border-slate-800 pb-3">
        <Award className="w-5 h-5 text-[#285872]" />
        {t("consultant_title")}
      </h2>
      <div className="flex flex-col gap-6">
        {recommendations.map((rec, index) => (
          <div key={index} className="flex gap-4">
            <div className="w-8 h-8 rounded-full bg-[#285872]/10 border border-[#285872]/20 flex items-center justify-center shrink-0 text-[#285872] font-black text-xs">
              {index + 1}
            </div>
            <div>
              <h4 className="text-sm font-extrabold text-slate-900 dark:text-white mb-1">
                {rec.title}
              </h4>
              <p className="text-xs text-slate-550 dark:text-slate-400 leading-relaxed font-medium">
                {rec.desc}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
