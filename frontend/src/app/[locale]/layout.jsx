import { NextIntlClientProvider } from "next-intl";
import { getMessages } from "next-intl/server";
import { notFound } from "next/navigation";
import { routing } from "@/i18n/routing";
import MainLayout from "@/components/layouts/MainLayout";
import { AuthProvider } from "@/context/AuthProvider";

export default async function LocaleLayout({ children, params }) {
  const { locale } = await params;

  if (!routing.locales.includes(locale)) {
    notFound();
  }

  const messages = await getMessages();

  return (
    <NextIntlClientProvider messages={messages}>
      <AuthProvider>
        <MainLayout>{children}</MainLayout>
      </AuthProvider>
    </NextIntlClientProvider>
  );
}
