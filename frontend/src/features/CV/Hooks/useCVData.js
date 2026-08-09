import { useState, useEffect, useRef, useCallback } from "react";
import { useAuth } from "@/context/AuthProvider";
import { cvApi } from "@/configs/apis";
import { useRouter } from "@/i18n/routing";
import { useTranslations } from "next-intl";

export function useCVData() {
  const { user, authLoading } = useAuth();
  const router = useRouter();
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
    if (e) e.preventDefault();
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

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setError("");
    setSuccess("");

    try {
      const updated = await cvApi.uploadCVAttachment(file);
      setAttachment(updated.attachment || "");
      setSuccess("CV attachment uploaded successfully!");
    } catch (err) {
      setError("Failed to upload CV file.");
    } finally {
      setUploading(false);
    }
  };

  const openAddProject = () => {
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

  const openEditProject = (proj) => {
    setEditingProject(proj);
    setProjectName(proj.name || "");
    setProjectRole(proj.role || "");
    setProjectTechs(proj.tech_stacks ? proj.tech_stacks.join(", ") : "");
    setProjectDesc(proj.description || "");
    setProjectStart(proj.start_date ? proj.start_date.split("T")[0] : "");
    setProjectEnd(proj.end_date ? proj.end_date.split("T")[0] : "");
    setProjectLink(proj.link || "");
    setProjectTeamSize(proj.team_size || 1);
    setProjectResp(proj.responsibilities || "");
    setShowProjectForm(true);
  };

  const handleSaveProject = async (e) => {
    if (e) e.preventDefault();
    setError("");

    const parsedTechs = projectTechs
      .split(",")
      .map((t) => t.trim())
      .filter(Boolean);

    const parsedResps = projectResp
      .split(",")
      .map((r) => r.trim())
      .filter(Boolean);

    const projectPayload = {
      name: projectName,
      role: projectRole,
      tech_stacks: parsedTechs,
      description: projectDesc,
      start_date: projectStart,
      end_date: projectEnd || null,
      link: projectLink || "",
      team_size: parseInt(projectTeamSize, 10) || 1,
      ...(parsedResps.length > 0 && { responsibilities: parsedResps }),
    };

    try {
      if (editingProject) {
        await cvApi.updateProject(editingProject.id, projectPayload);
      } else {
        await cvApi.createProject(projectPayload);
      }
      setShowProjectForm(false);
      fetchCV();
    } catch (err) {
      setError("Failed to save project.");
    }
  };

  const handleDeleteProject = async (projectId) => {
    if (!confirm("Are you sure you want to remove this project?")) return;
    try {
      await cvApi.deleteProject(projectId);
      fetchCV();
    } catch (err) {
      setError("Failed to delete project.");
    }
  };

  return {
    user,
    authLoading,
    jobPosition,
    setJobPosition,
    summary,
    setSummary,
    education,
    setEducation,
    skillsText,
    setSkillsText,
    attachment,
    usingCvMode,
    setUsingCvMode,
    projects,
    loading,
    saving,
    uploading,
    error,
    success,
    showProjectForm,
    setShowProjectForm,
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
    fileInputRef,
    handleSaveCV,
    handleFileUpload,
    openAddProject,
    openEditProject,
    handleSaveProject,
    handleDeleteProject,
  };
}
