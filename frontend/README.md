# AI-IT-Job-Market-Consultant - Frontend

This is the user-facing web application for the **AI IT Job Market Consultant (AIJMC)** platform. It provides interactive dashboards, job search interfaces, career analysis charts, and a career consultation chatbot.

---

## I. Architectural Decisions & Tech Stack

Following the system's Architecture Decision Records (ADRs):
*   **Core Framework:** **Next.js (React App Router)** (ADR-06) written in type-safe **TypeScript**.
*   **Styling & Components:** Styled with **Tailwind CSS** and modular, accessible UI components from **Shadcn UI**.
*   **Web Server (Production):** Proxy-passed through **Nginx** (ADR-01) with hardened security protocols.
    *   H2C smuggling vulnerabilities are mitigated by disabling empty protocol upgrades.
    *   Host header injection risks are prevented by securing the Nginx Host forwarding scope.
*   **Linting & Validation:** Configured with ESLint and automatic validation gates in our GitHub Actions pipeline (ADR-04) to block syntax errors and formatting discrepancies before deployment.

---

## II. Development Workflow

### 1. Local Setup & Execution
Ensure you have Node.js (v20+) installed. Inside the `frontend/` directory:

```bash
# Install dependencies
$ npm ci

# Run development server
$ npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser to inspect the application. The dev server supports hot module replacement (HMR).

### 2. Building for Production
Verify that the production build compiles successfully:

```bash
# Build the application
$ npm run build

# Start the standalone Node.js production server
$ npm run start
```

### 3. Code Linting & Formatting
Run ESLint to inspect quality warnings:

```bash
$ npm run lint
```
