import { useState, useEffect } from "react";
import { useAuth } from "@/context/AuthProvider";
import { useRouter } from "@/i18n/routing";
import { useTranslations } from "next-intl";
import { validateLogin, validateRegister } from "@/utils/field_validator";
import { toast } from "sonner";

export default function useAuthForm() {
  const t = useTranslations("Auth");
  const [isLogin, setIsLogin] = useState(true);
  const { user, authLoading, login, register } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!authLoading && user) {
      if (!user.first_name || !user.last_name) {
        router.replace("/counselee/profile?missing_name=true");
      } else {
        router.replace("/counselee/overview");
      }
    }
  }, [user, authLoading, router]);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [username, setUsername] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    const cleanEmail = email.trim();
    const cleanPassword = password.trim();
    const validationError = validateLogin(cleanEmail, cleanPassword, t);
    if (validationError) {
      setError(validationError);
      return;
    }
    setError("");
    setIsSubmitting(true);
    try {
      await login(cleanEmail, cleanPassword);
    } catch (err) {
      if (err?.status === 403) {
        toast.error(t("toast_login_403"));
        setError(t("toast_login_403"));
      } else {
        setError(err?.message || "Invalid email or password.");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRegisterSubmit = async (e) => {
    e.preventDefault();
    const cleanEmail = email.trim();
    const cleanUsername = username.trim();
    const cleanPassword = password.trim();
    const cleanConfirmPassword = confirmPassword.trim();
    const validationError = validateRegister(
      cleanEmail,
      cleanUsername,
      cleanPassword,
      cleanConfirmPassword,
      t,
    );
    if (validationError) {
      setError(validationError);
      return;
    }
    setError("");
    setIsSubmitting(true);
    try {
      await register(
        cleanEmail,
        cleanUsername,
        cleanPassword,
        cleanConfirmPassword,
      );
      toast.info(t("toast_confirm_email"));
      setIsLogin(true);
      setPassword("");
      setConfirmPassword("");
    } catch (err) {
      setError(
        err?.message || "Registration failed. Please check your inputs.",
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleToggle = (loginState) => {
    setIsLogin(loginState);
    setError("");
    setEmail("");
    setPassword("");
    setConfirmPassword("");
    setUsername("");
  };

  return {
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
    setError,
    isSubmitting,
    handleLoginSubmit,
    handleRegisterSubmit,
    handleToggle,
  };
}
