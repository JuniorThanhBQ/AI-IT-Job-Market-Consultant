"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "motion/react";
import {
  FileText,
  Briefcase,
  BookOpen,
  Plus,
  Loader2,
  CheckCircle,
  AlertCircle,
  Save,
  ChevronLeft,
  Upload,
  Paperclip,
  Trash2,
  Edit2,
  Calendar,
  Users,
  Link2,
} from "lucide-react";
import { useAuth } from "@/context/AuthProvider";
import { cvApi } from "@/configs/apis";
import { Link, useRouter } from "@/i18n/routing";
import { useLocale, useTranslations } from "next-intl";
import Header from "@/components/shared/Header";
import { cn } from "@/lib/utils";

export default function CVPage() {
  const { user, authLoading } = useAuth();
  const router = useRouter();
  const locale = useLocale();
  const t = useTranslations("Counselee.CV");

  const [jobPosition, setJobPosition] = useState("");
  const [summary, setSummary] = useState("");
  const [education, setEducation] = useState("");
  const [skillsText, setSkillsText] = useState("");
  const [attachment, setAttachment] = useState("");
  const [usingCvMode, setUsingCvMode] = useState(false);
  const [projects, setProjects] = useState([]);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [showProjectForm, setShowProjectForm] = useState(false);
  const [editingProject, setEditingProject] = useState(null);
  const [projectName, setProjectName] = useState("");
  const [projectRole, setProjectRole] = useState("");
  const [projectTechs, setProjectTechs] = useState("");
  const [projectDesc, setProjectDesc] = useState("");
  const [projectStart, setProjectStart] = useState("");
  const [projectEnd, setProjectEnd] = useState("");
  const [projectLink, setProjectLink] = useState("");
  const [projectTeamSize, setProjectTeamSize] = useState(1);
  const [projectResp, setProjectResp] = useState("");

  const fileInputRef = useRef(null);

  useEffect(() => {
    if (!authLoading && !user) {
      router.replace("/counselee/login");
    }
  }, [user, authLoading, router]);

  const fetchCV = useCallback(async () => {
    if (!user) return;
    setLoading(true);
    setError("");
    try {
      const data = await cvApi.getCV();
      setJobPosition(data.job_position || "");
      setSummary(data.summary || "");
      setEducation(data.education || "");
      setSkillsText(data.skills ? data.skills.join(", ") : "");
      setAttachment(data.attachment || "");
      setUsingCvMode(data.using_cv_mode || false);
      setProjects(data.projects || []);
    } catch (err) {
      setError(t("error"));
    } finally {
      setLoading(false);
    }
  }, [user, t]);

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchCV();
    }, 0);
    return () => clearTimeout(timer);
  }, [fetchCV]);

  const handleSaveCV = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError("");
    setSuccess("");

    const parsedSkills = skillsText
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);

    try {
      await cvApi.updateCV({
        job_position: jobPosition,
        summary: summary,
        education: education,
        skills: parsedSkills,
        using_cv_mode: usingCvMode,
      });
      setSuccess(t("success"));
    } catch (err) {
      setError(t("error"));
    } finally {
      setSaving(false);
    }
  };

  const handleToggleCvMode = async (val) => {
    setUsingCvMode(val);
    try {
      await cvApi.updateCV({
        using_cv_mode: val,
      });
      setSuccess(
        t("success_cv_mode", {
          mode: val ? t("mode_attachment") : t("mode_fields"),
        }),
      );
    } catch (err) {
      setError(t("error_toggle"));
      setUsingCvMode(!val);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const fileExt = file.name.split(".").pop()?.toLowerCase();
    if (fileExt !== "pdf" && fileExt !== "docx") {
      setError(t("error_file_format"));
      return;
    }

    setUploading(true);
    setError("");
    setSuccess("");

    try {
      const res = await cvApi.uploadCVAttachment(file.name);
      setSuccess(res.message || t("success"));
      setAttachment(file.name);
      setUsingCvMode(true);
    } catch (err) {
      setError(t("error_upload"));
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const handleAddProjectClick = () => {
    setEditingProject(null);
    setProjectName("");
    setProjectRole("");
    setProjectTechs("");
    setProjectDesc("");
    setProjectStart("");
    setProjectEnd("");
    setProjectLink("");
    setProjectTeamSize(1);
    setProjectResp("");
    setShowProjectForm(true);
  };

  const handleEditProjectClick = (proj) => {
    setEditingProject(proj);
    setProjectName(proj.name || "");
    setProjectRole(proj.role || "");
    setProjectTechs(proj.tech_stacks ? proj.tech_stacks.join(", ") : "");
    setProjectDesc(proj.description || "");
    setProjectStart(proj.start_date || "");
    setProjectEnd(proj.end_date || "");
    setProjectLink(proj.link || "");
    setProjectTeamSize(proj.team_size || 1);
    setProjectResp(
      proj.responsibilities ? proj.responsibilities.join(", ") : "",
    );
    setShowProjectForm(true);
  };

  const handleDeleteProject = async (projectId) => {
    if (!window.confirm(t("confirm_delete"))) return;
    setError("");
    setSuccess("");
    try {
      await cvApi.deleteProject(projectId);
      setSuccess(t("success_delete"));
      await fetchCV();
    } catch (err) {
      setError(t("error_delete"));
    }
  };

  const handleSaveProject = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError("");
    setSuccess("");

    const parsedTechs = projectTechs
      .split(",")
      .map((t) => t.trim())
      .filter(Boolean);
    const parsedResp = projectResp
      .split(",")
      .map((r) => r.trim())
      .filter(Boolean);

    const payload = {
      name: projectName,
      role: projectRole,
      tech_stacks: parsedTechs,
      description: projectDesc,
      start_date: projectStart,
      end_date: projectEnd,
      link: projectLink,
      team_size: parseInt(projectTeamSize) || 1,
      responsibilities: parsedResp,
    };

    try {
      if (editingProject) {
        await cvApi.updateProject(editingProject.id, payload);
        setSuccess(t("success_project_save"));
      } else {
        await cvApi.createProject(payload);
        setSuccess(t("success_project_save"));
      }
      setShowProjectForm(false);
      await fetchCV();
    } catch (err) {
      setError(t("error_project_save"));
    } finally {
      setSaving(false);
    }
  };

  if (authLoading || loading) {
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

      <Header />

      <main className="relative z-10 max-w-7xl mx-auto px-6 pt-28 flex flex-col gap-8">
        <div className="flex items-center gap-3 border-b border-slate-200 dark:border-slate-800 pb-4">
          <Link
            href="/counselee/overview"
            className="p-2 border border-slate-200 dark:border-slate-850 hover:bg-slate-100 dark:hover:bg-slate-900 rounded-xl transition-all text-slate-650 dark:text-slate-355 cursor-pointer"
          >
            <ChevronLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="text-2xl font-black tracking-tight text-slate-900 dark:text-white flex items-center gap-2">
              <FileText className="w-6 h-6 text-[#285872]" />
              {t("title")}
            </h1>
            <p className="text-xs text-slate-555 dark:text-slate-400 mt-0.5">
              {t("subtitle")}
            </p>
          </div>
        </div>

        <AnimatePresence>
          {success && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 dark:text-emerald-450 rounded-2xl p-4 flex items-center gap-2.5 text-sm font-semibold"
            >
              <CheckCircle className="w-5 h-5 text-emerald-500 shrink-0" />
              <span>{success}</span>
              <button
                onClick={() => setSuccess("")}
                className="ml-auto text-emerald-500 hover:opacity-85 font-black text-xs cursor-pointer"
              >
                ✕
              </button>
            </motion.div>
          )}

          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="bg-red-500/10 border border-red-500/20 text-red-500 dark:text-red-400 rounded-2xl p-4 flex items-center gap-2.5 text-sm font-semibold"
            >
              <AlertCircle className="w-5 h-5 text-red-500 shrink-0" />
              <span>{error}</span>
              <button
                onClick={() => setError("")}
                className="ml-auto text-red-500 hover:opacity-85 font-black text-xs cursor-pointer"
              >
                ✕
              </button>
            </motion.div>
          )}
        </AnimatePresence>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          <div className="lg:col-span-5 bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-8 backdrop-blur-md shadow-sm flex flex-col gap-6">
            <h2 className="text-base font-extrabold text-slate-900 dark:text-white pb-2 border-b border-slate-100 dark:border-slate-800">
              Core CV Credentials
            </h2>

            <div className="bg-slate-50 dark:bg-slate-950 border border-slate-250 dark:border-slate-850 rounded-2xl p-5 flex flex-col gap-4">
              <div className="flex items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-[#285872]/10 border border-[#285872]/20 flex items-center justify-center text-[#285872] shrink-0">
                    <Paperclip className="w-4.5 h-4.5" />
                  </div>
                  <div className="min-w-0">
                    <h3 className="text-xs font-extrabold text-slate-900 dark:text-white">
                      {t("attached_cv")}
                    </h3>
                    <p className="text-[10px] text-slate-550 dark:text-slate-400 font-medium truncate max-w-[150px]">
                      {attachment ? attachment : t("no_cv")}
                    </p>
                  </div>
                </div>
                <div>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".pdf,.docx"
                    onChange={handleFileUpload}
                    className="hidden"
                  />
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    disabled={uploading}
                    className="bg-[#285872] hover:bg-[#1c3f52] disabled:opacity-50 text-white rounded-full px-3 py-1.5 font-bold text-[10px] tracking-wide shadow-md transition-all flex items-center gap-1 cursor-pointer"
                  >
                    {uploading ? (
                      <Loader2 className="w-3 animate-spin" />
                    ) : (
                      <Upload className="w-3 h-3" />
                    )}
                    {uploading ? t("btn_uploading") : t("btn_upload")}
                  </button>
                </div>
              </div>

              {attachment && (
                <div className="flex items-center gap-3 border-t border-slate-200 dark:border-slate-800 pt-3">
                  <label className="relative flex items-center gap-2 cursor-pointer select-none">
                    <input
                      type="checkbox"
                      checked={usingCvMode}
                      onChange={(e) => handleToggleCvMode(e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-8 h-4 bg-slate-300 dark:bg-slate-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-3 after:w-3 after:transition-all peer-checked:bg-[#285872]" />
                    <span className="text-[10px] font-extrabold text-slate-555 dark:text-slate-400 uppercase tracking-widest pl-1">
                      {t("analyze_attachment")}
                    </span>
                  </label>
                </div>
              )}
            </div>

            <form onSubmit={handleSaveCV} className="flex flex-col gap-5">
              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-bold text-slate-450 dark:text-slate-500 uppercase tracking-widest pl-1 flex items-center gap-1">
                  <Briefcase className="w-3.5 h-3.5 text-slate-400" />
                  {t("target_position")}
                </label>
                <input
                  type="text"
                  value={jobPosition}
                  onChange={(e) => setJobPosition(e.target.value)}
                  placeholder={t("target_position_placeholder")}
                  className="w-full bg-slate-50 dark:bg-slate-955 border border-slate-200 dark:border-slate-850 rounded-xl p-3 outline-none focus:ring-1 focus:ring-[#285872] text-sm text-slate-900 dark:text-white font-medium"
                />
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-bold text-slate-450 dark:text-slate-500 uppercase tracking-widest pl-1">
                  {t("summary")}
                </label>
                <textarea
                  value={summary}
                  onChange={(e) => setSummary(e.target.value)}
                  placeholder={t("summary_placeholder")}
                  className="w-full bg-slate-50 dark:bg-slate-955 border border-slate-200 dark:border-slate-850 rounded-xl p-3 outline-none focus:ring-1 focus:ring-[#285872] text-sm text-slate-900 dark:text-white font-medium"
                  rows={3}
                />
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-bold text-slate-450 dark:text-slate-500 uppercase tracking-widest pl-1 flex items-center gap-1">
                  <BookOpen className="w-3.5 h-3.5 text-slate-400" />
                  {t("education")}
                </label>
                <textarea
                  value={education}
                  onChange={(e) => setEducation(e.target.value)}
                  placeholder={t("education_placeholder")}
                  className="w-full bg-slate-50 dark:bg-slate-955 border border-slate-200 dark:border-slate-850 rounded-xl p-3 outline-none focus:ring-1 focus:ring-[#285872] text-sm text-slate-900 dark:text-white font-medium"
                  rows={3}
                />
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-bold text-slate-450 dark:text-slate-500 uppercase tracking-widest pl-1">
                  {t("skills")}
                </label>
                <input
                  type="text"
                  value={skillsText}
                  onChange={(e) => setSkillsText(e.target.value)}
                  placeholder={t("skills_placeholder")}
                  className="w-full bg-slate-50 dark:bg-slate-955 border border-slate-200 dark:border-slate-850 rounded-xl p-3 outline-none focus:ring-1 focus:ring-[#285872] text-sm text-slate-900 dark:text-white font-medium"
                />
              </div>

              <button
                type="submit"
                disabled={saving}
                className="bg-[#285872] hover:bg-[#1c3f52] disabled:opacity-50 text-white rounded-full px-6 py-3 font-bold text-sm tracking-wide shadow-lg transition-all hover:scale-102 flex items-center justify-center gap-2 cursor-pointer mt-2"
              >
                {saving ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Save className="w-4.5 h-4.5" />
                )}
                {t("btn_save")}
              </button>
            </form>
          </div>

          <div className="lg:col-span-7 bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-8 backdrop-blur-md shadow-sm flex flex-col gap-6">
            <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
              <h2 className="text-base font-extrabold text-slate-900 dark:text-white">
                {t("projects_title", { count: projects.length })}
              </h2>
              {projects.length < 3 && !showProjectForm && (
                <button
                  type="button"
                  onClick={handleAddProjectClick}
                  className="bg-[#285872]/10 hover:bg-[#285872]/20 border border-[#285872]/20 text-[#285872] rounded-xl px-3.5 py-1.5 font-bold text-xs flex items-center gap-1 cursor-pointer transition-all"
                >
                  <Plus className="w-3.5 h-3.5" />
                  {t("btn_add_project")}
                </button>
              )}
            </div>

            <AnimatePresence mode="wait">
              {showProjectForm ? (
                <motion.div
                  key="project-form"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-850 rounded-[2rem] p-6 flex flex-col gap-4"
                >
                  <h3 className="text-sm font-extrabold text-slate-900 dark:text-white flex items-center gap-1.5">
                    {editingProject
                      ? t("project_edit_title")
                      : t("project_add_title")}
                  </h3>

                  <form
                    onSubmit={handleSaveProject}
                    className="flex flex-col gap-4"
                  >
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div className="flex flex-col gap-1.5">
                        <label className="text-[10px] font-bold text-slate-450 dark:text-slate-500 uppercase tracking-widest pl-1">
                          {t("project_name")}
                        </label>
                        <input
                          type="text"
                          required
                          value={projectName}
                          onChange={(e) => setProjectName(e.target.value)}
                          placeholder={t("project_name_placeholder")}
                          className="w-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-2.5 outline-none focus:ring-1 focus:ring-[#285872] text-xs font-semibold text-slate-900 dark:text-white"
                        />
                      </div>
                      <div className="flex flex-col gap-1.5">
                        <label className="text-[10px] font-bold text-slate-450 dark:text-slate-500 uppercase tracking-widest pl-1">
                          {t("project_role")}
                        </label>
                        <input
                          type="text"
                          required
                          value={projectRole}
                          onChange={(e) => setProjectRole(e.target.value)}
                          placeholder={t("project_role_placeholder")}
                          className="w-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-2.5 outline-none focus:ring-1 focus:ring-[#285872] text-xs font-semibold text-slate-900 dark:text-white"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                      <div className="flex flex-col gap-1.5">
                        <label className="text-[10px] font-bold text-slate-450 dark:text-slate-500 uppercase tracking-widest pl-1 flex items-center gap-1">
                          <Calendar className="w-3 h-3 text-slate-400" />
                          {t("start_date")}
                        </label>
                        <input
                          type="date"
                          required
                          value={projectStart}
                          onChange={(e) => setProjectStart(e.target.value)}
                          className="w-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-2.5 outline-none focus:ring-1 focus:ring-[#285872] text-xs font-semibold text-slate-900 dark:text-white"
                        />
                      </div>
                      <div className="flex flex-col gap-1.5">
                        <label className="text-[10px] font-bold text-slate-450 dark:text-slate-500 uppercase tracking-widest pl-1 flex items-center gap-1">
                          <Calendar className="w-3 h-3 text-slate-400" />
                          {t("end_date")}
                        </label>
                        <input
                          type="date"
                          required
                          value={projectEnd}
                          onChange={(e) => setProjectEnd(e.target.value)}
                          className="w-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-2.5 outline-none focus:ring-1 focus:ring-[#285872] text-xs font-semibold text-slate-900 dark:text-white"
                        />
                      </div>
                      <div className="flex flex-col gap-1.5">
                        <label className="text-[10px] font-bold text-slate-450 dark:text-slate-500 uppercase tracking-widest pl-1 flex items-center gap-1">
                          <Users className="w-3 h-3 text-slate-400" />
                          {t("team_size")}
                        </label>
                        <input
                          type="number"
                          required
                          min="1"
                          value={projectTeamSize}
                          onChange={(e) => setProjectTeamSize(e.target.value)}
                          className="w-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-2.5 outline-none focus:ring-1 focus:ring-[#285872] text-xs font-semibold text-slate-900 dark:text-white"
                        />
                      </div>
                    </div>

                    <div className="flex flex-col gap-1.5">
                      <label className="text-[10px] font-bold text-slate-450 dark:text-slate-500 uppercase tracking-widest pl-1">
                        {t("description")}
                      </label>
                      <textarea
                        required
                        value={projectDesc}
                        onChange={(e) => setProjectDesc(e.target.value)}
                        placeholder={t("description_placeholder")}
                        className="w-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-2.5 outline-none focus:ring-1 focus:ring-[#285872] text-xs font-semibold text-slate-900 dark:text-white"
                        rows={2}
                      />
                    </div>

                    <div className="flex flex-col gap-1.5">
                      <label className="text-[10px] font-bold text-slate-450 dark:text-slate-500 uppercase tracking-widest pl-1 flex items-center gap-1">
                        <Link2 className="w-3 h-3 text-slate-400" />
                        {t("project_link")}
                      </label>
                      <input
                        type="url"
                        required
                        value={projectLink}
                        onChange={(e) => setProjectLink(e.target.value)}
                        placeholder="https://github.com/my-project"
                        className="w-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-2.5 outline-none focus:ring-1 focus:ring-[#285872] text-xs font-semibold text-slate-900 dark:text-white"
                      />
                    </div>

                    <div className="flex flex-col gap-1.5">
                      <label className="text-[10px] font-bold text-slate-450 dark:text-slate-500 uppercase tracking-widest pl-1">
                        {t("tech_stacks")}
                      </label>
                      <input
                        type="text"
                        value={projectTechs}
                        onChange={(e) => setProjectTechs(e.target.value)}
                        placeholder={t("tech_stacks_placeholder")}
                        className="w-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-2.5 outline-none focus:ring-1 focus:ring-[#285872] text-xs font-semibold text-slate-900 dark:text-white"
                      />
                    </div>

                    <div className="flex flex-col gap-1.5">
                      <label className="text-[10px] font-bold text-slate-450 dark:text-slate-500 uppercase tracking-widest pl-1">
                        {t("responsibilities")}
                      </label>
                      <input
                        type="text"
                        value={projectResp}
                        onChange={(e) => setProjectResp(e.target.value)}
                        placeholder={t("responsibilities_placeholder")}
                        className="w-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-2.5 outline-none focus:ring-1 focus:ring-[#285872] text-xs font-semibold text-slate-900 dark:text-white"
                      />
                    </div>

                    <div className="flex gap-2.5 justify-end mt-2">
                      <button
                        type="button"
                        onClick={() => setShowProjectForm(false)}
                        className="bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-xl px-4 py-2 text-xs font-bold transition-all cursor-pointer"
                      >
                        Cancel
                      </button>
                      <button
                        type="submit"
                        disabled={saving}
                        className="bg-[#285872] hover:bg-[#1c3f52] disabled:opacity-50 text-white rounded-xl px-4 py-2 text-xs font-bold transition-all flex items-center gap-1 cursor-pointer"
                      >
                        {saving && <Loader2 className="w-3 h-3 animate-spin" />}
                        {t("btn_save_project")}
                      </button>
                    </div>
                  </form>
                </motion.div>
              ) : (
                <motion.div
                  key="projects-list"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="flex flex-col gap-4"
                >
                  {projects.length === 0 ? (
                    <div className="text-center py-10 opacity-70 text-sm font-semibold text-slate-400">
                      {t("no_projects")}
                    </div>
                  ) : (
                    projects.map((proj) => (
                      <div
                        key={proj.id}
                        className="bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-850 rounded-2xl p-5 flex flex-col gap-3.5 relative group"
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <h4 className="text-sm font-black text-slate-900 dark:text-white">
                              {proj.name}
                            </h4>
                            <span className="text-[10px] text-slate-450 dark:text-slate-500 font-bold block mt-0.5">
                              {proj.role} • Team of {proj.team_size}
                            </span>
                          </div>
                          <div className="flex items-center gap-1.5 opacity-90 group-hover:opacity-100 transition-opacity">
                            <button
                              type="button"
                              onClick={() => handleEditProjectClick(proj)}
                              className="p-2 hover:bg-slate-200 dark:hover:bg-slate-900 rounded-lg text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors cursor-pointer"
                            >
                              <Edit2 className="w-3.5 h-3.5" />
                            </button>
                            <button
                              type="button"
                              onClick={() => handleDeleteProject(proj.id)}
                              className="p-2 hover:bg-red-50 dark:hover:bg-red-955/20 rounded-lg text-slate-400 hover:text-red-500 transition-colors cursor-pointer"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          </div>
                        </div>

                        <p className="text-xs text-slate-600 dark:text-slate-350 leading-relaxed font-semibold">
                          {proj.description}
                        </p>

                        <div className="flex flex-col gap-2.5 pt-2 border-t border-slate-200/50 dark:border-slate-850">
                          <div>
                            <span className="text-[9px] font-bold text-slate-400 uppercase tracking-widest block mb-1">
                              Tech stacks
                            </span>
                            <div className="flex flex-wrap gap-1.5">
                              {proj.tech_stacks?.map((stack, idx) => (
                                <span
                                  key={idx}
                                  className="bg-slate-200/50 dark:bg-slate-900 text-slate-650 dark:text-slate-350 px-2 py-0.5 rounded-lg text-[9px] font-bold"
                                >
                                  {stack}
                                </span>
                              ))}
                            </div>
                          </div>

                          {proj.responsibilities &&
                            proj.responsibilities.length > 0 && (
                              <div>
                                <span className="text-[9px] font-bold text-slate-400 uppercase tracking-widest block mb-1">
                                  Key Responsibilities
                                </span>
                                <div className="flex flex-wrap gap-1.5">
                                  {proj.responsibilities.map((resp, idx) => (
                                    <span
                                      key={idx}
                                      className="bg-slate-200/20 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800 text-slate-650 dark:text-slate-355 px-2 py-0.5 rounded-lg text-[9px] font-bold"
                                    >
                                      {resp}
                                    </span>
                                  ))}
                                </div>
                              </div>
                            )}
                        </div>
                      </div>
                    ))
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </main>
    </div>
  );
}
