import { test, expect } from "@playwright/test";

const routes = [
  "/",
  "/en",
  "/vi",
  "/en/aijmc",
  "/vi/aijmc",
  "/en/counselee/auth",
  "/vi/counselee/auth",
  "/en/counselee/chatbot",
  "/vi/counselee/chatbot",
  "/en/counselee/consultant",
  "/vi/counselee/consultant",
  "/en/counselee/jobs",
  "/vi/counselee/jobs",
  "/en/counselee/jobs/advanced-search",
  "/vi/counselee/jobs/advanced-search",
  "/en/counselee/overview",
  "/vi/counselee/overview",
  "/en/counselee/profile",
  "/vi/counselee/profile",
  "/en/tos",
  "/vi/tos",
];

test.describe("Check frontend routing", () => {
  for (const route of routes) {
    test(`Route ${route} should not return 404`, async ({ page }) => {
      const response = await page.goto(route);
      expect(response).not.toBeNull();
      expect(response!.status()).not.toBe(404);
    });
  }
});
