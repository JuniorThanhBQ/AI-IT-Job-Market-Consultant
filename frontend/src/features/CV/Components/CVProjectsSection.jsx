"use client";

import {
  Briefcase,
  Plus,
  Edit2,
  Trash2,
  Calendar,
  Users,
  Link2,
  Lock,
} from "lucide-react";
import { useTranslations } from "next-intl";

export default function CVProjectsSection({
  projects,
  onOpenAddProject,
  onOpenEditProject,
  onDeleteProject,
  locked = false,
}) {
  const t = useTranslations("Counselee.CV");

  return (
    <div className="relative bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-8 backdrop-blur-md shadow-sm flex flex-col gap-6">
      {locked && (
        <div className="absolute inset-0 bg-white/70 dark:bg-slate-900/70 backdrop-blur-sm rounded-[2rem] z-10 flex flex-col items-center justify-center gap-3">
          <Lock className="w-6 h-6 text-slate-400" />
          <span className="text-xs font-bold text-slate-400 text-center px-4">
            Locked — using uploaded CV for analysis
          </span>
        </div>
      )}
      <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-4">
        <h2 className="text-xl font-extrabold text-slate-900 dark:text-white flex items-center gap-2.5">
          <Briefcase className="w-5 h-5 text-[#285872]" />
          {t("projects_title", { count: projects.length })}
        </h2>
        <button
          type="button"
          onClick={onOpenAddProject}
          className="bg-[#285872] hover:bg-[#1c3f52] text-white rounded-xl px-4 py-2 text-xs font-bold transition-all hover:scale-105 inline-flex items-center gap-1.5 cursor-pointer"
        >
          <Plus className="w-3.5 h-3.5" />
          {t("add_project")}
        </button>
      </div>

      {projects.length === 0 ? (
        <p className="text-xs text-slate-400 font-medium py-4 text-center">
          {t("no_projects")}
        </p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {projects.map((proj) => (
            <div
              key={proj.id}
              className="bg-slate-50 dark:bg-slate-955 border border-slate-200 dark:border-slate-850 rounded-2xl p-5 flex flex-col justify-between gap-4"
            >
              <div className="flex flex-col gap-2">
                <div className="flex items-start justify-between gap-2">
                  <h3 className="text-sm font-extrabold text-slate-900 dark:text-white leading-tight">
                    {proj.name}
                  </h3>
                  <div className="flex items-center gap-1">
                    <button
                      type="button"
                      onClick={() => onOpenEditProject(proj)}
                      className="p-1 text-slate-400 hover:text-[#285872] transition-colors"
                    >
                      <Edit2 className="w-3.5 h-3.5" />
                    </button>
                    <button
                      type="button"
                      onClick={() => onDeleteProject(proj.id)}
                      className="p-1 text-slate-400 hover:text-red-500 transition-colors"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>

                <span className="text-[11px] font-bold text-[#285872] uppercase tracking-wider">
                  {proj.role}
                </span>

                <div className="flex items-center gap-4 text-[10px] text-slate-400 font-semibold mt-1">
                  <span className="flex items-center gap-1">
                    <Calendar className="w-3 h-3" />
                    {proj.start_date
                      ? new Date(proj.start_date).toLocaleDateString()
                      : ""}{" "}
                    -{" "}
                    {proj.end_date
                      ? new Date(proj.end_date).toLocaleDateString()
                      : "Present"}
                  </span>
                  <span className="flex items-center gap-1">
                    <Users className="w-3 h-3" />
                    {proj.team_size || 1}
                  </span>
                </div>

                <p className="text-xs font-medium text-slate-650 dark:text-slate-350 leading-relaxed mt-2 whitespace-pre-line">
                  {proj.description}
                </p>

                {proj.responsibilities && (
                  <div className="mt-2 text-xs font-medium text-slate-600 dark:text-slate-400">
                    <span className="font-bold text-slate-700 dark:text-slate-300 block mb-1">
                      Responsibilities:
                    </span>
                    <p className="whitespace-pre-line">
                      {proj.responsibilities}
                    </p>
                  </div>
                )}
              </div>

              <div className="flex flex-col gap-2 pt-3 border-t border-slate-200 dark:border-slate-850">
                <div className="flex flex-wrap gap-1.5">
                  {proj.tech_stacks?.map((tItem, tIdx) => (
                    <span
                      key={tIdx}
                      className="bg-slate-200/60 dark:bg-slate-900 text-slate-700 dark:text-slate-300 px-2 py-0.5 rounded text-[9px] font-bold"
                    >
                      {tItem}
                    </span>
                  ))}
                </div>

                {proj.link && (
                  <a
                    href={proj.link}
                    target="_blank"
                    rel="noreferrer"
                    className="text-[11px] font-bold text-[#285872] hover:underline flex items-center gap-1 self-start"
                  >
                    <Link2 className="w-3 h-3" />
                    Project Link
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
