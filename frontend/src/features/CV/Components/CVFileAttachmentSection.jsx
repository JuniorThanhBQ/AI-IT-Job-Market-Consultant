"use client";

import { Paperclip, Upload, Loader2 } from "lucide-react";
import { useTranslations } from "next-intl";

export default function CVFileAttachmentSection({
  attachment,
  usingCvMode,
  setUsingCvMode,
  uploading,
  fileInputRef,
  onFileUpload,
}) {
  const t = useTranslations("Counselee.CV");

  return (
    <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-8 backdrop-blur-md shadow-sm flex flex-col gap-6">
      <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-4">
        <h2 className="text-xl font-extrabold text-slate-900 dark:text-white flex items-center gap-2.5">
          <Paperclip className="w-5 h-5 text-[#285872]" />
          {t("attachment_title")}
        </h2>
        <div className="flex items-center gap-2">
          <label className="text-xs font-bold text-slate-500 cursor-pointer flex items-center gap-2">
            <input
              type="checkbox"
              checked={usingCvMode}
              onChange={(e) => setUsingCvMode(e.target.checked)}
              className="rounded border-slate-300 text-[#285872] focus:ring-[#285872] w-4 h-4"
            />
            {t("prefer_uploaded_cv")}
          </label>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row items-center gap-6">
        <input
          type="file"
          ref={fileInputRef}
          onChange={onFileUpload}
          accept=".pdf,.docx,.doc"
          className="hidden"
        />

        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading}
          className="w-full sm:w-auto bg-slate-50 dark:bg-slate-955 border border-dashed border-slate-300 dark:border-slate-800 hover:border-[#285872] dark:hover:border-[#285872] rounded-2xl p-6 flex flex-col items-center justify-center gap-2 text-center transition-all cursor-pointer group"
        >
          {uploading ? (
            <Loader2 className="w-8 h-8 animate-spin text-[#285872]" />
          ) : (
            <Upload className="w-8 h-8 text-slate-400 group-hover:text-[#285872] transition-colors" />
          )}
          <span className="text-xs font-bold text-slate-700 dark:text-slate-200">
            {attachment ? t("replace_file") : t("upload_file")}
          </span>
          <span className="text-[10px] text-slate-400">
            {t("supported_formats")}
          </span>
        </button>

        {attachment && (
          <div className="flex-1 w-full bg-slate-50 dark:bg-slate-955 border border-slate-200 dark:border-slate-850 rounded-2xl p-4 flex items-center justify-between">
            <div className="flex items-center gap-3 overflow-hidden">
              <Paperclip className="w-4 h-4 text-[#285872] shrink-0" />
              <a
                href={attachment}
                target="_blank"
                rel="noreferrer"
                className="text-xs font-bold text-[#285872] hover:underline truncate"
              >
                {attachment.split("/").pop()}
              </a>
            </div>
            <span className="text-[10px] font-bold text-emerald-600 bg-emerald-100 dark:bg-emerald-955/30 px-2 py-1 rounded-full uppercase">
              {t("uploaded")}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
