"use client";

import { motion } from "motion/react";
import { Loader2 } from "lucide-react";
import { useChatbot } from "./Hooks/useChatbot";
import ChatbotHeader from "./Components/ChatbotHeader";
import ChatbotSidebar from "./Components/ChatbotSidebar";
import ChatbotMessageList from "./Components/ChatbotMessageList";
import ChatbotInput from "./Components/ChatbotInput";

export default function ChatbotPage() {
  const {
    user,
    authLoading,
    messages,
    inputMessage,
    setInputMessage,
    selectedIntent,
    setSelectedIntent,
    isSending,
    streamingMessage,
    error,
    confirmClear,
    setConfirmClear,
    chatEndRef,
    chatInputRef,
    suggestedIntents,
    handleSendMessage,
    handleClearHistory,
  } = useChatbot();

  if (authLoading || !user) {
    return (
      <div className="min-h-screen w-full flex items-center justify-center bg-slate-50 dark:bg-slate-955 text-slate-900 dark:text-white transition-colors duration-300">
        <Loader2 className="w-8 h-8 animate-spin text-[#285872]" />
      </div>
    );
  }

  return (
    <div className="relative min-h-screen bg-slate-50 dark:bg-slate-955 text-slate-900 dark:text-slate-100 flex flex-col font-sans transition-colors duration-300">
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

      <motion.div
        animate={{
          x: [0, 20, -10, 0],
          y: [0, -30, 20, 0],
          scale: [1, 1.1, 0.95, 1],
        }}
        transition={{ duration: 20, repeat: Infinity, ease: "easeInOut" }}
        className="absolute top-0 right-0 w-[45vw] h-[45vw] bg-[#285872]/10 dark:bg-[#285872]/15 rounded-full blur-[130px] pointer-events-none z-0"
      />
      <motion.div
        animate={{
          x: [0, -20, 15, 0],
          y: [0, 25, -15, 0],
          scale: [1, 1.05, 0.9, 1],
        }}
        transition={{ duration: 25, repeat: Infinity, ease: "easeInOut" }}
        className="absolute bottom-0 left-0 w-[40vw] h-[40vw] bg-[#285872]/10 dark:bg-[#285872]/10 rounded-full blur-[130px] pointer-events-none z-0"
      />

      <ChatbotHeader
        suggestedIntents={suggestedIntents}
        selectedIntent={selectedIntent}
        onSelectIntent={setSelectedIntent}
        confirmClear={confirmClear}
        setConfirmClear={setConfirmClear}
        onClearHistory={handleClearHistory}
      />

      <main className="relative z-10 flex-1 max-w-7xl w-full mx-auto px-6 py-8 flex flex-col lg:flex-row gap-8">
        <ChatbotSidebar
          suggestedIntents={suggestedIntents}
          selectedIntent={selectedIntent}
          onSelectIntent={setSelectedIntent}
        />

        <div className="flex-1 bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2.5rem] p-8 backdrop-blur-md flex flex-col shadow-sm">
          <ChatbotMessageList
            messages={messages}
            streamingMessage={streamingMessage}
            isSending={isSending}
            chatEndRef={chatEndRef}
          />

          <ChatbotInput
            inputMessage={inputMessage}
            setInputMessage={setInputMessage}
            isSending={isSending}
            error={error}
            chatInputRef={chatInputRef}
            onSendMessage={handleSendMessage}
          />
        </div>
      </main>
    </div>
  );
}
