"use client";

import { Sparkles } from "lucide-react";
import { Link } from "@/i18n/routing";
import { useTranslations } from "next-intl";

export default function ConsultantHeader() {
  const t = useTranslations("Counselee.Consultant");

  return (
    <div className="flex flex-col md:flex-row md:items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-4 gap-4">
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white flex items-center gap-2.5">
          <Sparkles className="w-8 h-8 text-[#285872] animate-pulse" />
          {t("title")}
        </h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          {t("subtitle")}
        </p>
      </div>
      <div className="flex items-center gap-3">
        <Link
          href="/counselee/jobs"
          className="bg-[#285872] hover:bg-[#1c3f52] text-white rounded-full px-5 py-2.5 font-bold text-xs tracking-wide shadow-lg transition-all hover:scale-105"
        >
          {t("back_market")}
        </Link>
      </div>
    </div>
  );
}
