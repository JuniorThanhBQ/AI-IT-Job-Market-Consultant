"use client";

import { use } from "react";
import { ChevronLeft, Loader2 } from "lucide-react";
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
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 relative overflow-hidden font-sans pb-16">
      <main className="w-full max-w-full px-4 sm:px-6 md:px-12 pt-24 pb-12 relative z-10 flex flex-col gap-6">
        <button
          onClick={() => router.back()}
          className="self-start flex items-center gap-2 text-sm font-bold text-slate-555 dark:text-slate-400 hover:text-[#285872] dark:hover:text-[#407c9c] transition-colors cursor-pointer group"
        >
          <ChevronLeft className="w-4 h-4 transition-transform group-hover:-translate-x-1" />
          {t("go_back")}
        </button>

        {loading ? (
          <div className="w-full py-32 flex items-center justify-center">
            <Loader2 className="w-10 h-10 animate-spin text-[#285872] dark:text-[#407c9c]" />
          </div>
        ) : error ? (
          <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-12 text-center backdrop-blur-md">
            <p className="text-red-655 dark:text-red-400 font-bold mb-4">
              {error}
            </p>
            <button
              onClick={fetchCompanyDetails}
              className="bg-[#285872] hover:bg-[#1c3f52] text-white rounded-full px-6 py-2.5 font-bold text-sm transition-colors cursor-pointer"
            >
              {t("try_again")}
            </button>
          </div>
        ) : (
          <div className="flex flex-col gap-8">
            <CompanyHeaderBox company={company} />
            <CompanyFactsGrid company={company} />

            {company.slogan && (
              <div className="py-4 border-l-2 border-[#285872] pl-6 my-2">
                <blockquote className="text-lg md:text-xl font-serif italic text-slate-700 dark:text-slate-300 leading-relaxed">
                  &quot;{company.slogan}&quot;
                </blockquote>
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
