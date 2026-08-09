"use client";

import { ChevronLeft, Save, Loader2 } from "lucide-react";
import { Link } from "@/i18n/routing";
import { useTranslations } from "next-intl";

export default function CVHeader({ saving, onSaveCV }) {
  const t = useTranslations("Counselee.CV");

  return (
    <div className="flex flex-col md:flex-row md:items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-4 gap-4">
      <div>
        <Link
          href="/counselee/overview"
          className="inline-flex items-center gap-1 text-xs font-bold text-[#285872] hover:underline mb-2"
        >
          <ChevronLeft className="w-3.5 h-3.5" />
          {t("back_overview")}
        </Link>
        <h1 className="text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white">
          {t("title")}
        </h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          {t("subtitle")}
        </p>
      </div>
      <div className="flex items-center gap-3">
        <button
          onClick={onSaveCV}
          disabled={saving}
          className="bg-[#285872] hover:bg-[#1c3f52] disabled:opacity-50 text-white rounded-full px-6 py-2.5 font-bold text-xs tracking-wide shadow-lg shadow-[#285872]/20 transition-all hover:scale-105 inline-flex items-center gap-2 cursor-pointer"
        >
          {saving ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Save className="w-4 h-4" />
          )}
          {t("save_cv")}
        </button>
      </div>
    </div>
  );
}
