"use client";

import { motion } from "motion/react";
import {
  ShieldCheck,
  CheckCircle2,
  XCircle,
  BookOpen,
  Sparkles,
  Loader2,
  RefreshCw,
} from "lucide-react";
import { useTranslations } from "next-intl";

export default function CVAnalysisTab({
  cv,
  cvAnalysisData,
  loadingCVAnalysis,
  hasCVAnalysis,
  onFetchCVAnalysis,
}) {
  const t = useTranslations("Counselee.Overview");

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

  return (
    <motion.div
      key="cv_analysis"
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -15 }}
      transition={{ duration: 0.2 }}
      className="flex flex-col gap-8"
    >
      <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-8 backdrop-blur-md shadow-sm">
        <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3 mb-6">
          <h2 className="text-xl font-extrabold text-slate-900 dark:text-white flex items-center gap-2.5">
            <ShieldCheck className="w-5 h-5 text-[#285872]" />
            {t("analysis_summary")}
          </h2>
          <button
            type="button"
            onClick={onFetchCVAnalysis}
            disabled={loadingCVAnalysis}
            className="bg-[#285872]/10 hover:bg-[#285872]/20 dark:bg-[#285872]/20 dark:hover:bg-[#285872]/30 text-[#285872] dark:text-[#58a0c9] border border-[#285872]/30 rounded-xl px-4 py-2 text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
          >
            {loadingCVAnalysis ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : hasCVAnalysis ? (
              <RefreshCw className="w-3.5 h-3.5" />
            ) : (
              <Sparkles className="w-3.5 h-3.5" />
            )}
            {loadingCVAnalysis
              ? "Analyzing CV..."
              : hasCVAnalysis
                ? "Re-analyze CV"
                : "Analyze CV with AI"}
          </button>
        </div>

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
                    strokeDashoffset: 376.8 - (376.8 * (cv?.score || 0)) / 100,
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
            {cvAnalysisData?.tool_outputs?.personalization_analysis?.must_have
              ?.length > 0 ? (
              cvAnalysisData.tool_outputs.personalization_analysis.must_have.map(
                (skill, idx) => (
                  <li key={idx}>Đã đáp ứng kỹ năng thị trường: {skill}</li>
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
            {cv?.exceed_page_limit && <li>{t("disadvantages_page_limit")}</li>}
            {cv?.structure_illogical && <li>{t("disadvantages_structure")}</li>}
            {cv?.bad_text_recognition && <li>{t("disadvantages_text_rec")}</li>}
            {cvAnalysisData?.tool_outputs?.personalization_analysis
              ?.need_to_import?.length > 0 ? (
              cvAnalysisData.tool_outputs.personalization_analysis.need_to_import.map(
                (skill, idx) => (
                  <li key={idx}>Thiếu kỹ năng thị trường yêu cầu: {skill}</li>
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
  );
}
