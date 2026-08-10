"use client";

import { MapPin, Gift } from "lucide-react";

export default function CompanyAboutSection({ company }) {
  return (
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
  );
}
