"use client";

import PageTransition from "@/components/shared/PageTransition";
import Introduction from "./Components/Introduction";
import AIJMCInfo from "./Components/AIJMCInfo";
import FounderInspiration from "./Components/FounderInspiration";
import FAQ from "./Components/FAQ";
import Contact from "./Components/Contact";

export default function HomePage({ activePage }) {
  const renderPage = () => {
    switch (activePage) {
      case "intro":
        return <Introduction />;
      case "aijmc":
        return <AIJMCInfo />;
      case "founder":
        return <FounderInspiration />;
      case "faq":
        return <FAQ />;
      case "contact":
        return <Contact />;
      default:
        return <Introduction />;
    }
  };

  return <PageTransition pageKey={activePage}>{renderPage()}</PageTransition>;
}
