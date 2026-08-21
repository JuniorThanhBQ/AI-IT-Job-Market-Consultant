import { useTranslations } from "next-intl";

export default function CompanyFactsGrid({ company }) {
  const t = useTranslations("Counselee.Company");
  const tEnum = useTranslations("Enums.CompanyType");

  const getCompanyType = (type) => {
    if (!type) return "—";
    try {
      return tEnum(type);
    } catch {
      return type;
    }
  };

  return (
    <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-8 backdrop-blur-md shadow-sm grid grid-cols-2 md:grid-cols-6 gap-6 text-sm font-sans">
      <div className="flex flex-col gap-1">
        <span className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest">
          {t("type")}
        </span>
        <span className="font-black text-slate-800 dark:text-slate-100">
          {getCompanyType(company.company_type)}
        </span>
      </div>
      <div className="flex flex-col gap-1">
        <span className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest">
          {t("size")}
        </span>
        <span className="font-black text-slate-800 dark:text-slate-100">
          {company.size || "—"}
        </span>
      </div>
      <div className="flex flex-col gap-1">
        <span className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest">
          {t("country")}
        </span>
        <span className="font-black text-slate-800 dark:text-slate-100">
          {company.country || "—"}
        </span>
      </div>
      <div className="flex flex-col gap-1">
        <span className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest">
          {t("working_days")}
        </span>
        <span className="font-black text-slate-800 dark:text-slate-100">
          {company.working_days || "—"}
        </span>
      </div>
      <div className="flex flex-col gap-1">
        <span className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest">
          {t("overtime")}
        </span>
        <span className="font-black text-slate-800 dark:text-slate-100">
          {company.overtime_policy || "—"}
        </span>
      </div>
      {company.website && (
        <div className="flex flex-col gap-1">
          <span className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest">
            {t("website")}
          </span>
          <a
            href={company.website}
            target="_blank"
            rel="noreferrer"
            className="font-black text-[#285872] dark:text-[#407c9c] hover:underline inline-flex items-center gap-0.5"
          >
            {t("visit_website")}
          </a>
        </div>
      )}
    </div>
  );
}
