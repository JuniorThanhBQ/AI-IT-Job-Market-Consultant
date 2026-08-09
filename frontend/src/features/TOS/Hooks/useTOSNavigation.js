export function useTOSNavigation() {
  const scrollToSection = (sectionKey) => {
    const el = document.getElementById(`tos-${sectionKey}`);
    if (el) {
      el.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }
  };

  return {
    scrollToSection,
  };
}
