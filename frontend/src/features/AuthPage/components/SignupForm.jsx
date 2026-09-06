import { motion } from "motion/react";
import { ArrowRight, Loader2 } from "lucide-react";

export default function SignupForm({
  t,
  username,
  setUsername,
  email,
  setEmail,
  password,
  setPassword,
  confirmPassword,
  setConfirmPassword,
  error,
  isSubmitting,
  onSubmit,
  onToggleLogin,
}) {
  return (
    <div className="w-full max-w-md mx-auto">
      <h2 className="text-3xl md:text-4xl lg:text-5xl leading-[1.3] font-black tracking-tighter uppercase text-slate-900 dark:text-white mb-2 text-center md:text-left">
        {t("signup_title")} <br />
        <span className="text-[#285872] dark:text-sky-400">
          {t("signup_subtitle")}
        </span>
      </h2>
      <p className="text-slate-500 dark:text-slate-400 text-xs md:text-sm font-medium mb-4 text-center md:text-left">
        {t("signup_desc")}
      </p>

      {error && (
        <div className="bg-red-500/10 border border-red-500/20 text-red-500 rounded-2xl p-3 mb-3 text-xs font-medium">
          {error}
        </div>
      )}

      <form className="flex flex-col gap-3" onSubmit={onSubmit}>
        <div className="flex flex-col gap-1">
          <label className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest pl-2">
            {t("label_username")}
          </label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder={t("placeholder_username")}
            className="w-full bg-slate-50 dark:bg-slate-950/50 border border-slate-200 dark:border-slate-800 rounded-xl px-5 py-2.5 outline-none focus:ring-2 focus:ring-[#285872] dark:focus:ring-[#407c9c] focus:border-transparent transition-all text-slate-900 dark:text-white font-medium text-sm"
            disabled={isSubmitting}
          />
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest pl-2">
            {t("label_email")}
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder={t("placeholder_email")}
            className="w-full bg-slate-50 dark:bg-slate-950/50 border border-slate-200 dark:border-slate-800 rounded-xl px-5 py-2.5 outline-none focus:ring-2 focus:ring-[#285872] dark:focus:ring-[#407c9c] focus:border-transparent transition-all text-slate-900 dark:text-white font-medium text-sm"
            disabled={isSubmitting}
          />
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest pl-2">
            {t("label_password")}
          </label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder={t("placeholder_password")}
            className="w-full bg-slate-50 dark:bg-slate-950/50 border border-slate-200 dark:border-slate-800 rounded-xl px-5 py-2.5 outline-none focus:ring-2 focus:ring-[#285872] dark:focus:ring-[#407c9c] focus:border-transparent transition-all text-slate-900 dark:text-white font-medium text-sm"
            disabled={isSubmitting}
          />
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest pl-2">
            {t("label_confirm_password")}
          </label>
          <input
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder={t("placeholder_confirm_password")}
            className="w-full bg-slate-50 dark:bg-slate-950/50 border border-slate-200 dark:border-slate-800 rounded-xl px-5 py-2.5 outline-none focus:ring-2 focus:ring-[#285872] dark:focus:ring-[#407c9c] focus:border-transparent transition-all text-slate-900 dark:text-white font-medium text-sm"
            disabled={isSubmitting}
          />
        </div>

        <motion.button
          whileHover={isSubmitting ? {} : { scale: 1.02 }}
          whileTap={isSubmitting ? {} : { scale: 0.98 }}
          disabled={isSubmitting}
          type="submit"
          className="w-full mt-4 bg-[#285872] text-white rounded-full py-3.5 text-base font-bold tracking-wide shadow-lg hover:bg-[#1c3f52] transition-colors flex items-center justify-center gap-2 group disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
        >
          {isSubmitting ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <>
              {t("btn_signup")}
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </>
          )}
        </motion.button>
      </form>

      <div className="mt-8 text-center md:hidden">
        <p className="text-slate-500 text-sm mb-2">{t("toggle_to_login")}</p>
        <button
          onClick={onToggleLogin}
          className="text-[#285872] font-bold cursor-pointer"
        >
          {t("btn_ghost_login")}
        </button>
      </div>
    </div>
  );
}
