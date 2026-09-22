"use client";

import useAuthForm from "./hooks/useAuthForm";
import LoginForm from "./components/LoginForm";
import SignupForm from "./components/SignupForm";
import AuthVisualPanel from "./components/AuthVisualPanel";
import { useTranslations } from "next-intl";
import { motion, AnimatePresence } from "motion/react";

export default function AuthPage() {
  const t = useTranslations("Auth");
  const {
    isLogin,
    email,
    setEmail,
    password,
    setPassword,
    confirmPassword,
    setConfirmPassword,
    username,
    setUsername,
    error,
    isSubmitting,
    handleLoginSubmit,
    handleRegisterSubmit,
    handleToggle,
  } = useAuthForm();

  return (
    <div className="relative min-h-screen w-full flex items-center justify-center bg-slate-50 dark:bg-slate-950 px-4 py-8 sm:py-12 overflow-hidden">
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

      <div className="relative z-10 w-full max-w-7xl">
        <motion.div
          layout
          className={`relative w-full min-h-[480px] bg-white dark:bg-slate-900 rounded-[2rem] shadow-2xl border border-slate-200 dark:border-slate-800 overflow-hidden flex flex-col ${
            isLogin ? "md:flex-row" : "md:flex-row-reverse"
          }`}
        >
          <motion.div
            layout
            className="w-full md:w-1/2 p-6 md:p-10 lg:p-12 flex flex-col justify-center z-10 bg-white dark:bg-slate-900 shrink-0"
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
                    confirmPassword={confirmPassword}
                    setConfirmPassword={setConfirmPassword}
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
                    confirmPassword={confirmPassword}
                    setConfirmPassword={setConfirmPassword}
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
