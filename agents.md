# Plan — Patiëntenbeheer met DSM-5 en Audit

## Overzicht

Full-stack app met 3 modules (Patiëntgegevens, DSM-5 Formulier, Audit) in het
Nederlands, met gebruikersauthenticatie en lock-based realtime samenwerking.

when user1 edits page, user 2 should see information but read-only
when user1 saves page, user 2 should see latest information and is able to edit

---

## Tech Stack

| Laag       | Keuze                              |
| ---------- | ---------------------------------- |
| Backend    | Python **FastAPI** (async + WSS)   |
| Frontend   | **Vue 3** (Composition API) + Pinia + Vue Router |
| Database   | **SQLite** via SQLAlchemy + aiosqlite |
| Auth       | JWT (access + refresh tokens)      |
| Realtime   | FastAPI WebSocket                  |

---

## Database Schema (SQLite)

### `users`
| Kolom         | Type         | Opmerking          |
|---------------|--------------|--------------------|
| id            | INTEGER PK   |                    |
| username      | TEXT UNIQUE  |                    |
| password_hash | TEXT         | bcrypt             |
| display_name  | TEXT         |                    |
| created_at    | TIMESTAMP    |                    |
| last_login    | TIMESTAMP    |                    |

### `patients`
| Kolom        | Type             | Opmerking               |
|--------------|------------------|-------------------------|
| id           | INTEGER PK       |                         |
| voornaam     | TEXT             |                         |
| achternaam   | TEXT             |                         |
| geboortedatum| DATE             |                         |
| bsn          | TEXT UNIQUE      | Burgerservicenummer     |
| adres        | TEXT             |                         |
| postcode     | TEXT             |                         |
| woonplaats   | TEXT             |                         |
| telefoon     | TEXT             |                         |
| email        | TEXT             |                         |
| notities     | TEXT             |                         |
| created_at   | TIMESTAMP        |                         |
| updated_at   | TIMESTAMP        |                         |
| created_by   | INTEGER FK→users |                         |
| updated_by   | INTEGER FK→users |                         |

### `dsm5_forms`
| Kolom       | Type             | Opmerking              |
|-------------|------------------|------------------------|
| id          | INTEGER PK       |                        |
| patient_id  | INTEGER FK→patients |                    |
| status      | TEXT             | 'concept', 'definitief'|
| dimensies   | JSON             | Scores per DSM-5-dimensie |
| criteria_a_t/m_e | TEXT/JSON  | Per criterium          |
| conclusie   | TEXT             |                        |
| created_at  | TIMESTAMP        |                        |
| updated_at  | TIMESTAMP        |                        |
| created_by  | INTEGER FK→users |                        |
| updated_by  | INTEGER FK→users |                        |

### `audit_logs`
| Kolom       | Type         | Opmerking               |
|-------------|--------------|-------------------------|
| id          | INTEGER PK   |                         |
| table_name  | TEXT         | 'patients' of 'dsm5_forms' |
| record_id   | INTEGER      | ID van gewijzigd record |
| action      | TEXT         | CREATE / UPDATE / DELETE |
| old_values  | TEXT         | JSON                    |
| new_values  | TEXT         | JSON                    |
| changed_by  | INTEGER FK→users |                    |
| changed_at  | TIMESTAMP    |                         |
| ip_address  | TEXT         |                         |

### `record_locks`
| Kolom      | Type         | Opmerking          |
|------------|--------------|--------------------|
| id         | INTEGER PK   |                    |
| table_name | TEXT         |                    |
| record_id  | INTEGER      |                    |
| locked_by  | INTEGER FK→users |                |
| locked_at  | TIMESTAMP    |                    |
| expires_at | TIMESTAMP    | Timeout na 5 min   |

---

## Frontend Routes (Vue 3)

| Pad                    | Component            | Beschrijving                |
| ---------------------- | -------------------- | --------------------------- |
| `/login`               | LoginView            | Inloggen                    |
| `/`                    | DashboardView        | 3 grote knoppen             |
| `/patienten`           | PatientListView      | Overzicht patiënten         |
| `/patienten/:id`       | PatientDetailView    | Bewerken (lock)             |
| `/patienten/:id/dsm5`  | Dsm5FormView         | DSM-5 formulier (lock)      |
| `/audit`               | AuditLogView         | Filterbaar overzicht        |
| `/audit/:id`           | AuditDetailView      | Detail van wijziging        |

---

## Realtime lock-systeem

1. Gebruiker A opent `/patienten/1` → POST `/api/lock` → lock aangemaakt
2. Gebruiker B opent zelfde pagina → GET `/api/lock/patienten/1` → **locked
   door A**
3. Frontend B toont *"Alleen-lezen — Gebruiker A bewerkt dit"* + disabled
   velden
4. WebSocket push naar B als A opslaat (auto-refresh data)
5. **Timeout**: lock vervalt na 5 minuten inactiviteit; heartbeat elke 30s

---

## Audit logging

- SQLAlchemy `after_update` / `after_insert` event handlers schrijven
  automatisch naar `audit_logs`
- Alleen daadwerkelijke wijzigingen (diff) worden gelogd
- Audit-pagina: zoeken op datum, gebruiker, tabel, actie

---

## API Endpoints

### Auth
- `POST /api/auth/register`  — Registreren
- `POST /api/auth/login`     — Inloggen → JWT
- `POST /api/auth/refresh`   — Token verlengen

### Patiënten
- `GET    /api/patients`       — Lijst (zoek/filter)
- `GET    /api/patients/{id}`  — Detail
- `POST   /api/patients`       — Aanmaken
- `PUT    /api/patients/{id}`  — Bewerken
- `DELETE /api/patients/{id}`  — Verwijderen (zacht)

### DSM-5
- `GET  /api/dsm5/{patient_id}`    — Formulier ophalen
- `POST /api/dsm5/{patient_id}`    — Aanmaken/opslaan
- `PUT  /api/dsm5/{id}`            — Bijwerken

### Locks
- `POST   /api/lock`                         — Lock aanvragen
- `DELETE /api/lock/{id}`                    — Lock vrijgeven
- `GET    /api/lock/{table}/{record_id}`     — Lock status

### Audit
- `GET /api/audit`         — Lijst met filters
- `GET /api/audit/{id}`    — Detail

### WebSocket
- `ws://host/ws/{token}`   — Lock-updates + data refreshes

---

## Directory structuur

```
Patient/
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── patient.py
│   │   ├── dsm5_form.py
│   │   ├── audit_log.py
│   │   └── record_lock.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── patient.py
│   │   ├── dsm5_form.py
│   │   └── audit.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── patients.py
│   │   ├── dsm5.py
│   │   ├── locks.py
│   │   └── audit.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── patient_service.py
│   │   ├── dsm5_service.py
│   │   ├── lock_service.py
│   │   └── audit_service.py
│   ├── websocket/
│   │   ├── __init__.py
│   │   └── manager.py
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── auth_middleware.py
│   │   └── audit_middleware.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.js
│   │   ├── router/index.js
│   │   ├── stores/
│   │   │   ├── auth.js
│   │   │   ├── patients.js
│   │   │   ├── dsm5.js
│   │   │   ├── locks.js
│   │   │   └── audit.js
│   │   ├── views/
│   │   │   ├── LoginView.vue
│   │   │   ├── DashboardView.vue
│   │   │   ├── PatientListView.vue
│   │   │   ├── PatientDetailView.vue
│   │   │   ├── Dsm5FormView.vue
│   │   │   ├── AuditLogView.vue
│   │   │   └── AuditDetailView.vue
│   │   ├── components/
│   │   │   ├── NavBar.vue
│   │   │   ├── PatientForm.vue
│   │   │   ├── Dsm5Formulier.vue
│   │   │   ├── AuditTable.vue
│   │   │   ├── ReadOnlyOverlay.vue
│   │   │   └── LoadingSpinner.vue
│   │   ├── composables/
│   │   │   ├── useAuth.js
│   │   │   ├── useWebSocket.js
│   │   │   └── useLock.js
│   │   └── assets/
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
└── agents.md
```

---

## Implementatievolgorde

| Fase | Onderdeel |
|------|-----------|
| 1 | Backend: project setup, database, modellen |
| 2 | Backend: auth (registreren, inloggen, JWT) |
| 3 | Backend: patients CRUD + audit logging |
| 4 | Backend: DSM-5 CRUD + audit logging |
| 5 | Backend: lock-systeem + WebSocket |
| 6 | Frontend: project setup, router, Pinia |
| 7 | Frontend: loginpagina + auth store |
| 8 | Frontend: dashboard met 3 knoppen |
| 9 | Frontend: patiëntenlijst + detail + formulier |
| 10 | Frontend: DSM-5 formulier |
| 11 | Frontend: lock-integratie (read-only overlay) |
| 12 | Frontend: auditpagina |
| 13 | Testen + finetunen |
