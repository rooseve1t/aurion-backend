---
trigger: glob
globs: app/**/*.py
---

When changing backend files:

- Read the surrounding endpoint or service flow before editing.
- Preserve schema, auth, and response contracts unless the task explicitly requires a change.
- Avoid fake “success” responses that hide errors.
- Do not hardcode secrets or unsafe defaults.
- If you touch auth, session, payments, or deployment-related code, reason through the full request lifecycle.

Before finishing a backend task, prefer to run:
- `python3 -m pytest -q tests/test_backend_mvp.py`
- `python3 -m pytest -q tests`

If tests fail, continue until the failure is understood and either fixed or clearly reported.
