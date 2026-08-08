"use client";

import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "motion/react";
import {
  User,
  TrendingUp,
  Award,
  Briefcase,
  DollarSign,
  Loader2,
  CheckCircle2,
  XCircle,
  BookOpen,
  MapPin,
  ShieldCheck,
} from "lucide-react";
import { useAuth } from "@/context/AuthProvider";
import { profileApi, cvApi, consultantApi } from "@/configs/apis";
import { useRouter } from "@/i18n/routing";
import { useLocale, useTranslations } from "next-intl";
import Header from "@/components/shared/Header";

export default function OverviewPage() {
  const { user, authLoading } = useAuth();
  const router = useRouter();
  const locale = useLocale();
  const t = useTranslations("Counselee.Overview");

  const [activeTab, setActiveTab] = useState("dashboard");
  const [profile, setProfile] = useState(null);
  const [cv, setCv] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [cvAnalysisData, setCvAnalysisData] = useState(null);
  const [marketAgentData, setMarketAgentData] = useState(null);

  useEffect(() => {
    if (!authLoading && !user) {
      router.replace("/counselee/login");
    }
  }, [user, authLoading, router]);

  const fetchProfileAndCv = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const profileData = await profileApi.getProfile();
      setProfile(profileData);
      const cvData = await cvApi.getCV();
      setCv(cvData);

      try {
        const marketData = await consultantApi.processAgentIntent(
          "MARKET_ANALYSIS",
          "DEMAND_TREND",
        );
        setMarketAgentData(marketData);
      } catch (err) {
        console.error(err);
      }

      try {
        const cvAnalysis = await consultantApi.processAgentIntent(
          "PERSONAL_STANDARD_EVALUATION",
          "CV_SCORE",
        );
        setCvAnalysisData(cvAnalysis);
        if (
          cvAnalysis?.tool_outputs?.personalization_analysis?.score !==
          undefined
        ) {
          setCv((prev) => ({
            ...prev,
            score: cvAnalysis.tool_outputs.personalization_analysis.score,
          }));
        }
      } catch (err) {
        console.error(err);
      }
    } catch (err) {
      setError("Could not fetch profile or CV data.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (user) {
      const timer = setTimeout(() => {
        fetchProfileAndCv();
      }, 0);
      return () => clearTimeout(timer);
    }
  }, [user, fetchProfileAndCv]);

  if (authLoading || loading) {
    return (
      <div className="min-h-screen w-full flex items-center justify-center bg-slate-50 dark:bg-slate-955 text-slate-900 dark:text-white transition-colors duration-300">
        <Loader2 className="w-8 h-8 animate-spin text-[#285872]" />
      </div>
    );
  }

  const checkpoints = [
    {
      label: t("checkpoint_page_count"),
      checked: cv ? !cv.exceed_page_limit : false,
    },
    {
      label: t("checkpoint_logical_structure"),
      checked: cv ? !cv.structure_illogical : false,
    },
    {
      label: t("checkpoint_text_recognition"),
      checked: cv ? !cv.bad_text_recognition : false,
    },
    {
      label: t("checkpoint_target_role"),
      checked: cv ? !!cv.job_position : false,
    },
    {
      label: t("checkpoint_skills_populated"),
      checked: cv ? !!(cv.skills && cv.skills.length > 0) : false,
    },
  ];

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
        <div className="flex flex-col md:flex-row md:items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-6 gap-4">
          <div>
            <h1 className="text-3xl font-black tracking-tight text-[#285872] dark:text-[#407c9c] flex items-center gap-2">
              {t("welcome_back", {
                name: profile?.first_name || user?.username,
              })}
            </h1>
            <p className="text-sm text-slate-555 mt-1">{t("subtitle")}</p>
          </div>
          <div className="flex bg-slate-100 dark:bg-slate-950 p-1 rounded-2xl border border-slate-200 dark:border-slate-850">
            <button
              onClick={() => setActiveTab("dashboard")}
              className={`px-5 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                activeTab === "dashboard"
                  ? "bg-[#285872] text-white shadow-md"
                  : "text-slate-555 hover:text-slate-855 dark:hover:text-slate-200"
              }`}
            >
              {t("tab_dashboard")}
            </button>
            <button
              onClick={() => setActiveTab("cv_analysis")}
              className={`px-5 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                activeTab === "cv_analysis"
                  ? "bg-[#285872] text-white shadow-md"
                  : "text-slate-555 hover:text-slate-855 dark:hover:text-slate-200"
              }`}
            >
              {t("tab_cv_analysis")}
            </button>
          </div>
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500/20 text-red-500 dark:text-red-400 rounded-[2rem] p-6 text-sm font-semibold">
            {error}
          </div>
        )}

        <AnimatePresence mode="wait">
          {activeTab === "dashboard" ? (
            <motion.div
              key="dashboard"
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -15 }}
              transition={{ duration: 0.2 }}
              className="grid grid-cols-1 lg:grid-cols-2 gap-8"
            >
              <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-8 backdrop-blur-md shadow-sm flex flex-col gap-6">
                <h2 className="text-xl font-extrabold text-slate-900 dark:text-white flex items-center gap-2.5 border-b border-slate-100 dark:border-slate-800 pb-3">
                  <User className="w-5.5 h-5.5 text-[#285872]" />
                  {t("profile_info")}
                </h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                  <div>
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block mb-0.5">
                      {t("first_name")}
                    </span>
                    <p className="text-sm font-bold text-slate-800 dark:text-slate-200">
                      {profile?.first_name || "—"}
                    </p>
                  </div>
                  <div>
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block mb-0.5">
                      {t("last_name")}
                    </span>
                    <p className="text-sm font-bold text-slate-800 dark:text-slate-200">
                      {profile?.last_name || "—"}
                    </p>
                  </div>
                  <div className="sm:col-span-2">
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block mb-0.5">
                      {t("birthday")}
                    </span>
                    <p className="text-sm font-bold text-slate-800 dark:text-slate-200">
                      {profile?.birthday
                        ? new Date(profile.birthday).toLocaleDateString()
                        : "—"}
                    </p>
                  </div>
                  <div className="sm:col-span-2">
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block mb-0.5">
                      {t("biography")}
                    </span>
                    <p className="text-sm font-medium text-slate-660 dark:text-slate-350 leading-relaxed whitespace-pre-line">
                      {profile?.biography || t("biography_empty")}
                    </p>
                  </div>
                  <div className="sm:col-span-2">
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block mb-0.5">
                      {t("career_goal")}
                    </span>
                    <p className="text-sm font-medium text-slate-655 dark:text-slate-300 leading-relaxed whitespace-pre-line">
                      {profile?.goal || t("goal_empty")}
                    </p>
                  </div>
                </div>
              </div>

              <div className="flex flex-col gap-8">
                <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-8 backdrop-blur-md shadow-sm">
                  <h2 className="text-xl font-extrabold text-slate-900 dark:text-white flex items-center gap-2.5 mb-6 border-b border-slate-100 dark:border-slate-800 pb-3">
                    <TrendingUp className="w-5.5 h-5.5 text-[#285872]" />
                    {t("market_trend")}
                  </h2>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-850 rounded-2xl p-4">
                      <span className="text-[10px] font-bold text-slate-450 uppercase tracking-widest block mb-1">
                        {t("target_role")}
                      </span>
                      <p className="text-base font-extrabold text-[#285872] line-clamp-1">
                        {trends.role}
                      </p>
                    </div>
                    <div className="bg-slate-50 dark:bg-slate-955 border border-slate-200 dark:border-slate-850 rounded-2xl p-4">
                      <span className="text-[10px] font-bold text-slate-450 uppercase tracking-widest block mb-1">
                        {t("active_postings")}
                      </span>
                      <p className="text-base font-extrabold text-slate-850 dark:text-white">
                        {trends.activeJobs}
                      </p>
                    </div>
                    <div className="bg-slate-50 dark:bg-slate-955 border border-slate-200 dark:border-slate-850 rounded-2xl p-4">
                      <span className="text-[10px] font-bold text-slate-450 uppercase tracking-widest block mb-1">
                        {t("avg_salary")}
                      </span>
                      <p className="text-base font-extrabold text-slate-850 dark:text-white">
                        {trends.salaryRange}
                      </p>
                    </div>
                    <div className="bg-slate-50 dark:bg-slate-955 border border-slate-200 dark:border-slate-850 rounded-2xl p-4">
                      <span className="text-[10px] font-bold text-slate-450 uppercase tracking-widest block mb-1">
                        {t("competition_rate")}
                      </span>
                      <p className="text-base font-extrabold text-slate-850 dark:text-white">
                        {trends.difficulty}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-8 backdrop-blur-md shadow-sm flex flex-col gap-6">
                  <div>
                    <h2 className="text-xl font-extrabold text-slate-900 dark:text-white flex items-center gap-2.5 border-b border-slate-100 dark:border-slate-800 pb-3">
                      <Award className="w-5.5 h-5.5 text-[#285872]" />
                      {t("skills_positions")}
                    </h2>
                  </div>

                  <div className="flex flex-col gap-4">
                    <div>
                      <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block mb-2">
                        {t("recommended_skills")}
                      </span>
                      <div className="flex flex-wrap gap-2">
                        {skillsSuggestions.map((skill, index) => (
                          <span
                            key={index}
                            className="bg-slate-100 dark:bg-slate-955 border border-slate-200 dark:border-slate-850 text-slate-700 dark:text-slate-355 px-3 py-1 rounded-xl text-xs font-bold"
                          >
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div className="mt-2">
                      <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block mb-2">
                        {t("target_job_tracks")}
                      </span>
                      <ul className="flex flex-col gap-2">
                        {jobPositions.map((pos, index) => (
                          <li
                            key={index}
                            className="flex items-center gap-2 text-xs font-semibold text-slate-655 dark:text-slate-300"
                          >
                            <Briefcase className="w-4 h-4 text-[#285872] shrink-0" />
                            {pos}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="cv_analysis"
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -15 }}
              transition={{ duration: 0.2 }}
              className="flex flex-col gap-8"
            >
              <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-8 backdrop-blur-md shadow-sm">
                <h2 className="text-xl font-extrabold text-slate-900 dark:text-white flex items-center gap-2.5 mb-6 border-b border-slate-100 dark:border-slate-800 pb-3">
                  <ShieldCheck className="w-5 h-5 text-[#285872]" />
                  {t("analysis_summary")}
                </h2>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
                  <div className="flex flex-col gap-4">
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block">
                      {t("boolean_checkpoints")}
                    </span>
                    <ul className="flex flex-col gap-3">
                      {checkpoints.map((cp, idx) => (
                        <li
                          key={idx}
                          className="flex items-center gap-3 text-xs font-semibold text-slate-700 dark:text-slate-350"
                        >
                          {cp.checked ? (
                            <CheckCircle2 className="w-5 h-5 text-emerald-500 shrink-0" />
                          ) : (
                            <XCircle className="w-5 h-5 text-red-500 shrink-0" />
                          )}
                          <span
                            className={
                              cp.checked
                                ? "text-slate-850 dark:text-slate-200"
                                : "text-slate-450"
                            }
                          >
                            {cp.label}
                          </span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="flex flex-col items-center justify-center border-t md:border-t-0 md:border-l border-slate-200 dark:border-slate-800 pt-6 md:pt-0 md:pl-8">
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block mb-4">
                      {t("total_cv_score")}
                    </span>
                    <div className="relative w-36 h-36 flex items-center justify-center">
                      <svg className="w-full h-full transform -rotate-90">
                        <circle
                          cx="72"
                          cy="72"
                          r="60"
                          className="stroke-slate-100 dark:stroke-slate-800"
                          strokeWidth="10"
                          fill="transparent"
                        />
                        <motion.circle
                          cx="72"
                          cy="72"
                          r="60"
                          className="stroke-[#285872] dark:stroke-[#407c9c]"
                          strokeWidth="10"
                          fill="transparent"
                          strokeDasharray={376.8}
                          initial={{ strokeDashoffset: 376.8 }}
                          animate={{
                            strokeDashoffset:
                              376.8 - (376.8 * (cv?.score || 0)) / 100,
                          }}
                          transition={{ duration: 1, ease: "easeOut" }}
                          strokeLinecap="round"
                        />
                      </svg>
                      <div className="absolute text-center">
                        <span className="text-3xl font-black text-slate-900 dark:text-white">
                          {cv?.score || 0}
                        </span>
                        <span className="text-[9px] font-black text-slate-450 block uppercase tracking-wider">
                          / 100
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-8 backdrop-blur-md shadow-sm">
                  <h2 className="text-lg font-extrabold text-emerald-600 dark:text-emerald-450 flex items-center gap-2 mb-4">
                    <CheckCircle2 className="w-5 h-5" />
                    {t("cv_advantages")}
                  </h2>
                  <ul className="flex flex-col gap-3 text-xs font-semibold text-slate-655 dark:text-slate-300 list-disc pl-5 leading-relaxed">
                    {cvAnalysisData?.tool_outputs?.personalization_analysis
                      ?.must_have?.length > 0 ? (
                      cvAnalysisData.tool_outputs.personalization_analysis.must_have.map(
                        (skill, idx) => (
                          <li key={idx}>
                            Đã đáp ứng kỹ năng thị trường: {skill}
                          </li>
                        ),
                      )
                    ) : (
                      <>
                        <li>{t("advantages_bullet1")}</li>
                        <li>{t("advantages_bullet2")}</li>
                        <li>{t("advantages_bullet3")}</li>
                        <li>{t("advantages_bullet4")}</li>
                      </>
                    )}
                  </ul>
                </div>

                <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-8 backdrop-blur-md shadow-sm">
                  <h2 className="text-lg font-extrabold text-red-500 dark:text-red-400 flex items-center gap-2 mb-4">
                    <XCircle className="w-5 h-5" />
                    {t("cv_disadvantages")}
                  </h2>
                  <ul className="flex flex-col gap-3 text-xs font-semibold text-slate-655 dark:text-slate-300 list-disc pl-5 leading-relaxed">
                    {cv?.exceed_page_limit && (
                      <li>{t("disadvantages_page_limit")}</li>
                    )}
                    {cv?.structure_illogical && (
                      <li>{t("disadvantages_structure")}</li>
                    )}
                    {cv?.bad_text_recognition && (
                      <li>{t("disadvantages_text_rec")}</li>
                    )}
                    {cvAnalysisData?.tool_outputs?.personalization_analysis
                      ?.need_to_import?.length > 0 ? (
                      cvAnalysisData.tool_outputs.personalization_analysis.need_to_import.map(
                        (skill, idx) => (
                          <li key={idx}>
                            Thiếu kỹ năng thị trường yêu cầu: {skill}
                          </li>
                        ),
                      )
                    ) : (
                      <li>{t("disadvantages_no_metrics")}</li>
                    )}
                  </ul>
                </div>
              </div>

              <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-8 backdrop-blur-md shadow-sm">
                <h2 className="text-xl font-extrabold text-slate-900 dark:text-white flex items-center gap-2.5 mb-4 border-b border-slate-100 dark:border-slate-800 pb-3">
                  <BookOpen className="w-5.5 h-5.5 text-[#285872]" />
                  {t("conclusion_suggestions")}
                </h2>
                <div className="flex flex-col gap-4">
                  <p className="text-sm font-semibold text-slate-700 dark:text-slate-350 leading-relaxed">
                    {cvAnalysisData?.tool_outputs?.personalization_analysis
                      ?.resume_improvement || t("conclusion_p1")}
                  </p>
                  {cvAnalysisData?.tool_outputs?.personalization_analysis
                    ?.nice_to_improve?.length > 0 && (
                    <ul className="flex flex-col gap-3 text-xs font-semibold text-slate-655 dark:text-slate-300 list-disc pl-5 leading-relaxed">
                      {cvAnalysisData.tool_outputs.personalization_analysis.nice_to_improve.map(
                        (skill, idx) => (
                          <li key={idx}>Nên cải thiện: {skill}</li>
                        ),
                      )}
                    </ul>
                  )}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}
