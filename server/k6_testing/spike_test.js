import http from 'k6/http';
import { check, sleep, fail } from 'k6';

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
const baseUrl = getEnvVar('NEXT_PUBLIC_BASE_URL');

export const options = {
  stages: [
    { duration: '10s', target: 10 },
    { duration: '10s', target: 100 },
    { duration: '20s', target: 200 },
    { duration: '10s', target: 0 },
  ],
  thresholds: {
    http_req_failed: ['rate < 0.05'],
  },
};

export function setup() {
  const payload = {
    username: username,
    password: password,
  };
  const params = {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  };
  const resLogin = http.post(`${baseUrl}/accounts/sessions/`, payload, params);
  if (resLogin.status !== 200) {
    fail('Login failed with status ' + resLogin.status + ': ' + resLogin.body);
  }
  const token = JSON.parse(resLogin.body).access_token;
  return { token };
}

export default function (data) {
  const params = {
    headers: {
      'Authorization': `Bearer ${data.token}`,
    },
  };
  const res = http.get(`${baseUrl}/jobs/?title=python`, params);
  check(res, {
    'status is 200': (r) => r.status === 200,
    'has jobs': (r) => {
      try {
        return Array.isArray(JSON.parse(r.body));
      } catch (e) {
        return false;
      }
    }
  });
  sleep(1);
}
