import { useState, useEffect, useRef, useCallback } from "react";
import { useAuth } from "@/context/AuthProvider";
import { APIS, BASE_URL } from "@/configs/apis";
import { useRouter } from "@/i18n/routing";
import { SUGGESTED_INTENTS } from "@/utils/const";
import { hasXSS, hasSQLInjection } from "@/utils/field_validator";

export const consultantApi = {
  processChatbotIntent: (intent, userInput) =>
    APIS.executeAgent({ intent, user_input: userInput }),
  getHistory: (params = {}) => APIS.getAgentHistory(params),
  clearHistory: () => APIS.clearAgentHistory(),
  executeAgent: (payload) => APIS.executeAgent(payload),
};

export const chatbotAPI = (intent, userInput) => {
  const token =
    typeof window !== "undefined" ? localStorage.getItem("token") : null;
  return fetch(`${BASE_URL}/consultants/agent/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "ngrok-skip-browser-warning": "true",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({
      intent: intent || "MARKET_ANALYSIS",
      user_input: userInput,
    }),
  });
};

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
      router.replace("/counselee/auth");
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
    if (hasXSS(userText) || hasSQLInjection(userText)) {
      setError("Invalid input.");
      return;
    }
    setInputMessage("");
    setError("");
    setMessages((prev) => [
      ...prev,
      { role: "user", text: userText, timestamp: new Date() },
    ]);
    setIsSending(true);
    setStreamingMessage("");

    try {
      const response = await chatbotAPI(selectedIntent, userText);
      if (!response.ok) {
        throw new Error("Chatbot API response was not OK");
      }

      const data = await response.json();
      const reply =
        data.final_result || data.output || data.result || "Analysis complete.";

      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          text: reply,
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
