import React from "react";

export const renderTextWithHtmlBreaks = (node) => {
  if (typeof node === "string") {
    if (/<br\s*\/?>/i.test(node)) {
      const parts = node.split(/<br\s*\/?>/i);
      return parts.map((part, index) => (
        <React.Fragment key={index}>
          {index > 0 && <br />}
          {part}
        </React.Fragment>
      ));
    }
    return node;
  }
  if (Array.isArray(node)) {
    return node.map((child, index) => (
      <React.Fragment key={index}>
        {renderTextWithHtmlBreaks(child)}
      </React.Fragment>
    ));
  }
  if (React.isValidElement(node)) {
    const children = node.props.children;
    if (children) {
      return React.cloneElement(node, {}, renderTextWithHtmlBreaks(children));
    }
  }
  return node;
};

export function isSafeUrl(url) {
  const trimmed = (url || "").trim();
  if (/^(\/|\.\/|\.\.\/|#)/.test(trimmed)) return true;
  try {
    const parsed = new URL(trimmed, "https://example.com");
    return ["http:", "https:", "mailto:", "tel:"].includes(parsed.protocol);
  } catch {
    return false;
  }
}

export function getFooterLinks(t) {
  return {
    product: [
      { name: t("link_jd_matching"), href: "/counselee/chatbot" },
      { name: t("link_tech_trends"), href: "/counselee/overview" },
      { name: t("link_career_roadmaps"), href: "/counselee/overview" },
      { name: t("link_pricing"), href: "/aijmc" },
    ],
    company: [
      { name: t("link_about_us"), href: "/aijmc" },
      { name: t("link_careers"), href: "/aijmc/founder-inspiration" },
      { name: t("link_blog"), href: "/aijmc/faq" },
      { name: t("link_contact"), href: "/aijmc/contact" },
    ],
    legal: [{ name: t("link_terms_of_service"), href: "/tos" }],
  };
}
