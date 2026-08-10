"use client";

import { use } from "react";
import { ChevronLeft, Loader2 } from "lucide-react";
import Header from "@/components/shared/Header";
import { useRouter } from "@/i18n/routing";
import { useTranslations } from "next-intl";
import { useCompanyDetail } from "./Hooks/useCompanyDetail";
import CompanyHeaderBox from "./Components/CompanyHeaderBox";
import CompanyFactsGrid from "./Components/CompanyFactsGrid";
import CompanyAboutSection from "./Components/CompanyAboutSection";
import CompanyJobsList from "./Components/CompanyJobsList";

export default function CompanyDetailPage({ params }) {
  const { id } = use(params);
  const router = useRouter();
  const t = useTranslations("Counselee.Company");
  const {
    company,
    loading,
    error,
    page,
    setPage,
    pageSize,
    fetchCompanyDetails,
  } = useCompanyDetail(id);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-955 relative overflow-hidden font-sans pb-16">
      <div
        className="absolute inset-0 pointer-events-none opacity-40 dark:opacity-[0.12] mix-blend-overlay z-0"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E")`,
        }}
      />

      <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-blue-500/10 dark:bg-blue-500/5 rounded-full blur-[120px] pointer-events-none z-0" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-indigo-500/10 dark:bg-indigo-500/5 rounded-full blur-[120px] pointer-events-none z-0" />

      <Header />

      <main className="max-w-[80vw] mx-auto px-4 sm:px-6 pt-24 pb-12 relative z-10 flex flex-col gap-6">
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
            <CompanyHeaderBox company={company} />
            <CompanyFactsGrid company={company} />

            {company.slogan && (
              <div className="italic text-slate-650 dark:text-slate-355 border-l-4 border-[#285872] pl-4 text-base font-bold bg-white/40 dark:bg-slate-900/20 py-3 rounded-r-xl">
                &quot;{company.slogan}&quot;
              </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
              <CompanyAboutSection company={company} />
              <CompanyJobsList
                company={company}
                page={page}
                setPage={setPage}
                pageSize={pageSize}
              />
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
