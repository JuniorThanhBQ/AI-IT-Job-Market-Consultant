"use client";

import Image from "next/image";
import { LOGO } from "@/assets/CloudinaryAssetsUrl";

export default function CompanyHeaderBox({ company }) {
  const source = company.jobs?.[0]?.source || "ITViec";
  const logoUrl = LOGO[source.toUpperCase()] || LOGO.AIJMC_LOGO;

  return (
    <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2.5rem] p-8 backdrop-blur-md flex items-center gap-5 shadow-sm">
      <div className="w-16 h-16 bg-white border border-slate-200 dark:border-slate-800 rounded-2xl flex items-center justify-center overflow-hidden p-2 shrink-0">
        <Image
          src={logoUrl}
          alt={source}
          width={64}
          height={64}
          className="w-full h-full object-contain"
        />
      </div>
      <div>
        <h1 className="text-2xl md:text-3xl font-extrabold text-slate-900 dark:text-white mb-2">
          {company.name}
        </h1>
        <p className="text-sm font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
          {company.industry || "Technology & Software"}
        </p>
      </div>
    </div>
  );
}
