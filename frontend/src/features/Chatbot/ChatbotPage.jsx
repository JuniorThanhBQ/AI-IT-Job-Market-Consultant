"use client";

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "motion/react";
import {
  Bot,
  Send,
  ArrowLeft,
  Sparkles,
  Layers,
  Loader2,
  User,
  Briefcase,
  AlertCircle,
  Building,
  MapPin,
  DollarSign,
  Clock,
  Compass,
} from "lucide-react";
import { useAuth } from "@/context/AuthProvider";
import { consultantApi } from "@/configs/apis";
import { Link, useRouter } from "@/i18n/routing";

export default function ChatbotPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();

  const [messages, setMessages] = useState([
    {
      id: "welcome",
      sender: "bot",
      text: "Hello! I am your AI Career Consultant. Send me a message or choose a specialized consulting option below to analyze your IT profile, suggest skills, or match relevant tech vacancies.",
      intent: "general",
      timestamp: new Date(),
    },
  ]);

  const [inputMessage, setInputMessage] = useState("");
  const [selectedIntent, setSelectedIntent] = useState("general_consulting");
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState("");

  const chatEndRef = useRef(null);

  // Suggested intents helper
  const suggestedIntents = [
    {
      id: "general_consulting",
      name: "Career Counseling",
      desc: "General IT career path advice & consulting.",
    },
    {
      id: "cv_analysis",
      name: "CV Assessment",
      desc: "Evaluate your CV strengths and improvement areas.",
    },
    {
      id: "job_matching",
      name: "Job Recommendation",
      desc: "Find job postings matching your current skills.",
    },
    {
      id: "skill_gap_analysis",
      name: "Skill Gap Analysis",
      desc: "Identify skills you need for desired tech roles.",
    },
  ];

  // Redirect if not logged in
  useEffect(() => {
    if (!authLoading && !user) {
      router.replace("/counselee/login");
    }
  }, [user, authLoading, router]);

  // Scroll to bottom on new messages
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isSending]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isSending) return;

    const userText = inputMessage;
    setInputMessage("");
    setError("");

    const userMsgId = `user-${Date.now()}`;
    const newMessages = [
      ...messages,
      {
        id: userMsgId,
        sender: "user",
        text: userText,
        timestamp: new Date(),
      },
    ];
    setMessages(newMessages);
    setIsSending(true);

    try {
      // Call Backend Chatbot Agent Orchestration
      const response = await consultantApi.processChatbotIntent(
        selectedIntent,
        userText,
      );

      setMessages((prev) => [
        ...prev,
        {
          id: `bot-${Date.now()}`,
          sender: "bot",
          text: response.result || "Processing completed successfully.",
          intent: response.intent_executed,
          sequence: response.sequence || [],
          toolOutputs: response.tool_outputs || null,
          timestamp: new Date(),
        },
      ]);
    } catch (err) {
      setError(
        "Failed to connect to the consultant agent. Please check your credentials and try again.",
      );
      setMessages((prev) => [
        ...prev,
        {
          id: `bot-err-${Date.now()}`,
          sender: "bot",
          text: "Oops! I encountered an error while coordinating the specialized career agents. Please try resubmitting.",
          isError: true,
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsSending(false);
    }
  };

  if (authLoading || !user) {
    return (
      <div className="min-h-screen w-full flex items-center justify-center bg-slate-50 dark:bg-slate-955 text-slate-900 dark:text-white transition-colors duration-300">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600 dark:text-blue-500" />
      </div>
    );
  }

  return (
    <div className="relative min-h-screen bg-slate-50 dark:bg-slate-955 text-slate-900 dark:text-slate-100 flex flex-col font-sans overflow-hidden transition-colors duration-300">
      {/* Organic noise background */}
      <div className="pointer-events-none absolute inset-0 z-0 opacity-[0.03] dark:opacity-[0.05] mix-blend-overlay">
        <svg className="w-full h-full">
          <filter id="noiseFilter">
            <feTurbulence
              type="fractalNoise"
              baseFrequency="0.75"
              numOctaves="3"
              stitchTiles="stitch"
            />
          </filter>
          <rect width="100%" height="100%" filter="url(#noiseFilter)" />
        </svg>
      </div>

      {/* Moving blurred gradient background circles */}
      <motion.div
        animate={{
          x: [0, 20, -10, 0],
          y: [0, -30, 20, 0],
          scale: [1, 1.1, 0.95, 1],
        }}
        transition={{ duration: 20, repeat: Infinity, ease: "easeInOut" }}
        className="absolute top-0 right-0 w-[45vw] h-[45vw] bg-blue-500/10 dark:bg-blue-600/15 rounded-full blur-[130px] pointer-events-none z-0"
      />
      <motion.div
        animate={{
          x: [0, -20, 15, 0],
          y: [0, 25, -15, 0],
          scale: [1, 1.05, 0.9, 1],
        }}
        transition={{ duration: 25, repeat: Infinity, ease: "easeInOut" }}
        className="absolute bottom-0 left-0 w-[40vw] h-[40vw] bg-purple-500/10 dark:bg-purple-600/15 rounded-full blur-[130px] pointer-events-none z-0"
      />

      {/* Main chat header */}
      <header className="relative z-10 border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-950/80 backdrop-blur-md shrink-0">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link
              href="/counselee/overview"
              className="text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white p-2.5 border border-slate-200 dark:border-slate-800 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-850 transition-all cursor-pointer"
            >
              <ArrowLeft className="w-4 h-4" />
            </Link>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center text-white shadow-lg">
                <Bot className="w-6 h-6 animate-pulse" />
              </div>
              <div>
                <h1 className="text-base font-extrabold text-slate-900 dark:text-white leading-tight">
                  AI Career Consultant
                </h1>
                <p className="text-[11px] text-emerald-600 dark:text-emerald-450 font-semibold uppercase tracking-wider flex items-center gap-1">
                  <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-ping" />
                  Active Agents Ready
                </p>
              </div>
            </div>
          </div>

          <div className="hidden md:flex bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-1.5 gap-2 max-w-lg">
            {suggestedIntents.map((intent) => (
              <button
                key={intent.id}
                onClick={() => setSelectedIntent(intent.id)}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                  selectedIntent === intent.id
                    ? "bg-blue-600 text-white shadow-md"
                    : "text-slate-550 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
                }`}
              >
                {intent.name}
              </button>
            ))}
          </div>
        </div>
      </header>

      {/* Chat application body */}
      <div className="relative z-10 flex-1 max-w-7xl w-full mx-auto px-6 py-6 flex flex-col lg:flex-row gap-6 min-h-0">
        {/* Left column: Sidebar for intent select & guidelines */}
        <aside className="lg:w-80 flex flex-col gap-6 shrink-0">
          <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-6 backdrop-blur-md flex flex-col gap-5">
            <h2 className="text-sm font-extrabold text-slate-900 dark:text-white uppercase tracking-wider flex items-center gap-2">
              <Compass className="w-4 h-4 text-blue-500" />
              Consulting Modes
            </h2>
            <div className="flex flex-col gap-3">
              {suggestedIntents.map((intent) => (
                <button
                  key={intent.id}
                  onClick={() => setSelectedIntent(intent.id)}
                  className={`text-left p-4 rounded-2xl border transition-all flex flex-col gap-1.5 group cursor-pointer ${
                    selectedIntent === intent.id
                      ? "bg-blue-600/10 border-blue-200 dark:border-blue-900 text-blue-600 dark:text-blue-400"
                      : "bg-slate-50/50 dark:bg-slate-955/40 border-slate-200 dark:border-slate-850 hover:border-slate-350 dark:hover:border-slate-750 text-slate-550 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
                  }`}
                >
                  <span className="text-xs font-extrabold tracking-wide uppercase group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                    {intent.name}
                  </span>
                  <span className="text-[11px] font-medium leading-relaxed opacity-80">
                    {intent.desc}
                  </span>
                </button>
              ))}
            </div>
          </div>

          <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-6 backdrop-blur-md hidden lg:flex flex-col gap-3">
            <h3 className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest">
              Multi-Agent Team
            </h3>
            <p className="text-[11px] text-slate-505 dark:text-slate-400 leading-relaxed font-medium">
              When processing an intent, the supervisor agent coordinates
              specialized sub-agents (e.g. CV Analyzer, Market Forecaster, Job
              Matcher) to execute sequences and compute the best matches.
            </p>
          </div>
        </aside>

        <main className="flex-1 bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-6 backdrop-blur-md flex flex-col min-h-0">
          {/* Scrollable message log */}
          <div className="flex-1 overflow-y-auto pr-2 space-y-6 min-h-0 scrollbar-thin scrollbar-thumb-slate-200 dark:scrollbar-thumb-slate-800">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex gap-3 max-w-3xl ${
                  msg.sender === "user" ? "ml-auto flex-row-reverse" : ""
                }`}
              >
                {msg.sender === "bot" ? (
                  <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white shrink-0 shadow-md">
                    <Bot className="w-5 h-5" />
                  </div>
                ) : (
                  <div className="w-8 h-8 rounded-lg bg-slate-100 border border-slate-200 dark:bg-slate-850 dark:border-slate-800 flex items-center justify-center text-slate-650 dark:text-slate-300 shrink-0">
                    <User className="w-5 h-5" />
                  </div>
                )}

                <div className="flex flex-col gap-2">
                  <div
                    className={`rounded-[2rem] px-6 py-4 text-sm font-medium leading-relaxed leading-[1.6] ${
                      msg.sender === "user"
                        ? "bg-blue-600 text-white rounded-tr-sm shadow-md"
                        : msg.isError
                          ? "bg-red-500/10 border border-red-500/20 text-red-400 rounded-tl-sm"
                          : "bg-slate-50 dark:bg-slate-900 border border-slate-150 dark:border-slate-850 text-slate-800 dark:text-slate-250 rounded-tl-sm shadow-sm"
                    }`}
                  >
                    <p className="whitespace-pre-line">{msg.text}</p>

                    {/* Collapsible reasoning path (sequence) */}
                    {msg.sequence && msg.sequence.length > 0 && (
                      <div className="mt-4 border-t border-slate-200 dark:border-slate-800 pt-3">
                        <span className="text-[10px] font-bold text-slate-450 dark:text-slate-500 uppercase tracking-widest flex items-center gap-1.5 mb-2">
                          <Layers className="w-3.5 h-3.5 text-blue-500" />
                          Agent Orchestration Sequence
                        </span>
                        <div className="flex flex-col gap-1.5 pl-2 border-l border-slate-200 dark:border-slate-800">
                          {msg.sequence.map((step, idx) => (
                            <div
                              key={idx}
                              className="flex items-center gap-2 text-[11px] text-slate-550 dark:text-slate-400 font-medium"
                            >
                              <span className="w-1.5 h-1.5 bg-blue-500 rounded-full shrink-0" />
                              <span>{step}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Rendering tool outputs if available (e.g. recommended jobs) */}
                    {msg.toolOutputs && (
                      <div className="mt-4 border-t border-slate-200 dark:border-slate-800 pt-3 flex flex-col gap-3">
                        <span className="text-[10px] font-bold text-slate-450 dark:text-slate-500 uppercase tracking-widest flex items-center gap-1.5">
                          <Briefcase className="w-3.5 h-3.5 text-blue-500" />
                          Extracted Matches
                        </span>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-1">
                          {typeof msg.toolOutputs === "object" ? (
                            Object.keys(msg.toolOutputs).map((key, i) => {
                              const val = msg.toolOutputs[key];
                              return (
                                <div
                                  key={i}
                                  className="bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-850 rounded-xl p-3 text-xs flex flex-col gap-1.5"
                                >
                                  <span className="font-bold text-slate-900 dark:text-white uppercase tracking-wider text-[10px] text-blue-600 dark:text-blue-400">
                                    {key.replace(/_/g, " ")}
                                  </span>
                                  <p className="text-[11px] text-slate-600 dark:text-slate-400 leading-relaxed whitespace-pre-line truncate">
                                    {typeof val === "string"
                                      ? val
                                      : JSON.stringify(val)}
                                  </p>
                                </div>
                              );
                            })
                          ) : (
                            <p className="text-[11px] text-slate-605 dark:text-slate-400">
                              {msg.toolOutputs}
                            </p>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                  <span className="text-[10px] text-slate-450 dark:text-slate-500 font-bold uppercase tracking-wider pl-2 mt-0.5">
                    {msg.timestamp.toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </span>
                </div>
              </div>
            ))}

            {/* Loading Indicator */}
            {isSending && (
              <div className="flex gap-3 max-w-lg">
                <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white shrink-0">
                  <Bot className="w-5 h-5 animate-pulse" />
                </div>
                <div className="bg-slate-50 dark:bg-slate-900 border border-slate-150 dark:border-slate-850 rounded-[2rem] rounded-tl-sm px-6 py-4 flex items-center gap-3">
                  <Loader2 className="w-4 h-4 animate-spin text-blue-500" />
                  <span className="text-xs text-slate-550 dark:text-slate-400 font-bold uppercase tracking-wider animate-pulse">
                    Coordinating Agents...
                  </span>
                </div>
              </div>
            )}

            <div ref={chatEndRef} />
          </div>

          {/* Form message input */}
          <form
            onSubmit={handleSendMessage}
            className="mt-6 border-t border-slate-150 dark:border-slate-800 pt-5 flex items-center gap-3 relative"
          >
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Ask about IT roles, salary structures, CV optimization, or select a mode..."
              className="flex-1 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-850 rounded-full px-6 py-4 outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent transition-all text-sm font-medium text-slate-900 dark:text-white placeholder-slate-450 dark:placeholder-slate-550"
              disabled={isSending}
            />
            <button
              type="submit"
              disabled={isSending || !inputMessage.trim()}
              className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white rounded-full p-4 shadow-lg shadow-blue-500/25 transition-all hover:scale-105 shrink-0 flex items-center justify-center cursor-pointer"
            >
              <Send className="w-5 h-5" />
            </button>
          </form>

          {/* Inline notification error */}
          {error && (
            <div className="mt-4 text-xs font-semibold text-red-500 flex items-center gap-1.5">
              <AlertCircle className="w-4 h-4" />
              {error}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
