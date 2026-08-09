"use client";

import { motion } from "motion/react";
import { Loader2 } from "lucide-react";
import Header from "@/components/shared/Header";
import { useConsultantData } from "./Hooks/useConsultantData";
import ConsultantHeader from "./Components/ConsultantHeader";
import MarketDemandCard from "./Components/MarketDemandCard";
import ConsultantSkillsChart from "./Components/ConsultantSkillsChart";
import ConsultantAdviceCard from "./Components/ConsultantAdviceCard";
import ConsultantJobMatches from "./Components/ConsultantJobMatches";

export default function ConsultantPage() {
  const {
    user,
    authLoading,
    marketSummary,
    skillsData,
    recommendations,
    recommendedJobs,
  } = useConsultantData();

  if (authLoading || !user) {
    return (
      <div className="min-h-screen w-full flex items-center justify-center bg-slate-50 dark:bg-slate-955 text-slate-900 dark:text-white transition-colors duration-300">
        <Loader2 className="w-8 h-8 animate-spin text-[#285872]" />
      </div>
    );
  }

  return (
    <div className="relative min-h-screen bg-slate-50 dark:bg-slate-955 text-slate-900 dark:text-slate-100 font-sans transition-colors duration-300 pb-20">
      <div className="pointer-events-none absolute inset-0 z-0 opacity-[0.03] dark:opacity-[0.05] mix-blend-overlay">
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
          scale: [1, 1.15, 0.95, 1],
        }}
        transition={{ duration: 25, repeat: Infinity, ease: "easeInOut" }}
        className="absolute top-0 right-0 w-[50vw] h-[50vw] bg-[#285872]/10 dark:bg-[#285872]/15 rounded-full blur-[140px] pointer-events-none z-0"
      />
      <motion.div
        animate={{
          x: [0, -30, 20, 0],
          y: [0, 35, -20, 0],
          scale: [1, 1.1, 0.9, 1],
        }}
        transition={{ duration: 30, repeat: Infinity, ease: "easeInOut" }}
        className="absolute bottom-0 left-0 w-[45vw] h-[45vw] bg-[#285872]/10 dark:bg-[#285872]/10 rounded-full blur-[140px] pointer-events-none z-0"
      />

      <Header />

      <main className="relative z-10 max-w-7xl mx-auto px-6 pt-28 flex flex-col gap-8">
        <ConsultantHeader />

        <section className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 flex flex-col gap-8">
            <MarketDemandCard marketSummary={marketSummary} />
            <ConsultantSkillsChart skillsData={skillsData} />
          </div>

          <div className="lg:col-span-1 flex flex-col gap-8">
            <ConsultantAdviceCard recommendations={recommendations} />
          </div>
        </section>

        <ConsultantJobMatches recommendedJobs={recommendedJobs} />
      </main>
    </div>
  );
}
