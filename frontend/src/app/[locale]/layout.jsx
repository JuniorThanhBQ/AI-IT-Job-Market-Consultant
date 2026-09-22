import { NextIntlClientProvider } from "next-intl";
import { getMessages } from "next-intl/server";
import { notFound } from "next/navigation";
import { routing } from "@/i18n/routing";
import MainLayout from "@/components/layouts/MainLayout";
import { AuthProvider } from "@/context/AuthProvider";
import { Toaster } from "sonner";

export default async function LocaleLayout({ children, params }) {
  const { locale } = await params;
  const messages = await getMessages();

  if (!routing.locales.includes(locale)) {
    notFound();
  }

  return (
    <NextIntlClientProvider messages={messages}>
      <AuthProvider>
        <MainLayout>{children}</MainLayout>
        <Toaster position="bottom-right" richColors />
      </AuthProvider>
    </NextIntlClientProvider>
  );
}
