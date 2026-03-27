---
trigger: glob
globs: src/**/*.{ts,tsx,css}
---

When changing frontend files:

- First inspect related components, hooks, stores, and service clients before editing.
- Keep API contracts aligned with the backend.
- Avoid introducing `any` when a concrete type is feasible.
- For auth-sensitive changes, review:
  - `src/store/authStore.ts`
  - `src/services/api.ts`
  - route/layout bootstrap logic
- For layout-sensitive changes, think about Safari/iOS safe areas and viewport behavior.

Before finishing a frontend task, prefer to run:
- `npm run lint`
- `npm run build`
- relevant tests if they exist

Do not present the result as done if build or lint is failing.
