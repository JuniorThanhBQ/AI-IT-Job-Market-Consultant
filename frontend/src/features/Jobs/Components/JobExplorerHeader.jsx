"use client";

import { useTranslations } from "next-intl";
import { Briefcase, SlidersHorizontal } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Link } from "@/i18n/routing";

export default function JobExplorerHeader() {
  const t = useTranslations("Counselee.Explorer");

  return (
    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div className="flex flex-col gap-2">
        <div className="flex items-center gap-3">
          <h1 className="text-3xl font-black text-slate-900 dark:text-white tracking-tight">
            {t("title")}
          </h1>
        </div>
        <p className="text-sm text-slate-500 dark:text-slate-400 max-w-2xl ml-1 leading-relaxed">
          {t("subtitle")}
        </p>
      </div>
      <div className="shrink-0 flex items-center">
        <Link href="/counselee/jobs/advanced-search">
          <Button
            variant="outline"
            className="border-[#285872]/30 text-[#285872] hover:bg-[#285872]/10 dark:border-slate-800 dark:text-slate-200 dark:hover:bg-slate-800 rounded-full px-5 py-5 text-sm font-bold flex items-center gap-2 cursor-pointer transition-colors"
          >
            {t("btn_advanced_search")}
          </Button>
        </Link>
      </div>
    </div>
  );
}
