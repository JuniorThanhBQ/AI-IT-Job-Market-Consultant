"use client";

import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { isSafeUrl, renderTextWithHtmlBreaks } from "@/utils/url";

function MarkdownRenderer({ content, className = "" }) {
  if (!content) return null;

  return (
    <div className={`space-y-1 ${className} max-w-full overflow-hidden`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          h1: ({ children }) => (
            <h1 className="text-lg font-black text-slate-900 dark:text-white mt-4 mb-2">
              {children}
            </h1>
          ),
          h2: ({ children }) => (
            <h2 className="text-base font-extrabold text-slate-900 dark:text-white mt-4 mb-1 border-b border-slate-100 dark:border-slate-800 pb-1">
              {children}
            </h2>
          ),
          h3: ({ children }) => (
            <h3 className="text-sm font-extrabold text-slate-900 dark:text-white mt-3 mb-1">
              {children}
            </h3>
          ),
          h4: ({ children }) => (
            <h4 className="text-xs font-black uppercase tracking-wider text-[#285872] dark:text-[#58a0c9] mt-3 mb-1">
              {children}
            </h4>
          ),
          p: ({ children }) => (
            <p className="text-xs font-medium text-slate-800 dark:text-slate-200 leading-relaxed my-1">
              {children}
            </p>
          ),
          blockquote: ({ children }) => (
            <blockquote className="border-l-4 border-[#285872] pl-3 py-1 my-2 bg-slate-50 dark:bg-slate-955/60 rounded-r-xl text-xs italic text-slate-650 dark:text-slate-355">
              {children}
            </blockquote>
          ),
          hr: () => (
            <hr className="my-4 border-slate-200 dark:border-slate-800" />
          ),
          ul: ({ children }) => (
            <ul className="list-disc pl-5 space-y-1.5 my-2 text-xs font-medium text-slate-755 dark:text-slate-300 leading-relaxed">
              {children}
            </ul>
          ),
          ol: ({ children, start }) => (
            <ol
              start={start}
              className="list-decimal pl-5 space-y-1.5 my-2 text-xs font-medium text-slate-755 dark:text-slate-300 leading-relaxed"
            >
              {children}
            </ol>
          ),
          li: ({ children }) => <li className="pl-1">{children}</li>,
          table: ({ children }) => (
            <div className="my-3 overflow-x-auto rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm w-full max-w-full">
              <table className="w-full text-left text-xs border-collapse">
                {children}
              </table>
            </div>
          ),
          thead: ({ children }) => (
            <thead className="bg-slate-100 dark:bg-slate-800/80 text-slate-900 dark:text-slate-100 font-bold border-b border-slate-200 dark:border-slate-700">
              {children}
            </thead>
          ),
          tbody: ({ children }) => (
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800 text-slate-755 dark:text-slate-300">
              {children}
            </tbody>
          ),
          tr: ({ children }) => (
            <tr className="hover:bg-slate-50 dark:hover:bg-slate-800/40 transition-colors">
              {children}
            </tr>
          ),
          th: ({ children, style }) => (
            <th
              className={`px-3 py-2.5 font-bold text-${style?.textAlign || "left"}`}
            >
              {renderTextWithHtmlBreaks(children)}
            </th>
          ),
          td: ({ children, style }) => (
            <td
              className={`px-3 py-2 leading-relaxed text-${style?.textAlign || "left"}`}
            >
              {renderTextWithHtmlBreaks(children)}
            </td>
          ),
          pre: ({ children }) => (
            <div className="my-3 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden w-full max-w-full">
              <pre className="overflow-x-auto p-3 bg-slate-50 dark:bg-slate-900 w-full max-w-full">
                {children}
              </pre>
            </div>
          ),
          code: ({ className, children }) => {
            const match = /language-(\w+)/.exec(className || "");
            const isInline = !match;
            if (isInline) {
              return (
                <code className="bg-slate-100 dark:bg-slate-800 text-[#285872] dark:text-[#58a0c9] px-1.5 py-0.5 rounded text-[11px] font-mono border border-slate-200 dark:border-slate-750">
                  {children}
                </code>
              );
            }
            const lang = match[1];
            return (
              <div className="w-full overflow-hidden">
                <div className="px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 bg-slate-100 dark:bg-slate-800/80 border-b border-slate-200 dark:border-slate-700">
                  {lang}
                </div>
                <code className="text-[11px] font-mono text-slate-800 dark:text-slate-200 whitespace-pre">
                  {children}
                </code>
              </div>
            );
          },
          a: ({ href, children }) => {
            const safe = isSafeUrl(href);
            return safe ? (
              <a
                href={href}
                target="_blank"
                rel="noopener noreferrer"
                className="text-[#285872] dark:text-[#58a0c9] underline hover:opacity-80 font-bold"
              >
                {children}
              </a>
            ) : (
              <span>{children}</span>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}

export default React.memo(MarkdownRenderer);
