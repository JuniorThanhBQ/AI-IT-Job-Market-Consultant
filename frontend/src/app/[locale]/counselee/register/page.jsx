"use client";

import { useEffect } from "react";
import { useRouter } from "@/i18n/routing";

export default function RegisterRedirectPage() {
  const router = useRouter();

  useEffect(() => {
    router.replace("/counselee/login");
  }, [router]);

  return null;
}
