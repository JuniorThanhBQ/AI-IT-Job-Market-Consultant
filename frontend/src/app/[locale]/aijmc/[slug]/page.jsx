import { notFound } from "next/navigation";
import HomePage from "@/features/HomePage/HomePage";

export default async function DynamicAijmcPage({ params }) {
  const { slug } = await params;

  const validSlugs = {
    "founder-inspiration": "founder",
    faq: "faq",
    tos: "tos",
    contact: "contact",
  };

  const activePage = validSlugs[slug];

  if (!activePage) {
    notFound();
  }

  return <HomePage activePage={activePage} />;
}
