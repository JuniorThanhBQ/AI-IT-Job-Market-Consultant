import { test, expect } from "@playwright/test";
import { LOGO } from "../src/assets/CloudinaryAssetsUrl";

test.describe("Cloudinary Assets Check", () => {
  for (const [key, url] of Object.entries(LOGO)) {
    test(`Asset ${key} should not return 4xx`, async ({ request }) => {
      const response = await request.head(url);
      expect(response.status()).toBeLessThan(400);
    });
  }
});
