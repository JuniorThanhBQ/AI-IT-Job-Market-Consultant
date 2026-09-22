"use client";

import { useTranslations } from "next-intl";
import { getFooterLinks } from "@/utils/url";

export function useFooter() {
  const t = useTranslations("Footer");
  const footerLinks = getFooterLinks(t);
  const containerVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { staggerChildren: 0.1, duration: 0.5 },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 10 },
    visible: { opacity: 1, y: 0 },
  };

  return {
    t,
    footerLinks,
    containerVariants,
    itemVariants,
  };
}
