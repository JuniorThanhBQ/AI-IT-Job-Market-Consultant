import { LOGO } from "@/assets/CloudinaryAssetsUrl";
import { motion, AnimatePresence } from "motion/react";
import { Plus } from "lucide-react";

export function getPlatformsList(t) {
  return [
    {
      name: t("platforms_itviec"),
      desc: t("platforms_itviec_desc"),
      image: LOGO.ITVIEC,
      delay: 0,
    },
    {
      name: t("platforms_topdev"),
      desc: t("platforms_topdev_desc"),
      image: LOGO.TOPDEV,
      delay: 0.1,
    },
    {
      name: t("platforms_itjobs"),
      desc: t("platforms_itjobs_desc"),
      image: LOGO.ITJOBS,
      delay: 0.2,
    },
    {
      name: t("platforms_vietnamworks"),
      desc: t("platforms_vietnamworks_desc"),
      image: LOGO.VIETNAMWORKS,
      delay: 0.3,
    },
  ];
}

export function getFeaturesList(t, { TrendingUp, BrainCircuit, FileUser }) {
  return [
    {
      title: t("feature_1_title"),
      desc: t("feature_1_desc"),
      icon: TrendingUp,
      color: "bg-slate-50 dark:bg-slate-900",
    },
    {
      title: t("feature_2_title"),
      desc: t("feature_2_desc"),
      icon: BrainCircuit,
      color: "bg-slate-50 dark:bg-slate-900",
    },
    {
      title: t("feature_3_title"),
      desc: t("feature_3_desc"),
      icon: FileUser,
      color: "bg-slate-50 dark:bg-slate-900",
    },
  ];
}

export const FAQItem = ({
  question,
  answer,
  isOpen,
  onClick,
  isDarkSection = false,
}) => {
  const borderColor = isDarkSection
    ? "border-slate-800"
    : "border-slate-200 dark:border-slate-800";

  const titleColor = isOpen
    ? isDarkSection
      ? "text-sky-400"
      : "text-[#285872] dark:text-sky-400"
    : isDarkSection
      ? "text-white group-hover:text-sky-400"
      : "text-slate-900 dark:text-white group-hover:text-[#285872] dark:group-hover:text-sky-400";

  const iconColor = isOpen
    ? isDarkSection
      ? "border-sky-400 text-sky-400 bg-sky-950/30"
      : "border-[#285872] text-[#285872] dark:border-sky-400 dark:text-sky-400 bg-sky-50 dark:bg-sky-950/30"
    : isDarkSection
      ? "border-slate-700 text-slate-400 group-hover:border-sky-400 group-hover:text-sky-400"
      : "border-slate-200 dark:border-slate-800 text-slate-400 group-hover:border-[#285872] group-hover:text-[#285872] dark:group-hover:border-sky-400 dark:group-hover:text-sky-400";

  const answerColor = isDarkSection
    ? "text-slate-400"
    : "text-slate-600 dark:text-slate-400";

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-10%" }}
      className={`border-b ${borderColor}`}
    >
      <button
        onClick={onClick}
        className="w-full flex justify-between items-center py-6 md:py-8 text-left group"
      >
        <h3
          className={`text-xl md:text-2xl font-bold tracking-tight transition-colors duration-300 pr-8 ${titleColor}`}
        >
          {question}
        </h3>
        <motion.div
          animate={{ rotate: isOpen ? 45 : 0 }}
          transition={{ duration: 0.3, ease: "easeInOut" }}
          className={`flex-shrink-0 w-10 h-10 rounded-full border flex items-center justify-center transition-colors duration-300 ${iconColor}`}
        >
          <Plus className="w-5 h-5" />
        </motion.div>
      </button>
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
            className="overflow-hidden"
          >
            <p
              className={`pb-8 text-base md:text-lg leading-relaxed max-w-4xl ${answerColor}`}
            >
              {answer}
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export function getAimsList(t, { BookOpen, Layers, Workflow, Cpu, Server }) {
  return [
    {
      time: t("aim_1_time"),
      title: t("aim_1_title"),
      desc: t("aim_1_desc"),
      icon: BookOpen,
    },
    {
      time: t("aim_2_time"),
      title: t("aim_2_time"),
      desc: t("aim_2_desc"),
      icon: Layers,
    },
    {
      time: t("aim_3_time"),
      title: t("aim_3_time"),
      desc: t("aim_3_desc"),
      icon: Workflow,
    },
    {
      time: t("aim_4_time"),
      title: t("aim_4_time"),
      desc: t("aim_4_desc"),
      icon: Cpu,
    },
    {
      time: t("aim_5_time"),
      title: t("aim_5_title"),
      desc: t("aim_5_desc"),
      icon: Server,
    },
  ];
}

export function getFounderSkillsList(t, { BrainCircuit, Terminal, Blocks }) {
  return [
    {
      title: t("skill_1"),
      desc: t("skill_1_desc"),
      icon: BrainCircuit,
      color: "text-purple-600 dark:text-purple-400",
      bg: "bg-purple-50 dark:bg-purple-900/30",
      border: "border-purple-100 dark:border-purple-900/50",
    },
    {
      title: t("skill_2"),
      desc: t("skill_2_desc"),
      icon: Terminal,
      color: "text-emerald-600 dark:text-emerald-400",
      bg: "bg-emerald-50 dark:bg-emerald-900/30",
      border: "border-emerald-100 dark:border-emerald-900/50",
    },
    {
      title: t("skill_3"),
      desc: t("skill_3_desc"),
      icon: Blocks,
      color: "text-blue-600 dark:text-blue-400",
      bg: "bg-blue-50 dark:bg-blue-900/30",
      border: "border-blue-100 dark:border-blue-900/50",
    },
  ];
}
