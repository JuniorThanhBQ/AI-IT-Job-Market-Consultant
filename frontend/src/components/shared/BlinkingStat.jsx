"use client";

import React, { useRef } from "react";
import { motion, useInView } from "motion/react";

export default function BlinkingStat({ targetValue, label }) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <div
      ref={ref}
      className="flex flex-col items-center justify-center p-6 md:p-8 bg-white/80 dark:bg-slate-900/40 backdrop-blur-md rounded-[2.5rem] border border-slate-200 dark:border-slate-800 shadow-2xl transition-all duration-500 hover:scale-105 hover:bg-white/90 dark:hover:bg-slate-900/50"
    >
      <motion.span
        animate={
          isInView
            ? {
                opacity: [1, 0, 1, 0, 1, 0, 1],
              }
            : {
                opacity: 0,
              }
        }
        transition={{
          duration: 1.5,
          times: [0, 0.16, 0.33, 0.5, 0.66, 0.83, 1],
          ease: "easeInOut",
        }}
        className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-black tracking-tight mb-4 min-h-[1.2em] font-mono text-transparent bg-clip-text bg-gradient-to-r from-blue-600 via-indigo-500 to-blue-600 dark:from-white dark:via-blue-100 dark:to-white"
      >
        {targetValue}
      </motion.span>
      <span className="text-sm md:text-base font-bold uppercase tracking-widest text-slate-500 dark:text-blue-200 text-center">
        {label}
      </span>
    </div>
  );
}
