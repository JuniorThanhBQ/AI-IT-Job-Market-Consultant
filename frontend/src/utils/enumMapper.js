import en from "@/messages/en.json";
import vi from "@/messages/vi.json";

const locales = { en, vi };

export function mapEnum(value, type, locale = "en") {
  if (!value) return "";
  const dictionary = locales[locale] || en;
  const enumDict = dictionary.Enums?.[type];
  if (!enumDict) return value;

  const matchedKey = Object.keys(enumDict).find(
    (key) => key.toLowerCase() === String(value).toLowerCase(),
  );
  return matchedKey ? enumDict[matchedKey] : value;
}

export function mapWorkingHours(value, locale = "en") {
  const dictionary = locales[locale] || en;
  const hoursDict = dictionary.Enums?.WorkingHours || {};
  if (!value) return hoursDict.Negotiable || "Negotiable";

  const normalized = String(value)
    .toLowerCase()
    .replace(/[\s_-]/g, "");
  if (normalized.includes("fulltime")) {
    return hoursDict.FullTime || "Full-time";
  }
  if (normalized.includes("parttime")) {
    return hoursDict.PartTime || "Part-time";
  }
  return hoursDict.Negotiable || "Negotiable";
}

export function formatSalaryRange(minSalary, maxSalary, locale = "en") {
  const dictionary = locales[locale] || en;
  const min = Number(minSalary || 0);
  const max = Number(maxSalary || 0);
  const negotiableText =
    dictionary.Enums?.WorkingHours?.Negotiable ||
    (locale === "vi" ? "Thỏa thuận" : "Negotiable");

  if (min === 0 && max === 0) {
    return negotiableText;
  }

  const baseValue = min > 0 ? min : max;
  const currency = baseValue > 100000 ? "VND" : "USD";
  const fromText = locale === "vi" ? "Từ" : "From";
  const upToText = locale === "vi" ? "Lên đến" : "Up to";

  if (min > 0 && max > 0) {
    return `${min.toLocaleString()} - ${max.toLocaleString()} ${currency}`;
  }
  if (min > 0) {
    return `${fromText} ${min.toLocaleString()} ${currency}`;
  }
  if (max > 0) {
    return `${upToText} ${max.toLocaleString()} ${currency}`;
  }

  return negotiableText;
}
