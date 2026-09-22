import { motion, AnimatePresence } from "motion/react";

export default function AuthVisualPanel({ t, isLogin, onToggle }) {
  return (
    <motion.div
      layout
      className="hidden md:flex w-1/2 relative bg-[#285872] text-white items-center justify-center p-8 md:p-10 lg:p-12 overflow-hidden shrink-0"
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
            <h3 className="text-2xl lg:text-3xl font-black tracking-tighter uppercase mb-4 leading-tight">
              {t("visual_login_heading")}
            </h3>
            <p className="text-[#eef4f7] text-sm md:text-base font-medium leading-relaxed mb-8">
              {t("visual_login_desc")}
            </p>
            <p className="text-[#d1e3ed] text-xs font-bold uppercase tracking-widest mb-4">
              {t("toggle_to_signup")}
            </p>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => onToggle(false)}
              className="border-2 border-white/30 hover:border-white text-white rounded-full px-8 py-3 text-sm font-bold tracking-wide transition-colors cursor-pointer"
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
            <h3 className="text-2xl lg:text-3xl font-black tracking-tighter uppercase mb-4 leading-tight">
              {t("visual_signup_heading")}
            </h3>
            <p className="text-[#eef4f7] text-sm md:text-base font-medium leading-relaxed mb-8">
              {t("visual_signup_desc")}
            </p>
            <p className="text-[#d1e3ed] font-bold uppercase tracking-widest mb-4">
              {t("toggle_to_login")}
            </p>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => onToggle(true)}
              className="border-2 border-white/30 hover:border-white text-white rounded-full px-10 py-4 font-bold tracking-wide transition-colors cursor-pointer"
            >
              {t("btn_ghost_login")}
            </motion.button>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
