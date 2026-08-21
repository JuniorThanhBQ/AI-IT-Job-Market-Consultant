"use client";

import Image from "next/image";
import { LOGO } from "@/assets/CloudinaryAssetsUrl";
import { useTranslations } from "next-intl";

export default function CompanyHeaderBox({ company }) {
  const t = useTranslations("Counselee.Company");
  const source = company.jobs?.[0]?.source || "ITViec";
  const logoUrl = LOGO[source.toUpperCase()] || LOGO.AIJMC_LOGO;

  return (
    <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-8 backdrop-blur-md shadow-sm flex flex-col gap-5">
      <div className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest flex items-center gap-2">
        <span>01</span>
        <span className="w-8 h-px bg-slate-200 dark:bg-slate-800" />
        <span>{t("profile")}</span>
      </div>

      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div className="flex items-center gap-6">
          <div className="w-20 h-20 bg-white border border-slate-200 dark:border-slate-800 rounded-[1.5rem] flex items-center justify-center overflow-hidden p-2.5 shrink-0 shadow-sm">
            <Image
              src={logoUrl}
              alt={source}
              width={80}
              height={80}
              className="w-full h-full object-contain"
            />
          </div>
          <div>
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-black text-slate-900 dark:text-white tracking-tighter leading-none mb-3">
              {company.name}
            </h1>
            <p className="text-xs font-black text-[#285872] dark:text-[#407c9c] uppercase tracking-widest">
              {company.industry || "Technology & Software"}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
