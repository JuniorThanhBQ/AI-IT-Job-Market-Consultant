"use client";

import { useTranslations } from "next-intl";

export default function TOSSections() {
  const t = useTranslations("TOS");
  return (
    <section className="flex-1 flex flex-col gap-8">
      <div className="mb-4">
        <h1 className="text-4xl md:text-5xl font-black tracking-tight text-slate-900 dark:text-white mb-3">
          {t("title")}
        </h1>
        <p className="text-base text-slate-500 dark:text-slate-400 font-medium">
          {t("subtitle")} <br /> {t("hostOrg")}
        </p>
      </div>

      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm divide-y divide-slate-100 dark:divide-slate-800 mb-12">
        <div id="tos-intro" className="p-8 sm:p-10 flex flex-col gap-6">
          <h2 className="text-xl font-bold text-slate-900 dark:text-white">
            {t("intro_title")}
          </h2>
          <p className="text-sm md:text-base text-slate-600 dark:text-slate-350 leading-relaxed text-justify">
            {t("intro_desc")}
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 rounded-xl">
              <span className="inline-block px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider bg-[#285872] text-white dark:bg-[#285872] dark:text-[#eef4f7] mb-3">
                {t("intro_badge1")}
              </span>
              <p className="text-xs md:text-sm text-slate-600 dark:text-slate-400 leading-relaxed text-justify">
                {t("intro_text1")}
              </p>
            </div>
            <div className="p-4 rounded-xl">
              <span className="inline-block px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider bg-[#285872] text-white dark:bg-[#285872] dark:text-[#eef4f7] mb-3">
                {t("intro_badge2")}
              </span>
              <p className="text-xs md:text-sm text-slate-600 dark:text-slate-400 leading-relaxed text-justify">
                {t("intro_text2")}
              </p>
            </div>
          </div>
        </div>

        <div id="tos-ip" className="p-8 sm:p-10 flex flex-col gap-6">
          <h2 className="text-xl font-bold text-slate-900 dark:text-white">
            {t("ip_title")}
          </h2>
          <p className="text-sm md:text-base text-slate-600 dark:text-slate-350 leading-relaxed text-justify">
            {t("ip_desc")}
          </p>
          <div className="flex flex-col gap-4">
            <div className="p-4 rounded-xl">
              <span className="inline-block px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider bg-[#285872] text-white dark:bg-[#285872] dark:text-[#eef4f7] mb-3">
                {t("ip_badge1")}
              </span>
              <p className="text-xs md:text-sm text-slate-600 dark:text-slate-400 leading-relaxed text-justify">
                {t("ip_text1")}
              </p>
            </div>
            <div className="p-4 rounded-xl">
              <span className="inline-block px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider bg-[#285872] text-white dark:bg-[#285872] dark:text-[#eef4f7] mb-3">
                {t("ip_badge2")}
              </span>
              <p className="text-xs md:text-sm text-slate-600 dark:text-slate-400 leading-relaxed text-justify">
                {t("ip_text2")}
              </p>
            </div>
            <div className="p-4 rounded-xl">
              <span className="inline-block px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider bg-[#285872] text-white dark:bg-[#285872] dark:text-[#eef4f7] mb-3">
                {t("ip_badge3")}
              </span>
              <p className="text-xs md:text-sm text-slate-600 dark:text-slate-400 leading-relaxed text-justify">
                {t("ip_text3")}
              </p>
            </div>
          </div>
        </div>

        <div id="tos-redirect" className="p-8 sm:p-10 flex flex-col gap-6">
          <h2 className="text-xl font-bold text-slate-900 dark:text-white">
            {t("redirect_title")}
          </h2>
          <p className="text-sm md:text-base text-slate-600 dark:text-slate-350 leading-relaxed text-justify">
            {t("redirect_desc")}
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 rounded-xl">
              <span className="inline-block px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider bg-[#285872] text-white dark:bg-[#285872] dark:text-[#eef4f7] mb-3">
                {t("redirect_badge1")}
              </span>
              <p className="text-xs md:text-sm text-slate-600 dark:text-slate-400 leading-relaxed text-justify">
                {t("redirect_text1")}
              </p>
            </div>
            <div className="p-4 rounded-xl">
              <span className="inline-block px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider bg-[#285872] text-white dark:bg-[#285872] dark:text-[#eef4f7] mb-3">
                {t("redirect_badge2")}
              </span>
              <p className="text-xs md:text-sm text-slate-600 dark:text-slate-400 leading-relaxed text-justify">
                {t("redirect_text2")}
              </p>
            </div>
          </div>
        </div>

        <div id="tos-privacy" className="p-8 sm:p-10 flex flex-col gap-6">
          <h2 className="text-xl font-bold text-slate-900 dark:text-white">
            {t("privacy_title")}
          </h2>
          <p className="text-sm md:text-base text-slate-600 dark:text-slate-350 leading-relaxed text-justify">
            {t("privacy_desc")}
          </p>
        </div>

        <div id="tos-disclaimer" className="p-8 sm:p-10 flex flex-col gap-6">
          <h2 className="text-xl font-bold text-slate-900 dark:text-white">
            {t("disclaimer_title")}
          </h2>
          <p className="text-sm md:text-base text-slate-655 dark:text-slate-350 leading-relaxed mb-2">
            {t("disclaimer_desc")}
          </p>
          <ul className="flex flex-col gap-3">
            {[
              t("disclaimer_point1"),
              t("disclaimer_point2"),
              t("disclaimer_point3"),
            ].map((point, i) => (
              <li
                key={i}
                className="flex gap-3 text-xs md:text-sm text-slate-500 dark:text-slate-400 leading-relaxed text-justify"
              >
                <span className="w-1.5 h-1.5 bg-[#285872] dark:bg-sky-400 rounded-full shrink-0 mt-2" />
                <span>{point}</span>
              </li>
            ))}
          </ul>
        </div>

        <div id="tos-takedown" className="p-8 sm:p-10 flex flex-col gap-6">
          <h2 className="text-xl font-bold text-slate-900 dark:text-white">
            {t("takedown_title")}
          </h2>
          <p className="text-sm md:text-base text-slate-600 dark:text-slate-300 leading-relaxed text-justify">
            {t("takedown_desc")}
          </p>
          <ul className="flex flex-col gap-3 border-b border-slate-100 dark:border-slate-800 pb-6">
            {[t("takedown_point1"), t("takedown_point2")].map((point, i) => (
              <li
                key={i}
                className="flex gap-3 text-xs md:text-sm text-slate-500 dark:text-slate-400 leading-relaxed text-justify"
              >
                <span className="w-1.5 h-1.5 bg-[#285872] dark:bg-sky-400 rounded-full shrink-0 mt-2" />
                <span>{point}</span>
              </li>
            ))}
          </ul>
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 mt-2">
            <div className="flex items-center gap-3">
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500 leading-tight">
                  {t("supportEmail")}
                </h4>
                <p className="text-sm font-extrabold text-slate-800 dark:text-white leading-normal mt-0.5 select-all">
                  2351050164thanh@ou.edu.vn
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
