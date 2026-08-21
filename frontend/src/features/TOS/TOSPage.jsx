"use client";

import TOSHeader from "./Components/TOSHeader";
import TOSNav from "./Components/TOSNav";
import TOSSections from "./Components/TOSSections";
import { motion } from "motion/react";
import { useTOSNavigation } from "./Hooks/useTOSNavigation";

export default function TOSPage() {
  const { scrollToSection } = useTOSNavigation();
  return (
    <div className="relative min-h-screen bg-slate-50 dark:bg-slate-955 text-slate-900 dark:text-slate-100 flex flex-col font-sans transition-colors duration-300">
      <div className="absolute inset-0 overflow-hidden pointer-events-none z-0">
        <div className="pointer-events-none absolute inset-0 opacity-[0.03] dark:opacity-[0.05] mix-blend-overlay">
          <svg className="w-full h-full">
            <filter id="noiseFilter">
              <feTurbulence
                type="fractalNoise"
                baseFrequency="0.75"
                numOctaves="3"
                stitchTiles="stitch"
              />
            </filter>
            <rect width="100%" height="100%" filter="url(#noiseFilter)" />
          </svg>
        </div>

        <motion.div
          animate={{
            x: [0, 30, -20, 0],
            y: [0, -40, 30, 0],
            scale: [1, 1.1, 0.95, 1],
          }}
          transition={{ duration: 25, repeat: Infinity, ease: "easeInOut" }}
          className="absolute top-0 right-0 w-[50vw] h-[50vw] bg-blue-500/10 dark:bg-blue-600/15 rounded-full blur-[130px]"
        />
        <motion.div
          animate={{
            x: [0, -30, 20, 0],
            y: [0, 30, -20, 0],
            scale: [1, 1.05, 0.9, 1],
          }}
          transition={{ duration: 30, repeat: Infinity, ease: "easeInOut" }}
          className="absolute bottom-0 left-0 w-[45vw] h-[45vw] bg-purple-500/10 dark:bg-purple-600/15 rounded-full blur-[130px]"
        />
      </div>

      <TOSHeader />

      <main className="relative z-10 flex-1 max-w-7xl w-full mx-auto px-6 py-12 flex flex-col lg:flex-row gap-8 min-h-0">
        <TOSNav onScrollToSection={scrollToSection} />
        <TOSSections />
      </main>
    </div>
  );
}
