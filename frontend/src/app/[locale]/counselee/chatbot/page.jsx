"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { Bot, ArrowRight } from "lucide-react";
import { useTranslations } from "next-intl";
import { Link } from "@/i18n/routing";

export default function AuthPage() {
  const t = useTranslations("Auth");
  const [isLogin, setIsLogin] = useState(true);

  return (
    <div className="relative min-h-screen w-full flex items-center justify-center bg-slate-50 dark:bg-slate-950 px-4 py-24 overflow-hidden">
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:32px_32px] z-0" />

      <motion.div
        animate={{
          scale: [1, 1.2, 1],
          opacity: [0.3, 0.5, 0.3],
        }}
        transition={{ duration: 15, repeat: Infinity, ease: "easeInOut" }}
        className="absolute top-1/4 left-1/4 w-[40vw] h-[40vw] bg-blue-500/20 rounded-full blur-[120px] pointer-events-none z-0"
      />

      <motion.div
        animate={{
          scale: [1, 1.3, 1],
          opacity: [0.2, 0.4, 0.2],
        }}
        transition={{ duration: 20, repeat: Infinity, ease: "easeInOut" }}
        className="absolute bottom-1/4 right-1/4 w-[35vw] h-[35vw] bg-indigo-500/20 rounded-full blur-[120px] pointer-events-none z-0"
      />

      <div className="relative z-10 w-full max-w-6xl">
        <div className="flex justify-center mb-10">
          <Link href="/" className="flex items-center gap-3 group">
            <motion.div
              whileHover={{ rotate: 10 }}
              whileTap={{ scale: 0.95 }}
              className="w-12 h-12 bg-blue-600 dark:bg-blue-500 rounded-2xl flex items-center justify-center text-white shadow-lg"
            >
              <Bot className="w-7 h-7" />
            </motion.div>
            <span className="text-3xl font-black text-slate-900 dark:text-white tracking-tighter uppercase">
              AIJMC
            </span>
          </Link>
        </div>

        <motion.div
          layout
          className={`relative w-full min-h-[650px] bg-white dark:bg-slate-900 rounded-[3rem] shadow-2xl border border-slate-200 dark:border-slate-800 overflow-hidden flex flex-col ${
            isLogin ? "md:flex-row" : "md:flex-row-reverse"
          }`}
        >
          <motion.div
            layout
            className="w-full md:w-1/2 p-8 md:p-16 flex flex-col justify-center z-10 bg-white dark:bg-slate-900 shrink-0"
          >
            <AnimatePresence mode="wait">
              {isLogin ? (
                <motion.div
                  key="login-form"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  transition={{ duration: 0.3 }}
                  className="w-full max-w-md mx-auto"
                >
                  <h2 className="text-5xl md:text-6xl leading-[1.2] font-black tracking-tighter uppercase text-slate-900 dark:text-white mb-4">
                    {t("login_title")} <br />
                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-500">
                      {t("login_subtitle")}
                    </span>
                  </h2>
                  <p className="text-slate-500 dark:text-slate-400 font-medium mb-10">
                    {t("login_desc")}
                  </p>

                  <form
                    className="flex flex-col gap-6"
                    onSubmit={(e) => e.preventDefault()}
                  >
                    <div className="flex flex-col gap-2">
                      <label className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest pl-2">
                        {t("label_email")}
                      </label>
                      <input
                        type="email"
                        placeholder={t("placeholder_email")}
                        className="w-full bg-slate-50 dark:bg-slate-950/50 border border-slate-200 dark:border-slate-800 rounded-2xl px-6 py-4 outline-none focus:ring-2 focus:ring-blue-600 dark:focus:ring-blue-500 focus:border-transparent transition-all text-slate-900 dark:text-white font-medium"
                      />
                    </div>

                    <div className="flex flex-col gap-2">
                      <label className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest pl-2">
                        {t("label_password")}
                      </label>
                      <input
                        type="password"
                        placeholder={t("placeholder_password")}
                        className="w-full bg-slate-50 dark:bg-slate-950/50 border border-slate-200 dark:border-slate-800 rounded-2xl px-6 py-4 outline-none focus:ring-2 focus:ring-blue-600 dark:focus:ring-blue-500 focus:border-transparent transition-all text-slate-900 dark:text-white font-medium"
                      />
                    </div>

                    <div className="flex justify-end">
                      <a
                        href="#"
                        className="text-sm font-bold text-blue-600 dark:text-blue-400 hover:underline"
                      >
                        {t("forgot_password")}
                      </a>
                    </div>

                    <motion.button
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      className="w-full mt-4 bg-blue-600 text-white rounded-full py-4 text-lg font-bold tracking-wide shadow-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2 group"
                    >
                      {t("btn_login")}
                      <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                    </motion.button>
                  </form>

                  <div className="mt-8 text-center md:hidden">
                    <p className="text-slate-500 text-sm mb-2">
                      {t("toggle_to_signup")}
                    </p>
                    <button
                      onClick={() => setIsLogin(false)}
                      className="text-blue-600 font-bold"
                    >
                      {t("btn_ghost_signup")}
                    </button>
                  </div>
                </motion.div>
              ) : (
                <motion.div
                  key="signup-form"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.3 }}
                  className="w-full max-w-md mx-auto"
                >
                  <h2 className="text-5xl md:text-6xl leading-[1.2] font-black tracking-tighter uppercase text-slate-900 dark:text-white mb-4">
                    {t("signup_title")} <br />
                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-500">
                      {t("signup_subtitle")}
                    </span>
                  </h2>
                  <p className="text-slate-500 dark:text-slate-400 font-medium mb-10">
                    {t("signup_desc")}
                  </p>

                  <form
                    className="flex flex-col gap-5"
                    onSubmit={(e) => e.preventDefault()}
                  >
                    <div className="flex flex-col gap-2">
                      <label className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest pl-2">
                        {t("label_name")}
                      </label>
                      <input
                        type="text"
                        placeholder={t("placeholder_name")}
                        className="w-full bg-slate-50 dark:bg-slate-950/50 border border-slate-200 dark:border-slate-800 rounded-2xl px-6 py-4 outline-none focus:ring-2 focus:ring-blue-600 dark:focus:ring-blue-500 focus:border-transparent transition-all text-slate-900 dark:text-white font-medium"
                      />
                    </div>

                    <div className="flex flex-col gap-2">
                      <label className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest pl-2">
                        {t("label_email")}
                      </label>
                      <input
                        type="email"
                        placeholder={t("placeholder_email")}
                        className="w-full bg-slate-50 dark:bg-slate-950/50 border border-slate-200 dark:border-slate-800 rounded-2xl px-6 py-4 outline-none focus:ring-2 focus:ring-blue-600 dark:focus:ring-blue-500 focus:border-transparent transition-all text-slate-900 dark:text-white font-medium"
                      />
                    </div>

                    <div className="flex flex-col gap-2">
                      <label className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest pl-2">
                        {t("label_password")}
                      </label>
                      <input
                        type="password"
                        placeholder={t("placeholder_password")}
                        className="w-full bg-slate-50 dark:bg-slate-950/50 border border-slate-200 dark:border-slate-800 rounded-2xl px-6 py-4 outline-none focus:ring-2 focus:ring-blue-600 dark:focus:ring-blue-500 focus:border-transparent transition-all text-slate-900 dark:text-white font-medium"
                      />
                    </div>

                    <motion.button
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      className="w-full mt-6 bg-blue-600 text-white rounded-full py-4 text-lg font-bold tracking-wide shadow-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2 group"
                    >
                      {t("btn_signup")}
                      <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                    </motion.button>
                  </form>

                  <div className="mt-8 text-center md:hidden">
                    <p className="text-slate-500 text-sm mb-2">
                      {t("toggle_to_login")}
                    </p>
                    <button
                      onClick={() => setIsLogin(true)}
                      className="text-blue-600 font-bold"
                    >
                      {t("btn_ghost_login")}
                    </button>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>

          <motion.div
            layout
            className="hidden md:flex w-1/2 relative bg-blue-600 text-white items-center justify-center p-16 overflow-hidden shrink-0"
          >
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_bottom_left,rgba(255,255,255,0.15)_0,transparent_60%)] pointer-events-none" />
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(0,0,0,0.15)_0,transparent_60%)] pointer-events-none" />

            <AnimatePresence mode="wait">
              {isLogin ? (
                <motion.div
                  key="login-visual"
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 1.05 }}
                  transition={{ duration: 0.3 }}
                  className="relative z-10 flex flex-col items-center text-center max-w-sm"
                >
                  <h3 className="text-4xl lg:text-5xl font-black tracking-tighter uppercase mb-6">
                    {t("visual_login_heading")}
                  </h3>
                  <p className="text-blue-100 text-lg font-medium leading-relaxed mb-10">
                    {t("visual_login_desc")}
                  </p>
                  <p className="text-sm text-blue-200 font-bold uppercase tracking-widest mb-4">
                    {t("toggle_to_signup")}
                  </p>
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => setIsLogin(false)}
                    className="border-2 border-white/30 hover:border-white text-white rounded-full px-10 py-4 font-bold tracking-wide transition-colors"
                  >
                    {t("btn_ghost_signup")}
                  </motion.button>
                </motion.div>
              ) : (
                <motion.div
                  key="signup-visual"
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 1.05 }}
                  transition={{ duration: 0.3 }}
                  className="relative z-10 flex flex-col items-center text-center max-w-sm"
                >
                  <h3 className="text-4xl lg:text-5xl font-black tracking-tighter uppercase mb-6">
                    {t("visual_signup_heading")}
                  </h3>
                  <p className="text-blue-100 text-lg font-medium leading-relaxed mb-10">
                    {t("visual_signup_desc")}
                  </p>
                  <p className="text-sm text-blue-200 font-bold uppercase tracking-widest mb-4">
                    {t("toggle_to_login")}
                  </p>
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => setIsLogin(true)}
                    className="border-2 border-white/30 hover:border-white text-white rounded-full px-10 py-4 font-bold tracking-wide transition-colors"
                  >
                    {t("btn_ghost_login")}
                  </motion.button>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
}
