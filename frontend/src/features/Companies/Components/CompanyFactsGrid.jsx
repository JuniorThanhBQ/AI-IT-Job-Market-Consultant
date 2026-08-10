"use client";

export default function CompanyFactsGrid({ company }) {
  return (
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
  );
}
