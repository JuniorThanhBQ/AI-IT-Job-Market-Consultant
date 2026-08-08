"use client";

import { use, useState, useEffect, useCallback } from "react";
import {
  Building,
  Loader2,
  ChevronLeft,
  Globe,
  MapPin,
  Gift,
  Briefcase,
} from "lucide-react";
import { useAuth } from "@/context/AuthProvider";
import { companyApi } from "@/configs/apis";
import Header from "@/components/shared/Header";
import { useRouter, Link } from "@/i18n/routing";
import { useLocale, useTranslations } from "next-intl";
import {
  mapEnum,
  mapWorkingHours,
  formatSalaryRange,
} from "@/utils/enumMapper";
import { LOGO } from "@/assets/CloudinaryAssetsUrl";
import Image from "next/image";

export default function CompanyDetailPage({ params }) {
  const { id } = use(params);
  const router = useRouter();
  const locale = useLocale();
  const t = useTranslations("Counselee.Company");
  const { user, authLoading } = useAuth();
  const [company, setCompany] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [page, setPage] = useState(1);
  const pageSize = 5;

  // Redirect if not logged in
  useEffect(() => {
    if (!authLoading && !user) {
      router.replace("/counselee/login");
    }
  }, [user, authLoading, router]);

  const fetchCompanyDetails = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const data = await companyApi.getCompanyDetails(id);
      setCompany(data);
    } catch (err) {
      console.error("Failed to fetch company details:", err);
      setError(
        "Could not load company profile. It may have been removed or is currently unavailable.",
      );
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    if (user && id) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      fetchCompanyDetails();
    }
  }, [user, id, fetchCompanyDetails]);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-955 relative overflow-hidden font-sans pb-16">
      {/* Organic noise background overlay */}
      <div
        className="absolute inset-0 pointer-events-none opacity-40 dark:opacity-[0.12] mix-blend-overlay z-0"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E")`,
        }}
      />

      {/* Moving blurred gradient background circles */}
      <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-blue-500/10 dark:bg-blue-500/5 rounded-full blur-[120px] pointer-events-none z-0" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-indigo-500/10 dark:bg-indigo-500/5 rounded-full blur-[120px] pointer-events-none z-0" />

      <Header />

      <main className="max-w-[80vw] mx-auto px-4 sm:px-6 pt-24 pb-12 relative z-10 flex flex-col gap-6">
        {/* Back Link */}
        <button
          onClick={() => router.back()}
          className="self-start flex items-center gap-2 text-sm font-bold text-slate-555 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors cursor-pointer group"
        >
          <ChevronLeft className="w-4 h-4 transition-transform group-hover:-translate-x-1" />
          {t("go_back")}
        </button>

        {loading ? (
          <div className="w-full py-32 flex items-center justify-center">
            <Loader2 className="w-10 h-10 animate-spin text-[#285872] dark:text-[#407c9c]" />
          </div>
        ) : error ? (
          <div className="bg-white/80 dark:bg-slate-900/40 border border-red-250 dark:border-red-900 rounded-[2rem] p-12 text-center backdrop-blur-md">
            <p className="text-red-655 dark:text-red-400 font-bold mb-4">
              {error}
            </p>
            <button
              onClick={fetchCompanyDetails}
              className="bg-[#285872] hover:bg-[#1c3f52] text-white rounded-full px-6 py-2.5 font-bold text-sm transition-colors cursor-pointer"
            >
              Try Again
            </button>
          </div>
        ) : (
          <div className="flex flex-col gap-8">
            {/* Header Box */}
            <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2.5rem] p-8 backdrop-blur-md flex items-center gap-5 shadow-sm">
              <div className="w-16 h-16 bg-white border border-slate-200 dark:border-slate-800 rounded-2xl flex items-center justify-center overflow-hidden p-2 shrink-0">
                {(() => {
                  const source = company.jobs?.[0]?.source || "ITViec";
                  const logoUrl = LOGO[source.toUpperCase()] || LOGO.AIJMC_LOGO;
                  return (
                    <Image
                      src={logoUrl}
                      alt={source}
                      width={64}
                      height={64}
                      className="w-full h-full object-contain"
                    />
                  );
                })()}
              </div>
              <div>
                <h1 className="text-2xl md:text-3xl font-extrabold text-slate-900 dark:text-white mb-2">
                  {company.name}
                </h1>
                <p className="text-sm font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                  {company.industry || "Technology & Software"}
                </p>
              </div>
            </div>

            {/* Facts Grid */}
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-6 backdrop-blur-md text-sm">
              <div>
                <span className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest block mb-0.5">
                  Company Type
                </span>
                <span className="font-bold text-slate-700 dark:text-slate-200">
                  {company.company_type || "N/A"}
                </span>
              </div>
              <div>
                <span className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest block mb-0.5">
                  Company Size
                </span>
                <span className="font-bold text-slate-700 dark:text-slate-200">
                  {company.size || "N/A"}
                </span>
              </div>
              <div>
                <span className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest block mb-0.5">
                  Country
                </span>
                <span className="font-bold text-slate-700 dark:text-slate-200">
                  {company.country || "N/A"}
                </span>
              </div>
              <div className="mt-3">
                <span className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest block mb-0.5">
                  Working Days
                </span>
                <span className="font-bold text-slate-700 dark:text-slate-200">
                  {company.working_days || "N/A"}
                </span>
              </div>
              <div className="mt-3">
                <span className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest block mb-0.5">
                  Overtime Policy
                </span>
                <span className="font-bold text-slate-700 dark:text-slate-200">
                  {company.overtime_policy || "N/A"}
                </span>
              </div>
              {company.website && (
                <div className="mt-3">
                  <span className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest block mb-0.5">
                    Website
                  </span>
                  <a
                    href={company.website}
                    target="_blank"
                    rel="noreferrer"
                    className="font-bold text-[#285872] dark:text-[#407c9c] hover:underline inline-flex items-center gap-1"
                  >
                    Visit Website ↗
                  </a>
                </div>
              )}
            </div>

            {/* Slogan */}
            {company.slogan && (
              <div className="italic text-slate-650 dark:text-slate-350 border-l-4 border-[#285872] pl-4 text-base font-bold bg-white/40 dark:bg-slate-900/20 py-3 rounded-r-xl">
                &quot;{company.slogan}&quot;
              </div>
            )}
            {/* Main Content Layout */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
              {/* Left Column (60%): Description, locations and benefits */}
              <div className="lg:col-span-7 flex flex-col gap-6">
                <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-8 backdrop-blur-md flex flex-col gap-4">
                  <h2 className="text-lg font-extrabold text-slate-900 dark:text-white border-b border-slate-150 dark:border-slate-800 pb-3 mb-2">
                    About the Company
                  </h2>
                  <p className="text-sm font-medium text-slate-650 dark:text-slate-355 leading-relaxed whitespace-pre-line">
                    {company.description || "No description provided."}
                  </p>
                </div>

                {company.addresses && company.addresses.length > 0 && (
                  <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-8 backdrop-blur-md flex flex-col gap-4">
                    <h2 className="text-lg font-extrabold text-slate-900 dark:text-white border-b border-slate-150 dark:border-slate-800 pb-3 mb-2 flex items-center gap-2">
                      <MapPin className="w-5 h-5 text-[#285872] shrink-0" />
                      Office Locations
                    </h2>
                    <ul className="flex flex-col gap-2.5 list-disc pl-5 text-sm text-slate-650 dark:text-slate-355 font-bold">
                      {company.addresses.map((addr, idx) => (
                        <li key={idx} className="leading-relaxed">
                          {addr}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {company.benefits && company.benefits.length > 0 && (
                  <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-8 backdrop-blur-md flex flex-col gap-4">
                    <h2 className="text-lg font-extrabold text-slate-900 dark:text-white border-b border-slate-150 dark:border-slate-800 pb-3 mb-2 flex items-center gap-2">
                      <Gift className="w-5 h-5 text-[#285872] shrink-0" />
                      Key Benefits & Perks
                    </h2>
                    <ul className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm text-slate-650 dark:text-slate-355 font-semibold">
                      {company.benefits.map((benefit, idx) => (
                        <li
                          key={idx}
                          className="flex items-start gap-2.5 leading-relaxed"
                        >
                          <span className="w-2 h-2 bg-[#285872] rounded-full mt-1.5 shrink-0" />
                          <span>{benefit}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* Right Column (40%): Company Job Openings list */}
              <div className="lg:col-span-5 flex flex-col gap-6">
                <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-6 backdrop-blur-md flex flex-col gap-5">
                  <h3 className="text-sm font-extrabold text-slate-900 dark:text-white pb-3 border-b border-slate-100 dark:border-slate-800 flex items-center gap-2">
                    <Briefcase className="w-4.5 h-4.5 text-[#285872]" />
                    {t("title", { count: company.jobs?.length || 0 })}
                  </h3>

                  {!company.jobs || company.jobs.length === 0 ? (
                    <p className="text-xs text-slate-500 font-medium py-10 text-center">
                      {t("no_jobs")}
                    </p>
                  ) : (
                    <>
                      <div className="flex flex-col gap-4">
                        {(company.jobs || [])
                          .slice((page - 1) * pageSize, page * pageSize)
                          .map((job) => (
                            <div
                              key={job.id}
                              className="bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-850 rounded-2xl p-4 flex flex-col gap-2.5 hover:border-[#285872]/45 transition-colors"
                            >
                              <Link
                                href={`/counselee/jobs/${job.id}`}
                                className="text-xs font-black text-[#285872] dark:text-[#407c9c] hover:underline leading-snug line-clamp-1"
                              >
                                {job.title}
                              </Link>
                              <div className="flex flex-wrap gap-1.5">
                                <span className="bg-slate-200/50 dark:bg-slate-900 text-slate-600 dark:text-slate-400 px-2 py-0.5 rounded text-[9px] font-bold uppercase">
                                  {mapEnum(
                                    job.seniority,
                                    "SeniorityLevel",
                                    locale,
                                  )}
                                </span>
                                <span className="bg-slate-200/50 dark:bg-slate-900 text-slate-600 dark:text-slate-400 px-2 py-0.5 rounded text-[9px] font-bold uppercase">
                                  {mapEnum(
                                    job.working_model,
                                    "WorkingModel",
                                    locale,
                                  )}
                                </span>
                              </div>
                              <span className="text-[10px] font-bold text-slate-450 dark:text-slate-500">
                                {formatSalaryRange(
                                  job.min_salary,
                                  job.max_salary,
                                  locale,
                                )}
                              </span>
                            </div>
                          ))}
                      </div>

                      {company.jobs.length > pageSize && (
                        <div className="flex items-center justify-between border-t border-slate-100 dark:border-slate-800 pt-4 mt-2">
                          <button
                            disabled={page === 1}
                            onClick={() => setPage((p) => p - 1)}
                            className="bg-slate-100 hover:bg-slate-200 dark:bg-slate-950 dark:hover:bg-slate-850 disabled:opacity-40 text-slate-700 dark:text-slate-300 rounded-lg px-3 py-1.5 text-[10px] font-bold transition-all cursor-pointer select-none"
                          >
                            {t("prev")}
                          </button>
                          <span className="text-[10px] font-black text-slate-500">
                            {t("page_indicator", {
                              page: page,
                              total: Math.ceil(company.jobs.length / pageSize),
                            })}
                          </span>
                          <button
                            disabled={page * pageSize >= company.jobs.length}
                            onClick={() => setPage((p) => p + 1)}
                            className="bg-slate-100 hover:bg-slate-200 dark:bg-slate-955 dark:hover:bg-slate-850 disabled:opacity-40 text-slate-700 dark:text-slate-300 rounded-lg px-3 py-1.5 text-[10px] font-bold transition-all cursor-pointer select-none"
                          >
                            {t("next")}
                          </button>
                        </div>
                      )}
                    </>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
