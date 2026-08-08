"use client";

import VerticalScrollbar from "@/components/shared/VerticalScrollbar";

const sections = [
  { id: "terms", label: "Terms" },
  { id: "privacy", label: "Privacy Policy" },
];

export default function TermsOfService() {
  return (
    <div className="relative w-full">
      <VerticalScrollbar sections={sections} />
      <section
        id="terms"
        className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-900 text-3xl font-bold"
      >
        Terms of Service
      </section>
      <section
        id="privacy"
        className="min-h-screen flex items-center justify-center bg-white dark:bg-slate-950 text-3xl font-bold"
      >
        Privacy Policy
      </section>
    </div>
  );
}
