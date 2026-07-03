# Frontend Tests — Patiëntenbeheer UI

## Testdata

Seed data (1 demo gebruiker + 1 patiënt met DSM-5 + Kindcheck) staat in:

- **JSON export**: `../seed_data/seed_data.json`
- **Import script**: `../seed_data/import.sh`

### Voorbeelddata

| Entiteit | Gegevens |
|----------|----------|
| **Gebruiker** | `demo` / `demo123` |
| **Patiënt** | Stefan de Vrij, BSN `648091958`, geb. `2001-01-04`, Alkmaar |
| **DSM-5** | Status `concept`, criteria A t/m E gevuld, conclusie "Conclusie staat hier" |
| **Kindcheck** | Datum `2020-01-01`, herkomst `instelling`, opkomst `true`, 0 kinderen |

### Herladen van testdata

```bash
# 1. Stop backend, verwijder DB
rm -f backend/patienten.db
# 2. Start backend opnieuw
# 3. Importeer seed data
bash seed_data/import.sh http://localhost:8001
```

---

## Technische stack

- **Framework**: Vue 3 + Vite + Vitest (aan te raden)
- **Component tests**: Vitest + @vue/test-utils
- **E2E tests**: Playwright of Cypress (optioneel)
- **Status**: ✅ Plan gereed — testbestanden nog niet geschreven

---

## Testcategorieën

### 1. Unit tests — Pinia stores

Testen van store-logica zonder Vue componenten. Gebruik `vitest` met
`pinia` test helpers.

| Store        | Testcases |
|--------------|-----------|
| `auth.js`    | login slaat tokens op, logout wist tokens, isLoggedIn computed |
| `patients.js`| fetchPatients vult lijst, createPatient voegt toe, updatePatient vervangt, deletePatient verwijdert |
| `dsm5.js`    | fetchForm, saveForm (POST vs PUT), fetchAllStatus, deleteForm |
| `kindcheck.js`| fetchTerminologie, fetchForm, saveForm met kinderen, updateForm, deleteForm, fetchAllStatus |
| `locks.js`   | acquireLock (success + 423), releaseLock, releaseAllLocks, startHeartbeat, stopHeartbeat, lockChanges counter, WebSocket connect/disconnect |
| `audit.js`   | fetchLogs met params, fetchLog detail |

### 2. Component tests — Vue components

Testen van rendering en gebruikersinteractie met `@vue/test-utils`.

| Component          | Testcases |
|--------------------|-----------|
| `NavBar.vue`       | Toon navigatie voor ingelogde gebruiker, verberg op loginpagina, active class voor huidige route, uitloggen roept auth.logout() aan |
| `ReadOnlyOverlay.vue` | Toont gebruikersnaam in boodschap, correcte styling bij locked-by-name prop |
| `LoadingSpinner.vue` | Toont meegegeven text prop, toont spinner SVG |
| `LoginView.vue`    | Form submit roept auth.login() aan, toon foutmelding bij mislukte login, knop disabled tijdens laden |
| `DashboardView.vue`| 4 knoppen met correcte router-pushes |
| `PatientListView.vue` | Toont tabel met patiënten, zoekfilter werkt, polling start/stopt, "Nieuwe patiënt" knop |
| `PatientDetailView.vue` | Form gevuld met data, lock-acquire bij mount, lock-release bij verlaten, opslaan/disabled bij lockError, verwijderen met confirm, geboortedatum in DD/MM/YYYY formaat met heen-en-weer conversie |
| `Dsm5FormView.vue` | Formulier geladen met bestaande data, lock op dsm5_forms, save roept saveForm aan, navigatieknoppen "Patiënt" en "Kindcheck" zichtbaar |
| `Dsm5OverviewView.vue` | Toont allStatus tabel, filter met/zonder formulier, statusBadge toont correct label |
| `KindcheckOverviewView.vue` | Toont allStatus tabel, filter met/zonder formulier, status badge |
| `KindcheckFormView.vue` | Formulier geladen met bestaande data, kinderen worden getoond, kind toevoegen/verwijderen werkt, lock op kindcheck_forms, terminologie ingeladen in selects, save met children array, navigatieknoppen "Patiënt" en "DSM-5" zichtbaar, datum en kind_gebdat in DD/MM/YYYY formaat met heen-en-weer conversie |
| `AuditLogView.vue` | Filters werken, paginatie knoppen, actie badges correcte kleur |
| `AuditDetailView.vue` | Toont log data, oude vs nieuwe waarden, JSON parsing |

### 3. Integration tests — Store + API

Testen of stores correct communiceren met de (gemockte) API.

| Scenario | Beschrijving |
|----------|--------------|
| Login flow | auth.login() → API call → token opgeslagen → WebSocket verbonden |
| Lock flow | acquireLock → POST /api/lock → lockStatus update → heartbeat start |
| Lock conflict | acquireLock → 423 → lockStatus toont locked info |
| Lock release | releaseLock → DELETE /api/lock → lockStatus.reset → heartbeat stop |
| Patient CRUD | create → lijst geüpdatet, update → item vervangen, delete → item verwijderd |
| DSM-5 save | saveForm → POST/PUT afhankelijk of formId bestaat |
| Kindcheck save | saveForm → POST met kinderen array, children worden naar API gestuurd |
| Kindcheck terminologie | fetchTerminologie → 4 code24 lijsten beschikbaar in store |
| Datum conversie | toDisplayDate("2020-01-04") → "04-01-2020", toApiDate("04-01-2020") → "2020-01-04" |
| Audit fetch | fetchLogs met filter params → correcte API call |

### 4. E2E tests (optioneel — Playwright)

Volledige browser tests met een draaiende backend.

| Scenario | Beschrijving |
|----------|--------------|
| Volledige login | Open /login → vul form in → submit → redirect naar / |
| Navigatie | Klik op "Patiënten" → `/patienten`, klik op logo → `/` |
| Patiënt aanmaken | `/patienten/nieuw` → vul form → opslaan → redirect naar `/patienten/{id}` |
| Lock conflict | Open `/patienten/1` in 2 browsers → tweede ziet ReadOnlyOverlay |
| Formulier bewerken | Open `/patienten/1/dsm5` → wijzig criteria → opslaan → blijft op `/patienten/1/dsm5` |
| Kindcheck formulier | Open `/patienten/1/kindcheck` → vul datum, herkomst, voeg kind toe → opslaan → blijft op `/patienten/1/kindcheck` |
| Kindcheck kinderen | Voeg meerdere kinderen toe, wijzig soort/zorg, verwijder kind → opslaan → formulier ververst, data bewaard |
| Audit bekijken | `/audit` → filter op tabel → zie logs → klik detail |

---

## Handmatig testen (zonder testrunner)

### Voorbereiding

1. Start de backend:
   ```bash
   cd backend && source venv/bin/activate
   uvicorn main:app --host 0.0.0.0 --port 8001 --reload
   ```

2. Start de frontend dev server:
   ```bash
   cd frontend && npm run dev
   # Draait op http://localhost:8002
   ```

3. Open http://localhost:8002 in de browser.

### Testflow — Complete happy path

#### 1. Registreren en inloggen
- Navigeer naar `/login`
- **Test**: Klik "Inloggen" zonder credentials → melding of geen actie (browser validatie)
- **Test**: Vul ongeldige credentials in → foutmelding "Ongeldige gebruikersnaam of wachtwoord"
- Registreer een gebruiker via de API (of voeg seed data toe):
  ```bash
  # Of gebruik het import script voor complete dataset:
  bash seed_data/import.sh http://localhost:8001
  ```
- **Test**: Login met `demo` / `demo123` → redirect naar dashboard

#### 2. Dashboard
- **Test**: 4 knoppen zichtbaar: "Patiëntgegevens", "DSM-5", "Kindcheck", "Audit"
- **Test**: Klik op "Patiëntgegevens" → `/patienten`
- **Test**: Klik op "DSM-5" → `/dsm5`
- **Test**: Klik op "Kindcheck" → `/kindcheck`
- **Test**: Klik op "Patiëntenbeheer" logo → terug naar `/`
- **Test**: Klik op "Uitloggen" → terug naar `/login`

#### 3. Patiëntenlijst
- **Test**: Lijst is leeg met melding "Geen patiënten gevonden"
- **Test**: Zoekveld werkt (typ iets, filter verversing)
- **Test**: Filter dropdown werkt (Alles/Voornaam/Achternaam/BSN/etc.)
- **Test**: Klik "+ Nieuwe patiënt" → `/patienten/nieuw`

#### 4. Patiënt aanmaken
- **Test**: Form toont alle velden (voornaam, achternaam, geboortedatum, BSN, adres, postcode, woonplaats, telefoon, email, notities)
- **Test**: Probeer op te slaan zonder voornaam → browser validation
- **Test**: Vul voornaam + achternaam in → klik "Opslaan" → redirect naar `/patienten/{nieuwId}` (detailpagina)
- **Test**: Patiënt verschijnt in de lijst
- **Test**: Geboortedatum invoerveld accepteert `DD/MM/YYYY` en wordt correct opgeslagen

#### 5. Patiënt bewerken
- **Test**: Klik op een patiënt in de lijst → `/patienten/{id}`
- **Test**: Form is gevuld met opgeslagen data
- **Test**: Wijzig woonplaats → klik "Opslaan" → blijft op `/patienten/{id}`, lock wordt ververst, form toont wijziging
- **Test**: Herlaad pagina → wijziging is bewaard
- **Test**: Knoppen "DSM-5" en "Kindcheck" zichtbaar voor bestaande patiënt
- **Test**: Geboortedatum getoond in `DD/MM/YYYY` formaat; wijzig datum → opslaan → datum correct bewaard

#### 6. Patiënt verwijderen
- **Test**: Klik "Verwijderen" → bevestigingsdialog verschijnt
- **Test**: Klik "Annuleren" → niets gebeurd
- **Test**: Klik "Verwijderen" → bevestig → terug naar lijst → patiënt weg

#### 7. DSM-5 formulier
- **Test**: Klik op een patiënt → klik "DSM-5 Formulier" → `/patienten/{id}/dsm5`
- **Test**: Form toont Status (Concept/Definitief), Criteria A t/m E, Dimensies, Conclusie
- **Test**: Vul criteria_a in → klik "Opslaan" → blijft op `/patienten/{id}/dsm5`, form ververst met opgeslagen data
- **Test**: Wijzig status naar "Definitief" → opslaan → blijft op pagina
- **Test**: Herlaad pagina → alle wijzigingen bewaard
- **Test**: Klik "Patiënt" knop → `/patienten/{id}`
- **Test**: Klik "Kindcheck" knop → `/patienten/{id}/kindcheck`

#### 8. Kindcheck formulier
- **Test**: Open een patiënt → klik "Kindcheck" → `/patienten/{id}/kindcheck`
- **Test**: Form toont datum, herkomst, klein/stief/pleeg, opkomst (radio)
- **Test**: Terminologie-selects zijn gevuld met opties uit de API
- **Test**: Klik "+ Kind toevoegen" → nieuw kind-blok verschijnt
- **Test**: Vul kind-naam, soort, gebdat, afhankelijk, zorg, overleden
- **Test**: Klik "Patiënt" knop → `/patienten/{id}`
- **Test**: Klik "DSM-5" knop → `/patienten/{id}/dsm5`
- **Test**: Klik "Verwijderen" op een kind → kind verdwijnt
- **Test**: Vul opmerking gedeelde zorg en alleen zorg in
- **Test**: Klik "Opslaan" → blijft op `/patienten/{id}/kindcheck`, form ververst met opgeslagen data
- **Test**: Herlaad pagina → alle data + kinderen bewaard
- **Test**: Voeg een extra kind toe → opslaan → kind is toegevoegd, blijft op pagina
- **Test**: Verwijder een kind → opslaan → kind is weg, blijft op pagina

#### 9. Kindcheck overzicht
- **Test**: Navigeer naar `/kindcheck` of klik "Kindcheck" in navbar
- **Test**: Tabel toont alle patiënten met "Ingevuld" / "Nog niet aangemaakt"
- **Test**: Filter op "Met formulier" / "Zonder formulier" werkt
- **Test**: Klik "Aanmaken/Openen" → juiste Kindcheck pagina

#### 10. DSM-5 overzicht
- **Test**: Navigeer naar `/dsm5` of klik "DSM-5 Formulier" in navbar
- **Test**: Tabel toont alle patiënten met formulierstatus
- **Test**: Filter op "Met formulier" / "Zonder formulier" werkt
- **Test**: Klik "Openen/Aanmaken" → juiste DSM-5 pagina

#### 11. Lock-systeem — Kindcheck (twee browsers)

Hetzelfde lock-patroon als DSM-5, maar voor kindcheck_forms:

- **Browser A**: Open `/patienten/1/kindcheck` → lock verkregen
- **Browser B**: Open `/patienten/1/kindcheck` → ReadOnlyOverlay + disabled velden
- **Browser A**: Sla op → Browser B data wordt ververst via WebSocket
- **Browser A**: Navigeer weg → Browser B kan lock overnemen

#### 12. Lock-systeem (twee browsers/incognito)

Open twee browsers (of één gewoon + één incognito):

**Browser A (normaal)**: Login als `demo` / `demo123`
**Browser B (incognito)**: Registreer + login als andere gebruiker:
```bash
curl -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"user2","password":"test123","display_name":"Tweede Gebruiker"}'
```

- **Browser A**: Open `/patienten/1` → je kunt bewerken (lock verkregen)
- **Browser B**: Open `/patienten/1` → ReadOnlyOverlay verschijnt met "Tweede Gebruiker" of juist "Demo Gebruiker"
- **Browser B**: Input velden zijn disabled
- **Browser A**: Sla op → Browser B data wordt ververst (3s polling)
- **Browser A**: Navigeer weg (lock release) → Browser B ziet lock_changed via WebSocket, probeert lock te krijgen
- **Browser B**: Kan nu bewerken

#### 13. Audit log — Kindcheck
- **Test**: Maak kindcheck formulier aan → audit log met `table_name=kindcheck_forms`, `action=CREATE`
- **Test**: Wijzig formulier → audit log met `action=UPDATE` + diff
- **Test**: Verwijder formulier → audit log met `action=DELETE`
- **Test**: Filter audit op tabel "DSM-5" → alleen kindcheck_forms logs

#### 14. Audit log
- **Test**: Navigeer naar `/audit`
- **Test**: Zie logs van eerdere CREATE/UPDATE/DELETE acties
- **Test**: Filter op tabel "Patiënten" → alleen patient-logs
- **Test**: Filter op actie "Aangemaakt" → alleen CREATE logs
- **Test**: Klik "Details" → `/audit/{id}`
- **Test**: Zie oude vs nieuwe waarden in JSON

#### 15. Edge cases

| Scenario | Hoe testen |
|----------|------------|
| Netwerkfout | Zet backend uit → probeer handeling → foutmelding |
| Token verlopen | Wacht 60 min of verlaat ACCESS_TOKEN_EXPIRE_MINUTES in .env → verversing gebeurt automatisch |
| Dubbele BSN | Maak patiënt met BSN "123", maak tweede metzelfde BSN → foutmelding |
| Kindcheck zonder patiënt | Navigeer naar `/patienten/9999/kindcheck` → foutmelding |
| DSM-5 zonder patiënt | Navigeer naar `/patienten/9999/dsm5` → foutmelding |
| Kindcheck — 0 kinderen | Sla formulier leeg op (geen kinderen) → formulier bestaat maar kinderen-array is leeg |
| Kindcheck — veel kinderen | Voeg 10+ kinderen toe → formulier nog steeds goed op te slaan |
| Lege audit | Wis database → audit pagina toont "Geen audit logs gevonden" |
| Paginatie audit | Maak >25 logs → controleer "Volgende" knop werkt |
| Polling na lock conflict | Lock een record → andere browser ziet polling (3s) van data |
| Formulier bewaren bij lock | Terwijl gelockt, wijzigingen maken → opslaan moet disabled zijn |

### 16. Dashboard — 4 knoppen
- **Test**: Dashboard toont 4 knoppen: Patiëntgegevens, DSM-5, Kindcheck, Audit
- **Test**: DSM-5 knop linkt naar `/dsm5`
- **Test**: Kindcheck knop linkt naar `/kindcheck`
- **Test**: NavBar toont "Kindcheck" tab met paarse active color

### 17. Responsive / layout
- **Test**: Resize browser naar mobiele breedte → layout past aan (Tailwind grid)
- **Test**: Navigatie toont nog steeds alle items
- **Test**: Tabellen scrollen horizontaal indien nodig

---

## Automatische tests opzetten (Vitest)

### Installatie

```bash
cd frontend
npm install -D vitest @vue/test-utils jsdom
```

Voeg aan `package.json` toe:
```json
{
  "scripts": {
    "test": "vitest run",
    "test:watch": "vitest",
    "test:coverage": "vitest run --coverage"
  }
}
```

Voeg aan `vite.config.js` toe:
```js
/// <reference types="vitest" />
export default defineConfig({
  test: {
    environment: 'jsdom',
    globals: true,
  },
  // ...bestaande config
})
```

### Voorbeeld test — auth store

Maak `src/stores/__tests__/auth.test.js`:

```javascript
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '../auth'
import { describe, it, expect, beforeEach, vi } from 'vitest'

describe('auth store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
  })

  it('begint niet ingelogd', () => {
    const auth = useAuthStore()
    expect(auth.isLoggedIn).toBe(false)
    expect(auth.token).toBeNull()
  })

  it('login slaat tokens op', async () => {
    const auth = useAuthStore()
    // Mock api.post
    vi.mock('../../api', () => ({
      default: {
        post: vi.fn().mockResolvedValue({
          data: {
            access_token: 'test_access',
            refresh_token: 'test_refresh',
          },
        }),
        get: vi.fn().mockResolvedValue({ data: {} }),
      },
    }))
    await auth.login('user', 'pass')
    expect(localStorage.getItem('access_token')).toBe('test_access')
    expect(auth.isLoggedIn).toBe(true)
  })

  it('logout wist tokens', () => {
    const auth = useAuthStore()
    auth.token = 'some_token'
    localStorage.setItem('access_token', 'some_token')
    auth.logout()
    expect(localStorage.getItem('access_token')).toBeNull()
    expect(auth.token).toBeNull()
  })
})
```

### Voorbeeld test — NavBar component

Maak `src/components/__tests__/NavBar.test.js`:

```javascript
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import NavBar from '../NavBar.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'Dashboard', component: { template: '<div></div>' } },
    { path: '/login', name: 'Login', component: { template: '<div></div>' } },
    { path: '/patienten', name: 'Patienten', component: { template: '<div></div>' } },
  ],
})

describe('NavBar', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('toont navigatie op dashboard', async () => {
    router.push('/')
    await router.isReady()
    const wrapper = mount(NavBar, {
      global: { plugins: [router, createPinia()] },
    })
    expect(wrapper.text()).toContain('Patiëntenbeheer')
    expect(wrapper.text()).toContain('Patiënten')
    expect(wrapper.text()).toContain('Uitloggen')
  })

  it('verbergt navigatie op loginpagina', async () => {
    router.push('/login')
    await router.isReady()
    const wrapper = mount(NavBar, {
      global: { plugins: [router, createPinia()] },
    })
    expect(wrapper.find('nav').exists()).toBe(false)
  })
})
```

### Draaien

```bash
cd frontend
npm run test          # Eenmalig
npm run test:watch    # Watch mode
```
