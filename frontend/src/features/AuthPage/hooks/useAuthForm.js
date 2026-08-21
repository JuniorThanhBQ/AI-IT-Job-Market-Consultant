import { useState, useEffect } from "react";
import { useAuth } from "@/context/AuthProvider";
import { useRouter } from "@/i18n/routing";
import { useTranslations } from "next-intl";
import { validateLogin, validateRegister } from "@/utils/field_validator";

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
  const [username, setUsername] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    const validationError = validateLogin(email, password, t);
    if (validationError) {
      setError(validationError);
      return;
    }
    setError("");
    setIsSubmitting(true);
    try {
      await login(email, password);
    } catch (err) {
      setError(err?.message || "Invalid email or password.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRegisterSubmit = async (e) => {
    e.preventDefault();
    const validationError = validateRegister(email, username, password, t);
    if (validationError) {
      setError(validationError);
      return;
    }
    setError("");
    setIsSubmitting(true);
    try {
      await register(email, username, password);
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
    setUsername("");
  };

  return {
    isLogin,
    email,
    setEmail,
    password,
    setPassword,
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
