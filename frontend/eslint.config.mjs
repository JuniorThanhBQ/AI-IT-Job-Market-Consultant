import { defineConfig, globalIgnores } from "eslint/config";
import prettier from "eslint-config-prettier/flat";
import nextVitals from "eslint-config-next/core-web-vitals";

const eslintConfig = defineConfig([
  ...nextVitals,
  prettier,

  globalIgnores([
    ".next/**",
    "out/**",
    "build/**",
    "coverage/**",
    "dist/**",
    ".turbo/**",
    "next-env.d.ts",
  ]),
]);

export default eslintConfig;
