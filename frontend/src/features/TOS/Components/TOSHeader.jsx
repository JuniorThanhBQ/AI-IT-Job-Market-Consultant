"use client";

import { useTranslations } from "next-intl";
import { Link } from "@/i18n/routing";

export default function TOSHeader() {
  const t = useTranslations("TOS");

  return (
    <header className="relative z-10 border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-955/80 backdrop-blur-md shrink-0">
      <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
        <Link
          href="/"
          className="flex items-center gap-2 text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors text-sm font-bold uppercase tracking-wider"
        >
          {t("backHome")}
        </Link>
        <div className="flex items-center gap-2 text-xs font-semibold text-slate-400">
          <span>{t("lastUpdated")}</span>
        </div>
      </div>
    </header>
  );
}
