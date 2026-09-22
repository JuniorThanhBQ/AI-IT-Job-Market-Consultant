import validator from "validator";

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
  return validator.isEmail(email);
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

export function isValidUsername(username) {
  if (!username) return false;
  return /^[a-zA-Z0-9_]{3,}$/.test(username);
}

export function validateLogin(email, password, t) {
  const cleanEmail = (email || "").trim();
  const cleanPassword = (password || "").trim();
  if (!cleanEmail || !cleanPassword) {
    return t ? t("validation_fill_fields") : "Please fill in all fields.";
  }
  if (hasXSS(cleanEmail) || hasXSS(cleanPassword)) {
    return t ? t("validation_xss") : "Invalid input.";
  }
  if (hasSQLInjection(cleanEmail) || hasSQLInjection(cleanPassword)) {
    return t ? t("validation_sqli") : "Invalid input.";
  }
  if (!isValidEmail(cleanEmail)) {
    return t ? t("validation_email") : "Please enter a valid email address.";
  }
  return null;
}

export function validateRegister(
  email,
  username,
  password,
  confirmPassword,
  t,
) {
  const cleanEmail = (email || "").trim();
  const cleanUsername = (username || "").trim();
  const cleanPassword = (password || "").trim();
  const cleanConfirmPassword = (confirmPassword || "").trim();
  if (
    !cleanEmail ||
    !cleanUsername ||
    !cleanPassword ||
    !cleanConfirmPassword
  ) {
    return t ? t("validation_fill_fields") : "Please fill in all fields.";
  }
  if (cleanPassword !== cleanConfirmPassword) {
    return t ? t("validation_password_mismatch") : "Passwords do not match.";
  }
  if (!isValidUsername(cleanUsername)) {
    return t
      ? t("validation_username_invalid")
      : "Username must be at least 3 characters long and contain only letters.";
  }
  if (hasXSS(cleanEmail) || hasXSS(cleanUsername) || hasXSS(cleanPassword)) {
    return t ? t("validation_xss") : "Invalid input.";
  }
  if (
    hasSQLInjection(cleanEmail) ||
    hasSQLInjection(cleanUsername) ||
    hasSQLInjection(cleanPassword)
  ) {
    return t ? t("validation_sqli") : "Invalid input.";
  }
  if (!isValidEmail(cleanEmail)) {
    return t ? t("validation_email") : "Please enter a valid email address.";
  }
  if (!isStrongPassword(cleanPassword)) {
    return t
      ? t("validation_password_weak")
      : "Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one number, and one special character.";
  }
  return null;
}

export function isSpamName(name) {
  if (!name) return false;
  const lowercase = name.toLowerCase();
  if (/(.)\1{3,}/.test(lowercase)) return true;
  if (/(.{2,})\1{2,}/.test(lowercase)) return true;
  if (/[bcdfghjklmnpqrstvwxyz]{5,}/i.test(lowercase)) return true;
  return false;
}

export function isValidAge(birthdayStr) {
  if (!birthdayStr) return false;
  const birthday = new Date(birthdayStr);
  if (isNaN(birthday.getTime())) return false;
  const today = new Date();
  let age = today.getFullYear() - birthday.getFullYear();
  const m = today.getMonth() - birthday.getMonth();
  if (m < 0 || (m === 0 && today.getDate() < birthday.getDate())) {
    age--;
  }
  return age >= 16 && age <= 100;
}

export function validateProfile(
  firstName,
  lastName,
  birthday,
  biography,
  goal,
  t,
) {
  const cleanFirstName = (firstName || "").trim();
  const cleanLastName = (lastName || "").trim();
  const cleanBio = (biography || "").trim();
  const cleanGoal = (goal || "").trim();

  if (!cleanFirstName || !cleanLastName) {
    return t ? t("validation_fill_fields") : "Please fill in all fields.";
  }

  if (cleanFirstName.length < 2 || cleanFirstName.length > 64) {
    return t
      ? t("validation_firstname_length")
      : "First name must be between 2 and 64 characters.";
  }
  if (cleanLastName.length < 2 || cleanLastName.length > 64) {
    return t
      ? t("validation_lastname_length")
      : "Last name must be between 2 and 64 characters.";
  }

  const fields = [cleanFirstName, cleanLastName, cleanBio, cleanGoal];
  if (fields.some(hasXSS)) {
    return t
      ? t("validation_xss")
      : "Input contains unsafe HTML or script tags.";
  }
  if (fields.some(hasSQLInjection)) {
    return t ? t("validation_sqli") : "Input contains unsafe SQL patterns.";
  }

  if (isSpamName(cleanFirstName) || isSpamName(cleanLastName)) {
    return t
      ? t("validation_name_spam")
      : "The name appears to be invalid or spam.";
  }

  if (birthday) {
    if (!isValidAge(birthday)) {
      return t
        ? t("validation_age_invalid")
        : "Age must be between 16 and 100 years old.";
    }
  }

  if (cleanBio.length > 512) {
    return t
      ? t("validation_bio_length")
      : "Biography cannot exceed 512 characters.";
  }
  if (cleanGoal.length > 512) {
    return t
      ? t("validation_goal_length")
      : "Goal cannot exceed 512 characters.";
  }

  return null;
}
