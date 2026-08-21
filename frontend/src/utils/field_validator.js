export function hasXSS(value) {
  if (!value) return false;
  const lowercaseVal = value.toLowerCase();
  const xssPatterns = [
    /<script[^>]*>/,
    /javascript:/,
    /onerror\s*=/,
    /onload\s*=/,
    /onmouseover\s*=/,
    /<\/?[a-z][\s\S]*>/,
  ];
  return xssPatterns.some((pattern) => pattern.test(lowercaseVal));
}

export function hasSQLInjection(value) {
  if (!value) return false;
  const lowercaseVal = value.toLowerCase();
  const sqlPatterns = [
    /['"`;\-\-]/,
    /\bor\b.*\b\d+\s*=\s*\d+/,
    /\bunion\b.*\bselect\b/,
    /\bselect\b.*\bfrom\b/,
    /\binsert\b.*\binto\b/,
    /\bdelete\b.*\bfrom\b/,
    /\bdrop\b.*\btable\b/,
  ];
  return sqlPatterns.some((pattern) => pattern.test(lowercaseVal));
}

export function isValidEmail(email) {
  if (!email) return false;
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

export function isStrongPassword(password) {
  if (!password) return false;
  const minLength = 8;
  const hasUpperCase = /[A-Z]/.test(password);
  const hasLowerCase = /[a-z]/.test(password);
  const hasNumbers = /\d/.test(password);
  const hasNonalphas = /\W/.test(password);
  return (
    password.length >= minLength &&
    hasUpperCase &&
    hasLowerCase &&
    hasNumbers &&
    hasNonalphas
  );
}

export function validateLogin(email, password, t) {
  if (!email || !password) {
    return t ? t("validation_fill_fields") : "Please fill in all fields.";
  }
  if (hasXSS(email) || hasXSS(password)) {
    return t
      ? t("validation_xss")
      : "Input contains unsafe HTML or script tags.";
  }
  if (hasSQLInjection(email) || hasSQLInjection(password)) {
    return t ? t("validation_sqli") : "Input contains unsafe SQL patterns.";
  }
  if (!isValidEmail(email)) {
    return t ? t("validation_email") : "Please enter a valid email address.";
  }
  return null;
}

export function validateRegister(email, username, password, t) {
  if (!email || !username || !password) {
    return t ? t("validation_fill_fields") : "Please fill in all fields.";
  }
  if (!username.trim()) {
    return t ? t("validation_username_blank") : "Username cannot be blank.";
  }
  if (hasXSS(email) || hasXSS(username) || hasXSS(password)) {
    return t
      ? t("validation_xss")
      : "Input contains unsafe HTML or script tags.";
  }
  if (
    hasSQLInjection(email) ||
    hasSQLInjection(username) ||
    hasSQLInjection(password)
  ) {
    return t ? t("validation_sqli") : "Input contains unsafe SQL patterns.";
  }
  if (!isValidEmail(email)) {
    return t ? t("validation_email") : "Please enter a valid email address.";
  }
  if (!isStrongPassword(password)) {
    return t
      ? t("validation_password_weak")
      : "Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one number, and one special character.";
  }
  return null;
}
