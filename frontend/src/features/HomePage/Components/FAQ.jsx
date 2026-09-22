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
        className="relative min-h-screen pt-32 pb-20 px-6 md:px-12 bg-slate-50 dark:bg-slate-950"
      >
        <div className="w-full max-w-7xl mx-auto relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="mb-16 md:mb-20"
          >
            <h1 className="text-2xl md:text-3xl lg:text-4xl leading-[1.2] font-black tracking-tighter uppercase text-slate-900 dark:text-white">
              {t("hero_title")}
              <span className="text-[#285872] dark:text-sky-400">
                {" "}
                {t("hero_subtitle")}
              </span>
            </h1>
          </motion.div>

          <div className="flex flex-col lg:flex-row gap-12 lg:gap-16">
            <div className="lg:w-1/3">
              <motion.h2
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                className="text-base md:text-lg font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500"
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
        className="relative min-h-screen py-20 px-6 md:px-12 bg-slate-100 dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800"
      >
        <div className="w-full max-w-7xl mx-auto relative z-10">
          <div className="flex flex-col lg:flex-row gap-12 lg:gap-16">
            <div className="lg:w-1/3">
              <motion.h2
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                className="text-base md:text-lg font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400"
              >
                {t("section_technical")}
              </motion.h2>
            </div>
            <div className="lg:w-2/3 border-t border-slate-200 dark:border-slate-800 text-justify">
              {technicalFaqs.map((faq, index) => (
                <FAQItem
                  key={index}
                  question={faq.q}
                  answer={faq.a}
                  isOpen={activeTech === index}
                  onClick={() =>
                    setActiveTech(activeTech === index ? null : index)
                  }
                />
              ))}
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
