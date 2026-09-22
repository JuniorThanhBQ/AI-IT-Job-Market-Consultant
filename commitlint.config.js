module.exports = {
  extends: ["@commitlint/config-conventional"],
  rules: {
    "type-enum": [
      2,
      "always",
      ["Release", "Tag", "Documentation", "Enhancement", "Maintenance"],
    ],
    "type-case": [2, "always", "pascal-case"],
  },
};
