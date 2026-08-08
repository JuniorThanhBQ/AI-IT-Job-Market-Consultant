import { motion } from "motion/react";
import { ArrowRight, Loader2 } from "lucide-react";

export default function LoginForm({
  t,
  email,
  setEmail,
  password,
  setPassword,
  error,
  isSubmitting,
  onSubmit,
  onToggleSignUp,
}) {
  return (
    <div className="w-full max-w-md mx-auto">
      <h2 className="text-5xl md:text-6xl leading-[1.2] font-black tracking-tighter uppercase text-slate-900 dark:text-white mb-4">
        {t("login_title")} <br />
        <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#285872] to-[#407c9c]">
          {t("login_subtitle")}
        </span>
      </h2>
      <p className="text-slate-505 dark:text-slate-400 font-medium mb-10">
        {t("login_desc")}
      </p>

      {error && (
        <div className="bg-red-500/10 border border-red-500/20 text-red-500 rounded-2xl p-4 mb-6 text-sm font-medium">
          {error}
        </div>
      )}

      <form className="flex flex-col gap-6" onSubmit={onSubmit}>
        <div className="flex flex-col gap-2">
          <label className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest pl-2">
            {t("label_email")}
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder={t("placeholder_email")}
            className="w-full bg-slate-50 dark:bg-slate-950/50 border border-slate-200 dark:border-slate-800 rounded-2xl px-6 py-4 outline-none focus:ring-2 focus:ring-[#285872] dark:focus:ring-[#407c9c] focus:border-transparent transition-all text-slate-900 dark:text-white font-medium"
            disabled={isSubmitting}
          />
        </div>

        <div className="flex flex-col gap-2">
          <label className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest pl-2">
            {t("label_password")}
          </label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder={t("placeholder_password")}
            className="w-full bg-slate-50 dark:bg-slate-950/50 border border-slate-200 dark:border-slate-800 rounded-2xl px-6 py-4 outline-none focus:ring-2 focus:ring-[#285872] dark:focus:ring-[#407c9c] focus:border-transparent transition-all text-slate-900 dark:text-white font-medium"
            disabled={isSubmitting}
          />
        </div>

        <div className="flex justify-end">
          <a
            href="#"
            className="text-sm font-bold text-[#285872] dark:text-[#407c9c] hover:underline"
          >
            {t("forgot_password")}
          </a>
        </div>

        <motion.button
          whileHover={isSubmitting ? {} : { scale: 1.02 }}
          whileTap={isSubmitting ? {} : { scale: 0.98 }}
          disabled={isSubmitting}
          type="submit"
          className="w-full mt-4 bg-[#285872] text-white rounded-full py-4 text-lg font-bold tracking-wide shadow-lg hover:bg-[#1c3f52] transition-colors flex items-center justify-center gap-2 group disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
        >
          {isSubmitting ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <>
              {t("btn_login")}
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </>
          )}
        </motion.button>
      </form>

      <div className="mt-8 text-center md:hidden">
        <p className="text-slate-500 text-sm mb-2">{t("toggle_to_signup")}</p>
        <button
          onClick={onToggleSignUp}
          className="text-[#285872] font-bold cursor-pointer"
        >
          {t("btn_ghost_signup")}
        </button>
      </div>
    </div>
  );
}
