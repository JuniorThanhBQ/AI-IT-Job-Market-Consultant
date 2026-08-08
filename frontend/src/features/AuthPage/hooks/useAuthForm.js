import { useState } from "react";
import { useAuth } from "@/context/AuthProvider";

export default function useAuthForm() {
  const [isLogin, setIsLogin] = useState(true);
  const { login, register } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [username, setUsername] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      setError("Please fill in all fields.");
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
    if (!email || !password || !username) {
      setError("Please fill in all fields.");
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
