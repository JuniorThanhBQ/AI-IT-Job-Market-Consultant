import http from 'k6/http';
import { check, sleep } from 'k6';

const envContent = open('../.env');

function getEnvVar(key) {
  const lines = envContent.split(/\r?\n/);
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (line.startsWith(key + '=')) {
      return line.substring(key.length + 1).replace(/^['"]|['"]$/g, '');
    }
  }
  return __ENV[key] || '';
}

const username = getEnvVar('TEST_USER');
const password = getEnvVar('PASSWORD');
const baseUrl = getEnvVar('NEXT_PUBLIC_BASE_URL_LOCAL');

export const options = {
  vus: 1,
  duration: '1s',
};

export default function () {
  const resAuthPage = http.get('https://ai-it-job-market-consultant.vercel.app/en/counselee/auth');
  check(resAuthPage, {
    'auth page status is 200': (r) => r.status === 200,
  });

  const payload = {
    username: username,
    password: password,
  };

  const params = {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  };

  const resLogin = http.post(
    `${baseUrl}/accounts/sessions/`,
    payload,
    params
  );

  check(resLogin, {
    'login status is 200': (r) => r.status === 200,
    'has token': (r) => {
      try {
        return JSON.parse(r.body).access_token !== undefined;
      } catch (e) {
        return false;
      }
    }
  });

  sleep(1);
}
