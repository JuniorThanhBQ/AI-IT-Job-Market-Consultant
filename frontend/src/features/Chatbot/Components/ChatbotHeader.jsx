"use client";

import { ArrowLeft, Trash2 } from "lucide-react";
import { Link } from "@/i18n/routing";
import { LOGO } from "@/assets/CloudinaryAssetsUrl";
import Image from "next/image";

export default function ChatbotHeader({
  suggestedIntents,
  selectedIntent,
  onSelectIntent,
  confirmClear,
  setConfirmClear,
  onClearHistory,
}) {
  return (
    <header className="relative z-10 border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-950/80 backdrop-blur-md shrink-0">
      <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <Link
            href="/counselee/overview"
            className="text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white p-2.5 border border-slate-200 dark:border-slate-800 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-850 transition-all cursor-pointer"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white border border-[#285872]/20 rounded-xl flex items-center justify-center p-1.5 shadow-sm shrink-0 overflow-hidden">
              <Image
                src={LOGO.AIJMC_LOGO}
                alt="AIJMC Logo"
                width={36}
                height={36}
                className="w-full h-full object-contain"
                loading="eager"
              />
            </div>
            <div>
              <h1 className="text-base font-extrabold text-slate-900 dark:text-white leading-tight">
                AIJMC Chatbot
              </h1>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="hidden lg:flex bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-1 gap-1.5">
            {suggestedIntents.map((intent) => (
              <button
                key={intent.id}
                onClick={() => onSelectIntent(intent.id)}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                  selectedIntent === intent.id
                    ? "bg-[#285872] text-white shadow-md"
                    : "text-slate-550 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
                }`}
              >
                {intent.name}
              </button>
            ))}
          </div>

          {confirmClear ? (
            <div className="flex items-center gap-1.5">
              <button
                onClick={onClearHistory}
                className="text-xs bg-red-500 hover:bg-red-600 text-white px-3 py-2 rounded-xl font-bold transition-all cursor-pointer"
              >
                Confirm Clear
              </button>
              <button
                onClick={() => setConfirmClear(false)}
                className="text-xs bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 text-slate-600 dark:text-slate-300 px-3 py-2 rounded-xl font-bold transition-all cursor-pointer"
              >
                Cancel
              </button>
            </div>
          ) : (
            <button
              onClick={() => setConfirmClear(true)}
              title="Clear Chat History"
              className="p-2.5 hover:bg-slate-100 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-800 rounded-xl text-slate-400 hover:text-red-500 transition-colors cursor-pointer"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
