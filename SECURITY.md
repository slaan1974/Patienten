# Security Audit Report — Patiëntenbeheer

**Version:** 1.0.0
**Audit Date:** June 20, 2026
**Project:** Patient Management System (Patiëntenbeheer)
**Deployment Context:** Internet-facing, single-server (Raspberry Pi), uvicorn on port 8002
**Data Classification:** Medical/PII — BSN (Dutch national ID), psychiatric assessments (DSM-5), child welfare records (Kindcheck)

---

## Table of Contents

1. [Vulnerability Summary](#1-vulnerability-summary)
2. [Per-Page Audit Matrix](#2-per-page-audit-matrix)
3. [Detailed Findings](#3-detailed-findings)
4. [OWASP Top 10 (2021) Mapping](#4-owasp-top-10-2021-mapping)
5. [Remediation Roadmap](#5-remediation-roadmap)
6. [Responsible Disclosure Policy](#6-responsible-disclosure-policy)
7. [Security Checklist](#7-security-checklist)

---

## 1. Vulnerability Summary

| ID | Severity | Category | Affected Component | Status |
|---|---|---|---|---|
| C-01 | **CRITICAL** | No HTTPS/TLS | Deployment (all traffic) | Open |
| C-02 | **CRITICAL** | Weak Default Secret Key | `backend/config.py:6` | Open |
| C-03 | **CRITICAL** | CORS `*` with Credentials | `backend/main.py:48-54` | Open |
| C-04 | **CRITICAL** | No Rate Limiting on Auth | `backend/routers/auth.py` | Open |
| C-05 | **CRITICAL** | Open User Registration | `backend/routers/auth.py:11` | Open |
| C-06 | **CRITICAL** | No Role-Based Access Control | Global (all routes) | Open |
| C-07 | **CRITICAL** | BSN Stored in Plain Text | `backend/models/patient.py:13` | Open |
| H-01 | **HIGH** | No Password Policy | `backend/schemas/user.py` | Open |
| H-02 | **HIGH** | No Account Lockout | `backend/services/auth_service.py` | Open |
| H-03 | **HIGH** | Token in WebSocket URL | `frontend/src/stores/locks.js:15` | Open |
| H-04 | **HIGH** | No Token Revocation | `backend/services/auth_service.py` | Open |
| H-05 | **HIGH** | SQLite in Production | `backend/config.py:5` | Open |
| H-06 | **HIGH** | No Content Security Policy | `backend/main.py` (response headers) | Open |
| H-07 | **HIGH** | Missing Security HTTP Headers | `backend/main.py` (response headers) | Open |
| H-08 | **HIGH** | All Users Can List All Patients | `backend/routers/patients.py:19` | Open |
| H-09 | **HIGH** | Audit Log Shows User ID, Not Display Name | `backend/routers/audit.py` | Open |
| M-01 | **MEDIUM** | No CSRF Protection | Frontend (Bearers mitigate partially) | Open |
| M-02 | **MEDIUM** | No `.env.example` Committed | Project root | Open |
| M-03 | **MEDIUM** | No Input Sanitization on Text Fields | All text input fields | Open |
| M-04 | **MEDIUM** | Kindcheck Children Replace Not Atomic | `backend/services/kindcheck_service.py:71` | Open |
| M-05 | **MEDIUM** | Patient Delete Lacks Lock Check | `backend/routers/patients.py:70` | Open |
| M-06 | **MEDIUM** | DSM-5/Kindcheck Delete Lacks Lock Check | `backend/routers/dsm5.py:78`, `routers/kindcheck.py:88` | Open |
| M-07 | **MEDIUM** | JWT `sub` Not Validated as Integer | `backend/services/auth_service.py:45` | Open |
| L-01 | **LOW** | Verbose Error Messages | Backend exception handlers | Open |
| L-02 | **LOW** | No Logout Everywhere | `backend/routers/auth.py` | Open |
| L-03 | **LOW** | `beforeUnload` Relies on `keepalive` Fetch | `frontend/src/stores/locks.js:91-95` | Open |
| L-04 | **LOW** | No Database Access Controls on SQLite File | `backend/patienten.db` | Open |

---

## 2. Per-Page Audit Matrix

### 2.1 Frontend Routes

| # | Route | View | Auth? | Sensitive Data Displayed | API Calls | XSS Risk | CSRF | IDOR | Auth Guard | Score |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `/login` | LoginView | No | None | `POST /api/auth/login` | Low (Vue escapes) | N/A (Bearer) | N/A | N/A | ⚠️ |
| 2 | `/` | DashboardView | Yes | None | None | Low | N/A | N/A | `localStorage` check | ⚠️ |
| 3 | `/patienten` | PatientListView | Yes | BSN, names, addresses, phone | `GET /api/patients` (3s poll) | Low | N/A | **All patients visible to any user** | `localStorage` check | 🔴 |
| 4 | `/patienten/:id` | PatientDetailView | Yes | BSN, full PII, notes | `GET/PUT/DELETE /api/patients/:id`, `POST /api/lock` | Low | N/A | No per-record auth | `localStorage` check | 🔴 |
| 5 | `/patienten/:id/dsm5` | Dsm5FormView | Yes | Psychiatric assessment text | `GET/POST/DELETE /api/dsm5/*`, lock | Low | N/A | No per-record auth | `localStorage` check | 🔴 |
| 6 | `/dsm5` | Dsm5OverviewView | Yes | BSN, names, form status | `GET /api/dsm5/status/all` | Low | N/A | **BSN exposed in overview** | `localStorage` check | 🔴 |
| 7 | `/kindcheck` | KindcheckOverviewView | Yes | BSN, names, form status | `GET /api/kindcheck/status/all` | Low | N/A | **BSN exposed in overview** | `localStorage` check | 🔴 |
| 8 | `/patienten/:id/kindcheck` | KindcheckFormView | Yes | Child welfare data, children names | `GET/POST/DELETE /api/kindcheck/*`, lock | Low | N/A | No per-record auth | `localStorage` check | 🔴 |
| 9 | `/audit` | AuditLogView | Yes | Full change history (all PII) | `GET /api/audit` (filtered) | Low | N/A | **Any user sees all audit logs** | `localStorage` check | 🔴 |
| 10 | `/audit/:id` | AuditDetailView | Yes | Old/new values with PII in diff | `GET /api/audit/:id` | **Stored XSS in JSON diff display** (`v-html` via `<pre>`) | N/A | Any user sees any log | `localStorage` check | 🔴 |

### 2.2 Backend API Endpoints

| # | Method | Path | Auth | Audit | Lock Check | Rate Limited | Notes |
|---|---|---|---|---|---|---|---|
| 1 | POST | `/api/auth/register` | No | No | N/A | **No** | Open registration |
| 2 | POST | `/api/auth/login` | No | No | N/A | **No** | Brute-force target |
| 3 | POST | `/api/auth/refresh` | No | No | N/A | **No** | Token rotation |
| 4 | GET | `/api/health` | No | No | N/A | **No** | Info leak |
| 5 | GET | `/api/patients` | Yes | No | N/A | No | **All patients returned** |
| 6 | GET | `/api/patients/:id` | Yes | No | No | No | |
| 7 | POST | `/api/patients` | Yes | ✅ CREATE | No | No | |
| 8 | PUT | `/api/patients/:id` | Yes | ✅ UPDATE | **No** | No | Can edit while locked |
| 9 | DELETE | `/api/patients/:id` | Yes | ✅ DELETE | **No** | No | Can delete while locked |
| 10 | GET | `/api/dsm5/:patient_id` | Yes | No | No | No | |
| 11 | POST | `/api/dsm5/:patient_id` | Yes | ✅ CREATE/UPDATE | No | No | |
| 12 | PUT | `/api/dsm5/form/:form_id` | Yes | ✅ UPDATE | **No** | No | Can edit while locked |
| 13 | DELETE | `/api/dsm5/form/:form_id` | Yes | ✅ DELETE | **No** | No | Can delete while locked |
| 14 | GET | `/api/dsm5/status/all` | Yes | No | N/A | No | **BSN returned in response** |
| 15 | GET | `/api/kindcheck/terminologie` | Yes | No | N/A | No | |
| 16 | GET | `/api/kindcheck/:patient_id` | Yes | No | No | No | |
| 17 | POST | `/api/kindcheck/:patient_id` | Yes | ✅ CREATE/UPDATE | No | No | |
| 18 | PUT | `/api/kindcheck/form/:form_id` | Yes | ✅ UPDATE | **No** | No | Can edit while locked |
| 19 | DELETE | `/api/kindcheck/form/:form_id` | Yes | ✅ DELETE | **No** | No | Can delete while locked |
| 20 | GET | `/api/kindcheck/status/all` | Yes | No | N/A | No | **BSN returned in response** |
| 21 | POST | `/api/lock` | Yes | No | N/A | No | |
| 22 | DELETE | `/api/lock` | Yes | No | N/A | No | |
| 23 | POST | `/api/lock/release-all` | Yes | No | N/A | No | |
| 24 | GET | `/api/lock/:table/:id` | Yes | No | N/A | No | |
| 25 | POST | `/api/lock/refresh` | Yes | No | N/A | No | |
| 26 | GET | `/api/audit` | Yes | No | N/A | No | **All audit logs visible** |
| 27 | GET | `/api/audit/:log_id` | Yes | No | N/A | No | |
| 28 | WS | `/ws/:token` | Token in URL | No | N/A | No | **Token in server logs** |

---

## 3. Detailed Findings

### 🔴 CRITICAL

#### C-01: No HTTPS/TLS
- **Location:** `deploy/setup_pi.sh:53`, `deploy/patient.service:9`
- **Description:** The uvicorn server runs on `--host 0.0.0.0 --port 8002` with no TLS. All traffic — including passwords, JWT tokens, and medical data — traverses the network in plain text.
- **Impact:** Complete compromise of confidentiality. MITM attacker can intercept credentials, steal tokens, and read/modify all patient data, psychiatric assessments, and BSN numbers.
- **CVSS 3.1:** 9.8 (AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
- **Remediation:** Terminate TLS at a reverse proxy (nginx/caddy) or configure uvicorn with SSL certificates. Obtain Let's Encrypt certificate via Certbot. Redirect HTTP→HTTPS.

#### C-02: Weak Default Secret Key
- **Location:** `backend/config.py:6`
- **Description:** Default `SECRET_KEY = "vervang-dit-met-een-veilige-sleutel-in-productie"` (Dutch for "replace this with a secure key in production"). If the `.env` file is missing, this hardcoded value is used.
- **Impact:** An attacker who knows this default string can forge arbitrary JWT tokens, impersonate any user, and gain full system access.
- **CVSS 3.1:** 9.8 (AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
- **Remediation:** Remove the hardcoded default. Raise a `RuntimeError` if `SECRET_KEY` is not set in the environment. The deploy script (`setup_pi.sh:33`) already generates a random key — ensure this is enforced.

#### C-03: CORS `*` with Credentials
- **Location:** `backend/main.py:48-54`
- **Description:** `allow_origins=["*"]` combined with `allow_credentials=True`. Per the CORS specification, this is invalid and most browsers treat it as `allow_origins=["null"]` or refuse to send credentials entirely. Effectively disables CORS protection.
- **Impact:** Any website can make authenticated requests on behalf of logged-in users. Enables CSRF-like attacks against the API.
- **CVSS 3.1:** 8.8 (AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
- **Remediation:** Set `allow_origins` to the explicit list of allowed origins (e.g., `["https://patienten.example.com"]`). Either remove `allow_credentials` or use explicit origins.

#### C-04: No Rate Limiting on Auth Endpoints
- **Location:** `backend/routers/auth.py:11-23`
- **Description:** `POST /api/auth/login` and `POST /api/auth/register` have no rate limiting, captcha, or progressive delay.
- **Impact:** Attacker can brute-force passwords at unlimited speed. Can also spam user registration to fill the database.
- **CVSS 3.1:** 7.5 (AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
- **Remediation:** Implement rate limiting using `slowapi` (FastAPI middleware) or a custom IP-based rate limiter. Apply strict limits to `/api/auth/login` (e.g., 5 attempts/minute/IP) and `/api/auth/register` (e.g., 1 registration/hour/IP).

#### C-05: Open User Registration
- **Location:** `backend/routers/auth.py:11-12`
- **Description:** `POST /api/auth/register` is unauthenticated and unrestricted. No email verification, admin approval, or CAPTCHA.
- **Impact:** Anyone on the internet can create an account and gain full access to all patient data, psychiatric assessments, and audit logs.
- **CVSS 3.1:** 9.1 (AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
- **Remediation:** Either (a) require admin approval for new registrations, (b) restrict registration to specific email domains, (c) require an invite code, or (d) disable open registration entirely and create users via a seed script.

#### C-06: No Role-Based Access Control (RBAC)
- **Location:** Global — no role concept exists
- **Description:** Every authenticated user has full read/write/delete access to every patient, every form, every audit log, and all system functions. No admin/user distinction.
- **Impact:** A compromised or malicious low-privilege account (e.g., a temp worker) has the same access as a system administrator. Can delete all data, access all BSN numbers, and tamper with psychiatric assessments.
- **CVSS 3.1:** 8.6 (AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
- **Remediation:** Implement at minimum two roles: `admin` and `user`. `admin` can manage users and settings; `user` can manage patients/forms but cannot delete or register new users. Use a permission enum or bitmask on the `User` model.

#### C-07: BSN Stored in Plain Text
- **Location:** `backend/models/patient.py:13`
- **Description:** The Dutch BSN (Burger Service Nummer) — a national identifier equivalent to SSN — is stored as plain `String` with no encryption at rest.
- **Impact:** If the SQLite file is exfiltrated or the server is compromised, all BSN numbers are immediately readable. BSN is sensitive PII under GDPR (special category if linked to medical data).
- **CVSS 3.1:** 7.5 (AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
- **Remediation:** Encrypt the `bsn` field at application level using `cryptography.fernet` with a separate encryption key. Decrypt only when displaying to authorized users. Consider using SQLAlchemy custom type decorators.

### 🟠 HIGH

#### H-01: No Password Policy
- **Location:** `backend/schemas/user.py:5-7`
- **Description:** `password: str` has no minimum length, complexity, or character restrictions.
- **Impact:** Users can choose weak passwords like `"123"` or `"password"`, making brute-force and credential-stuffing attacks trivial.
- **CVSS 3.1:** 6.8 (AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
- **Remediation:** Add Pydantic validators: minimum 8 characters, require at least one uppercase, one lowercase, one digit. Enforce on registration and password change.

#### H-02: No Account Lockout
- **Location:** `backend/services/auth_service.py:62-68`
- **Description:** Failed login attempts are not tracked. An attacker can make unlimited login attempts.
- **Impact:** Combined with C-04 (no rate limiting), an attacker can brute-force passwords indefinitely.
- **CVSS 3.1:** 6.5 (AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
- **Remediation:** Track failed attempts in the database (`User.failed_login_attempts`, `User.locked_until`). Lock account after 5 failed attempts for 15 minutes.

#### H-03: Token in WebSocket URL
- **Location:** `frontend/src/stores/locks.js:15`, `backend/routers/websocket.py:11`
- **Description:** JWT token is passed as a URL path parameter: `/ws/{token}`. URLs are commonly logged by web servers, proxies, and browsers; stored in browser history; and leaked via `Referer` headers.
- **Impact:** JWT token (valid for 60 minutes) can be leaked through server logs, browser history, or `Referer` headers to third-party resources.
- **CVSS 3.1:** 7.5 (AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N)
- **Remediation:** Pass the token via WebSocket sub-protocol header (`Sec-WebSocket-Protocol`) or as a query parameter with `SameSite` considerations, or implement a short-lived WebSocket-specific token.

#### H-04: No Token Revocation
- **Location:** `backend/services/auth_service.py:33-38` (`decode_token`)
- **Description:** JWT tokens cannot be invalidated server-side. A stolen token is valid until expiration (60 minutes for access, 7 days for refresh).
- **Impact:** If a token is stolen (via XSS, MITM, or WebSocket URL leak), the attacker can use it for up to 60 minutes (access) or 7 days (refresh) with no way to revoke it.
- **CVSS 3.1:** 7.4 (AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N)
- **Remediation:** Maintain a token blacklist (Redis or database table) for revoked tokens. Check the blacklist on every authenticated request. Alternatively, use short-lived access tokens (5 minutes) with refresh token rotation.

#### H-05: SQLite in Production
- **Location:** `backend/config.py:5`
- **Description:** `DATABASE_URL = "sqlite+aiosqlite:///./patienten.db"` — SQLite is used as the production database.
- **Impact:** (a) No concurrent write access — serializes all writes. (b) No access controls — anyone with filesystem access can read the entire database file including password hashes and BSN numbers. (c) No encryption at rest. (d) Limited scalability.
- **CVSS 3.1:** 7.1 (AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
- **Remediation:** Migrate to PostgreSQL for production. Use encrypted volumes. At minimum, set restrictive file permissions (0600) on the database file and ensure it is outside the web root.

#### H-06: No Content Security Policy
- **Location:** `backend/main.py` — no CSP middleware
- **Description:** No `Content-Security-Policy` header is set on any response.
- **Impact:** If an XSS vulnerability exists, the attacker can execute arbitrary JavaScript. No protection against data exfiltration via inline scripts.
- **CVSS 3.1:** 6.1 (AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:N)
- **Remediation:** Implement a strict CSP via FastAPI middleware or at the reverse proxy level: `default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self' ws:; form-action 'self'`.

#### H-07: Missing Security HTTP Headers
- **Location:** `backend/main.py` — no security headers middleware
- **Description:** The following headers are absent:
  - `Strict-Transport-Security` (HSTS)
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `Referrer-Policy: strict-origin-when-cross-origin`
  - `Permissions-Policy` (formerly Feature-Policy)
  - `X-XSS-Protection` (deprecated but still used by older browsers)
- **Impact:** Increased attack surface for clickjacking, MIME-type confusion, referrer leakage.
- **CVSS 3.1:** 5.3 (AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:N)
- **Remediation:** Add a FastAPI middleware that sets all security headers on every response.

#### H-08: All Users Can List All Patients
- **Location:** `backend/routers/patients.py:19-24`
- **Description:** `GET /api/patients` returns every patient in the system with no access scoping. The overview endpoints (`/api/dsm5/status/all`, `/api/kindcheck/status/all`) also include BSN numbers.
- **Impact:** Any authenticated user (including a newly registered attacker) can dump the entire patient directory including BSN numbers, addresses, and phone numbers.
- **CVSS 3.1:** 6.5 (AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
- **Remediation:** Remove BSN from overview endpoints. Implement data scoping so users only see patients they are responsible for (via a `user_patients` association table if needed).

#### H-09: Audit Log Shows User ID, Not Display Name
- **Location:** `backend/routers/audit.py`, `frontend/src/views/AuditLogView.vue:113`
- **Description:** The audit log displays `changed_by` as a numeric user ID (e.g., `1`, `2`), not the human-readable `display_name`.
- **Impact:** Audit logs are less useful for non-technical users. This reduces accountability.
- **CVSS 3.1:** 3.5 (AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:N/A:N)
- **Remediation:** Join with `users` table in the audit query to return `display_name`. Update `AuditLogOut` schema to include `changed_by_name`.

### 🟡 MEDIUM

#### M-01: No CSRF Protection
- **Location:** Global frontend
- **Description:** The frontend uses Bearer tokens (not cookie-based auth), which partially mitigates CSRF. However, no CSRF tokens are implemented.
- **Impact:** Low in current architecture since Bearer tokens are not automatically sent by browsers. But if any endpoint were to accept cookie-based auth in the future, this would become critical.
- **Remediation:** Implement double-submit cookie pattern or `SameSite=Strict` cookies if cookie-based auth is ever introduced.

#### M-02: No `.env.example` Committed
- **Location:** Project root
- **Description:** No `.env.example` file documents the required environment variables. New developers/deployers may miss setting `SECRET_KEY`, `DATABASE_URL`, etc.
- **Remediation:** Create `.env.example` with all required variables and documentation comments.

#### M-03: No Input Sanitization on Text Fields
- **Location:** All schema input fields accept raw strings
- **Description:** Pydantic schemas validate types but do not sanitize or strip HTML/script content from text fields like `notities`, `conclusie`, `opmerking*`, etc.
- **Impact:** If any field is rendered via `v-html` instead of `{{ }}` interpolation (or if a future change introduces this), stored XSS is possible.
- **Remediation:** Use Pydantic validators to strip HTML tags from text fields. Never render user content with `v-html` — use `{{ }}` interpolation (Vue auto-escapes).

#### M-04: Kindcheck Children Replace Not Atomic
- **Location:** `backend/services/kindcheck_service.py:71-84`
- **Description:** `_replace_kinderen()` deletes all existing children then inserts new ones. If the server crashes between delete and insert, data loss occurs.
- **Impact:** Partial data loss of children records during concurrent update or server failure.
- **Remediation:** Wrap the delete+insert in a database transaction (use `async with db.begin_nested()` for a savepoint).

#### M-05: Patient Delete Lacks Lock Check
- **Location:** `backend/routers/patients.py:70-84`
- **Description:** `DELETE /api/patients/{patient_id}` does not check whether the record is currently locked by another user. A record can be deleted while someone is editing it.
- **Impact:** Data loss — user A is editing a patient while user B deletes it. User A's save will fail (404) but their work is lost.
- **Remediation:** Check lock status before delete. Return `423 Locked` if the record is locked by another user.

#### M-06: DSM-5/Kindcheck Delete Lacks Lock Check
- **Location:** `backend/routers/dsm5.py:78-92`, `backend/routers/kindcheck.py:88-102`
- **Description:** Same vulnerability as M-05 for DSM-5 and Kindcheck delete endpoints.
- **Remediation:** Same as M-05 — check lock before delete.

#### M-07: JWT `sub` Not Validated as Integer
- **Location:** `backend/services/auth_service.py:45`
- **Description:** `user_id = int(payload["sub"])` — The code blindly casts to int without validating that `sub` is a numeric string. A malformed or maliciously crafted token could cause a `ValueError`.
- **Impact:** Potential denial of service (500 error) or, if combined with a type confusion vulnerability, could lead to authorization bypass.
- **Remediation:** Validate `sub` is a digit string before casting. Wrap in try/except.

### 🟢 LOW

#### L-01: Verbose Error Messages
- **Location:** Various backend endpoints
- **Description:** Error messages in Dutch are user-friendly but may leak implementation details. For example, "Gebruikersnaam bestaat al" reveals whether a username is registered.
- **Impact:** Enables username enumeration for targeted attacks.
- **Remediation:** Return generic error messages on login failure ("Ongeldige gebruikersnaam of wachtwoord" — already done for login, but register and other endpoints should also be generic).

#### L-02: No Logout Everywhere
- **Location:** `backend/routers/auth.py`
- **Description:** No "logout everywhere" endpoint exists. Users cannot invalidate all their sessions.
- **Impact:** If a user suspects their account is compromised, they cannot force all sessions to log out.
- **Remediation:** Implement a token blacklist and a `POST /api/auth/logout-all` endpoint.

#### L-03: `beforeUnload` Relies on `keepalive` Fetch
- **Location:** `frontend/src/stores/locks.js:91-95`
- **Description:** The `releaseAllLocks()` function uses `fetch()` with `keepalive: true` to release locks on page close. `keepalive` fetches are unreliable in some browsers and may not complete if the browser tab is killed.
- **Impact:** Locks may be held after a user closes their browser tab, requiring the 5-minute timeout to expire.
- **Remediation:** Use `navigator.sendBeacon()` instead of `fetch()` with `keepalive` for more reliable delivery.

#### L-04: No Database Access Controls on SQLite File
- **Location:** `backend/patienten.db` (runtime)
- **Description:** The SQLite database file is stored directly in the backend directory with default filesystem permissions.
- **Impact:** Any user or process on the server with filesystem access can read/write the database directly, bypassing all application-level security.
- **Remediation:** Set file permissions to `0600` (owner read/write only). Store outside web root. Implement filesystem-level access controls.

---

## 4. OWASP Top 10 (2021) Mapping

| OWASP Category | Related Findings |
|---|---|
| **A01: Broken Access Control** | C-06, H-08, H-09, M-05, M-06 |
| **A02: Cryptographic Failures** | C-01, C-07, H-05 |
| **A03: Injection** | M-03 (XSS), M-07 (type confusion) |
| **A04: Insecure Design** | C-04, C-05, H-01, H-02, H-04 |
| **A05: Security Misconfiguration** | C-02, C-03, H-06, H-07, M-02 |
| **A06: Vulnerable Components** | (Not assessed — dependency audit needed) |
| **A07: Identification/Auth Failures** | C-04, C-05, H-01, H-02, H-03, H-04, L-02 |
| **A08: Software/Data Integrity** | M-04 |
| **A09: Security Logging/Monitoring** | (No monitoring/alerting at all) |
| **A10: Server-Side Request Forgery** | (Not applicable) |

---

## 5. Remediation Roadmap

### 🚨 Immediate (Week 1 — must fix before internet exposure)

| ID | Action | Effort | Impact |
|---|---|---|---|
| C-02 | Remove hardcoded default SECRET_KEY, fail if unset | 30 min | Prevents trivial JWT forgery |
| C-03 | Replace CORS `*` with explicit origins | 30 min | Prevents credential theft via CORS |
| C-05 | Disable open registration or add invite-only | 1 hr | Prevents unauthorized system access |
| C-01 | Set up HTTPS with nginx/caddy + Let's Encrypt | 2 hr | Encrypts all traffic |
| H-03 | Move WebSocket token from URL to sub-protocol header | 1 hr | Prevents token leakage |
| H-06 | Add CSP header middleware | 1 hr | Mitigates XSS impact |
| H-07 | Add security headers middleware | 30 min | Hardens against clickjacking/MIME |

### 📅 Short-term (Month 1)

| ID | Action | Effort |
|---|---|---|
| C-06 | Implement RBAC (admin/user roles) | 2 days |
| C-04 | Add rate limiting to auth endpoints | 4 hr |
| C-07 | Encrypt BSN at rest | 1 day |
| H-01 | Add Pydantic password validators | 1 hr |
| H-02 | Implement account lockout | 4 hr |
| H-04 | Add token blacklist/revocation | 1 day |
| M-01 | Verify CSRF posture, add SameSite cookies | 2 hr |
| M-05 | Add lock checks to delete endpoints | 2 hr |
| M-06 | Add lock checks to DSM-5/Kindcheck deletes | 2 hr |

### 📆 Medium-term (Quarter 1)

| ID | Action | Effort |
|---|---|---|
| H-05 | Migrate from SQLite to PostgreSQL | 3 days |
| H-08 | Implement patient data scoping | 2 days |
| H-09 | Show display names in audit log | 4 hr |
| M-03 | Add input sanitization validators | 1 day |
| M-04 | Wrap kindcheck child replace in transaction | 2 hr |
| M-07 | Validate JWT `sub` payload | 30 min |
| L-01 | Review and fix verbose error messages | 2 hr |
| L-02 | Add logout-all endpoint | 2 hr |
| L-03 | Switch `fetch(keepalive)` to `sendBeacon()` | 1 hr |
| L-04 | Harden SQLite file permissions | 30 min |
| M-02 | Create `.env.example` | 30 min |

### 🏛️ Long-term (Quarter 2+)

| Action | Description |
|---|---|
| **Penetration Testing** | Third-party security audit of the deployed system |
| **Dependency Scanning** | Regular `pip audit` / `npm audit` / SBOM generation |
| **Security Monitoring** | Centralized logging, alerting, IDS |
| **Incident Response Plan** | Document procedure for security breaches |
| **Data Protection Impact Assessment** | Required under GDPR for medical data processing |
| **Bug Bounty Program** | Formalize researcher rewards |

---

## 6. Responsible Disclosure Policy

### 6.1 Scope

This policy applies to the Patiëntenbeheer application and all its components:

- The FastAPI backend (Python)
- The Vue 3 frontend (JavaScript)
- Deployment scripts and configuration
- The SQLAlchemy database layer

### 6.2 Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it privately.

**Contact:** `[PLEASE INSERT SECURITY CONTACT EMAIL]`

**PGP Key:** `[PLEASE INSERT PGP KEY FINGERPRINT AND LINK]`

**Alternative:** If an email contact is not available, please file an issue on the project repository with `[SECURITY]` in the title and mark it as confidential if the platform supports it.

### 6.3 What to Include

When reporting, please include:

- **Type** of vulnerability (XSS, SQLi, IDOR, etc.)
- **Affected** endpoint/component and file path
- **Steps** to reproduce (conceptual is fine, avoid data exfiltration in proof of concept)
- **Potential** impact
- **Suggested** remediation (optional)

### 6.4 Expectations

- **Acknowledgment** within 3 business days
- **Initial assessment** within 5 business days
- **Fix timeline** communicated within 10 business days
  - CRITICAL/HIGH: targeted fix within 7 days
  - MEDIUM/LOW: targeted fix within 30 days
- **Disclosure coordination**: We will coordinate public disclosure with you. Default is 90 days after fix release.

### 6.5 Safe Harbor

We will not pursue legal action against researchers who:

- Follow this disclosure policy
- Make a good-faith effort to avoid privacy violations, data destruction, and service interruption
- Do not access or modify data beyond what is necessary to demonstrate the vulnerability
- Report findings privately first

### 6.6 Bounty Program

At this time, the project does not offer a formal bug bounty program. We may offer acknowledgment in our release notes at the researcher's discretion.

### 6.7 Out of Scope

- Physical attacks against servers/hardware
- Social engineering attacks against project staff
- Denial of service attacks
- Already-known vulnerabilities listed in this document

---

## 7. Security Checklist

### 7.1 Pre-Deployment Checklist

| Item | Done? |
|---|---|
| Default SECRET_KEY removed, `.env` enforced | ☐ |
| HTTPS/TLS configured with valid certificate | ☐ |
| CORS restricted to specific origins | ☐ |
| Registration disabled or invite-only | ☐ |
| Rate limiting configured on auth endpoints | ☐ |
| CSP and security headers added | ☐ |
| BSN encryption implemented | ☐ |
| Database migrated to PostgreSQL | ☐ |
| RBAC roles implemented | ☐ |
| Password policy enforced | ☐ |
| Account lockout configured | ☐ |
| WebSocket token moved from URL | ☐ |
| Token revocation/blacklist active | ☐ |
| Lock checks on all delete endpoints | ☐ |
| All inputs sanitized | ☐ |
| Audit logs show display names | ☐ |
| Security headers verified with `securityheaders.com` | ☐ |
| `.env.example` created | ☐ |

### 7.2 Annual Audit Checklist

| Item | Frequency |
|---|---|
| Dependency vulnerability scan (`pip audit`, `npm audit`) | Monthly |
| Penetration test | Annually |
| User access review | Quarterly |
| Token/key rotation | Annually |
| Incident response drill | Annually |
| GDPR compliance review | Annually |

---

*This security audit was performed on June 20, 2026. All findings are based on source code review of the committed codebase. Findings are reported in good faith to improve the security posture of the system.*
