"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { Plus } from "lucide-react";
import VerticalScrollbar from "@/components/shared/VerticalScrollbar";
import { useTranslations } from "next-intl";

const FAQItem = ({
  question,
  answer,
  isOpen,
  onClick,
  isDarkSection = false,
}) => {
  const borderColor = isDarkSection
    ? "border-slate-800"
    : "border-slate-200 dark:border-slate-800";

  const titleColor = isOpen
    ? isDarkSection
      ? "text-blue-400"
      : "text-blue-600 dark:text-blue-400"
    : isDarkSection
      ? "text-white group-hover:text-blue-400"
      : "text-slate-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400";

  const iconColor = isOpen
    ? isDarkSection
      ? "border-blue-400 text-blue-400 bg-blue-900/20"
      : "border-blue-600 text-blue-600 dark:border-blue-400 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20"
    : isDarkSection
      ? "border-slate-700 text-slate-400 group-hover:border-blue-400 group-hover:text-blue-400"
      : "border-slate-200 dark:border-slate-800 text-slate-400 group-hover:border-blue-600 group-hover:text-blue-600 dark:group-hover:border-blue-400 dark:group-hover:text-blue-400";

  const answerColor = isDarkSection
    ? "text-slate-400"
    : "text-slate-600 dark:text-slate-400";

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-10%" }}
      className={`border-b ${borderColor}`}
    >
      <button
        onClick={onClick}
        className="w-full flex justify-between items-center py-8 md:py-10 text-left group"
      >
        <h3
          className={`text-2xl md:text-4xl font-bold tracking-tight transition-colors duration-300 pr-8 ${titleColor}`}
        >
          {question}
        </h3>
        <motion.div
          animate={{ rotate: isOpen ? 45 : 0 }}
          transition={{ duration: 0.3, ease: "easeInOut" }}
          className={`flex-shrink-0 w-12 h-12 rounded-full border flex items-center justify-center transition-colors duration-300 ${iconColor}`}
        >
          <Plus className="w-6 h-6" />
        </motion.div>
      </button>
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
            className="overflow-hidden"
          >
            <p
              className={`pb-10 text-lg md:text-xl leading-relaxed max-w-4xl ${answerColor}`}
            >
              {answer}
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default function FAQ() {
  const t = useTranslations("FAQ");
  const generalFaqs = t.raw("general_faqs");
  const technicalFaqs = t.raw("technical_faqs");

  const [activeGeneral, setActiveGeneral] = useState(0);
  const [activeTech, setActiveTech] = useState(0);

  const sections = [
    { id: "general", label: t("nav_general") },
    { id: "technical", label: t("nav_technical") },
  ];

  return (
    <div className="relative w-full bg-slate-50 dark:bg-slate-950">
      <VerticalScrollbar sections={sections} />

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
            <h1 className="text-4xl md:text-5xl lg:text-6xl leading-[0.9] font-black tracking-tighter uppercase text-slate-900 dark:text-white">
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
            <div className="lg:w-2/3 border-t border-slate-200 dark:border-slate-800">
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
