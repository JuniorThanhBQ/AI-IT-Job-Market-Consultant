# AIJMC Next.js Frontend

A key component of the AIJMC system that acts as an intermediary between the user interface and the backend, forwarding business requests.

## Architectural and Technology Decisions

- Framework: Next.js (JavaScript-based).
- UI Components: Tailwind CSS is used to design modular, accessible UI components. Additionally, buttons and interactive elements utilize the Shadcn UI library for ease of management.
- Web Server: Requests are forwarded via Nginx, incorporating security protocols, rate limiting, and caching.
- Host header injection risks are mitigated by securing Nginx's host forwarding scope.

## Note
The `next-intl` library is used for Vietnamese-English localization, with translation files located in the `src/messages` directory. Currently, the system supports only Vietnamese and English.

## Frontend Structure
```text
frontend/
├── Dockerfile
├── README.md
├── commitlint.config.js
├── components.json
├── eslint.config.mjs
├── jsconfig.json
├── next.config.mjs
├── nginx.conf
├── package.json
├── playwright.config.ts
├── postcss.config.mjs
├── public/
│   └── vercel.svg
├── src/
│   ├── app/
│   │   ├── [locale]/
│   │   ├── favicon.ico
│   │   ├── globals.css
│   │   ├── layout.jsx
│   │   └── page.jsx
│   ├── assets/
│   │   └── CloudinaryAssetsUrl.js
│   ├── components/
│   │   ├── layouts/
│   │   ├── shared/
│   │   └── ui/
│   ├── configs/
│   │   └── apis.js
│   ├── context/
│   │   └── AuthProvider.jsx
│   ├── features/
│   │   ├── AuthPage/
│   │   ├── Chatbot/
│   │   ├── Companies/
│   │   ├── HomePage/
│   │   ├── Jobs/
│   │   ├── Overview/
│   │   ├── Profile/
│   │   └── TOS/
│   ├── i18n/
│   │   ├── request.js
│   │   └── routing.js
│   ├── lib/
│   │   └── utils.js
│   ├── messages/
│   │   ├── en.json
│   │   └── vi.json
│   ├── utils/
│   │   ├── const.js
│   │   ├── enumMapper.js
│   │   ├── field_validator.js
│   │   ├── homepage_utils.js
│   │   ├── navigation.js
│   │   └── url.js
│   └── proxy.js
└── tests/
    ├── cloudinary.spec.ts
    └── router.spec.ts
```
