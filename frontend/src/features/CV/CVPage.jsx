"use client";

import { motion } from "motion/react";
import { Loader2, CheckCircle, AlertCircle } from "lucide-react";
import Header from "@/components/shared/Header";
import { useCVData } from "./Hooks/useCVData";
import CVHeader from "./Components/CVHeader";
import CVFileAttachmentSection from "./Components/CVFileAttachmentSection";
import CVGeneralInfoForm from "./Components/CVGeneralInfoForm";
import CVProjectsSection from "./Components/CVProjectsSection";
import CVProjectModal from "./Components/CVProjectModal";

export default function CVPage() {
  const {
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
  } = useCVData();

  if (loading) {
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

      <Header />

      <main className="relative z-10 max-w-7xl mx-auto px-6 pt-28 flex flex-col gap-6">
        <CVHeader saving={saving} onSaveCV={handleSaveCV} />

        {error && (
          <div className="bg-red-500/10 border border-red-500/20 text-red-500 rounded-2xl p-4 flex items-center gap-2 text-xs font-bold">
            <AlertCircle className="w-4 h-4 shrink-0" />
            {error}
          </div>
        )}

        {success && (
          <div className="bg-emerald-500/10 border border-emerald-500/20 text-emerald-500 rounded-2xl p-4 flex items-center gap-2 text-xs font-bold">
            <CheckCircle className="w-4 h-4 shrink-0" />
            {success}
          </div>
        )}

        <CVFileAttachmentSection
          attachment={attachment}
          usingCvMode={usingCvMode}
          setUsingCvMode={setUsingCvMode}
          uploading={uploading}
          fileInputRef={fileInputRef}
          onFileUpload={handleFileUpload}
        />

        <form
          onSubmit={handleSaveCV}
          className="grid grid-cols-1 lg:grid-cols-5 gap-6 items-start"
        >
          <div className="lg:col-span-3">
            <CVGeneralInfoForm
              jobPosition={jobPosition}
              setJobPosition={setJobPosition}
              summary={summary}
              setSummary={setSummary}
              education={education}
              setEducation={setEducation}
              skillsText={skillsText}
              setSkillsText={setSkillsText}
              locked={usingCvMode}
            />
          </div>

          <div className="lg:col-span-2">
            <CVProjectsSection
              projects={projects}
              onOpenAddProject={openAddProject}
              onOpenEditProject={openEditProject}
              onDeleteProject={handleDeleteProject}
              locked={usingCvMode}
            />
          </div>
        </form>
      </main>

      <CVProjectModal
        showProjectForm={showProjectForm}
        onClose={() => setShowProjectForm(false)}
        editingProject={editingProject}
        projectName={projectName}
        setProjectName={setProjectName}
        projectRole={projectRole}
        setProjectRole={setProjectRole}
        projectTechs={projectTechs}
        setProjectTechs={setProjectTechs}
        projectDesc={projectDesc}
        setProjectDesc={setProjectDesc}
        projectStart={projectStart}
        setProjectStart={setProjectStart}
        projectEnd={projectEnd}
        setProjectEnd={setProjectEnd}
        projectLink={projectLink}
        setProjectLink={setProjectLink}
        projectTeamSize={projectTeamSize}
        setProjectTeamSize={setProjectTeamSize}
        projectResp={projectResp}
        setProjectResp={setProjectResp}
        onSaveProject={handleSaveProject}
      />
    </div>
  );
}
