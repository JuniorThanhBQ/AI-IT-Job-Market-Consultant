"use client";

import Image from "next/image";
import { Link } from "@/i18n/routing";
import { motion } from "motion/react";
import { PROJECT_NAME, LINKS } from "@/utils/const";
import { LOGO } from "@/assets/CloudinaryAssetsUrl";
import { useFooter } from "@/components/shared/hooks/useFooter";

export default function Footer() {
  const { t, footerLinks, containerVariants, itemVariants } = useFooter();

  return (
    <footer className="bg-slate-50 dark:bg-slate-950 border-t border-slate-200 dark:border-slate-800 pt-12 pb-6">
      <motion.div
        className="max-w-7xl mx-auto px-6"
        variants={containerVariants}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, margin: "-50px" }}
      >
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-12 lg:gap-8 mb-16 text-center md:text-left">
          <motion.div
            variants={itemVariants}
            className="lg:col-span-2 flex flex-col items-center md:items-start"
          >
            <Link href="/" className="flex items-center gap-2 mb-6 group">
              <div className="w-12 h-12  rounded-lg flex items-center justify-center text-white transition-transform group-hover:scale-105">
                <Image
                  src={LOGO.AIJMC_LOGO}
                  alt="AIJMC Logo"
                  width={320}
                  height={320}
                  className="h-44 w-auto object-contain"
                  loading="eager"
                />
              </div>
              <span className="text-xl font-bold text-slate-900 dark:text-white tracking-tight">
                {PROJECT_NAME.LONG}
              </span>
            </Link>
            <p className="text-slate-600 dark:text-slate-400 max-w-sm mb-6 leading-relaxed">
              {t("description")}
            </p>
          </motion.div>

          <motion.div
            variants={itemVariants}
            className="flex flex-col items-center md:items-start"
          >
            <h3 className="font-semibold text-slate-900 dark:text-white mb-4">
              {t("category_product")}
            </h3>
            <ul className="flex flex-col gap-3 items-center md:items-start">
              {footerLinks.product.map((link) => (
                <li key={link.name}>
                  <Link
                    href={link.href}
                    className="text-slate-600 dark:text-slate-400 hover:text-[#285872] dark:hover:text-sky-400 text-sm transition-colors"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </motion.div>

          <motion.div
            variants={itemVariants}
            className="flex flex-col items-center md:items-start"
          >
            <h3 className="font-semibold text-slate-900 dark:text-white mb-4">
              {t("category_company")}
            </h3>
            <ul className="flex flex-col gap-3 items-center md:items-start">
              {footerLinks.company.map((link) => (
                <li key={link.name}>
                  <Link
                    href={link.href}
                    className="text-slate-600 dark:text-slate-400 hover:text-[#285872] dark:hover:text-sky-400 text-sm transition-colors"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </motion.div>

          <motion.div
            variants={itemVariants}
            className="flex flex-col items-center md:items-start"
          >
            <h3 className="font-semibold text-slate-900 dark:text-white mb-4">
              {t("category_legal")}
            </h3>
            <ul className="flex flex-col gap-3 items-center md:items-start">
              {footerLinks.legal.map((link) => (
                <li key={link.name}>
                  <Link
                    href={link.href}
                    className="text-slate-600 dark:text-slate-400 hover:text-[#285872] dark:hover:text-sky-400 text-sm transition-colors"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </motion.div>
        </div>

        <motion.div
          variants={itemVariants}
          className="pt-8 border-t border-slate-200 dark:border-slate-800 flex flex-col md:flex-row items-center justify-between gap-4"
        >
          <p className="text-sm text-slate-500 dark:text-slate-400 text-center md:text-left">
            © {new Date().getFullYear()} {PROJECT_NAME.LONG}. {t("since")} 2026.
          </p>
          <div className="flex flex-wrap items-center justify-center gap-2 text-sm text-slate-500 dark:text-slate-400 text-center md:text-right">
            <span>{t("graduation_project")}</span>
            <div>
              <a
                href={LINKS.OUHCMC}
                target="_blank"
                className="flex items-center gap-1.5"
                rel="noreferrer"
              >
                <motion.div
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.95 }}
                  className="p-1 rounded-md bg-slate-200/50 dark:bg-slate-800 transition-colors duration-300 hover:bg-white dark:hover:bg-slate-200 hover:shadow-sm"
                >
                  <Image
                    src={LOGO.OUHCMC}
                    alt="HCMC-OU Logo"
                    className="w-5 h-5 object-contain"
                    width={40}
                    height={40}
                  />
                </motion.div>
                <span className="font-medium text-slate-900 dark:text-white">
                  HCMC-OU
                </span>
              </a>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </footer>
  );
}
