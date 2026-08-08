"use client";

import { useState, useEffect } from "react";
import { motion } from "motion/react";
import {
  TrendingUp,
  Award,
  Building,
  User,
  Briefcase,
  DollarSign,
  Loader2,
  Calendar,
  Sparkles,
  BarChart2,
  ChevronRight,
  BookOpen,
  MapPin,
} from "lucide-react";
import { useAuth } from "@/context/AuthProvider";
import { Link, useRouter } from "@/i18n/routing";
import { useLocale, useTranslations } from "next-intl";
import Header from "@/components/shared/Header";

export default function ConsultantPage() {
  const { user, authLoading } = useAuth();
  const router = useRouter();
  const locale = useLocale();
  const t = useTranslations("Counselee.Consultant");

  useEffect(() => {
    if (!authLoading && !user) {
      router.replace("/counselee/login");
    }
  }, [user, authLoading, router]);

  const marketSummary = {
    totalOpenings: "1,248",
    growth: "+14.2%",
    avgSalary: "$1,850",
    topField: "AI & Cloud Engineering",
    desc: t("market_summary_desc"),
  };

  const skillsData = [
    { name: "React / Next.js", percentage: 86, color: "bg-[#285872]" },
    {
      name: "Python / PyTorch / FastAPI",
      percentage: 78,
      color: "bg-[#387494]",
    },
    { name: "Node.js / Express", percentage: 65, color: "bg-[#458bad]" },
    { name: "AWS / GCP Infrastructure", percentage: 58, color: "bg-[#54a1c6]" },
    { name: "Docker / Kubernetes", percentage: 52, color: "bg-[#6ab3d8]" },
    { name: "SQL & Relational DBs", percentage: 46, color: "bg-[#81c5e8]" },
  ];

  const recommendations = [
    {
      title: t("rec_1_title"),
      desc: t("rec_1_desc"),
    },
    {
      title: t("rec_2_title"),
      desc: t("rec_2_desc"),
    },
    {
      title: t("rec_3_title"),
      desc: t("rec_3_desc"),
    },
  ];

  const recommendedJobs = [
    {
      id: 1,
      title: "Senior React Engineer",
      company: "VNG Corporation",
      matchScore: 98,
      salary: "$2,200 - $3,000",
      location: "HCMC",
      model: "Hybrid",
      tags: ["React", "Senior", "TypeScript"],
    },
    {
      id: 2,
      title: "AI Python Developer",
      company: "FPT Software",
      matchScore: 94,
      salary: "$1,500 - $2,500",
      location: "HCMC",
      model: "Onsite",
      tags: ["Python", "FastAPI", "AI Agents"],
    },
    {
      id: 3,
      title: "Fullstack Node.js Developer",
      company: "VinGroup Tech",
      matchScore: 91,
      salary: "$1,800 - $2,600",
      location: "Remote / Hanoi",
      model: "Remote",
      tags: ["Node.js", "React", "Docker"],
    },
  ];

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
        <div className="flex flex-col md:flex-row md:items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-4 gap-4">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white flex items-center gap-2.5">
              <Sparkles className="w-8 h-8 text-[#285872] animate-pulse" />
              {t("title")}
            </h1>
            <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
              {t("subtitle")}
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Link
              href="/counselee/jobs"
              className="bg-[#285872] hover:bg-[#1c3f52] text-white rounded-full px-5 py-2.5 font-bold text-xs tracking-wide shadow-lg transition-all hover:scale-105"
            >
              {t("back_market")}
            </Link>
          </div>
        </div>

        <section className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 flex flex-col gap-8">
            <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-8 backdrop-blur-md shadow-sm">
              <h2 className="text-xl font-extrabold text-slate-900 dark:text-white flex items-center gap-2.5 mb-6 border-b border-slate-100 dark:border-slate-800 pb-3">
                <TrendingUp className="w-5 h-5 text-[#285872]" />
                {t("demand_title")}
              </h2>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
                <div className="bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-850 rounded-2xl p-4">
                  <span className="text-[10px] font-bold text-slate-450 dark:text-slate-500 uppercase tracking-widest block mb-1">
                    {t("active_openings")}
                  </span>
                  <p className="text-2xl font-black text-[#285872]">
                    {marketSummary.totalOpenings}
                  </p>
                  <span className="text-[10px] font-bold text-emerald-600 dark:text-emerald-450">
                    {marketSummary.growth} {t("active_openings_index")}
                  </span>
                </div>
                <div className="bg-slate-50 dark:bg-slate-955 border border-slate-200 dark:border-slate-850 rounded-2xl p-4">
                  <span className="text-[10px] font-bold text-slate-450 dark:text-slate-500 uppercase tracking-widest block mb-1">
                    {t("avg_salary")}
                  </span>
                  <p className="text-2xl font-black text-slate-900 dark:text-white">
                    {marketSummary.avgSalary}
                  </p>
                  <span className="text-[10px] font-medium text-slate-450">
                    {t("avg_salary_median")}
                  </span>
                </div>
                <div className="bg-slate-50 dark:bg-slate-955 border border-slate-200 dark:border-slate-850 rounded-2xl p-4 col-span-2">
                  <span className="text-[10px] font-bold text-slate-450 dark:text-slate-500 uppercase tracking-widest block mb-1">
                    {t("growth_domain")}
                  </span>
                  <p className="text-lg font-extrabold text-slate-900 dark:text-white mt-1.5">
                    {marketSummary.topField}
                  </p>
                </div>
              </div>
              <p className="text-sm font-medium text-slate-650 dark:text-slate-350 leading-relaxed">
                {marketSummary.desc}
              </p>
            </div>

            <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-8 backdrop-blur-md shadow-sm">
              <h2 className="text-xl font-extrabold text-slate-900 dark:text-white flex items-center gap-2.5 mb-6 border-b border-slate-100 dark:border-slate-800 pb-3">
                <BarChart2 className="w-5 h-5 text-[#285872]" />
                {t("skills_chart")}
              </h2>
              <div className="flex flex-col gap-5">
                {skillsData.map((skill, index) => (
                  <div key={index} className="flex flex-col gap-1.5">
                    <div className="flex justify-between items-center text-xs font-bold">
                      <span className="text-slate-700 dark:text-slate-300">
                        {skill.name}
                      </span>
                      <span className="text-[#285872]">
                        {t("skills_postings", { percentage: skill.percentage })}
                      </span>
                    </div>
                    <div className="w-full h-3 bg-slate-100 dark:bg-slate-955 border border-slate-200 dark:border-slate-850/80 rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${skill.percentage}%` }}
                        transition={{ duration: 1, delay: index * 0.1 }}
                        className={`h-full ${skill.color} rounded-full`}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="lg:col-span-1 flex flex-col gap-8">
            <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-8 backdrop-blur-md shadow-sm">
              <h2 className="text-xl font-extrabold text-slate-900 dark:text-white flex items-center gap-2.5 mb-6 border-b border-slate-100 dark:border-slate-800 pb-3">
                <Award className="w-5 h-5 text-[#285872]" />
                {t("consultant_title")}
              </h2>
              <div className="flex flex-col gap-6">
                {recommendations.map((rec, index) => (
                  <div key={index} className="flex gap-4">
                    <div className="w-8 h-8 rounded-full bg-[#285872]/10 border border-[#285872]/20 flex items-center justify-center shrink-0 text-[#285872] font-black text-xs">
                      {index + 1}
                    </div>
                    <div>
                      <h4 className="text-sm font-extrabold text-slate-900 dark:text-white mb-1">
                        {rec.title}
                      </h4>
                      <p className="text-xs text-slate-550 dark:text-slate-400 leading-relaxed font-medium">
                        {rec.desc}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2.5rem] p-8 backdrop-blur-md shadow-sm w-full">
          <h2 className="text-xl font-extrabold text-slate-900 dark:text-white flex items-center gap-2.5 mb-6 border-b border-slate-100 dark:border-slate-800 pb-3">
            <BookOpen className="w-5 h-5 text-[#285872]" />
            {t("jobs_title")}
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {recommendedJobs.map((job) => (
              <div
                key={job.id}
                className="bg-slate-50/40 dark:bg-slate-950/20 border border-slate-200 dark:border-slate-850 rounded-[2rem] p-6 flex flex-col justify-between gap-6 hover:border-slate-350 dark:hover:border-slate-800 transition-all group"
              >
                <div className="flex flex-col gap-3">
                  <div className="flex justify-between items-start gap-2">
                    <span className="bg-emerald-100 dark:bg-emerald-955/40 text-emerald-600 px-3 py-1 rounded-full text-[9px] font-black tracking-wider uppercase">
                      {t("match", { matchScore: job.matchScore })}
                    </span>
                    <span className="text-xs font-bold text-slate-450 flex items-center gap-1">
                      <MapPin className="w-3.5 h-3.5" />
                      {job.location}
                    </span>
                  </div>
                  <div>
                    <h3 className="text-base font-extrabold text-slate-900 dark:text-white group-hover:text-[#285872] transition-colors line-clamp-1">
                      {job.title}
                    </h3>
                    <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mt-0.5">
                      {job.company}
                    </p>
                  </div>
                  <div className="flex flex-wrap gap-1.5 mt-1">
                    {job.tags.map((tag, tIndex) => (
                      <span
                        key={tIndex}
                        className="bg-slate-100 dark:bg-slate-900 text-slate-600 dark:text-slate-400 px-2.5 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="flex items-center justify-between border-t border-slate-200 dark:border-slate-800/80 pt-4 mt-1">
                  <span className="text-xs font-extrabold text-emerald-600 flex items-center">
                    <DollarSign className="w-4 h-4 shrink-0" />
                    {job.salary}
                  </span>
                  <Link
                    href={`/counselee/jobs`}
                    className="text-[10px] text-[#285872] font-black uppercase tracking-wider flex items-center gap-0.5"
                  >
                    {t("view_details")}
                    <ChevronRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}
