"use client";

import { Loader2 } from "lucide-react";
import { LOGO } from "@/assets/CloudinaryAssetsUrl";
import Image from "next/image";
import MarkdownRenderer from "@/components/shared/MarkdownRenderer";

export default function ChatbotMessageList({
  messages,
  streamingMessage,
  isSending,
  chatEndRef,
}) {
  return (
    <div className="flex-1 overflow-y-auto pr-2 space-y-6 min-h-0 scrollbar-thin scrollbar-thumb-slate-200 dark:scrollbar-thumb-slate-800">
      {messages.length === 0 && !streamingMessage && !isSending && (
        <div className="flex-1 flex flex-col items-center justify-center text-center p-8 select-none opacity-80 mt-16">
          <div className="w-16 h-16 rounded-full overflow-hidden bg-white border border-[#285872]/20 flex items-center justify-center mb-4 p-2 shadow-sm">
            <Image
              src={LOGO.AIJMC_LOGO}
              alt="AIJMC Logo"
              width={48}
              height={48}
              className="w-full h-full object-contain"
              loading="eager"
            />
          </div>
          <h4 className="text-base font-extrabold text-slate-900 dark:text-white">
            AI IT Career Consultation
          </h4>
          <p className="text-xs text-slate-500 mt-2 max-w-sm leading-relaxed">
            Select a specialized mode from the sidebar or type a query about
            salaries, tech market demands, or CV advice to begin.
          </p>
        </div>
      )}

      {messages.map((msg, index) => (
        <div
          key={index}
          className={`flex gap-3 max-w-3xl ${
            msg.role === "user" ? "ml-auto flex-row-reverse" : "mr-auto"
          }`}
        >
          {msg.role === "bot" && (
            <div className="w-9 h-9 rounded-xl overflow-hidden bg-white border border-[#285872]/20 flex items-center justify-center shrink-0 p-1.5 shadow-sm">
              <Image
                src={LOGO.AIJMC_LOGO}
                alt="AIJMC Logo"
                width={28}
                height={28}
                className="w-full h-full object-contain"
                loading="eager"
              />
            </div>
          )}

          <div
            className={`rounded-[1.75rem] px-6 py-4 text-xs font-medium leading-relaxed ${
              msg.role === "user"
                ? "bg-[#285872] text-white rounded-tr-none shadow-md whitespace-pre-line"
                : msg.isError
                  ? "bg-red-500/10 border border-red-500/20 text-red-500 rounded-tl-none"
                  : "bg-white/90 dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 text-slate-850 dark:text-slate-200 rounded-tl-none shadow-sm"
            }`}
          >
            {msg.role === "bot" ? (
              <MarkdownRenderer content={msg.text} />
            ) : (
              msg.text
            )}
          </div>
        </div>
      ))}

      {(streamingMessage || isSending) && (
        <div className="flex gap-3 max-w-3xl mr-auto">
          <div className="w-9 h-9 rounded-xl overflow-hidden bg-white border border-[#285872]/20 flex items-center justify-center shrink-0 p-1.5 shadow-sm">
            <Image
              src={LOGO.AIJMC_LOGO}
              alt="AIJMC Logo"
              width={28}
              height={28}
              className="w-full h-full object-contain"
              loading="eager"
            />
          </div>
          <div className="rounded-[1.75rem] rounded-tl-none px-6 py-4 text-xs font-medium leading-relaxed bg-white/90 dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 text-slate-850 dark:text-slate-200 min-h-[48px] flex items-center shadow-sm">
            {streamingMessage ? (
              <MarkdownRenderer content={streamingMessage} />
            ) : (
              <div className="flex items-center gap-2 text-xs text-slate-400">
                <Loader2 className="w-4 h-4 animate-spin text-[#285872]" />
                <span>Consulting multi-agent swarm...</span>
              </div>
            )}
          </div>
        </div>
      )}

      <div ref={chatEndRef} />
    </div>
  );
}
