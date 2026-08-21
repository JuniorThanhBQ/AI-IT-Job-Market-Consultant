"use client";

import { useEffect } from "react";
import { Send, AlertCircle } from "lucide-react";

export default function ChatbotInput({
  inputMessage,
  setInputMessage,
  isSending,
  error,
  chatInputRef,
  onSendMessage,
}) {
  useEffect(() => {
    if (!inputMessage && chatInputRef.current) {
      chatInputRef.current.style.height = "auto";
    }
  }, [inputMessage, chatInputRef]);

  return (
    <div className="mt-6 border-t border-slate-150 dark:border-slate-800 pt-5 flex flex-col gap-2 shrink-0">
      <form
        onSubmit={onSendMessage}
        className="flex items-center gap-3 relative"
      >
        <textarea
          ref={chatInputRef}
          rows={1}
          maxLength={500}
          value={inputMessage}
          onChange={(e) => {
            setInputMessage(e.target.value);
            e.target.style.height = "auto";
            e.target.style.height = `${e.target.scrollHeight}px`;
          }}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              onSendMessage(e);
            }
          }}
          placeholder="Ask about IT career paths, salaries, skills, or specific job positions..."
          className="flex-1 bg-white/80 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-850 rounded-2xl px-6 py-4 outline-none focus:ring-2 focus:ring-[#285872] focus:border-transparent transition-all text-xs font-bold text-slate-900 dark:text-white placeholder-slate-400 resize-none overflow-hidden"
          disabled={isSending}
        />
        <button
          type="submit"
          disabled={isSending || !inputMessage.trim()}
          className="bg-[#285872] hover:bg-[#1c3f52] disabled:opacity-40 text-white rounded-2xl px-6 py-4 shadow-lg shadow-[#285872]/20 transition-all hover:scale-105 shrink-0 flex items-center justify-center cursor-pointer"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>

      {error && (
        <div className="text-xs font-semibold text-red-500 flex items-center gap-1.5 px-2">
          <AlertCircle className="w-4 h-4" />
          {error}
        </div>
      )}
    </div>
  );
}
