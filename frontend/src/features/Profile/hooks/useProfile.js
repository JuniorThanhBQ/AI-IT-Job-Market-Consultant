"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/context/AuthProvider";
import { profileApi } from "@/configs/apis";
import { useRouter } from "@/i18n/routing";
import { useLocale, useTranslations } from "next-intl";
import { useSearchParams } from "next/navigation";

export function useProfile() {
  const { user, authLoading } = useAuth();
  const router = useRouter();
  const locale = useLocale();
  const t = useTranslations("Counselee.Profile");
  const searchParams = useSearchParams();
  const isMissingName = searchParams.get("missing_name") === "true";
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [birthday, setBirthday] = useState("");
  const [biography, setBiography] = useState("");
  const [goal, setGoal] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    if (!authLoading && !user) {
      router.replace("/counselee/auth");
    }
  }, [user, authLoading, router]);

  useEffect(() => {
    async function fetchProfile() {
      if (!user) return;
      try {
        const data = await profileApi.getProfile();
        if (data) {
          setFirstName(data.first_name || "");
          setLastName(data.last_name || "");
          if (data.birthday) {
            setBirthday(data.birthday.split("T")[0]);
          }
          setBiography(data.biography || "");
          setGoal(data.goal || "");
        }
      } catch (err) {
        setError(t("error"));
      } finally {
        setLoading(false);
      }
    }
    fetchProfile();
  }, [user, t]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError("");
    setSuccess("");

    try {
      await profileApi.updateProfile({
        first_name: firstName,
        last_name: lastName,
        birthday: birthday ? `${birthday}T00:00:00` : null,
        biography,
        goal,
      });
      setSuccess(t("success"));
      setTimeout(() => {
        if (isMissingName) {
          router.push("/counselee/overview");
          setTimeout(() => {
            window.location.reload();
          }, 50);
        } else {
          window.location.reload();
        }
      }, 1500);
    } catch (err) {
      setError(t("error"));
    } finally {
      setSaving(false);
    }
  };

  return {
    user,
    authLoading,
    router,
    locale,
    t,
    firstName,
    setFirstName,
    lastName,
    setLastName,
    birthday,
    setBirthday,
    biography,
    setBiography,
    goal,
    setGoal,
    loading,
    saving,
    error,
    success,
    isMissingName,
    handleSubmit,
  };
}
