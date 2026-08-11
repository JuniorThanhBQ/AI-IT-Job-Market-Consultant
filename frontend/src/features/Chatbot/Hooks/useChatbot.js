import { useState, useEffect, useRef, useCallback } from "react";
import { useAuth } from "@/context/AuthProvider";
import { consultantApi } from "@/configs/apis";
import { useRouter } from "@/i18n/routing";

export const SUGGESTED_INTENTS = [
  {
    id: "MARKET_ANALYSIS",
    name: "Market Analysis",
    desc: "Analyze IT trends, salary distributions, and market demand.",
  },
  {
    id: "PERSONAL_STANDARD_EVALUATION",
    name: "Career Evaluation",
    desc: "Assess your profile and compare skills with current job criteria.",
  },
  {
    id: "JOB_RECOMMEND",
    name: "Job Recommendation",
    desc: "Discover vacancies closely matching your tech stack.",
  },
  {
    id: "DEEP_ANALYSIS_EVALUATION",
    name: "Deep CV Analysis",
    desc: "Run comprehensive AI feedback to optimize your CV/Resume.",
  },
];

export function useChatbot() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();

  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [selectedIntent, setSelectedIntent] = useState("MARKET_ANALYSIS");
  const [isSending, setIsSending] = useState(false);
  const [streamingMessage, setStreamingMessage] = useState("");
  const [error, setError] = useState("");
  const [confirmClear, setConfirmClear] = useState(false);

  const chatEndRef = useRef(null);
  const chatInputRef = useRef(null);

  useEffect(() => {
    if (!authLoading && !user) {
      router.replace("/counselee/login");
    }
  }, [user, authLoading, router]);

  const loadHistory = useCallback(async () => {
    try {
      const data = await consultantApi.getHistory();
      const historyMessages = [];
      data.forEach((item) => {
        if (
          item.user_input &&
          item.user_input !== "deleted" &&
          item.user_input !== "System query for Action:"
        ) {
          historyMessages.push({
            role: "user",
            text: item.user_input,
            timestamp: item.created_at || new Date(),
          });
        }
        if (item.output && item.output !== "deleted") {
          historyMessages.push({
            role: "bot",
            text: item.output,
            timestamp: item.created_at || new Date(),
          });
        }
      });
      setMessages(historyMessages);
    } catch (err) {
      console.error(err);
    }
  }, []);

  useEffect(() => {
    if (user) {
      const timer = setTimeout(() => {
        loadHistory();
      }, 0);
      return () => clearTimeout(timer);
    }
  }, [user, loadHistory]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingMessage, isSending]);

  const handleClearHistory = async () => {
    try {
      await consultantApi.clearHistory();
      setMessages([]);
      setConfirmClear(false);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSendMessage = async (e) => {
    if (e) e.preventDefault();
    if (!inputMessage.trim() || isSending) return;

    const userText = inputMessage.trim();
    setInputMessage("");
    setError("");
    setMessages((prev) => [
      ...prev,
      { role: "user", text: userText, timestamp: new Date() },
    ]);
    setIsSending(true);
    setStreamingMessage("");

    try {
      const token =
        typeof window !== "undefined" ? localStorage.getItem("token") : null;
      const response = await fetch(
        `${"/api/v1"}/consultants/chatbot/process-intent`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            intent: selectedIntent,
            user_input: userText,
          }),
        },
      );

      if (!response.ok) {
        throw new Error("Chatbot API response was not OK");
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
            } catch (err) {
              console.error(err);
            }
          }
        }
      }

      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          text: accumulatedText || "Analysis complete.",
          timestamp: new Date(),
        },
      ]);
      setStreamingMessage("");
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          text: "I encountered an error coordinating the specialized career agents. Please try again.",
          isError: true,
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsSending(false);
      setTimeout(() => chatInputRef.current?.focus(), 50);
    }
  };

  return {
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
    suggestedIntents: SUGGESTED_INTENTS,
    handleSendMessage,
    handleClearHistory,
  };
}
