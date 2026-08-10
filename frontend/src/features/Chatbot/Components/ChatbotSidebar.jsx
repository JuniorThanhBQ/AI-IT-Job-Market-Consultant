"use client";

import { Compass, Cpu } from "lucide-react";

export default function ChatbotSidebar({
  suggestedIntents,
  selectedIntent,
  onSelectIntent,
}) {
  return (
    <aside className="lg:w-80 flex flex-col gap-6 shrink-0">
      <div className="bg-white/80 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-900 rounded-[2rem] p-6 backdrop-blur-md flex flex-col gap-5">
        <h2 className="text-xs font-extrabold text-slate-900 dark:text-white uppercase tracking-wider flex items-center gap-2">
          <Compass className="w-4 h-4 text-[#285872] dark:text-[#407c9c]" />
          Agent Consulting Modes
        </h2>
        <div className="flex flex-col gap-3">
          {suggestedIntents.map((intent) => (
            <button
              key={intent.id}
              onClick={() => onSelectIntent(intent.id)}
              className={`text-left p-4 rounded-2xl border transition-all flex flex-col gap-1.5 group cursor-pointer ${
                selectedIntent === intent.id
                  ? "bg-[#285872]/10 border-[#285872]/40 text-[#285872] dark:text-[#52a0cc]"
                  : "bg-slate-50/50 dark:bg-slate-955/40 border-slate-200 dark:border-slate-850 hover:border-slate-350 dark:hover:border-slate-750 text-slate-550 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
              }`}
            >
              <span className="text-xs font-extrabold tracking-wide uppercase group-hover:text-[#285872] dark:group-hover:text-[#52a0cc] transition-colors">
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
        <h3 className="text-xs font-extrabold text-slate-900 dark:text-white uppercase tracking-widest flex items-center gap-2">
          <Cpu className="w-4 h-4 text-[#285872] dark:text-[#407c9c]" />
          Multi-Agent Collaboration
        </h3>
        <p className="text-[11px] text-slate-505 dark:text-slate-400 leading-relaxed font-medium">
          When sending prompts, the orchestrator delegates queries to
          Personalization, Recommendation, and Market Intelligence agents with
          dynamic streaming output.
        </p>
      </div>
    </aside>
  );
}
