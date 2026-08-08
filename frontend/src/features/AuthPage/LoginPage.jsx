"use client";

import { motion, AnimatePresence } from "motion/react";
import { useTranslations } from "next-intl";
import { Link } from "@/i18n/routing";
import Image from "next/image";
import { LOGO } from "@/assets/CloudinaryAssetsUrl";
import useAuthForm from "./hooks/useAuthForm";
import LoginForm from "./components/LoginForm";
import SignupForm from "./components/SignupForm";
import AuthVisualPanel from "./components/AuthVisualPanel";

export default function AuthPage() {
  const t = useTranslations("Auth");
  const {
    isLogin,
    email,
    setEmail,
    password,
    setPassword,
    username,
    setUsername,
    error,
    isSubmitting,
    handleLoginSubmit,
    handleRegisterSubmit,
    handleToggle,
  } = useAuthForm();

  return (
    <div className="relative min-h-screen w-full flex items-center justify-center bg-slate-50 dark:bg-slate-955 px-4 py-24 overflow-hidden">
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:32px_32px] z-0" />

      <motion.div
        animate={{
          scale: [1, 1.2, 1],
          opacity: [0.3, 0.5, 0.3],
        }}
        transition={{ duration: 15, repeat: Infinity, ease: "easeInOut" }}
        className="absolute top-1/4 left-1/4 w-[40vw] h-[40vw] bg-[#285872]/20 rounded-full blur-[120px] pointer-events-none z-0"
      />

      <motion.div
        animate={{
          scale: [1, 1.3, 1],
          opacity: [0.2, 0.4, 0.2],
        }}
        transition={{ duration: 20, repeat: Infinity, ease: "easeInOut" }}
        className="absolute bottom-1/4 right-1/4 w-[35vw] h-[35vw] bg-[#285872]/15 rounded-full blur-[120px] pointer-events-none z-0"
      />

      <div className="relative z-10 w-full max-w-6xl">
        <div className="flex justify-center -mt-8 -mb-6">
          <Link href="/" className="group flex items-center justify-center">
            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="relative w-72 h-54 flex items-center justify-center"
            >
              <Image
                src={LOGO.AIJMC_LOGO}
                alt="AIJMC Logo"
                width={288}
                height={288}
                className="w-full h-full object-contain"
                priority
              />
            </motion.div>
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
                  className="w-full"
                >
                  <LoginForm
                    t={t}
                    email={email}
                    setEmail={setEmail}
                    password={password}
                    setPassword={setPassword}
                    error={error}
                    isSubmitting={isSubmitting}
                    onSubmit={handleLoginSubmit}
                    onToggleSignUp={() => handleToggle(false)}
                  />
                </motion.div>
              ) : (
                <motion.div
                  key="signup-form"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.3 }}
                  className="w-full"
                >
                  <SignupForm
                    t={t}
                    username={username}
                    setUsername={setUsername}
                    email={email}
                    setEmail={setEmail}
                    password={password}
                    setPassword={setPassword}
                    error={error}
                    isSubmitting={isSubmitting}
                    onSubmit={handleRegisterSubmit}
                    onToggleLogin={() => handleToggle(true)}
                  />
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>

          <AuthVisualPanel t={t} isLogin={isLogin} onToggle={handleToggle} />
        </motion.div>
      </div>
    </div>
  );
}
