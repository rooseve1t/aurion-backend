# Aurion OS Instructions for Windsurf Cascade

You are working in the `Aurion OS` production repository.

Primary goal:
- Produce working, verified changes with minimal regressions.

Core behavior:
- Read existing code before editing. Do not assume architecture or contracts.
- Prefer small, surgical fixes over broad rewrites unless a rewrite is clearly required.
- Preserve existing product behavior unless the task explicitly asks for a change.
- Never claim a feature works unless you actually verified it locally or can clearly state what remains unverified.
- Never invent API keys, credentials, production state, or external integrations.
- Never use leaked or public third-party secrets from the internet or GitHub.

Quality bar:
- Double-check your own work before presenting it.
- After each meaningful code change, re-read the changed files and validate imports, types, names, and obvious logic paths.
- Run the narrowest relevant verification first, then broader verification when the change is substantial.
- If verification fails, keep working until the failure is understood and either fixed or clearly documented.
- If you cannot verify something, explicitly say what you could not verify and why.

Verification policy:
- For frontend changes, prefer running the relevant combination of:
  - `npm run lint`
  - `npm run build`
  - targeted tests when available
- For backend changes, prefer running the relevant combination of:
  - `python3 -m pytest -q tests/test_backend_mvp.py`
  - `python3 -m pytest -q tests`
  - targeted endpoint or smoke validation when needed
- For auth, session, routing, deployment, or payments changes, always think in end-to-end flows, not just unit scope.

Auth/session safety:
- Treat login, refresh, logout, token persistence, and `/auth/me` as one connected system.
- Be conservative with forced logout behavior.
- Avoid changes that can silently clear tokens or redirect users unless failure is confirmed.

Deployment safety:
- Before deploy, ensure the app builds successfully.
- Prefer same-origin production configuration unless there is a deliberate reason not to.
- Do not point production to temporary tunnels or unstable preview endpoints.

Communication style:
- Be concise, factual, and honest.
- Report:
  - what changed,
  - how it was verified,
  - what is still risky or unverified.

Project-specific reminders:
- This repo contains both frontend and backend concerns in one workspace.
- The production site is `https://www.aurionai.ru`.
- Creator/admin access must not be blocked by paid subscription gating.
- Safari and iOS layout issues are high priority and should be checked when touching layout or auth flows.
