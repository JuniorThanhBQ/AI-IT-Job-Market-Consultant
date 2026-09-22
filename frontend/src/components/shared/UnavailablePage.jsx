"use client";

import React, { useState } from "react";
import {
  Laptop,
  Cloud,
  Server,
  RefreshCw,
  CheckCircle2,
  XCircle,
} from "lucide-react";
import { useTranslations } from "next-intl";
import { useRouter } from "@/i18n/routing";
import { BASE_URL } from "@/configs/apis";

export default function UnavailablePage() {
  const t = useTranslations("UnavailablePage");
  const [retrying, setRetrying] = useState(false);
  const router = useRouter();

  const handleRetry = async () => {
    setRetrying(true);
    try {
      const res = await fetch(BASE_URL);
      if (res.status < 500) {
        router.push("/");
        return;
      }
    } catch {}
    setTimeout(() => {
      setRetrying(false);
    }, 1000);
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-slate-50 dark:bg-slate-950 p-4 sm:p-6 select-none font-sans">
      <div className="w-full max-w bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm p-6 sm:p-10 space-y-8">
        <div className="border-b border-slate-100 dark:border-slate-800 pb-6 text-left">
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-slate-100">
            {t("status_title")}
          </h1>
        </div>

        <div className="py-2">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 relative">
            <div className="flex flex-col items-center text-center p-3.5 rounded-lg border border-slate-200 dark:border-slate-800 dark:bg-slate-900/50">
              <div className="w-10 h-10 rounded-full bg-emerald-100 dark:bg-emerald-950/60 flex items-center justify-center text-emerald-600 dark:text-emerald-400 mb-2">
                <Laptop className="w-5 h-5" />
              </div>
              <h3 className="font-bold text-slate-900 dark:text-slate-100 text-sm">
                {t("node_browser")}
              </h3>
              <div className="flex items-center gap-1 text-emerald-600 dark:text-emerald-400 text-xs font-semibold mt-0.5">
                <span>{t("status_working")}</span>
              </div>
            </div>

            <div className="flex flex-col items-center text-center p-3.5 rounded-lg border border-slate-200 dark:border-slate-800 dark:bg-slate-900/50">
              <div className="w-10 h-10 rounded-full bg-emerald-100 dark:bg-emerald-950/60 flex items-center justify-center text-emerald-600 dark:text-emerald-400 mb-2">
                <Cloud className="w-5 h-5" />
              </div>
              <h3 className="font-bold text-slate-900 dark:text-slate-100 text-sm">
                {t("node_edge")}
              </h3>
              <div className="flex items-center gap-1 text-emerald-600 dark:text-emerald-400 text-xs font-semibold mt-0.5">
                <span>{t("status_working")}</span>
              </div>
            </div>

            <div className="flex flex-col items-center text-center p-3.5 rounded-lg border border-rose-200 dark:border-rose-900/50 dark:bg-rose-950/20">
              <div className="w-10 h-10 rounded-full bg-rose-100 dark:bg-rose-950/60 flex items-center justify-center text-rose-600 dark:text-rose-400 mb-2">
                <Server className="w-5 h-5" />
              </div>
              <h3 className="font-bold text-slate-900 dark:text-slate-100 text-sm">
                {t("node_host")}
              </h3>
              <div className="flex items-center gap-1 text-rose-600 dark:text-rose-400 text-xs font-semibold mt-0.5">
                <span>{t("status_error")}</span>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-left pt-2">
          <div className="space-y-2">
            <h4 className="font-bold text-sm uppercase tracking-wider text-slate-700 dark:text-slate-300">
              {t("what_happened_title")}
            </h4>
            <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
              {t("what_happened_desc")}
            </p>
          </div>
          <div className="space-y-2">
            <h4 className="font-bold text-sm uppercase tracking-wider text-slate-700 dark:text-slate-300">
              {t("what_can_do_title")}
            </h4>
            <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
              {t("what_can_do_desc")}
            </p>
          </div>
        </div>

        <div className="pt-2 flex flex-col sm:flex-row items-center justify-between gap-4 border-t border-slate-100 dark:border-slate-800">
          <button
            onClick={handleRetry}
            disabled={retrying}
            className="w-full sm:w-auto px-6 py-2.5 rounded-lg bg-[#285872] hover:bg-[#1e4358] text-white text-sm font-semibold transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
          >
            <RefreshCw
              className={`w-4 h-4 ${retrying ? "animate-spin" : ""}`}
            />
            <span>{t("retry_btn")}</span>
          </button>

          <div className="text-xs text-slate-500 dark:text-slate-400 text-center sm:text-right">
            <span>{t("support_contact")}: </span>
            <a
              href="mailto:2351050164thanh@ou.edu.vn"
              className="text-[#285872] dark:text-sky-400 hover:underline font-medium"
            >
              2351050164thanh@ou.edu.vn
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
