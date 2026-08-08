import Header from "@/components/shared/Header";
import Footer from "@/components/shared/Footer";
import TOSConsentModal from "@/components/shared/TOSConsentModal";

export default function MainLayout({ children }) {
  return (
    <div className="flex flex-col min-h-screen">
      <TOSConsentModal />
      <Header />
      <main className="flex-1 pt-20">{children}</main>
      <Footer />
    </div>
  );
}
