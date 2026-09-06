"use client";

import TOSHeader from "./Components/TOSHeader";
import TOSNav from "./Components/TOSNav";
import TOSSections from "./Components/TOSSections";
import { useTOSNavigation } from "./Hooks/useTOSNavigation";

export default function TOSPage() {
  const { scrollToSection } = useTOSNavigation();
  return (
    <div className="relative min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 flex flex-col font-sans transition-colors duration-300">
      <TOSHeader />

      <main className="relative z-10 flex-1 max-w-7xl w-full mx-auto px-6 py-12 flex flex-col lg:flex-row gap-8 min-h-0">
        <TOSNav onScrollToSection={scrollToSection} />
        <TOSSections />
      </main>
    </div>
  );
}
