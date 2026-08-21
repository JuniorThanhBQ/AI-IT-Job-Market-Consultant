export function getHeaderCTA(isAuthenticated, pathname, t) {
  if (!isAuthenticated) {
    return {
      label: t("get_started"),
      href: "/counselee/auth",
    };
  }
  if (pathname.includes("/counselee/jobs")) {
    return {
      label: t("cta_overview"),
      href: "/counselee/overview",
    };
  }
  return {
    label: t("cta_dashboard"),
    href: "/counselee/jobs",
  };
}
