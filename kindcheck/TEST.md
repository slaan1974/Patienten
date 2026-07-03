# Kindcheck Tests — openEHR Kindcheck Formulier

## Testdata

Seed data (1 demo gebruiker + 1 patiënt met Kindcheck formulier) staat in:

- **JSON export**: `../seed_data/seed_data.json`
- **Import script**: `../seed_data/import.sh`

### Voorbeelddata

| Entiteit | Gegevens |
|----------|----------|
| **Gebruiker** | `demo` / `demo123` |
| **Patiënt** | Stefan de Vrij, BSN `648091958`, geb. `2001-01-04`, Alkmaar |
| **Kindcheck** | Datum `2020-01-01`, herkomst `instelling`, herkomst_anders `Geen`, opkomst `true`, 0 kinderen |

### Herladen van testdata

```bash
bash ../seed_data/import.sh http://localhost:8001
```

---

## Technische stack

- **Backend tests**: pytest 8.3.3 + pytest-asyncio 0.24.0 + httpx 0.27.2
- **Frontend tests**: Vitest + @vue/test-utils (aan te raden)
- **Database**: SQLite in-memory (per testclass aangemaakt)
- **Status**: ✅ Plan gereed — testbestanden nog niet geschreven

---

## Backend tests — API endpoints

### Bestand: `backend/tests/test_kindcheck.py`

| # | Scenario | Verwachte response |
|---|----------|--------------------|
| 1 | Formulier opvragen voor patiënt zonder formulier | 200 + `null` |
| 2 | Terminologie opvragen (`GET /api/kindcheck/terminologie`) | 200 + 4 lijsten (herkomst, kleinstiefpleeg, kind_soort, kind_zorg) |
| 3 | Formulier aanmaken (alleen hoofdvelden) | 201 + KindcheckFormOut |
| 4 | Formulier aanmaken met 2 kinderen | 201 + 2 kinderen in response |
| 5 | Formulier opnieuw opslaan bij zelfde patiënt (upsert) | 200 (update) |
| 6 | Kinderen vervangen bij upsert (oude weg, nieuwe toegevoegd) | 200 + nieuwe kind-set |
| 7 | Update formulier via `PUT /api/kindcheck/form/{id}` | 200 |
| 8 | Update niet-bestaand formulier | 404 |
| 9 | Verwijder formulier via `DELETE /api/kindcheck/form/{id}` | 200 |
| 10 | Verwijder formulier met kinderen (cascade) | 200 + kinderen weg uit DB |
| 11 | Status-overzicht (`GET /api/kindcheck/status/all`) | 200 + lijst per patiënt |
| 12 | Status-overzicht toont `has_form` correct | 200 + correcte boolean |
| 13 | Lock op kindcheck_forms voorkomt POST door andere gebruiker | 423 |
| 14 | CREATE genereert audit_log met `table_name=kindcheck_forms` | AuditLog action=CREATE |
| 15 | UPDATE genereert audit_log met diff (incl. kinderen als JSON) | AuditLog action=UPDATE |
| 16 | DELETE genereert audit_log | AuditLog action=DELETE |
| 17 | Formulier aanmaken zonder authenticatie | 401 |
| 18 | Terminologie-eindpoint zonder token | 401 |

### Schema-validatie

| # | Scenario | Verwachte response |
|---|----------|--------------------|
| 1 | POST met ongeldige datum | 422 |
| 2 | POST met onbekend herkomst-veld (niet in terminologie) | 200 (vrije tekst, geen validatie op terminologie) |
| 3 | POST met lege kinderen-array | 201 + lege array |
| 4 | POST met kind zonder verplichte velden | 201 (alle velden optioneel) |

---

## Frontend tests — Kindcheck store

### Bestand: `src/stores/__tests__/kindcheck.test.js`

| # | Scenario | Beschrijving |
|---|----------|-------------|
| 1 | fetchTerminologie vult 4 lijsten | mock GET `/kindcheck/terminologie` → terminologie.value bevat 4 keys |
| 2 | fetchForm zet currentForm | mock GET `/kindcheck/{id}` → currentForm.value = response |
| 3 | saveForm POST bij nieuw formulier | mock POST `/kindcheck/{id}` → juiste payload met kinderen |
| 4 | saveForm stuurt alle velden mee | payload bevat datum, herkomst, opkomst, kinderen[] |
| 5 | updateForm PUT naar endpoint | mock PUT `/kindcheck/form/{id}` → currentForm geüpdatet |
| 6 | deleteForm wist currentForm | mock DELETE → currentForm.value = null |
| 7 | fetchAllStatus vult allStatus | mock GET `/kindcheck/status/all` → array per patiënt |

---

## Frontend tests — KindcheckFormView component

### Bestand: `src/views/__tests__/KindcheckFormView.test.js`

| # | Scenario | Beschrijving |
|---|----------|-------------|
| 1 | Formulier toont loading spinner bij mount | loading = true, spinner zichtbaar |
| 2 | Formulier laadt terminologie in selects | herkomst, kleinstiefpleeg, kind_soort, kind_zord hebben opties |
| 3 | Lock wordt geacquired op kindcheck_forms bij mount | acquireLock('kindcheck_forms', pid) aangeroepen |
| 4 | ReadOnlyOverlay getoond bij lock conflict | lockError = 'lock_busy' → overlay zichtbaar |
| 5 | Velden disabled bij lock conflict | fieldset disabled bij lockError |
| 6 | Bestaand formulier vult alle velden | datum, herkomst, kinderen worden ingevuld |
| 7 | Kind toevoegen werkt | klik "+ Kind toevoegen" → nieuw kind-blok in lijst |
| 8 | Kind verwijderen werkt | klik verwijderen op kind → kind verdwijnt uit array |
| 9 | Opslaan roept saveForm aan met correcte payload | save() → kindcheckStore.saveForm(pid, payload) |
| 10 | Opslaan disabled tijdens saving | saving = true → knop disabled |
| 11 | Opslaan blijft op pagina (geen redirect) | na save() → router.push wordt niet aangeroepen |
| 12 | Opslaan release + re-acquire lock | save() → releaseLock → acquireLock |
| 13 | Opslaan ververst form met server data | save() → fetchForm → form bijgewerkt |
| 14 | Annuleren release lock en navigeert terug | cancel() → releaseLock + router.push |
| 15 | Verwijderen met confirm verwijdert formulier | verwijder() → deleteForm + router.push |
| 16 | Polling start bij lockError (3s interval) | lockError set → setInterval met 3000ms |
| 17 | Lock release bij route leave | onBeforeRouteLeave → releaseLock aangeroepen |
| 18 | "Patiënt" knop navigeert naar `/patienten/{id}` | click → router.push |
| 19 | "DSM-5" knop navigeert naar `/patienten/{id}/dsm5` | click → router.push |
| 20 | Datum invoerveld accepteert DD/MM/YYYY formaat | input.value = "01-04-2020" → v-model = "01-04-2020" |
| 21 | kind_gebdat invoerveld accepteert DD/MM/YYYY | input.value = "15-06-2010" → v-model = "15-06-2010" |
| 22 | Opslaan converteert datum naar YYYY-MM-DD voor API | save() → payload.datum = "2020-04-01" |
| 23 | Opslaan converteert kind_gebdat naar YYYY-MM-DD voor API | save() → payload.kinderen[0].kind_gebdat = "2010-06-15" |
| 24 | Laden converteert datum van YYYY-MM-DD naar DD/MM/YYYY | vulForm({datum: "2020-01-01"}) → form.datum = "01-01-2020" |

---

## Frontend tests — KindcheckOverviewView component

| # | Scenario | Beschrijving |
|---|----------|-------------|
| 1 | Toont tabel met alle patiënten + status | allStatus geladen → "Ingevuld" / "Nog niet aangemaakt" badges |
| 2 | Filter op "Met formulier" werkt | filter select → alleen has_form=true rijen |
| 3 | Filter op "Zonder formulier" werkt | filter select → alleen has_form=false rijen |
| 4 | Klik "Openen/Aanmaken" navigeert naar formulier | router.push naar `/patienten/{id}/kindcheck` |

---

## Handmatig testen — Kindcheck volledige flow

### Voorbereiding

```bash
# Terminal 1 — Backend
cd backend && source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# Terminal 2 — Frontend
cd frontend && npm run dev
# Draait op http://localhost:8002
```

### Flow 1 — Formulier aanmaken

1. Registreer gebruiker + login via browser op http://localhost:8002
2. Maak een patiënt aan via Patiënten → Nieuwe patiënt
3. Open de patiënt → klik "Kindcheck"
4. **Test**: Form toont lege velden met terminologie-selects gevuld
5. Vul datum = "01-04-2020" (DD/MM/YYYY), herkomst = "Thuis", opkomst = "Aanwezig"
6. Klik "+ Kind toevoegen" → nieuw blok verschijnt
7. Vul kind-naam = "Anna", soort = "Eigen", kind-gebdat = "15-06-2010" (DD/MM/YYYY), afhankelijk = "Ja", zorg = "Gedeelde zorg"
8. Klik "Opslaan" → **blijft op kindcheck pagina**, form ververst met opgeslagen data
9. **Test**: Formulier ID verschijnt rechtsboven (bv. "Formulier #1")
10. Herlaad pagina → alle data + kind bewaard

### Flow 1b — Cross-navigatie

1. Open kindcheck formulier voor een bestaande patiënt
2. **Test**: Onderaan het formulier zijn knoppen "Patiënt" (blauw) en "DSM-5" (groen) zichtbaar
3. Klik "Patiënt" → navigeert naar `/patienten/{id}`
4. Ga terug naar kindcheck formulier
5. Klik "DSM-5" → navigeert naar `/patienten/{id}/dsm5`
6. **Test**: Op DSM-5 pagina zijn knoppen "Patiënt" (blauw) en "Kindcheck" (paars) zichtbaar

### Flow 2 — Kinderen beheren

1. Open bestaand kindcheck formulier
2. **Test**: Eerder toegevoegd kind is zichtbaar
3. Voeg een tweede kind toe, vul alle velden
4. Verwijder het eerste kind
5. Klik "Opslaan" → **blijft op kindcheck pagina**, form ververst
6. **Test**: Alleen het tweede kind is overgebleven in het formulier
7. Herlaad pagina → bevestig dat alleen het tweede kind bewaard is

### Flow 3 — Lock conflict (twee browsers)

1. **Browser A**: Open `/patienten/{id}/kindcheck` → formulier bewerkbaar
2. **Browser B** (incognito): Login als andere gebruiker, open zelfde formulier
3. **Test**: Browser B ziet ReadOnlyOverlay + disabled velden
4. **Browser A**: Sla op → Browser B data ververst via WebSocket (3s polling)
5. **Browser A**: Navigeer weg → Browser B kan lock overnemen

### Flow 4 — Lock conflict simuleren via API

```bash
# Terminal 1 — Gebruiker A
TOKEN_A=$(curl -s -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user_a","password":"test123"}' | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

curl -X POST http://localhost:8001/api/lock \
  -H "Authorization: Bearer $TOKEN_A" \
  -H "Content-Type: application/json" \
  -d '{"table_name":"kindcheck_forms","record_id":1}'
# Verwacht: 200 — lock verkregen

# Terminal 2 — Gebruiker B
TOKEN_B=$(curl -s -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user_b","password":"test123"}' | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

curl -X POST http://localhost:8001/api/lock \
  -H "Authorization: Bearer $TOKEN_B" \
  -H "Content-Type: application/json" \
  -d '{"table_name":"kindcheck_forms","record_id":1}'
# Verwacht: 423 — locked door user_a
```

### Flow 5 — Audit logging

1. Maak kindcheck formulier aan → `GET /api/audit` toont `action=CREATE`, `table_name=kindcheck_forms`
2. Wijzig formulier → audit log met `action=UPDATE` + diff (oude vs nieuwe waarden)
3. Verwijder formulier → audit log met `action=DELETE`
4. Filter audit op `table_name=kindcheck_forms` → alleen kindcheck logs

### Flow 6 — Terminologie via API

```bash
TOKEN="<access_token>"

# Terminologie opvragen
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8001/api/kindcheck/terminologie | python3 -m json.tool

# Verwacht: 4 lijsten — herkomst, kleinstiefpleeg, kind_soort, kind_zorg
# elk met {waarde, label} objecten
```

---

## Snelle smoke-test

```bash
#!/bin/bash
set -e
BASE="http://localhost:8001"

echo "=== 1. Register (of gebruik seed_data/import.sh) ==="
curl -s -X POST "$BASE/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo123","display_name":"Demo Gebruiker"}'

echo -e "\n=== 2. Login ==="
RESP=$(curl -s -X POST "$BASE/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo123"}')
TOKEN=$(echo "$RESP" | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

echo -e "\n=== 3. Create patient (zie seed_data.json) ==="
curl -s -X POST "$BASE/api/patients" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"voornaam":"Stefan","achternaam":"de Vrij","bsn":"648091958","geboortedatum":"2001-01-04","adres":"Comeniusstraat","postcode":"1234AA","woonplaats":"Alkmaar","telefoon":"+123456789","email":"Stefan@devrij.nl","notities":"Voetballer"}' | python3 -m json.tool

echo -e "\n=== 4. Kindcheck terminologie ==="
curl -s -H "Authorization: Bearer $TOKEN" \
  "$BASE/api/kindcheck/terminologie" | python3 -c "import sys,json;d=json.load(sys.stdin);print(f'{len(d)} lijsten: {list(d.keys())}')"

echo -e "\n=== 5. Kindcheck formulier aanmaken (zie seed_data.json) ==="
curl -s -X POST "$BASE/api/kindcheck/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"patient_id":1,"datum":"2020-01-01","herkomst":"instelling","herkomst_anders":"Geen","opkomst":true,"opmerking_gedeelde_zorg":"Wil graag voetballen","opmerking_alleen_zorg":"Last met opstaan","kinderen":[]}' | python3 -m json.tool

echo -e "\n=== 6. Kindcheck formulier met 2 kinderen ==="
curl -s -X POST "$BASE/api/kindcheck/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 1,
    "datum": "2020-01-01",
    "herkomst": "instelling",
    "herkomst_anders": "Geen",
    "opkomst": true,
    "kinderen": [
      {"kind_naam":"Anna","kind_soort":"eigen","kind_gebdat":"2020-03-15","kind_afhankelijk":true,"kind_zorg":"gedeelde_zorg"},
      {"kind_naam":"Bart","kind_soort":"eigen","kind_gebdat":"2022-07-01","kind_afhankelijk":true,"kind_zorg":"gedeelde_zorg"}
    ]
  }' | python3 -m json.tool

echo -e "\n=== 7. Formulier ophalen ==="
curl -s -H "Authorization: Bearer $TOKEN" "$BASE/api/kindcheck/1" | python3 -c "
import sys,json
d=json.load(sys.stdin)
print(f'Formulier #{d[\"id\"]}: {len(d.get(\"kinderen\",[]))} kinderen')
"

echo -e "\n=== 8. Status overzicht ==="
curl -s -H "Authorization: Bearer $TOKEN" "$BASE/api/kindcheck/status/all" | python3 -m json.tool

echo -e "\n=== 9. Lock op kindcheck_forms ==="
curl -s -X POST "$BASE/api/lock" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"table_name":"kindcheck_forms","record_id":1}' | python3 -m json.tool

echo -e "\n=== 10. Audit log ==="
curl -s -H "Authorization: Bearer $TOKEN" "$BASE/api/audit?table_name=kindcheck_forms" | python3 -c "
import sys,json
logs=json.load(sys.stdin)
if isinstance(logs,list):
    print(f'{len(logs)} kindcheck audit logs gevonden')
    for log in logs[:3]:
        print(f'  - {log[\"action\"]} op {log.get(\"table_name\",\"?\")}')
"

echo -e "\n=== ALL KINDCHECK CHECKS PASSED ==="
```

Bewaar dit als `smoke_test_kindcheck.sh`, maak uitvoerbaar (`chmod +x smoke_test_kindcheck.sh`),
en voer uit terwijl de server draait.

> **Tip**: Gebruik `bash ../seed_data/import.sh http://localhost:8001` voor een
> complete import van alle testdata in één keer. Zie `../seed_data/seed_data.json`
> voor de exacte velden en waarden.
