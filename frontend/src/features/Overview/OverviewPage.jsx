"use client";

import { motion, AnimatePresence } from "motion/react";
import { Loader2 } from "lucide-react";
import Header from "@/components/shared/Header";
import { useOverviewData } from "./Hooks/useOverviewData";
import OverviewHeaderBanner from "./Components/OverviewHeaderBanner";
import DashboardTab from "./Components/DashboardTab";

export default function OverviewPage() {
  const {
    user,
    authLoading,
    activeTab,
    setActiveTab,
    profile,
    cv,
    loading,
    loadingMarketData,
    error,
    cvAnalysisData,
    marketAgentData,
    fetchMarketAnalysis,
  } = useOverviewData();

  if (authLoading || loading) {
    return (
      <div className="min-h-screen w-full flex items-center justify-center bg-slate-50 dark:bg-slate-955 text-slate-900 dark:text-white transition-colors duration-300">
        <Loader2 className="w-8 h-8 animate-spin text-[#285872]" />
      </div>
    );
  }

  const getMarketTrends = () => {
    const role = cv?.job_position || "Software Developer";
    let activeJobs = "840+";
    let salaryRange = "$1,450 - $2,250";
    let difficulty = "Medium-High";
    let growth = "+18.4% YoY";

    try {
      if (marketAgentData?.tool_outputs?.market_overview) {
        const rawStats = marketAgentData.tool_outputs.market_overview;
        const overview =
          typeof rawStats === "string" ? JSON.parse(rawStats) : rawStats;
        if (overview.total_jobs !== undefined) {
          activeJobs = `${overview.total_jobs}`;
          difficulty = overview.total_jobs > 500 ? "High" : "Medium";
          growth = overview.total_jobs > 200 ? "+12.4% YoY" : "+5.2% YoY";
        }
        if (overview.salary_stats && overview.salary_stats.length > 0) {
          const stats = overview.salary_stats[0];
          salaryRange = `$${stats.min_salary.toLocaleString()} - $${stats.max_salary.toLocaleString()}`;
        }
      }
    } catch (err) {
      console.error(err);
    }

    return {
      role,
      activeJobs,
      salaryRange,
      difficulty,
      growth,
    };
  };

  const getSkillsSuggestions = () => {
    const dynamicSkills =
      cvAnalysisData?.tool_outputs?.personalization_analysis?.need_to_import;
    if (dynamicSkills && dynamicSkills.length > 0) {
      return dynamicSkills.map((skill) => skill.split(" (")[0]);
    }
    const role = (cv?.job_position || "").toLowerCase();
    if (role.includes("react") || role.includes("frontend")) {
      return [
        "Next.js & SSR frameworks",
        "TypeScript core modules",
        "Tailwind CSS customization",
        "Jest & React Testing Library",
        "Webpack/Vite bundling",
      ];
    }
    if (
      role.includes("python") ||
      role.includes("ai") ||
      role.includes("data")
    ) {
      return [
        "FastAPI & Async processing",
        "PyTorch / Tensor modeling",
        "Docker containerization",
        "PostgreSQL database optimization",
        "Pandas & Numpy analysis",
      ];
    }
    return [
      "Git & GitHub workflows",
      "Docker & container pipelines",
      "Linux system commands",
      "RESTful API architecture",
      "CI/CD automated testing",
    ];
  };

  const getJobPositions = () => {
    const role = cv?.job_position || "Developer";
    return [
      `Full-stack ${role} Engineer`,
      `Cloud Infrastructure & DevOps for ${role}`,
      `Technical Lead specializing in ${role} architectures`,
    ];
  };

  const trends = getMarketTrends();
  const skillsSuggestions = getSkillsSuggestions();
  const jobPositions = getJobPositions();

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
          x: [0, 20, -15, 0],
          y: [0, -30, 20, 0],
          scale: [1, 1.1, 0.95, 1],
        }}
        transition={{ duration: 25, repeat: Infinity, ease: "easeInOut" }}
        className="absolute top-0 right-0 w-[50vw] h-[50vw] bg-[#285872]/10 dark:bg-[#285872]/15 rounded-full blur-[140px] pointer-events-none z-0"
      />

      <Header />

      <main className="relative z-10 max-w-7xl mx-auto px-6 pt-28 flex flex-col gap-8">
        <OverviewHeaderBanner
          name={profile?.first_name || user?.username}
          activeTab={activeTab}
          setActiveTab={setActiveTab}
        />

        {error && (
          <div className="bg-red-500/10 border border-red-500/20 text-red-500 dark:text-red-400 rounded-[2rem] p-6 text-sm font-semibold">
            {error}
          </div>
        )}

        <AnimatePresence mode="wait">
          {activeTab === "dashboard" ? (
            <DashboardTab
              profile={profile}
              trends={trends}
              skillsSuggestions={skillsSuggestions}
              jobPositions={jobPositions}
              loadingMarketData={loadingMarketData}
              hasMarketData={!!marketAgentData}
              onFetchMarketAnalysis={fetchMarketAnalysis}
            />
          ) : (
            <h1></h1>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}
