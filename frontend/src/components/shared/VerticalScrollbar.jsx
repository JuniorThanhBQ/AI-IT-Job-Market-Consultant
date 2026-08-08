"use client";

import { useSyncExternalStore } from "react";
import { createPortal } from "react-dom";
import { motion } from "motion/react";
import { useScrollSpy } from "@/hooks/useScrollSpy";

const emptySubscribe = () => () => {};

export default function VerticalScrollbar({ sections }) {
  const isMounted = useSyncExternalStore(
    emptySubscribe,
    () => true,
    () => false,
  );

  const activeId = useScrollSpy(sections.map((s) => s.id));

  const scrollTo = (id) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: "smooth" });
    }
  };

  if (!isMounted) return null;

  return createPortal(
    <div className="fixed right-6 top-1/2 -translate-y-1/2 z-[100] flex flex-col gap-4 pointer-events-auto">
      {sections.map((section) => (
        <button
          key={section.id}
          onClick={() => scrollTo(section.id)}
          className="group relative flex items-center justify-end"
        >
          <span className="absolute right-8 opacity-0 group-hover:opacity-100 transition-opacity text-xs font-medium bg-slate-800 text-white px-2 py-1 rounded whitespace-nowrap">
            {section.label}
          </span>
          <motion.div
            className={`w-3 h-3 rounded-full transition-colors ${
              activeId === section.id
                ? "bg-blue-600"
                : "bg-slate-300 dark:bg-slate-700"
            }`}
            whileHover={{ scale: 1.5 }}
          />
        </button>
      ))}
    </div>,
    document.body,
  );
}
