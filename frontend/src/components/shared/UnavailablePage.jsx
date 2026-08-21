"use client";

import React, { useState } from "react";
import { ServerOff, RefreshCw } from "lucide-react";
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
      await fetch(BASE_URL);
      router.push("/");
      return;
    } catch (e) {}
    setTimeout(() => {
      setRetrying(false);
    }, 1000);
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-slate-50 dark:bg-slate-950 p-6 text-center select-none">
      <div className="max-w-md w-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-[2.5rem] p-8 shadow-sm flex flex-col items-center gap-6">
        <div className="w-16 h-16 rounded-full bg-red-500/10 dark:bg-red-500/20 flex items-center justify-center text-red-500">
          <ServerOff className="w-8 h-8" />
        </div>
        <div className="space-y-2">
          <h1 className="text-xl font-extrabold text-slate-900 dark:text-white">
            {t("title")}
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 leading-relaxed">
            {t("desc")}
          </p>
        </div>
        <button
          onClick={handleRetry}
          disabled={retrying}
          className="w-full py-3.5 px-6 rounded-2xl bg-[#285872] hover:bg-[#1e4358] text-white text-sm font-bold transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${retrying ? "animate-spin" : ""}`} />
          {t("retry_btn")}
        </button>
      </div>
    </div>
  );
}
