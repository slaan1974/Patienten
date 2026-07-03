# Patiëntenbeheer — Patient Management System

Full-stack medische applicatie voor het beheren van patiëntgegevens, DSM-5 formulieren, Kindcheck formulieren en audit logging. Ontworpen voor een Raspberry Pi deployment met ondersteuning voor realtime samenwerking via lock-mechanisme en WebSocket.

## Modules

| Module | Beschrijving |
|--------|-------------|
| **Patiëntgegevens** | CRUD voor patiënten met zoeken/filteren, BSN, adres, contactgegevens |
| **DSM-5 Formulier** | Psychiatrisch beoordelingsformulier per patiënt (criteria A t/m E, dimensies, conclusie) |
| **Kindcheck** | Jeugdzorg-instrument voor kindgegevens met herhaalbare kinderen-editor en code24 terminologie |
| **Audit** | Wijzigingenlog met diff-weergave, filterbaar op tabel/actie/datum |

## Gebruik

### Snel starten (development)

```bash
# Backend
cd backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# Frontend (andere terminal)
cd frontend
npm run dev          # draait op http://localhost:8002
```

### Seed data laden

```bash
bash seed_data/import.sh http://localhost:8001
# Gebruiker: demo / demo123
```

### Productie (Raspberry Pi)

```bash
bash deploy/setup_pi.sh
# Draait op poort 8002 met systemd-service
```

## Technische stack

| Laag | Keuze |
|------|-------|
| Backend | Python FastAPI (async) + SQLAlchemy + SQLite |
| Frontend | Vue 3 + Pinia + Vue Router + Tailwind CSS 4 |
| Realtime | FastAPI WebSocket |
| Auth | JWT (access + refresh tokens, bcrypt) |

## API overzicht

### Auth
- `POST /api/auth/register` — Registreren
- `POST /api/auth/login` — Inloggen
- `POST /api/auth/refresh` — Token verversen

### Patiënten
- `GET /api/patients` — Lijst (zoeken/filteren)
- `GET /api/patients/{id}` — Detail
- `POST /api/patients` — Aanmaken
- `PUT /api/patients/{id}` — Bewerken
- `DELETE /api/patients/{id}` — Verwijderen

### DSM-5
- `GET /api/dsm5/{patient_id}` — Formulier ophalen
- `POST /api/dsm5/{patient_id}` — Aanmaken/bijwerken
- `PUT /api/dsm5/form/{form_id}` — Formulier updaten
- `DELETE /api/dsm5/form/{form_id}` — Verwijderen
- `GET /api/dsm5/status/all` — Overzicht per patiënt

### Kindcheck
- `GET /api/kindcheck/terminologie` — Code24 keuzelijsten
- `GET /api/kindcheck/{patient_id}` — Formulier ophalen
- `POST /api/kindcheck/{patient_id}` — Aanmaken/bijwerken
- `PUT /api/kindcheck/form/{form_id}` — Formulier updaten
- `DELETE /api/kindcheck/form/{form_id}` — Verwijderen
- `GET /api/kindcheck/status/all` — Overzicht per patiënt

### Locks
- `POST /api/lock` — Lock aanvragen
- `DELETE /api/lock` — Lock vrijgeven
- `GET /api/lock/{table}/{record_id}` — Lock status
- `POST /api/lock/release-all` — Alle locks vrijgeven
- `POST /api/lock/refresh` — Lock heartbeat

### Audit
- `GET /api/audit` — Lijst (met filters)
- `GET /api/audit/{id}` — Detail met diff

### WebSocket
- `ws://host/ws/{token}` — Lock-updates en data refreshes

## Realtime lock-systeem

Meerdere gebruikers kunnen tegelijk werken, maar slechts één gebruiker tegelijk bewerkt een record:

1. Gebruiker opent een formulier → lock wordt aangevraagd
2. Andere gebruikers zien een *"Alleen-lezen — [gebruiker] bewerkt dit"* melding
3. Bij opslaan krijgen andere gebruikers via WebSocket een melding en wordt hun data ververst
4. Lock vervalt na 5 minuten inactiviteit (heartbeat elke 30s)

## Datumnotatie

Alle datumvelden gebruiken **DD/MM/YYYY** formaat in de UI, met automatische conversie naar YYYY-MM-DD voor de API.

## Projectstructuur

```
Patient/
├── backend/          # FastAPI server
│   ├── main.py
│   ├── models/       # SQLAlchemy modellen
│   ├── schemas/      # Pydantic schemas
│   ├── routers/      # API endpoints
│   ├── services/     # Business logic
│   ├── middleware/    # JWT + audit middleware
│   └── websocket/    # WebSocket manager
├── frontend/         # Vue 3 SPA
│   └── src/
│       ├── views/    # Pagina's
│       ├── stores/   # Pinia stores
│       ├── components/
│       └── router/
├── deploy/           # Deployment scripts
│   ├── setup_pi.sh
│   └── patient.service
├── seed_data/        # Testdata
│   ├── seed_data.json
│   └── import.sh
└── kindcheck/        # openEHR archetype
```
# Patienten
