"use client";

import { usePathname } from "next/navigation";
import Header from "@/components/shared/Header";
import Footer from "@/components/shared/Footer";

export default function MainLayout({ children }) {
  const pathname = usePathname();
  const isUnavailable = pathname?.includes("/unavailable");

  if (isUnavailable) {
    return <main className="min-h-screen">{children}</main>;
  }

  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <main className="flex-1 pt-20">{children}</main>
      <Footer />
    </div>
  );
}
