"use client";

import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "motion/react";
import {
  Bot,
  User,
  Briefcase,
  FileText,
  Plus,
  Trash2,
  Edit2,
  LogOut,
  Globe,
  Search,
  Building,
  DollarSign,
  MapPin,
  Sparkles,
  Upload,
  Loader2,
  CheckCircle,
  AlertCircle,
} from "lucide-react";
import { useAuth } from "@/context/AuthProvider";
import { profileApi, cvApi, jobApi, companyApi } from "@/configs/apis";
import { Link, useRouter } from "@/i18n/routing";

export default function OverviewPage() {
  const { user, logout, loading: authLoading } = useAuth();
  const router = useRouter();

  // Active Tab: "profile" or "jobs"
  const [activeTab, setActiveTab] = useState("profile");

  // Profile and CV States
  const [profile, setProfile] = useState(null);
  const [cv, setCv] = useState(null);
  const [profileLoading, setProfileLoading] = useState(true);
  const [profileError, setProfileError] = useState("");
  const [profileSuccess, setProfileSuccess] = useState("");

  // Edit states
  const [isEditingProfile, setIsEditingProfile] = useState(false);
  const [editedBackground, setEditedBackground] = useState("");
  const [editedInterests, setEditedInterests] = useState("");
  const [editedLocations, setEditedLocations] = useState("");

  const [isEditingCv, setIsEditingCv] = useState(false);
  const [editedSummary, setEditedSummary] = useState("");
  const [editedEducation, setEditedEducation] = useState("");
  const [editedSkills, setEditedSkills] = useState("");

  // Projects states
  const [isAddingProject, setIsAddingProject] = useState(false);
  const [editingProjectId, setEditingProjectId] = useState(null);
  const [projectTitle, setProjectTitle] = useState("");
  const [projectDesc, setProjectDesc] = useState("");
  const [projectUrl, setProjectUrl] = useState("");

  // Job Search States
  const [jobs, setJobs] = useState([]);
  const [jobsLoading, setJobsLoading] = useState(false);
  const [searchTitle, setSearchTitle] = useState("");
  const [searchSeniority, setSearchSeniority] = useState("");
  const [searchWorkingModel, setSearchWorkingModel] = useState("");
  const [searchMinSalary, setSearchMinSalary] = useState("");
  const [page, setPage] = useState(1);
  const pageSize = 10;

  // Redirect if not logged in
  useEffect(() => {
    if (!authLoading && !user) {
      router.replace("/counselee/login");
    }
  }, [user, authLoading, router]);

  const fetchProfileAndCv = useCallback(async () => {
    setProfileLoading(true);
    setProfileError("");
    try {
      const profileData = await profileApi.getProfile();
      setProfile(profileData);
      setEditedBackground(profileData.background || "");
      setEditedInterests(profileData.career_interests || "");
      setEditedLocations(profileData.locations || "");

      const cvData = await cvApi.getCV();
      setCv(cvData);
      setEditedSummary(cvData.summary || "");
      setEditedEducation(cvData.education || "");
      setEditedSkills(cvData.skills || "");
    } catch (err) {
      setProfileError("Could not fetch profile or CV data.");
    } finally {
      setProfileLoading(false);
    }
  }, []);

  // Load Profile and CV Data
  useEffect(() => {
    if (user) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      fetchProfileAndCv();
    }
  }, [user, fetchProfileAndCv]);

  const fetchJobs = async (resetPage = false) => {
    setJobsLoading(true);
    let currentPage = page;
    if (resetPage) {
      setPage(1);
      currentPage = 1;
    }
    try {
      const params = {
        skip: (currentPage - 1) * pageSize,
        limit: pageSize,
      };
      if (searchTitle) params.title = searchTitle;
      if (searchSeniority) params.seniority = searchSeniority;
      if (searchWorkingModel) params.working_model = searchWorkingModel;
      if (searchMinSalary) params.min_salary = searchMinSalary;

      const data = await jobApi.getJobs(params);
      setJobs(data || []);
    } catch (err) {
      console.error("Failed to load jobs", err);
    } finally {
      setJobsLoading(false);
    }
  };

  // Load Jobs
  useEffect(() => {
    if (user && activeTab === "jobs") {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      fetchJobs();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user, activeTab, page]);

  // Handle Profile Update
  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    setProfileSuccess("");
    setProfileError("");
    try {
      const updated = await profileApi.updateProfile({
        background: editedBackground,
        career_interests: editedInterests,
        locations: editedLocations,
      });
      setProfile(updated);
      setIsEditingProfile(false);
      setProfileSuccess("Profile updated successfully!");
    } catch (err) {
      setProfileError("Failed to update profile.");
    }
  };

  // Handle CV Update
  const handleUpdateCv = async (e) => {
    e.preventDefault();
    setProfileSuccess("");
    setProfileError("");
    try {
      const updated = await cvApi.updateCV({
        summary: editedSummary,
        education: editedEducation,
        skills: editedSkills,
      });
      setCv(updated);
      setIsEditingCv(false);
      setProfileSuccess("CV updated successfully!");
    } catch (err) {
      setProfileError("Failed to update CV.");
    }
  };

  // Project Actions
  const handleAddProject = async (e) => {
    e.preventDefault();
    if (!projectTitle) return;
    try {
      await cvApi.createProject({
        title: projectTitle,
        description: projectDesc,
        project_url: projectUrl,
      });
      setIsAddingProject(false);
      setProjectTitle("");
      setProjectDesc("");
      setProjectUrl("");
      fetchProfileAndCv();
      setProfileSuccess("Project added successfully!");
    } catch (err) {
      setProfileError("Failed to add project.");
    }
  };

  const handleEditProjectClick = (proj) => {
    setEditingProjectId(proj.id);
    setProjectTitle(proj.title);
    setProjectDesc(proj.description || "");
    setProjectUrl(proj.project_url || "");
  };

  const handleUpdateProjectSubmit = async (e) => {
    e.preventDefault();
    if (!projectTitle) return;
    try {
      await cvApi.updateProject(editingProjectId, {
        title: projectTitle,
        description: projectDesc,
        project_url: projectUrl,
      });
      setEditingProjectId(null);
      setProjectTitle("");
      setProjectDesc("");
      setProjectUrl("");
      fetchProfileAndCv();
      setProfileSuccess("Project updated successfully!");
    } catch (err) {
      setProfileError("Failed to update project.");
    }
  };

  const handleDeleteProject = async (projectId) => {
    if (!confirm("Are you sure you want to delete this project?")) return;
    try {
      await cvApi.deleteProject(projectId);
      fetchProfileAndCv();
      setProfileSuccess("Project deleted successfully!");
    } catch (err) {
      setProfileError("Failed to delete project.");
    }
  };

  // File Upload (Mock)
  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      await cvApi.uploadAttachment(file);
      setProfileSuccess(`CV Attachment "${file.name}" uploaded successfully!`);
    } catch (err) {
      setProfileError("Failed to upload CV attachment.");
    }
  };

  if (authLoading || !user) {
    return (
      <div className="min-h-screen w-full flex items-center justify-center bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-white transition-colors duration-300">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600 dark:text-blue-500" />
      </div>
    );
  }

  return (
    <div className="relative min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 font-sans transition-colors duration-300">
      {/* Organic noise background */}
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

      {/* Background gradients matching LandingPage */}
      <motion.div
        animate={{
          x: [0, 20, -10, 0],
          y: [0, -30, 20, 0],
          scale: [1, 1.1, 0.95, 1],
        }}
        transition={{ duration: 20, repeat: Infinity, ease: "easeInOut" }}
        className="absolute top-0 right-0 w-[45vw] h-[45vw] bg-blue-500/10 dark:bg-blue-600/15 rounded-full blur-[130px] pointer-events-none z-0"
      />
      <motion.div
        animate={{
          x: [0, -20, 15, 0],
          y: [0, 25, -15, 0],
          scale: [1, 1.05, 0.9, 1],
        }}
        transition={{ duration: 25, repeat: Infinity, ease: "easeInOut" }}
        className="absolute bottom-0 left-0 w-[40vw] h-[40vw] bg-purple-500/10 dark:bg-purple-600/15 rounded-full blur-[130px] pointer-events-none z-0"
      />

      {/* Main navigation header */}
      <header className="relative z-10 border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-950/80 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center text-white shadow-lg">
              <Bot className="w-6 h-6" />
            </div>
            <span className="text-2xl font-black tracking-tighter uppercase text-slate-900 dark:text-white">
              AIJMC
            </span>
          </Link>

          <div className="flex items-center gap-6">
            <Link
              href="/counselee/chatbot"
              className="bg-blue-600 hover:bg-blue-500 text-white rounded-full px-6 py-2.5 font-bold text-sm tracking-wide shadow-lg shadow-blue-500/20 flex items-center gap-2 transition-all hover:scale-105"
            >
              <Sparkles className="w-4 h-4 animate-pulse" />
              Career Chatbot
            </Link>
            <button
              onClick={logout}
              className="text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white p-2 transition-colors flex items-center gap-1.5 font-semibold text-sm cursor-pointer"
            >
              <LogOut className="w-4 h-4" />
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main content grid */}
      <main className="relative z-10 max-w-7xl mx-auto px-6 py-12">
        <div className="flex flex-col gap-8">
          {/* Welcome User Banner */}
          <div className="bg-white/45 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-8 backdrop-blur-md flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div>
              <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight text-slate-900 dark:text-white mb-2">
                Welcome back,{" "}
                <span className="text-blue-600 dark:text-blue-500">
                  {user.username}
                </span>
                !
              </h1>
              <p className="text-slate-500 dark:text-slate-400 font-medium">
                Manage your profile, CV experiences, and search real-time tech
                jobs.
              </p>
            </div>
            <div className="flex bg-slate-100 dark:bg-slate-955 border border-slate-200 dark:border-slate-800 rounded-2xl p-1.5 w-fit shrink-0">
              <button
                onClick={() => setActiveTab("profile")}
                className={`flex items-center gap-2 px-5 py-2.5 rounded-xl font-bold text-sm transition-all cursor-pointer ${
                  activeTab === "profile"
                    ? "bg-blue-600 text-white shadow-lg"
                    : "text-slate-505 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
                }`}
              >
                <User className="w-4 h-4" />
                Profile & CV
              </button>
              <button
                onClick={() => setActiveTab("jobs")}
                className={`flex items-center gap-2 px-5 py-2.5 rounded-xl font-bold text-sm transition-all cursor-pointer ${
                  activeTab === "jobs"
                    ? "bg-blue-600 text-white shadow-lg"
                    : "text-slate-505 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
                }`}
              >
                <Briefcase className="w-4 h-4" />
                Job Explorer
              </button>
            </div>
          </div>

          {/* Toast-style Messages */}
          <AnimatePresence>
            {profileSuccess && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded-2xl p-4 flex items-center gap-2.5 text-sm font-medium"
              >
                <CheckCircle className="w-5 h-5 text-emerald-400 shrink-0" />
                <span>{profileSuccess}</span>
                <button
                  onClick={() => setProfileSuccess("")}
                  className="ml-auto text-emerald-400 hover:text-emerald-300 font-bold"
                >
                  ✕
                </button>
              </motion.div>
            )}

            {profileError && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="bg-red-500/10 border border-red-500/20 text-red-400 rounded-2xl p-4 flex items-center gap-2.5 text-sm font-medium"
              >
                <AlertCircle className="w-5 h-5 text-red-400 shrink-0" />
                <span>{profileError}</span>
                <button
                  onClick={() => setProfileError("")}
                  className="ml-auto text-red-400 hover:text-red-300 font-bold"
                >
                  ✕
                </button>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Loader */}
          {profileLoading && activeTab === "profile" && (
            <div className="w-full py-20 flex items-center justify-center">
              <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
            </div>
          )}

          {/* TAB 1: Profile & CV view */}
          {!profileLoading && activeTab === "profile" && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Left Column: Profile fields */}
              <div className="lg:col-span-1 flex flex-col gap-8">
                <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-6 backdrop-blur-md">
                  <div className="flex items-center justify-between mb-6">
                    <h2 className="text-xl font-extrabold text-slate-900 dark:text-white flex items-center gap-2.5">
                      <User className="w-5 h-5 text-blue-600 dark:text-blue-500" />
                      Consultant Profile
                    </h2>
                    {!isEditingProfile && (
                      <button
                        onClick={() => setIsEditingProfile(true)}
                        className="text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white p-2 border border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 rounded-xl transition-all cursor-pointer"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                    )}
                  </div>

                  {isEditingProfile ? (
                    <form
                      onSubmit={handleUpdateProfile}
                      className="flex flex-col gap-4"
                    >
                      <div className="flex flex-col gap-1.5">
                        <label className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider pl-1">
                          Background/Education Summary
                        </label>
                        <textarea
                          value={editedBackground}
                          onChange={(e) => setEditedBackground(e.target.value)}
                          placeholder="e.g. Computer Science student at OUHCMC"
                          className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-250 dark:border-slate-850 rounded-xl p-3 outline-none focus:ring-1 focus:ring-blue-600 text-sm text-slate-900 dark:text-white font-medium"
                          rows={3}
                        />
                      </div>
                      <div className="flex flex-col gap-1.5">
                        <label className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider pl-1">
                          Career Interests
                        </label>
                        <input
                          type="text"
                          value={editedInterests}
                          onChange={(e) => setEditedInterests(e.target.value)}
                          placeholder="e.g. AI Engineer, Python Developer"
                          className="w-full bg-slate-50 dark:bg-slate-955 border border-slate-250 dark:border-slate-850 rounded-xl p-3 outline-none focus:ring-1 focus:ring-blue-600 text-sm text-slate-900 dark:text-white font-medium"
                        />
                      </div>
                      <div className="flex flex-col gap-1.5">
                        <label className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider pl-1">
                          Preferred Locations
                        </label>
                        <input
                          type="text"
                          value={editedLocations}
                          onChange={(e) => setEditedLocations(e.target.value)}
                          placeholder="e.g. Ho Chi Minh City, Remote"
                          className="w-full bg-slate-50 dark:bg-slate-955 border border-slate-250 dark:border-slate-850 rounded-xl p-3 outline-none focus:ring-1 focus:ring-blue-600 text-sm text-slate-900 dark:text-white font-medium"
                        />
                      </div>
                      <div className="flex items-center gap-3 mt-2">
                        <button
                          type="submit"
                          className="bg-blue-600 hover:bg-blue-500 text-white rounded-full px-5 py-2.5 font-bold text-xs shadow-md transition-colors cursor-pointer"
                        >
                          Save Changes
                        </button>
                        <button
                          type="button"
                          onClick={() => {
                            setIsEditingProfile(false);
                            setEditedBackground(profile?.background || "");
                            setEditedInterests(profile?.career_interests || "");
                            setEditedLocations(profile?.locations || "");
                          }}
                          className="border border-slate-200 dark:border-slate-800 text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white rounded-full px-5 py-2.5 font-bold text-xs transition-colors cursor-pointer"
                        >
                          Cancel
                        </button>
                      </div>
                    </form>
                  ) : (
                    <div className="flex flex-col gap-5">
                      <div>
                        <span className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest block mb-1">
                          Background Info
                        </span>
                        <p className="text-sm font-medium text-slate-700 dark:text-slate-300 leading-relaxed">
                          {profile?.background || "Not specified yet."}
                        </p>
                      </div>
                      <div>
                        <span className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest block mb-1">
                          Interests
                        </span>
                        <p className="text-sm font-medium text-slate-700 dark:text-slate-300">
                          {profile?.career_interests || "Not specified yet."}
                        </p>
                      </div>
                      <div>
                        <span className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest block mb-1">
                          Preferred Locations
                        </span>
                        <p className="text-sm font-medium text-slate-700 dark:text-slate-300 flex items-center gap-1.5">
                          <MapPin className="w-4 h-4 text-slate-400 dark:text-slate-500" />
                          {profile?.locations || "Not specified yet."}
                        </p>
                      </div>
                    </div>
                  )}
                </div>

                {/* CV Attachment Upload Card */}
                <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-6 backdrop-blur-md">
                  <h2 className="text-xl font-extrabold text-slate-900 dark:text-white flex items-center gap-2.5 mb-4">
                    <FileText className="w-5 h-5 text-blue-600 dark:text-blue-500" />
                    CV PDF Attachment
                  </h2>
                  <div className="border border-dashed border-slate-200 dark:border-slate-800 rounded-2xl p-6 flex flex-col items-center justify-center text-center">
                    <Upload className="w-8 h-8 text-slate-400 dark:text-slate-500 mb-3" />
                    <p className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2">
                      Upload your latest resume
                    </p>
                    <p className="text-[11px] text-slate-450 dark:text-slate-500 mb-4">
                      Accepts PDF files up to 5MB
                    </p>
                    <label className="bg-slate-100 hover:bg-slate-200 dark:bg-slate-950 dark:hover:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-white rounded-full px-5 py-2.5 font-bold text-xs transition-colors cursor-pointer inline-block">
                      Select File
                      <input
                        type="file"
                        accept=".pdf"
                        onChange={handleFileUpload}
                        className="hidden"
                      />
                    </label>
                  </div>
                </div>
              </div>

              {/* Right Column: CV Summary, Skills, Projects */}
              <div className="lg:col-span-2 flex flex-col gap-8">
                {/* CV Overview Card                 <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-6 backdrop-blur-md">
                  <div className="flex items-center justify-between mb-6">
                    <h2 className="text-xl font-extrabold text-slate-900 dark:text-white flex items-center gap-2.5">
                      <FileText className="w-5 h-5 text-blue-600 dark:text-blue-500" />
                      Curriculum Vitae
                    </h2>
                    {!isEditingCv && (
                      <button
                        onClick={() => setIsEditingCv(true)}
                        className="text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white p-2 border border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 rounded-xl transition-all cursor-pointer"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                    )}
                  </div>

                  {isEditingCv ? (
                    <form onSubmit={handleUpdateCv} className="flex flex-col gap-4">
                      <div className="flex flex-col gap-1.5">
                        <label className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider pl-1">
                          Professional Summary
                        </label>
                        <textarea
                          value={editedSummary}
                          onChange={(e) => setEditedSummary(e.target.value)}
                          placeholder="Write a brief professional intro..."
                          className="w-full bg-slate-50 dark:bg-slate-955 border border-slate-250 dark:border-slate-850 rounded-xl p-3 outline-none focus:ring-1 focus:ring-blue-600 text-sm text-slate-900 dark:text-white font-medium"
                          rows={3}
                        />
                      </div>
                      <div className="flex flex-col gap-1.5">
                        <label className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider pl-1">
                          Education History
                        </label>
                        <textarea
                          value={editedEducation}
                          onChange={(e) => setEditedEducation(e.target.value)}
                          placeholder="e.g. BS in Information Technology - OUHCMC (2023 - 2027)"
                          className="w-full bg-slate-50 dark:bg-slate-955 border border-slate-250 dark:border-slate-850 rounded-xl p-3 outline-none focus:ring-1 focus:ring-blue-600 text-sm text-slate-900 dark:text-white font-medium"
                          rows={2}
                        />
                      </div>
                      <div className="flex flex-col gap-1.5">
                        <label className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider pl-1">
                          Technical Skills
                        </label>
                        <input
                          type="text"
                          value={editedSkills}
                          onChange={(e) => setEditedSkills(e.target.value)}
                          placeholder="e.g. React, Next.js, Python, PostgreSQL"
                          className="w-full bg-slate-50 dark:bg-slate-955 border border-slate-250 dark:border-slate-850 rounded-xl p-3 outline-none focus:ring-1 focus:ring-blue-600 text-sm text-slate-900 dark:text-white font-medium"
                        />
                      </div>
                      <div className="flex items-center gap-3 mt-2">
                        <button
                          type="submit"
                          className="bg-blue-600 hover:bg-blue-500 text-white rounded-full px-5 py-2.5 font-bold text-xs shadow-md transition-colors cursor-pointer"
                        >
                          Save Changes
                        </button>
                        <button
                          type="button"
                          onClick={() => {
                            setIsEditingCv(false);
                            setEditedSummary(cv?.summary || "");
                            setEditedEducation(cv?.education || "");
                            setEditedSkills(cv?.skills || "");
                          }}
                          className="border border-slate-200 dark:border-slate-800 text-slate-505 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white rounded-full px-5 py-2.5 font-bold text-xs transition-colors cursor-pointer"
                        >
                          Cancel
                        </button>
                      </div>
                    </form>
                  ) : (
                    <div className="flex flex-col gap-6">
                      <div>
                        <span className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest block mb-1">
                          Summary
                        </span>
                        <p className="text-sm font-medium text-slate-700 dark:text-slate-300 leading-relaxed">
                          {cv?.summary || "Add a CV summary to showcase your skills."}
                        </p>
                      </div>
                      <div>
                        <span className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest block mb-1">
                          Education
                        </span>
                        <p className="text-sm font-medium text-slate-700 dark:text-slate-300 leading-relaxed">
                          {cv?.education || "Add your educational history."}
                        </p>
                      </div>
                      <div>
                        <span className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest block mb-1">
                          Skills
                        </span>
                        <div className="flex flex-wrap gap-2 mt-1.5">
                          {cv?.skills ? (
                            cv.skills.split(",").map((skill, index) => (
                              <span
                                key={index}
                                className="bg-slate-100 dark:bg-slate-955 border border-slate-200 dark:border-slate-850 text-blue-600 dark:text-blue-400 px-3.5 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider"
                              >
                                {skill.trim()}
                              </span>
                            ))
                          ) : (
                            <span className="text-sm font-medium text-slate-500">No skills added yet.</span>
                          )}
                        </div>
                      </div>
                    </div>
                  )}
                </div>div>

                {/* CV Projects Card */}
                <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-6 backdrop-blur-md">
                  <div className="flex items-center justify-between mb-6">
                    <h2 className="text-xl font-extrabold text-slate-900 dark:text-white flex items-center gap-2.5">
                      <Briefcase className="w-5 h-5 text-blue-600 dark:text-blue-500" />
                      Key Projects
                    </h2>
                    {!isAddingProject && !editingProjectId && (
                      <button
                        onClick={() => setIsAddingProject(true)}
                        className="bg-blue-600/10 hover:bg-blue-600 text-blue-600 hover:text-white border border-blue-200 dark:border-blue-900 hover:border-transparent rounded-xl px-4 py-2 text-xs font-bold tracking-wide flex items-center gap-1.5 transition-all cursor-pointer"
                      >
                        <Plus className="w-3.5 h-3.5" />
                        Add Project
                      </button>
                    )}
                  </div>

                  {/* Add / Edit Project Form */}
                  {(isAddingProject || editingProjectId) && (
                    <form
                      onSubmit={
                        isAddingProject
                          ? handleAddProject
                          : handleUpdateProjectSubmit
                      }
                      className="border border-slate-200 dark:border-slate-850 rounded-2xl p-5 mb-6 bg-slate-50 dark:bg-slate-955 flex flex-col gap-4"
                    >
                      <h3 className="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-wider">
                        {isAddingProject
                          ? "Create CV Project"
                          : "Edit CV Project"}
                      </h3>
                      <div className="flex flex-col gap-1.5">
                        <label className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider pl-1">
                          Project Title
                        </label>
                        <input
                          type="text"
                          value={projectTitle}
                          onChange={(e) => setProjectTitle(e.target.value)}
                          placeholder="e.g. Porting CV Parser Agent"
                          className="w-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-3 outline-none focus:ring-1 focus:ring-blue-600 text-sm text-slate-900 dark:text-white font-medium"
                          required
                        />
                      </div>
                      <div className="flex flex-col gap-1.5">
                        <label className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider pl-1">
                          Description
                        </label>
                        <textarea
                          value={projectDesc}
                          onChange={(e) => setProjectDesc(e.target.value)}
                          placeholder="Describe the stack and what you built..."
                          className="w-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-3 outline-none focus:ring-1 focus:ring-blue-600 text-sm text-slate-900 dark:text-white font-medium"
                          rows={2}
                        />
                      </div>
                      <div className="flex flex-col gap-1.5">
                        <label className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider pl-1">
                          Project Link URL (Optional)
                        </label>
                        <input
                          type="url"
                          value={projectUrl}
                          onChange={(e) => setProjectUrl(e.target.value)}
                          placeholder="https://github.com/..."
                          className="w-full bg-white dark:bg-slate-905 border border-slate-200 dark:border-slate-800 rounded-xl p-3 outline-none focus:ring-1 focus:ring-blue-600 text-sm text-slate-900 dark:text-white font-medium"
                        />
                      </div>
                      <div className="flex items-center gap-3">
                        <button
                          type="submit"
                          className="bg-blue-600 hover:bg-blue-500 text-white rounded-full px-5 py-2.5 font-bold text-xs shadow-md transition-colors cursor-pointer"
                        >
                          {isAddingProject ? "Add Project" : "Update Project"}
                        </button>
                        <button
                          type="button"
                          onClick={() => {
                            setIsAddingProject(false);
                            setEditingProjectId(null);
                            setProjectTitle("");
                            setProjectDesc("");
                            setProjectUrl("");
                          }}
                          className="border border-slate-200 dark:border-slate-800 text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white rounded-full px-5 py-2.5 font-bold text-xs transition-colors cursor-pointer"
                        >
                          Cancel
                        </button>
                      </div>
                    </form>
                  )}

                  {/* Projects List */}
                  <div className="flex flex-col gap-4">
                    {cv?.projects && cv.projects.length > 0 ? (
                      cv.projects.map((proj) => (
                        <div
                          key={proj.id}
                          className="bg-white dark:bg-slate-955/40 border border-slate-200 dark:border-slate-850 rounded-2xl p-5 flex flex-col md:flex-row md:items-start justify-between gap-4 transition-all hover:border-slate-300 dark:hover:border-slate-800"
                        >
                          <div className="flex flex-col gap-1">
                            <h3 className="text-base font-bold text-slate-900 dark:text-white">
                              {proj.title}
                            </h3>
                            {proj.project_url && (
                              <a
                                href={proj.project_url}
                                target="_blank"
                                rel="noreferrer"
                                className="text-xs font-bold text-blue-600 dark:text-blue-400 hover:underline flex items-center gap-1 w-fit"
                              >
                                <Globe className="w-3.5 h-3.5" />
                                {proj.project_url}
                              </a>
                            )}
                            <p className="text-sm font-medium text-slate-505 dark:text-slate-400 mt-2 leading-relaxed">
                              {proj.description || "No description added."}
                            </p>
                          </div>
                          <div className="flex items-center gap-2 shrink-0 self-end md:self-start">
                            <button
                              onClick={() => handleEditProjectClick(proj)}
                              className="text-slate-505 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white p-2 border border-slate-200 dark:border-slate-850 hover:border-slate-350 dark:hover:border-slate-800 rounded-xl transition-all cursor-pointer"
                            >
                              <Edit2 className="w-3.5 h-3.5" />
                            </button>
                            <button
                              onClick={() => handleDeleteProject(proj.id)}
                              className="text-red-655 dark:text-red-400 hover:text-red-500 p-2 border border-red-200 dark:border-red-950/40 hover:border-red-900 rounded-xl transition-all cursor-pointer"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          </div>
                        </div>
                      ))
                    ) : (
                      <p className="text-sm font-medium text-slate-500 py-4 text-center">
                        No projects listed in your CV. Add one to stand out.
                      </p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: Jobs Search view */}
          {activeTab === "jobs" && (
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
              {/* Left Column: Search & Filter Panel */}
              <div className="lg:col-span-1 flex flex-col gap-8">
                <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-6 backdrop-blur-md flex flex-col gap-5">
                  <h2 className="text-xl font-extrabold text-slate-900 dark:text-white flex items-center gap-2.5">
                    <Search className="w-5 h-5 text-blue-600 dark:text-blue-500" />
                    Filters
                  </h2>
                  <div className="flex flex-col gap-1.5">
                    <label className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider pl-1">
                      Search Title
                    </label>
                    <input
                      type="text"
                      value={searchTitle}
                      onChange={(e) => setSearchTitle(e.target.value)}
                      placeholder="e.g. Developer, Python"
                      className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-850 rounded-xl p-3 outline-none focus:ring-1 focus:ring-blue-600 text-sm text-slate-900 dark:text-white font-medium"
                    />
                  </div>
                  <div className="flex flex-col gap-1.5">
                    <label className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider pl-1">
                      Seniority Level
                    </label>
                    <select
                      value={searchSeniority}
                      onChange={(e) => setSearchSeniority(e.target.value)}
                      className="w-full bg-slate-50 dark:bg-slate-955 border border-slate-200 dark:border-slate-850 rounded-xl p-3 outline-none focus:ring-1 focus:ring-blue-600 text-sm text-slate-900 dark:text-white font-medium"
                    >
                      <option value="">All Seniority Levels</option>
                      <option value="intern">Intern</option>
                      <option value="junior">Junior</option>
                      <option value="middle">Middle</option>
                      <option value="senior">Senior</option>
                      <option value="lead">Lead</option>
                    </select>
                  </div>
                  <div className="flex flex-col gap-1.5">
                    <label className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider pl-1">
                      Working Model
                    </label>
                    <select
                      value={searchWorkingModel}
                      onChange={(e) => setSearchWorkingModel(e.target.value)}
                      className="w-full bg-slate-50 dark:bg-slate-955 border border-slate-200 dark:border-slate-850 rounded-xl p-3 outline-none focus:ring-1 focus:ring-blue-600 text-sm text-slate-900 dark:text-white font-medium"
                    >
                      <option value="">All Models</option>
                      <option value="remote">Remote</option>
                      <option value="hybrid">Hybrid</option>
                      <option value="onsite">On-site</option>
                    </select>
                  </div>
                  <div className="flex flex-col gap-1.5">
                    <label className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider pl-1">
                      Min Salary (USD)
                    </label>
                    <input
                      type="number"
                      value={searchMinSalary}
                      onChange={(e) => setSearchMinSalary(e.target.value)}
                      placeholder="e.g. 1000"
                      className="w-full bg-slate-50 dark:bg-slate-955 border border-slate-200 dark:border-slate-850 rounded-xl p-3 outline-none focus:ring-1 focus:ring-blue-600 text-sm text-slate-900 dark:text-white font-medium"
                    />
                  </div>
                  <div className="flex items-center gap-3 mt-2">
                    <button
                      onClick={() => fetchJobs(true)}
                      className="w-full bg-blue-600 hover:bg-blue-500 text-white rounded-full py-3 font-bold text-sm shadow-md transition-colors cursor-pointer"
                    >
                      Apply Filters
                    </button>
                    <button
                      onClick={() => {
                        setSearchTitle("");
                        setSearchSeniority("");
                        setSearchWorkingModel("");
                        setSearchMinSalary("");
                        setPage(1);
                        setTimeout(() => fetchJobs(true), 50);
                      }}
                      className="border border-slate-200 dark:border-slate-800 text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white rounded-full px-5 py-3 font-bold text-sm transition-colors cursor-pointer"
                    >
                      Clear
                    </button>
                  </div>
                </div>
              </div>

              {/* Right Column: Matched Jobs List */}
              <div className="lg:col-span-3 flex flex-col gap-6">
                {jobsLoading ? (
                  <div className="w-full py-20 flex items-center justify-center">
                    <Loader2 className="w-8 h-8 animate-spin text-blue-600 dark:text-blue-500" />
                  </div>
                ) : jobs.length > 0 ? (
                  <div className="flex flex-col gap-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {jobs.map((job) => (
                        <div
                          key={job.id}
                          onClick={() =>
                            router.push(`/counselee/jobs/${job.id}`)
                          }
                          className="cursor-pointer bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-6 backdrop-blur-md flex flex-col justify-between gap-6 transition-all hover:border-slate-350 dark:hover:border-slate-800 group"
                        >
                          <div className="flex flex-col gap-3">
                            <div className="flex items-center gap-3">
                              <div className="w-10 h-10 bg-slate-50 dark:bg-slate-955 border border-slate-200 dark:border-slate-850 rounded-xl flex items-center justify-center text-slate-450">
                                <Building className="w-5 h-5 text-slate-500" />
                              </div>
                              <div>
                                <h3 className="text-base font-extrabold text-slate-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                                  {job.title}
                                </h3>
                                <p className="text-xs text-slate-505 dark:text-slate-400 font-semibold uppercase tracking-wider">
                                  {job.company_name || "Company Profile"}
                                </p>
                              </div>
                            </div>

                            <div className="flex flex-wrap gap-2 mt-2">
                              <span className="bg-slate-50 dark:bg-slate-955 border border-slate-200 dark:border-slate-850 text-slate-650 dark:text-slate-400 px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider">
                                {job.seniority}
                              </span>
                              <span className="bg-slate-50 dark:bg-slate-955 border border-slate-200 dark:border-slate-850 text-slate-650 dark:text-slate-400 px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider">
                                {job.working_model}
                              </span>
                            </div>
                          </div>

                          <div className="flex items-center justify-between border-t border-slate-150 dark:border-slate-855 pt-4">
                            <p className="text-xs font-bold text-emerald-600 dark:text-emerald-400 flex items-center gap-1">
                              <DollarSign className="w-4 h-4 shrink-0" />
                              {job.min_salary
                                ? `${job.min_salary} - ${
                                    job.max_salary || "Negotiable"
                                  }`
                                : "Competitive"}
                            </p>
                            <span className="text-[10px] text-slate-550 dark:text-slate-400 font-bold uppercase tracking-wider">
                              View details →
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* Pagination Controls */}
                    <div className="flex items-center justify-between bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-2xl p-4 backdrop-blur-md shadow-sm">
                      <button
                        disabled={page === 1 || jobsLoading}
                        onClick={() => setPage((prev) => Math.max(prev - 1, 1))}
                        className="px-5 py-2.5 rounded-xl border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 disabled:opacity-50 disabled:hover:bg-transparent font-bold text-sm transition-colors cursor-pointer"
                      >
                        ← Previous
                      </button>
                      <span className="text-sm font-bold text-slate-505 dark:text-slate-400">
                        Page {page}
                      </span>
                      <button
                        disabled={jobs.length < pageSize || jobsLoading}
                        onClick={() => setPage((prev) => prev + 1)}
                        className="px-5 py-2.5 rounded-xl border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 disabled:opacity-50 disabled:hover:bg-transparent font-bold text-sm transition-colors cursor-pointer"
                      >
                        Next →
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-12 text-center backdrop-blur-md">
                    <Briefcase className="w-12 h-12 text-slate-400 dark:text-slate-505 mx-auto mb-4 animate-bounce" />
                    <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2">
                      No jobs matched your criteria
                    </h3>
                    <p className="text-sm text-slate-505 dark:text-slate-400">
                      Try clearing filters or adjusting search terms to explore
                      available opportunities.
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
