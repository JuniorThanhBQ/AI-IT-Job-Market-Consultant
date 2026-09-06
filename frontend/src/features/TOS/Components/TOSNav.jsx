"use client";

import { useTranslations } from "next-intl";

export default function TOSNav({ onScrollToSection }) {
  const t = useTranslations("TOS");

  const navItems = [
    { key: "intro", label: t("intro_title").split(". ")[1] },
    { key: "ip", label: t("ip_title").split(". ")[1] },
    { key: "redirect", label: t("redirect_title").split(". ")[1] },
    { key: "privacy", label: t("privacy_title").split(". ")[1] },
    { key: "disclaimer", label: t("disclaimer_title").split(". ")[1] },
    { key: "takedown", label: t("takedown_title").split(". ")[1] },
  ];

  return (
    <aside className="hidden lg:block lg:w-80 shrink-0">
      <div className="lg:sticky lg:top-28 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 flex flex-col gap-4 shadow-sm">
        <h2 className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest">
          Navigation
        </h2>
        <nav className="flex flex-col gap-2">
          {navItems.map((item) => (
            <button
              key={item.key}
              onClick={() => onScrollToSection(item.key)}
              className="text-left py-2 px-3 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-400 hover:text-[#285872] dark:hover:text-sky-400 transition-all text-xs font-bold uppercase tracking-wider cursor-pointer"
            >
              {item.label}
            </button>
          ))}
        </nav>
      </div>
    </aside>
  );
}
