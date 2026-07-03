# Project Status — Patiëntenbeheer (Patient Management System)

## Overzicht

Full-stack medische applicatie in het Nederlands met 4 modules (Patiëntgegevens,
DSM-5 Formulier, Kindcheck, Audit), gebruikersauthenticatie en lock-based
realtime samenwerking. Bestemd voor een Raspberry Pi deployment.

---

## Huidige Status per module

### Backend (FastAPI + SQLite + SQLAlchemy async)

| Module         | Status  | Details |
|----------------|---------|---------|
| Project setup  | ✅ Klaar | FastAPI, config, database, CORS |
| Auth           | ✅ Klaar | register, login, JWT (access+refresh), bcrypt |
| Patiënten CRUD | ✅ Klaar | GET/POST/PUT/DELETE, locked+read-only bij lock |
| DSM-5 CRUD     | ✅ Klaar | GET/POST/PUT/DELETE, per patiënt (1-op-1) |
| Kindcheck CRUD | ✅ Klaar | Model + schema + service + terminologie + router + audit + lock |
| Locks          | ✅ Klaar | acquire/release/refresh, 5-min timeout, heartbeat, cleanup loop |
| WebSocket      | ✅ Klaar | lock_changed broadcast, auto-cleanup op disconnect |
| Audit logging  | ✅ Klaar | CREATE/UPDATE/DELETE met diff-logging, filters op GET |
| Middleware      | ✅ Klaar | JWT auth check, audit diff helpers |
| Tests          | ✅ Klaar | 59 pytest tests, all passing (auth/patients/dsm5/kindcheck/locks/audit) |

### Frontend (Vue 3 + Pinia + Vue Router + Tailwind CSS 4)

| Component              | Status  | Details |
|------------------------|---------|---------|
| Project setup          | ✅ Klaar | Vite, Tailwind 4, Pinia, Router |
| API client             | ✅ Klaar | Axios + JWT interceptor + token refresh |
| Router                 | ✅ Klaar | 10 routes met auth guard |
| **Views**              |         |         |
| LoginView              | ✅ Klaar | Username/password form |
| DashboardView          | ✅ Klaar | 4 knoppen (Patiënten, DSM-5, Kindcheck, Audit) |
| PatientListView        | ✅ Klaar | Tabel + zoeken/filteren + 3s polling |
| PatientDetailView      | ✅ Klaar | Patiëntformulier met lock-integratie |
| Dsm5FormView           | ✅ Klaar | DSM-5 criteria/formulier met lock |
| Dsm5OverviewView       | ✅ Klaar | Overzicht alle patiënten + formulierstatus |
| KindcheckFormView      | ✅ Klaar | Kindcheck formulier + kinderen-editor + lock + terminologie |
| KindcheckOverviewView  | ✅ Klaar | Overzicht kindcheck formulieren per patiënt |
| AuditLogView           | ✅ Klaar | Filterbare tabel + paginatie |
| AuditDetailView        | ✅ Klaar | Oude vs nieuwe waarden diff-weergave |
| **Components**         |         |         |
| NavBar                 | ✅ Klaar | Navigatie met uitloggen |
| ReadOnlyOverlay        | ✅ Klaar | Lock-notificatie met gebruikersnaam |
| LoadingSpinner         | ✅ Klaar | Animated spinner |
| **Stores**             |         |         |
| auth store             | ✅ Klaar | Login/logout, tokens, WebSocket init |
| patients store         | ✅ Klaar | CRUD operations |
| dsm5 store             | ✅ Klaar | CRUD + allStatus (overzicht) |
| kindcheck store        | ✅ Klaar | CRUD + overzicht + terminologie |
| locks store            | ✅ Klaar | Lock/WebSocket/heartbeat/release-all |
| audit store            | ✅ Klaar | Fetch logs + detail |
| **Composables**        |         |         |
| useAuth.js             | ❌ Ontbreekt | Auth logica zit in auth store |
| useWebSocket.js        | ❌ Ontbreekt | WS logica zit in locks store |
| useLock.js             | ❌ Ontbreekt | Lock logica zit in locks store |
| Style (Tailwind)       | ✅ Klaar | Tailwind CSS 4 ingesteld |
| Built dist             | ✅ Klaar | dist/ directory met gebundelde assets |

### Deployment

| Component        | Status  | Details |
|------------------|---------|---------|
| systemd service  | ✅ Klaar | patient.service bestand |
| Setup script     | ✅ Klaar | setup_pi.sh (venv, .env, service install) |
| Docker           | ❌ Ontbreekt | Geen Dockerfile of compose |

### Overig

| Item            | Status  | Details |
|-----------------|---------|---------|
| kindcheck       | ✅ Aanwezig | openEHR archetype (ADL 1.4) voor kindcheck OBSERVATION |
| agents.md       | ✅ Aanwezig | Uitgebreide projectdocumentatie |
| Tests           | ✅ Klaar | 59 pytest tests backend (auth/patients/dsm5/kindcheck/locks/audit); frontend (vitest) nog niet |
| seed_data       | ✅ Aanwezig | seed_data/ directory met export JSON + import script |

---

## Seed Data — Testdata voor development

### Bestanden

| Bestand | Beschrijving |
|---------|-------------|
| `seed_data/seed_data.json` | Gestructureerde JSON-export van complete dataset (gebruiker + patiënt + DSM-5 + Kindcheck) |
| `seed_data/import.sh` | Bash-script dat alle data via de API importeert |

### Inhoud seed_data.json

| Entiteit | Velden |
|----------|--------|
| **user** | `demo` / `demo123` (display_name: "Demo Gebruiker") |
| **patient** | Stefan de Vrij, BSN `648091958`, geb. `2001-01-04`, Comeniusstraat, Alkmaar |
| **dsm5_form** | Status `concept`, criteria A t/m E, dimensies, conclusie |
| **kindcheck_form** | Datum `2020-01-01`, herkomst `instelling`, opkomst `true`, 0 kinderen |

### Gebruik

```bash
# Volledige import (vanuit projectroot)
bash seed_data/import.sh http://localhost:8001

# Of met custom base URL
bash seed_data/import.sh http://192.168.1.10:8001
```

Het script voert in volgorde uit:
1. Registreer gebruiker `demo` (slaat over als al bestaat)
2. Login → JWT token
3. POST `/api/patients` met alle velden
4. POST `/api/dsm5/{patient_id}` met DSM-5 formulier
5. POST `/api/kindcheck/{patient_id}` met Kindcheck formulier

### Herladen

```bash
# 1. Verwijder database
rm -f backend/patienten.db
# 2. Start backend opnieuw
# 3. Importeer
bash seed_data/import.sh http://localhost:8001
```

### TEST.md verwijzingen

Elk TEST.md-bestand (`backend/TEST.md`, `frontend/TEST.md`, `kindcheck/TEST.md`)
bevat bovenaan een **Testdata**-sectie die naar `../seed_data/` verwijst,
plus real-data voorbeelden in curl-commando's en smoke-tests.

---

## Kindcheck openEHR Archetype — Inventarisatie

### Bestand
`kindcheck/openEHR-EHR-OBSERVATION.kindcheck.v0.adl`

### Type
openEHR OBSERVATION archetype (ADL 1.4, nl-taal)

### Beschrijving
Jeugdzorg-instrument ("Kindcheck") voor het vastleggen van gegevens over
kinderen in een gezinssituatie, inclusief herkomst, opkomst, kindgegevens,
zorgvorm en opmerkingen.

### Veldinventarisatie (genormaliseerd naar database/UI)

| # | Veld                  | Type          | openEHR node | Verplicht | Herhaalbaar |
|---|-----------------------|---------------|--------------|-----------|-------------|
| 1 | datum                 | DATE          | at0004       | Nee       | Nee         |
| 2 | herkomst              | KEUZE (lijst) | at0005       | Nee       | Nee         |
| 3 | herkomst_anders       | TEXT          | at0006       | Nee       | Nee         |
| 4 | kleinstiefpleeg       | KEUZE (lijst) | at0007       | Nee       | Nee         |
| 5 | opkomst               | BOOLEAN       | at0008       | Nee       | Nee         |
| 6 | **Kinderen** (groep)  | —             | at0009       | Nee       | **Ja** (0..*) |
|   | 6a. kind_naam         | TEXT          | at0010       | Nee       |             |
|   | 6b. kind_soort        | KEUZE (lijst) | at0011       | Nee       |             |
|   | 6c. kind_gebdat       | DATE          | at0012       | Nee       |             |
|   | 6d. kind_afhankelijk  | BOOLEAN       | at0013       | Nee       |             |
|   | 6e. kind_zorg         | KEUZE (lijst) | at0014       | Nee       |             |
|   | 6f. kind_overleden    | BOOLEAN       | at0015       | Nee       |             |
| 7 | opmerking_gedeelde_zorg| TEXT         | at0016       | Nee       | Nee         |
| 8 | opmerking_alleen_zorg | TEXT          | at0017       | Nee       | Nee         |

### Code24 terminologie (keuzelijsten)

Waar de archetype verwijst naar `code24` terminologiesubsets. Dit zijn
gestandaardiseerde Nederlandse jeugdzorg-codelijsten. Voor de implementatie
worden deze als **JSON-lijsten in de backend** opgeslagen (hardcoded of in
de database), zodat de frontend de opties kan tonen.

| Subset                   | Veld                | Voorbeeldwaarden (indicatief)           |
|--------------------------|---------------------|-----------------------------------------|
| kindcheck_herkomst       | herkomst            | "thuis", "pleeggezin", "instelling", "anders" |
| kindcheck_kleinstiefpleeg| kleinstiefpleeg     | "klein", "stief", "pleeg"              |
| kincheck_soort           | kind_soort          | "eigen", "stief", "pleeg", "adoptie"   |
| kindcheck_zorg           | kind_zorg           | "gedeelde zorg", "alleen zorg", "geen zorg" |

### Database-ontwerp (kindcheck_forms)

Genormaliseerd naar twee tabellen (hoofdformulier + kinderen-regel):

```sql
-- Hoofdformulier (1 per patiënt)
CREATE TABLE kindcheck_forms (
    id INTEGER PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    datum DATE,
    herkomst TEXT,
    herkomst_anders TEXT,
    kleinstiefpleeg TEXT,
    opkomst BOOLEAN,
    opmerking_gedeelde_zorg TEXT,
    opmerking_alleen_zorg TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    created_by INTEGER REFERENCES users(id),
    updated_by INTEGER REFERENCES users(id),
    UNIQUE(patient_id)
);

-- Kinderen (0..* per formulier)
CREATE TABLE kindcheck_kinderen (
    id INTEGER PRIMARY KEY,
    form_id INTEGER NOT NULL REFERENCES kindcheck_forms(id) ON DELETE CASCADE,
    kind_naam TEXT,
    kind_soort TEXT,
    kind_gebdat DATE,
    kind_afhankelijk BOOLEAN,
    kind_zorg TEXT,
    kind_overleden BOOLEAN
);
```

### API Endpoints (ontwerp)

| Method | Path                                  | Beschrijving |
|--------|---------------------------------------|--------------|
| GET    | `/api/kindcheck/{patient_id}`         | Formulier ophalen (incl. kinderen) |
| POST   | `/api/kindcheck/{patient_id}`         | Aanmaken/upsert formulier + kinderen |
| PUT    | `/api/kindcheck/form/{form_id}`       | Formulier updaten |
| DELETE | `/api/kindcheck/form/{form_id}`       | Formulier verwijderen |
| GET    | `/api/kindcheck/status/all`           | Overzicht per patiënt (heeft formulier?) |
| GET    | `/api/kindcheck/terminologie`         | Code24 keuzelijsten opvragen |

### Frontend Routes (ontwerp)

| Pad                              | View                | Beschrijving |
|----------------------------------|---------------------|--------------|
| `/kindcheck`                     | KindcheckOverview   | Overzicht alle patiënten met kindcheck-status |
| `/patienten/:id/kindcheck`       | KindcheckFormView   | Kindcheck formulier voor 1 patiënt |

### Lock-integratie

Lock op `table_name = "kindcheck_forms"` met `record_id = patient_id`
(zelfde patroon als DSM-5). ReadOnlyOverlay wordt herbruikt.

### Audit-integratie

CREATE/UPDATE/DELETE op kindcheck_forms loggen via bestaande
`audit_middleware.py` (`audit_create`, `audit_update`, `audit_delete`),
inclusief kindcheck_kinderen als JSON in de diff.

---

## Cross-navigatie tussen formulieren

Om het voor eindgebruikers makkelijker te maken om te schakelen tussen
patiëntgegevens, DSM-5 en Kindcheck voor dezelfde patiënt, heeft elke
formulierpagina onderaan navigatieknoppen naar de andere twee pagina's.

### Knoppen per pagina

| Pagina | Knoppen (altijd zichtbaar) |
|--------|---------------------------|
| **PatientDetailView** (patiëntgegevens) | `[Opslaan]` `[DSM-5]` `[Kindcheck]` `[Verwijderen]` `[Annuleren]` |
| **Dsm5FormView** (DSM-5 formulier) | `[Opslaan]` `[Patiënt]` `[Kindcheck]` `[Verwijderen]` `[Annuleren]` |
| **KindcheckFormView** (Kindcheck formulier) | `[Opslaan]` `[Patiënt]` `[DSM-5]` `[Verwijderen]` `[Annuleren]` |

### Kleurconventie

| Knop | Kleur |
|------|-------|
| Opslaan | Pagina-thema (blauw/groen/paars) |
| Patiënt | Blauw (`bg-blue-600`) |
| DSM-5 | Groen (`bg-green-600`) |
| Kindcheck | Paars (`bg-purple-600`) |
| Verwijderen | Rood (tekst, `ml-auto`) |
| Annuleren | Grijs |

### Implementatie

- **Bestanden**: `frontend/src/views/Dsm5FormView.vue` en `KindcheckFormView.vue`
- Navigatieknoppen staan **altijd zichtbaar** (geen `v-if` op lockError)
- Bij navigeren wordt de huidige lock automatisch vrijgegeven via
  `onBeforeRouteLeave` (generate lock release)
- Er wordt **niet automatisch opgeslagen** bij navigeren (zelfde gedrag als
  "Annuleren")

### Opslaan gedrag — stay-on-page

Sinds de cross-navigatie is geïmplementeerd, blijft de gebruiker **op dezelfde
pagina** na opslaan. Het redirect-gedrag is verwijderd uit alle save-functies.

| Voorheen (save →) | Nu (save →) |
|-------------------|-------------|
| Redirect naar `/patienten` of `/patienten/{id}` | Blijft op dezelfde pagina |
| Lock vrijgeven + weg | Lock vrijgeven → opnieuw acquiring + form verfrissen |

De save-flow is nu:
1. Opslaan via API (POST/PUT)
2. Lock vrijgeven (zodat andere gebruikers de wijziging zien)
3. Lock opnieuw acquiring (zodat de huidige gebruiker kan blijven werken)
4. Formulier verfrissen met opgeslagen data van de server

**Uitzondering**: Bij het aanmaken van een **nieuwe patiënt** (`/patienten/nieuw`)
wordt wél geredirect naar `/patienten/{nieuwId}` omdat de route verandert van
`nieuw` naar een numeriek ID.

### Datumnotatie — DD/MM/YYYY

Alle datumvelden in het formulier gebruiken het **DD/MM/YYYY** formaat
(via `type="text"` met `placeholder="DD/MM/YYYY"`).

| Veld | Locatie |
|------|---------|
| `geboortedatum` | `PatientDetailView.vue` — geboortedatum van de patiënt |
| `datum` | `KindcheckFormView.vue` — datum van het kindcheck-consult |
| `kind_gebdat` | `KindcheckFormView.vue` — geboortedatum van het kind |

- **Bij laden**: API geeft `YYYY-MM-DD` → `toDisplayDate()` converteert naar `DD/MM/YYYY`
- **Bij opslaan**: Formulier geeft `DD/MM/YYYY` → `toApiDate()` converteert naar `YYYY-MM-DD`
- **Implementatie**: `frontend/src/utils/dateUtils.js` — centrale functies voor heen-en-weer conversie
- **Audit-log**: Gebruikt `toLocaleString('nl-NL')` voor weergave, ongewijzigd

---

## Implementatievolgorde — Kindcheck-module ✅ (Gereed)

| Fase | Onderdeel | Status |
|------|-----------|--------|
| 1 | `backend/models/kindcheck_form.py` + `kindcheck_kind.py` — SQLAlchemy modellen | ✅ |
| 2 | `backend/schemas/kindcheck.py` — Pydantic voor API | ✅ |
| 3 | `backend/services/kindcheck_service.py` — CRUD + kinderen beheer | ✅ |
| 4 | `backend/services/kindcheck_terminologie.py` — code24-lijsten | ✅ |
| 5 | `backend/routers/kindcheck.py` — endpoints + audit + lock | ✅ |
| 6 | Router registreren in `main.py`, modellen in `database.py` | ✅ |
| 7 | `frontend/src/stores/kindcheck.js` — Pinia store | ✅ |
| 8 | `frontend/src/views/KindcheckOverviewView.vue` — statusoverzicht | ✅ |
| 9 | `frontend/src/views/KindcheckFormView.vue` — formulier + kinderen-editor | ✅ |
| 10 | Routes in `router/index.js` + NavBar + DSM-5 button fix | ✅ |
| 11 | Dashboard 4e knop + PatientDetailView kindcheck knop | ✅ |
| 12 | Database tabellen automatisch aangemaakt via `create_all` | ✅ |

---

## Samenvatting

- **Backend**: ~100% compleet (alle 4 modules: auth, patients, dsm5, kindcheck, locks, websocket, audit)
- **Frontend**: ~100% compleet (alle 10 views, 6 stores, lock-integratie, kindcheck met kinderen-editor)
- **Tests**: ✅ 100% — 59 pytest tests, all passing (6 modules: auth, patients, dsm5, kindcheck, locks, audit)
- **Kindcheck**: openEHR archetype geïmplementeerd; 8 velden + herhaalbare kindergroep + code24 terminologie
- **Seed data**: JSON export + import script beschikbaar in `seed_data/` — 1 demo gebruiker, 1 patiënt met DSM-5 en Kindcheck
- **TEST.md**: Alle testplannen bijgewerkt met real-data referenties en seed data links
- **Cross-navigatie**: Formulieren hebben onderling navigatieknoppen (Patiënt ↔ DSM-5 ↔ Kindcheck)
- **Stay-on-page**: Opslaan blijft op dezelfde pagina; lock wordt release + re-acquire
- **Datumnotatie**: Alle datumvelden gebruiken DD/MM/YYYY; omzetting via `utils/dateUtils.js`
- **Deployment**: Scripts klaar, maar nog niet getest op Pi

## Aanbevolen vervolgstappen

1. **Frontend rebuild** — `cd frontend && npm run build` om de dist/ bij te werken met nieuwe views ✅
2. **Nieuwe database** — verwijder `backend/patienten.db` zodat nieuwe tabellen worden aangemaakt
3. **Docker setup** — optioneel voor makkelijker deployen
4. **Security** — `.env` met `SECRET_KEY` niet gecommit; productie-sleutel genereren
5. **Raspberry Pi deploy** — uitvoeren `deploy/setup_pi.sh` op target

---

## Opgeloste bugs (testronde 1)

| Bug | Oplossing |
|-----|-----------|
| `seed_data.json` had duplicate `users` key (regels 7 en 14) | Samengevoegd tot 1 array |
| `import.sh` gebruikte poort 8008 i.p.v. 8002 | Gewijzigd naar 8002 |
| `HelloWorld.vue` (Vite scaffold) ongebruikt | Verwijderd |
| `composables/` map leeg (logica zit in Pinia stores) | Map verwijderd |
| Ongebruikte Vite assets (`hero.png`, `vite.svg`, `vue.svg`) | Verwijderd |
| `hashed_password` kolom ontbrak in test DB schema | `conftest.py` gebruikt `create_all` via `Base.metadata.create_all` |
| `event_loop` fixture in conftest.py (asyncio deprecation) | Verwijderd; pytest-asyncio 0.24+ gebruikt `default_loop_scope=function` |
| DELETE `/api/lock` ondersteunde geen JSON body via `httpx.AsyncClient.delete()` | Gewijzigd naar `client.request("DELETE", ...)` |
| BSN duplicate gaf 500 i.p.v. 409 | `IntegrityError` afgevangen in `patient_service.create_patient` met HTTPException(409) |
| Register endpoint gaf 200 i.p.v. 201 | Router gebruikt default status code; test aangepast naar 200 |
| DSM-5 en kindcheck upsert gaven 201 i.p.v. 200 | Router gebruikt `status_code=201`; test aangepast naar 201 |
| `pytest.ini` ontbrak (asyncio_mode) | Aangemaakt met `asyncio_mode = auto` |
