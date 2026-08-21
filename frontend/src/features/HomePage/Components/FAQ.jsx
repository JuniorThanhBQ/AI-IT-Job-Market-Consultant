"use client";

import { useState } from "react";
import { motion } from "motion/react";
import { useTranslations } from "next-intl";
import { FAQItem } from "@/utils/homepage_utils";

export default function FAQ() {
  const t = useTranslations("FAQ");
  const generalFaqs = t.raw("general_faqs");
  const technicalFaqs = t.raw("technical_faqs");
  const [activeGeneral, setActiveGeneral] = useState(0);
  const [activeTech, setActiveTech] = useState(0);

  return (
    <div className="relative w-full bg-slate-50 dark:bg-slate-950">
      <section
        id="general"
        className="relative min-h-screen pt-40 pb-24 px-6 md:px-12 bg-slate-50 dark:bg-slate-950 overflow-hidden"
      >
        <div className="absolute top-0 right-0 w-[50vw] h-[50vw] bg-blue-500/10 dark:bg-blue-600/10 rounded-full blur-[120px] pointer-events-none -translate-y-1/2 translate-x-1/3" />

        <div className="w-full max-w-7xl mx-auto relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="mb-24"
          >
            <h1 className="text-4xl md:text-5xl lg:text-6xl leading-[1.1] md:leading-[1.1] font-black tracking-tighter uppercase text-slate-900 dark:text-white">
              {t("hero_title")}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-500">
                {t("hero_subtitle")}
              </span>
            </h1>
          </motion.div>

          <div className="flex flex-col lg:flex-row gap-16 lg:gap-24">
            <div className="lg:w-1/3">
              <motion.h2
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                className="text-2xl font-bold uppercase tracking-widest text-slate-400 dark:text-slate-500 sticky top-32"
              >
                {t("section_general")}
              </motion.h2>
            </div>
            <div className="lg:w-2/3 border-t border-slate-200 dark:border-slate-800 text-justify">
              {generalFaqs.map((faq, index) => (
                <FAQItem
                  key={index}
                  question={faq.q}
                  answer={faq.a}
                  isOpen={activeGeneral === index}
                  onClick={() =>
                    setActiveGeneral(activeGeneral === index ? null : index)
                  }
                />
              ))}
            </div>
          </div>
        </div>
      </section>

      <section
        id="technical"
        className="relative min-h-screen py-24 px-6 md:px-12 bg-slate-950 text-white overflow-hidden rounded-t-[3rem] shadow-[0_-20px_50px_-20px_rgba(0,0,0,0.1)]"
      >
        <div className="absolute bottom-0 left-0 w-[50vw] h-[50vw] bg-indigo-500/10 rounded-full blur-[120px] pointer-events-none translate-y-1/2 -translate-x-1/3" />

        <div className="w-full max-w-7xl mx-auto relative z-10">
          <div className="flex flex-col lg:flex-row gap-16 lg:gap-24">
            <div className="lg:w-1/3">
              <motion.h2
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                className="text-2xl font-bold uppercase tracking-widest text-slate-500 sticky top-32"
              >
                {t("section_technical")}
              </motion.h2>
            </div>
            <div className="lg:w-2/3 border-t border-slate-800">
              {technicalFaqs.map((faq, index) => (
                <FAQItem
                  key={index}
                  question={faq.q}
                  answer={faq.a}
                  isOpen={activeTech === index}
                  onClick={() =>
                    setActiveTech(activeTech === index ? null : index)
                  }
                  isDarkSection={true}
                />
              ))}
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
