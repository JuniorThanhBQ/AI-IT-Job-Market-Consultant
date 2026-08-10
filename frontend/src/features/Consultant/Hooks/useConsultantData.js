import { useEffect } from "react";
import { useAuth } from "@/context/AuthProvider";
import { useRouter } from "@/i18n/routing";
import { useTranslations } from "next-intl";

export function useConsultantData() {
  const { user, authLoading } = useAuth();
  const router = useRouter();
  const t = useTranslations("Counselee.Consultant");

  useEffect(() => {
    if (!authLoading && !user) {
      router.replace("/counselee/login");
    }
  }, [user, authLoading, router]);

  const marketSummary = {
    totalOpenings: "1,248",
    growth: "+14.2%",
    avgSalary: "$1,850",
    topField: "AI & Cloud Engineering",
    desc: t("market_summary_desc"),
  };

  const skillsData = [
    { name: "React / Next.js", percentage: 86, color: "bg-[#285872]" },
    {
      name: "Python / PyTorch / FastAPI",
      percentage: 78,
      color: "bg-[#387494]",
    },
    { name: "Node.js / Express", percentage: 65, color: "bg-[#458bad]" },
    { name: "AWS / GCP Infrastructure", percentage: 58, color: "bg-[#54a1c6]" },
    { name: "Docker / Kubernetes", percentage: 52, color: "bg-[#6ab3d8]" },
    { name: "SQL & Relational DBs", percentage: 46, color: "bg-[#81c5e8]" },
  ];

  const recommendations = [
    {
      title: t("rec_1_title"),
      desc: t("rec_1_desc"),
    },
    {
      title: t("rec_2_title"),
      desc: t("rec_2_desc"),
    },
    {
      title: t("rec_3_title"),
      desc: t("rec_3_desc"),
    },
  ];

  const recommendedJobs = [
    {
      id: 1,
      title: "Senior React Engineer",
      company: "VNG Corporation",
      matchScore: 98,
      salary: "$2,200 - $3,000",
      location: "HCMC",
      model: "Hybrid",
      tags: ["React", "Senior", "TypeScript"],
    },
    {
      id: 2,
      title: "AI Python Developer",
      company: "FPT Software",
      matchScore: 94,
      salary: "$1,500 - $2,500",
      location: "HCMC",
      model: "Onsite",
      tags: ["Python", "FastAPI", "AI Agents"],
    },
    {
      id: 3,
      title: "Fullstack Node.js Developer",
      company: "VinGroup Tech",
      matchScore: 91,
      salary: "$1,800 - $2,600",
      location: "Remote / Hanoi",
      model: "Remote",
      tags: ["Node.js", "React", "Docker"],
    },
  ];

  return {
    user,
    authLoading,
    marketSummary,
    skillsData,
    recommendations,
    recommendedJobs,
  };
}
