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
import { useRouter } from "@/i18n/routing";

export default function CompanyDetailPage({ params }) {
  const { id } = use(params);
  const router = useRouter();
  const { user, authLoading } = useAuth();
  const [company, setCompany] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

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

      <main className="max-w-4xl mx-auto px-4 sm:px-6 pt-24 pb-12 relative z-10 flex flex-col gap-6">
        {/* Back Link */}
        <button
          onClick={() => router.back()}
          className="self-start flex items-center gap-2 text-sm font-bold text-slate-550 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors cursor-pointer group"
        >
          <ChevronLeft className="w-4 h-4 transition-transform group-hover:-translate-x-1" />
          Go Back
        </button>

        {loading ? (
          <div className="w-full py-32 flex items-center justify-center">
            <Loader2 className="w-10 h-10 animate-spin text-blue-600 dark:text-blue-500" />
          </div>
        ) : error ? (
          <div className="bg-white/80 dark:bg-slate-900/40 border border-red-250 dark:border-red-900 rounded-[2rem] p-12 text-center backdrop-blur-md">
            <p className="text-red-600 dark:text-red-400 font-bold mb-4">
              {error}
            </p>
            <button
              onClick={fetchCompanyDetails}
              className="bg-blue-600 hover:bg-blue-500 text-white rounded-full px-6 py-2.5 font-bold text-sm transition-colors cursor-pointer"
            >
              Try Again
            </button>
          </div>
        ) : (
          <div className="flex flex-col gap-8">
            {/* Header Box */}
            <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2.5rem] p-8 backdrop-blur-md flex items-center gap-5 shadow-sm">
              <div className="w-16 h-16 bg-slate-100 dark:bg-slate-950 border border-slate-200 dark:border-slate-850 rounded-2xl flex items-center justify-center text-slate-400">
                <Building className="w-8 h-8 text-blue-600 dark:text-blue-500" />
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
                    className="font-bold text-blue-600 dark:text-blue-400 hover:underline inline-flex items-center gap-1"
                  >
                    Visit Website ↗
                  </a>
                </div>
              )}
            </div>

            {/* Slogan */}
            {company.slogan && (
              <div className="italic text-slate-650 dark:text-slate-350 border-l-4 border-blue-500 pl-4 text-base font-bold bg-white/40 dark:bg-slate-900/20 py-3 rounded-r-xl">
                &quot;{company.slogan}&quot;
              </div>
            )}

            {/* Main Content Layout */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Left Column: Description */}
              <div className="lg:col-span-2 flex flex-col gap-6">
                <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-8 backdrop-blur-md flex flex-col gap-4">
                  <h2 className="text-lg font-extrabold text-slate-900 dark:text-white border-b border-slate-150 dark:border-slate-800 pb-3 mb-2">
                    About the Company
                  </h2>
                  <p className="text-sm font-medium text-slate-650 dark:text-slate-355 leading-relaxed whitespace-pre-line">
                    {company.description || "No description provided."}
                  </p>
                </div>

                {/* Office locations list */}
                {company.addresses && company.addresses.length > 0 && (
                  <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-8 backdrop-blur-md flex flex-col gap-4">
                    <h2 className="text-lg font-extrabold text-slate-900 dark:text-white border-b border-slate-150 dark:border-slate-800 pb-3 mb-2 flex items-center gap-2">
                      <MapPin className="w-5 h-5 text-blue-500 shrink-0" />
                      Office Locations
                    </h2>
                    <ul className="flex flex-col gap-2.5 list-disc pl-5 text-sm text-slate-650 dark:text-slate-350 font-bold">
                      {company.addresses.map((addr, idx) => (
                        <li key={idx} className="leading-relaxed">
                          {addr}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* Right Column: Benefits & Key Perks */}
              <div className="lg:col-span-1 flex flex-col gap-6">
                {company.benefits && company.benefits.length > 0 && (
                  <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-6 backdrop-blur-md">
                    <h3 className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-4 flex items-center gap-2">
                      <Gift className="w-4 h-4 text-blue-500" />
                      Key Benefits
                    </h3>
                    <ul className="flex flex-col gap-3 text-sm text-slate-650 dark:text-slate-350 font-semibold">
                      {company.benefits.map((benefit, idx) => (
                        <li
                          key={idx}
                          className="flex items-start gap-2.5 leading-relaxed"
                        >
                          <span className="w-2 h-2 bg-blue-550 rounded-full mt-1.5 shrink-0" />
                          <span>{benefit}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
