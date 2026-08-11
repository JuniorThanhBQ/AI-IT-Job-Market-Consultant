"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "motion/react";
import {
  MessageSquare,
  Bot,
  X,
  Send,
  Trash2,
  Loader2,
  Trash,
  Maximize2,
} from "lucide-react";
import { useAuth } from "@/context/AuthProvider";
import { useLocale, useTranslations } from "next-intl";
import { consultantApi } from "@/configs/apis";
import { cn } from "@/lib/utils";
import { LOGO } from "@/assets/CloudinaryAssetsUrl";
import Image from "next/image";
import { useRouter } from "@/i18n/routing";
import MarkdownRenderer from "./MarkdownRenderer";

export default function ChatbotPopup() {
  const { isAuthenticated } = useAuth();
  const locale = useLocale();
  const router = useRouter();
  const t = useTranslations("Counselee.Chat");

  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [streamingMessage, setStreamingMessage] = useState("");
  const [activeIntent, setActiveIntent] = useState("MARKET_ANALYSIS");
  const [confirmClear, setConfirmClear] = useState(false);

  const messagesEndRef = useRef(null);
  const chatInputRef = useRef(null);

  const loadHistory = useCallback(async () => {
    try {
      const data = await consultantApi.getHistory();
      const historyMessages = [];
      data.forEach((item) => {
        if (item.user_input && item.user_input !== "deleted") {
          historyMessages.push({ role: "user", text: item.user_input });
        }
        if (item.output && item.output !== "deleted") {
          historyMessages.push({ role: "bot", text: item.output });
        }
      });
      setMessages(historyMessages);
    } catch (err) {
      console.error(err);
    }
  }, []);

  useEffect(() => {
    if (isOpen && isAuthenticated) {
      const timer = setTimeout(() => {
        loadHistory();
      }, 0);
      return () => clearTimeout(timer);
    }
  }, [isOpen, isAuthenticated, loadHistory]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingMessage, isOpen]);

  const handleClearHistory = async () => {
    try {
      await consultantApi.clearHistory();
      setMessages([]);
      setConfirmClear(false);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userText = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", text: userText }]);
    setLoading(true);
    setStreamingMessage("");

    try {
      const token = localStorage.getItem("token");
      const response = await fetch(
        `${
          process.env.BACKEND_INTERNAL_URL || "http://localhost:8081/api/v1"
        }/consultants/chatbot/process-intent`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            intent: activeIntent,
            user_input: userText,
          }),
        },
      );

      if (!response.ok) {
        throw new Error();
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let done = false;
      let textBuffer = "";
      let accumulatedText = "";

      while (!done) {
        const { value, done: readerDone } = await reader.read();
        done = readerDone;
        if (value) {
          const chunkStr = decoder.decode(value, { stream: !done });
          textBuffer += chunkStr;
          const lines = textBuffer.split("\n");
          textBuffer = lines.pop() || "";

          for (const line of lines) {
            if (!line.trim()) continue;
            try {
              const parsed = JSON.parse(line);
              if (parsed.type === "chunk" && parsed.text) {
                accumulatedText += parsed.text;
                setStreamingMessage(accumulatedText);
              }
            } catch (e) {
              // Ignore partial JSON parse errors
            }
          }
        }
      }

      setMessages((prev) => [...prev, { role: "bot", text: accumulatedText }]);
      setStreamingMessage("");
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "bot", text: t("error_message") },
      ]);
    } finally {
      setLoading(false);
      setTimeout(() => chatInputRef.current?.focus(), 50);
    }
  };

  if (!isAuthenticated) return null;

  return (
    <>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 z-50 w-14 h-14 bg-[#285872] hover:bg-[#1c3f52] text-white rounded-full flex items-center justify-center shadow-2xl transition-all duration-300 hover:scale-110 active:scale-95 group cursor-pointer"
      >
        {isOpen ? (
          <X className="w-6 h-6 transition-transform duration-300 rotate-90" />
        ) : (
          <Bot className="w-6 h-6 animate-pulse" />
        )}
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 50, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 50, scale: 0.95 }}
            transition={{ type: "spring", stiffness: 350, damping: 30 }}
            className="fixed bottom-24 right-6 w-[90vw] md:w-[65vw] h-[600px] max-w-[calc(100vw-3rem)] max-h-[calc(100vh-8rem)] z-50 bg-white/95 dark:bg-slate-900/95 border border-slate-200 dark:border-slate-800 rounded-[2rem] shadow-2xl flex flex-col overflow-hidden backdrop-blur-md"
          >
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-150 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950/20">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl overflow-hidden bg-white border border-[#285872]/20 flex items-center justify-center shrink-0">
                  <Image
                    src={LOGO.AIJMC_LOGO}
                    alt="AIJMC Logo"
                    width={32}
                    height={32}
                    className="w-8 h-8 object-contain"
                    loading="eager"
                  />
                </div>
                <div>
                  <h3 className="text-sm font-extrabold text-slate-900 dark:text-white">
                    Market AI Advisor
                  </h3>
                  <span className="text-[10px] text-emerald-500 font-bold flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-ping" />
                    {t("online")}
                  </span>
                </div>
              </div>
              <div className="flex items-center gap-2">
                {confirmClear ? (
                  <div className="flex items-center gap-1.5">
                    <button
                      onClick={handleClearHistory}
                      className="text-[10px] bg-red-100 hover:bg-red-200 text-red-655 px-2.5 py-1.5 rounded-lg font-bold transition-all cursor-pointer"
                    >
                      {t("confirm_clear")}
                    </button>
                    <button
                      onClick={() => setConfirmClear(false)}
                      className="text-[10px] bg-slate-100 hover:bg-slate-200 text-slate-600 px-2.5 py-1.5 rounded-lg font-bold transition-all cursor-pointer"
                    >
                      {t("cancel_clear")}
                    </button>
                  </div>
                ) : (
                  <button
                    onClick={() => setConfirmClear(true)}
                    className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg text-slate-400 hover:text-red-500 transition-colors cursor-pointer"
                  >
                    <Trash2 className="w-4.5 h-4.5" />
                  </button>
                )}
                <button
                  type="button"
                  onClick={() => {
                    setIsOpen(false);
                    router.push("/counselee/chatbot");
                  }}
                  title="Open Full Chat Experience"
                  className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg text-slate-400 hover:text-[#285872] dark:hover:text-[#58a0c9] transition-colors cursor-pointer"
                >
                  <Maximize2 className="w-4.5 h-4.5" />
                </button>
                <button
                  onClick={() => setIsOpen(false)}
                  className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg text-slate-400 hover:text-slate-650 transition-colors cursor-pointer"
                >
                  <X className="w-4.5 h-4.5" />
                </button>
              </div>
            </div>

            <div className="flex flex-wrap gap-2 px-6 py-3 bg-slate-50/30 dark:bg-slate-950/10 border-b border-slate-100 dark:border-slate-850">
              {[
                { id: "MARKET_ANALYSIS", label: "Market Analysis" },
                {
                  id: "PERSONAL_STANDARD_EVALUATION",
                  label: "Career Evaluation",
                },
                { id: "JOB_RECOMMEND", label: "Job Recommend" },
                { id: "DEEP_ANALYSIS_EVALUATION", label: "Deep CV Analysis" },
              ].map((tab) => {
                const isActive = activeIntent === tab.id;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveIntent(tab.id)}
                    className={cn(
                      "text-[10px] font-bold px-3 py-1.5 rounded-full transition-all border cursor-pointer select-none",
                      isActive
                        ? "bg-[#285872] border-[#285872] text-white"
                        : "bg-transparent border-slate-200 dark:border-slate-800 text-slate-500 hover:text-slate-800 dark:hover:text-slate-200",
                    )}
                  >
                    {tab.label}
                  </button>
                );
              })}
            </div>

            <div className="flex-1 overflow-y-auto px-6 py-4 flex flex-col gap-4">
              {messages.length === 0 && !streamingMessage && !loading && (
                <div className="flex-1 flex flex-col items-center justify-center text-center p-6 select-none opacity-80 mt-12">
                  <div className="w-14 h-14 rounded-full overflow-hidden bg-white border border-[#285872]/20 flex items-center justify-center mb-4">
                    <Image
                      src={LOGO.AIJMC_LOGO}
                      alt="AIJMC Logo"
                      width={40}
                      height={40}
                      className="w-10 h-10 object-contain"
                      loading="eager"
                    />
                  </div>
                  <h4 className="text-sm font-extrabold text-slate-800 dark:text-slate-200">
                    {t("welcome_title")}
                  </h4>
                  <p className="text-xs text-slate-500 mt-2 max-w-[280px] leading-relaxed">
                    {t("welcome_desc")}
                  </p>
                </div>
              )}

              {messages.map((msg, index) => (
                <div
                  key={index}
                  className={cn(
                    "flex gap-3 max-w-[85%]",
                    msg.role === "user"
                      ? "ml-auto flex-row-reverse"
                      : "mr-auto",
                  )}
                >
                  {msg.role === "bot" && (
                    <div className="w-8 h-8 rounded-lg overflow-hidden bg-white border border-[#285872]/20 flex items-center justify-center shrink-0">
                      <Image
                        src={LOGO.AIJMC_LOGO}
                        alt="AIJMC Logo"
                        width={24}
                        height={24}
                        className="w-6 h-6 object-contain"
                        loading="eager"
                      />
                    </div>
                  )}
                  <div
                    className={cn(
                      "px-4 py-2.5 rounded-[1.25rem] text-xs leading-relaxed font-medium",
                      msg.role === "user"
                        ? "bg-[#285872] text-white rounded-tr-none whitespace-pre-line"
                        : "bg-slate-100 dark:bg-slate-800 text-slate-850 dark:text-slate-200 rounded-tl-none border border-slate-200/50 dark:border-slate-700/50",
                    )}
                  >
                    {msg.role === "bot" ? (
                      <MarkdownRenderer content={msg.text} />
                    ) : (
                      msg.text
                    )}
                  </div>
                </div>
              ))}

              {(streamingMessage || loading) && (
                <div className="flex gap-3 max-w-[85%] mr-auto">
                  <div className="w-8 h-8 rounded-lg overflow-hidden bg-white border border-[#285872]/20 flex items-center justify-center shrink-0">
                    <Image
                      src={LOGO.AIJMC_LOGO}
                      alt="AIJMC Logo"
                      width={24}
                      height={24}
                      className="w-6 h-6 object-contain"
                      loading="eager"
                    />
                  </div>
                  <div className="px-4 py-2.5 rounded-[1.25rem] rounded-tl-none text-xs leading-relaxed bg-slate-100 dark:bg-slate-800 text-slate-850 dark:text-slate-200 border border-slate-200/50 dark:border-slate-700/50 min-h-[40px] flex items-center">
                    {streamingMessage ? (
                      <MarkdownRenderer content={streamingMessage} />
                    ) : (
                      <Loader2 className="w-4 h-4 animate-spin text-[#285872]" />
                    )}
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            <form
              onSubmit={handleSend}
              className="p-4 border-t border-slate-150 dark:border-slate-800 bg-white/50 dark:bg-slate-900/50 flex items-center gap-2"
            >
              <input
                ref={chatInputRef}
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder={t("input_placeholder")}
                disabled={loading}
                className="flex-1 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-850 rounded-2xl px-4 py-3 text-sm outline-none focus:ring-1 focus:ring-[#285872] text-slate-900 dark:text-white font-medium"
              />
              <button
                type="submit"
                disabled={!input.trim() || loading}
                className="w-11 h-11 bg-[#285872] hover:bg-[#1c3f52] disabled:opacity-40 text-white rounded-xl flex items-center justify-center transition-all cursor-pointer shrink-0 shadow-md"
              >
                <Send className="w-4.5 h-4.5" />
              </button>
            </form>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
