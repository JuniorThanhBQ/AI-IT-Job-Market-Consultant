"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { useAuth } from "@/context/AuthProvider";
import { useLocale, useTranslations } from "next-intl";
import { useRouter } from "@/i18n/routing";
import { consultantApi, chatbotAPI } from "@/features/Chatbot/Hooks/useChatbot";
import { hasXSS, hasSQLInjection } from "@/utils/field_validator";

export function useChatbot() {
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
    if (hasXSS(userText) || hasSQLInjection(userText)) {
      setMessages((prev) => [
        ...prev,
        { role: "user", text: userText },
        { role: "bot", text: "Unsafe input detected." },
      ]);
      return;
    }
    setMessages((prev) => [...prev, { role: "user", text: userText }]);
    setLoading(true);
    setStreamingMessage("");

    try {
      const response = await chatbotAPI(activeIntent, userText);
      if (!response.ok) {
        throw new Error();
      }

      const data = await response.json();
      const reply = data.final_result || data.output || data.result || "";
      setMessages((prev) => [...prev, { role: "bot", text: reply }]);
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

  const [secondsElapsed, setSecondsElapsed] = useState(0);

  useEffect(() => {
    let intervalId;
    if (loading && !streamingMessage) {
      intervalId = setInterval(() => {
        setSecondsElapsed((prev) => prev + 1);
      }, 1000);
    }
    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
      setSecondsElapsed(0);
    };
  }, [loading, streamingMessage]);

  const getLoadingMessage = () => {
    if (secondsElapsed < 5) {
      return t("loading_processing");
    }
    if (secondsElapsed > 10 && secondsElapsed <= 20) {
      return t("loading_large_input");
    }
    if (secondsElapsed > 20 && secondsElapsed <= 30) {
      return t("loading_heavy_payload");
    }
    if (secondsElapsed > 30) {
      return t("loading_almost_there");
    }
    return t("loading_default");
  };

  return {
    isAuthenticated,
    locale,
    router,
    t,
    isOpen,
    setIsOpen,
    messages,
    setMessages,
    input,
    setInput,
    loading,
    setLoading,
    streamingMessage,
    setStreamingMessage,
    activeIntent,
    setActiveIntent,
    confirmClear,
    setConfirmClear,
    messagesEndRef,
    chatInputRef,
    handleClearHistory,
    handleSend,
    getLoadingMessage,
  };
}
