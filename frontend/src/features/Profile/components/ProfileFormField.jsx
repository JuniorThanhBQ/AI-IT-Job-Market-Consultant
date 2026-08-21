"use client";

import React from "react";

export function ProfileFormField({
  index,
  label,
  type = "text",
  value,
  onChange,
  required = false,
  isTextArea = false,
  rows = 3,
  placeholder = "",
}) {
  const labelIndex = index < 10 ? `0${index} /` : `${index} /`;

  return (
    <div className="flex flex-col gap-3 group">
      <label className="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest font-mono flex items-center gap-2">
        <span>{labelIndex}</span>
        <span>{label}</span>
      </label>

      {isTextArea ? (
        <textarea
          rows={rows}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          className="bg-slate-50/50 dark:bg-slate-900/30 border border-slate-200 dark:border-slate-800 focus:border-[#285872] dark:focus:border-white focus:ring-0 rounded-2xl px-4 py-3 text-sm font-medium outline-none resize-none transition-colors text-slate-900 dark:text-white"
        />
      ) : (
        <input
          type={type}
          required={required}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          className="bg-transparent border-0 border-b border-slate-200 dark:border-slate-800 focus:border-slate-900 dark:focus:border-white focus:ring-0 rounded-none px-0 py-3 text-sm font-semibold outline-none transition-colors text-slate-900 dark:text-white"
        />
      )}
    </div>
  );
}
