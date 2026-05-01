# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | Yes       |

---

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please **do not** open a public GitHub issue.

Instead, report it responsibly by emailing the maintainers directly. Include:

- A clear description of the vulnerability
- Steps to reproduce the issue
- Potential impact assessment
- Any suggested remediation (optional)

You can expect an acknowledgement within **48 hours** and a resolution or mitigation plan within **14 business days** for confirmed vulnerabilities.

---

## Security Design Principles

This application follows a **no-backend-persistence** model. Uploaded files are processed entirely in memory and are never written to disk or stored in any database. No user data is retained between requests.

---

## File Upload Security

- **Allowed extensions only** — the API accepts `.xlsx`, `.xlsm`, `.csv`, and `.tsv` files. All other file types are rejected with HTTP 400.
- **File size cap** — uploads are limited to **10 MB**. Requests exceeding this limit are rejected with HTTP 413.
- **Content validation** — files are parsed immediately on receipt. Malformed or unreadable files produce a structured error and are discarded; they are never forwarded or stored.
- **No execution** — uploaded files are only parsed as structured data (spreadsheet/CSV). No macros, scripts, or embedded objects are executed.
- **Memory-only processing** — file bytes are read into memory, processed, and then garbage-collected. No temporary files are created on the filesystem.

---

## API Security

- **Input validation** — all request parameters and file contents are validated server-side using Pydantic v2 models before any processing occurs.
- **Strict typing** — response models enforce field types and reject unexpected fields, preventing data leakage through accidental model exposure.
- **No authentication by default** — this application is designed for internal/intranet use. If exposing it publicly, place it behind an authentication layer (e.g. OAuth2 proxy, API gateway, VPN).
- **CORS** — Cross-Origin Resource Sharing is currently set to allow all origins for development convenience. Before production deployment, restrict `allow_origins` in `backend/app/main.py` to the specific frontend domain.
- **No secrets in responses** — the API never echoes back environment variables, internal paths, or system information in responses or error messages.

---

## Dependency Security

### Backend (Python)

- Dependencies are pinned to specific versions in `backend/requirements.txt` to prevent unexpected upstream changes.
- Run a dependency audit regularly:
  ```bash
  pip install pip-audit
  pip-audit -r backend/requirements.txt
  ```

### Frontend (JavaScript)

- Dependencies are managed via `npm` with a committed `package-lock.json` for reproducible installs.
- Run a dependency audit regularly:
  ```bash
  cd frontend && npm audit
  ```
- Address `HIGH` and `CRITICAL` severity advisories promptly. Use `npm audit fix` for automatic safe upgrades.

---

## Data Privacy

- **No PII storage** — uploaded Jira exports may contain employee names (used as "Assignee"). This data is processed in-memory to generate aggregations and is never persisted, logged, or transmitted to third parties.
- **No analytics or telemetry** — the application does not include any third-party tracking, analytics scripts, or telemetry collection.
- **No cookies** — the application does not set any cookies or use browser storage (localStorage, sessionStorage, IndexedDB).
- **Transport** — in production, always serve the application over **HTTPS/TLS**. Replit deployments enforce TLS automatically.

---

## Secrets Management

- **No secrets in source code** — API keys, credentials, and environment-specific configuration must never be committed to the repository.
- **Environment variables** — use `.env` files locally (excluded via `.gitignore`) or a secrets manager in production. Never hard-code credentials.
- **`.gitignore`** — ensure `.env`, `*.key`, `*.pem`, and similar sensitive files are listed in `.gitignore`.

---

## Infrastructure & Deployment Hardening

- **Host binding** — the backend binds to `localhost` only in development, preventing external access to the raw API port. In production, place the application behind a reverse proxy (e.g. nginx, Caddy, or a managed load balancer).
- **Production server** — use a production-grade ASGI server (e.g. Gunicorn + Uvicorn workers) instead of `uvicorn --reload` in production environments.
- **Dependency isolation** — run the application in an isolated environment (container, virtual environment, or managed runtime) to limit the blast radius of any compromised dependency.
- **Least privilege** — the application process should run as a non-root user with the minimum filesystem permissions required.
- **Security headers** — add the following HTTP response headers via a reverse proxy or middleware in production:

  | Header | Recommended Value |
  |--------|-------------------|
  | `Strict-Transport-Security` | `max-age=63072000; includeSubDomains` |
  | `X-Content-Type-Options` | `nosniff` |
  | `X-Frame-Options` | `DENY` |
  | `Content-Security-Policy` | `default-src 'self'` (adjust for fonts/assets) |
  | `Referrer-Policy` | `strict-origin-when-cross-origin` |

---

## Secure Development Practices

- **Code review** — all changes must be reviewed before merging to the main branch.
- **Branch protection** — enable branch protection rules on `main`/`master` in GitHub to require pull request reviews and passing status checks before merging.
- **No force-push to main** — force-pushing to the main branch is prohibited.
- **Signed commits** — contributors are encouraged to sign commits with GPG keys (`git config commit.gpgsign true`).
- **Static analysis** — run linters and static analysis tools as part of the CI pipeline:
  ```bash
  # Python
  pip install bandit
  bandit -r backend/app/

  # JavaScript (if ESLint is configured)
  cd frontend && npx eslint src/
  ```

---

## Incident Response

In the event of a confirmed security incident:

1. **Contain** — isolate the affected system immediately (take the service offline if necessary).
2. **Assess** — determine the scope, affected data, and attack vector.
3. **Notify** — inform relevant stakeholders and, if personal data is involved, comply with applicable data breach notification obligations (e.g. GDPR Article 33).
4. **Remediate** — apply patches, rotate any exposed credentials, and harden the affected component.
5. **Review** — conduct a post-incident review and update security controls to prevent recurrence.

---

## Compliance Notes

This application processes workforce performance data (story points, sprint metrics, assignee names). Depending on your jurisdiction and organisational policies, this may be subject to:

- **GDPR / UK GDPR** — if processing data of EU/UK employees, ensure a lawful basis for processing and honour data subject rights.
- **Internal HR / data governance policies** — consult your organisation's data governance team before deploying in an environment where employee performance data is processed.

---

*Last updated: May 2026*
