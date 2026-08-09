"use client";

import { motion } from "motion/react";
import { useTranslations } from "next-intl";

export default function CVProjectModal({
  showProjectForm,
  onClose,
  editingProject,
  projectName,
  setProjectName,
  projectRole,
  setProjectRole,
  projectTechs,
  setProjectTechs,
  projectDesc,
  setProjectDesc,
  projectStart,
  setProjectStart,
  projectEnd,
  setProjectEnd,
  projectLink,
  setProjectLink,
  projectTeamSize,
  setProjectTeamSize,
  projectResp,
  setProjectResp,
  onSaveProject,
}) {
  const t = useTranslations("Counselee.CV");

  if (!showProjectForm) return null;

  return (
    <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-[2.5rem] p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl"
      >
        <h3 className="text-xl font-extrabold text-slate-900 dark:text-white mb-6">
          {editingProject ? t("btn_edit_project") : t("btn_add_project")}
        </h3>

        <form onSubmit={onSaveProject} className="flex flex-col gap-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block mb-1">
                Project Name *
              </label>
              <input
                required
                type="text"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                className="w-full bg-slate-50 dark:bg-slate-955 border border-slate-200 dark:border-slate-850 rounded-xl px-4 py-2.5 text-xs font-bold"
              />
            </div>
            <div>
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block mb-1">
                Role *
              </label>
              <input
                required
                type="text"
                value={projectRole}
                onChange={(e) => setProjectRole(e.target.value)}
                className="w-full bg-slate-50 dark:bg-slate-955 border border-slate-200 dark:border-slate-850 rounded-xl px-4 py-2.5 text-xs font-bold"
              />
            </div>
            <div>
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block mb-1">
                Start Date *
              </label>
              <input
                required
                type="date"
                value={projectStart}
                onChange={(e) => setProjectStart(e.target.value)}
                className="w-full bg-slate-50 dark:bg-slate-955 border border-slate-200 dark:border-slate-850 rounded-xl px-4 py-2.5 text-xs font-bold"
              />
            </div>
            <div>
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block mb-1">
                End Date (optional — leave empty if ongoing)
              </label>
              <input
                type="date"
                value={projectEnd}
                onChange={(e) => setProjectEnd(e.target.value)}
                className="w-full bg-slate-50 dark:bg-slate-955 border border-slate-200 dark:border-slate-850 rounded-xl px-4 py-2.5 text-xs font-bold"
              />
            </div>
            <div>
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block mb-1">
                Team Size
              </label>
              <input
                type="number"
                min="1"
                value={projectTeamSize}
                onChange={(e) => setProjectTeamSize(e.target.value)}
                className="w-full bg-slate-50 dark:bg-slate-955 border border-slate-200 dark:border-slate-850 rounded-xl px-4 py-2.5 text-xs font-bold"
              />
            </div>
            <div>
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block mb-1">
                Project Link
              </label>
              <input
                type="text"
                value={projectLink}
                onChange={(e) => setProjectLink(e.target.value)}
                placeholder="https://..."
                className="w-full bg-slate-50 dark:bg-slate-955 border border-slate-200 dark:border-slate-850 rounded-xl px-4 py-2.5 text-xs font-bold"
              />
            </div>
          </div>

          <div>
            <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block mb-1">
              Tech Stacks (comma separated)
            </label>
            <input
              type="text"
              value={projectTechs}
              onChange={(e) => setProjectTechs(e.target.value)}
              placeholder="e.g. React, Node.js, PostgreSQL"
              className="w-full bg-slate-50 dark:bg-slate-955 border border-slate-200 dark:border-slate-850 rounded-xl px-4 py-2.5 text-xs font-bold"
            />
          </div>

          <div>
            <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block mb-1">
              Description *
            </label>
            <textarea
              required
              rows={3}
              value={projectDesc}
              onChange={(e) => setProjectDesc(e.target.value)}
              className="w-full bg-slate-50 dark:bg-slate-955 border border-slate-200 dark:border-slate-850 rounded-xl px-4 py-2 text-xs font-medium"
            />
          </div>

          <div>
            <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block mb-1">
              Key Responsibilities
            </label>
            <textarea
              rows={3}
              value={projectResp}
              onChange={(e) => setProjectResp(e.target.value)}
              className="w-full bg-slate-50 dark:bg-slate-955 border border-slate-200 dark:border-slate-850 rounded-xl px-4 py-2 text-xs font-medium"
            />
          </div>

          <div className="flex justify-end gap-3 mt-4 border-t border-slate-100 dark:border-slate-800 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 text-slate-700 dark:text-slate-300 rounded-xl px-5 py-2.5 text-xs font-bold transition-colors cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="bg-[#285872] hover:bg-[#1c3f52] text-white rounded-xl px-6 py-2.5 text-xs font-bold transition-colors cursor-pointer"
            >
              Save Project
            </button>
          </div>
        </form>
      </motion.div>
    </div>
  );
}
