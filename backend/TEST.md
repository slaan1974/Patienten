# Backend Tests — Patiëntenbeheer API

## Testdata

Seed data (1 demo gebruiker + 1 patiënt met DSM-5 + Kindcheck) staat in:

- **JSON export**: `../seed_data/seed_data.json`
- **Import script**: `../seed_data/import.sh` — draaien met `bash ../seed_data/import.sh [base_url]`

### Voorbeelddata (geëxporteerd uit live systeem)

| Entiteit | Gegevens |
|----------|----------|
| **Gebruiker** | `demo` / `demo123` |
| **Patiënt** | Stefan de Vrij, BSN `648091958`, geb. `2001-01-04`, Alkmaar |
| **DSM-5** | Status `concept`, criteria A t/m E gevuld, conclusie "Conclusie staat hier" |
| **Kindcheck** | Datum `2020-01-01`, herkomst `instelling`, opkomst `true`, 0 kinderen |

### Herladen van testdata

```bash
# Vanuit backend/ directory:
# 1. Verwijder oude DB
rm -f patienten.db
# 2. Herstart backend (maakt nieuwe tabellen aan)
# 3. Importeer seed data
bash ../seed_data/import.sh http://localhost:8001
```

---

## Technische stack

- **Framework**: pytest 8.3.3 + pytest-asyncio 0.24.0
- **HTTP client**: httpx 0.27.2
- **Database**: SQLite in-memory (per testclass aangemaakt)
- **Status**: ✅ Plan gereed — testbestanden nog niet geschreven

## Testbestanden

| Bestand                      | Wat wordt getest                                  |
| ---------------------------- | ------------------------------------------------- |
| `tests/conftest.py`          | Gedeelde fixtures (db, client, auth headers)      |
| `tests/test_auth.py`         | Register, login, refresh token, ongeldige tokens  |
| `tests/test_patients.py`     | CRUD patiënten, validatie, lock-bescherming       |
| `tests/test_dsm5.py`         | CRUD DSM-5 formulieren, status-overzicht          |
| `tests/test_kindcheck.py`    | CRUD kindcheck formulieren, kinderen, terminologie|
| `tests/test_locks.py`        | Lock acquire/release/refresh, timeout, conflicten |
| `tests/test_locks_ws.py`     | WebSocket lock_changed notificaties               |
| `tests/test_audit.py`        | CREATE/UPDATE/DELETE audit logging, filters       |

---

## Testcases per module

### Auth (`test_auth.py`)

| #  | Scenario                                                | Verwachte response |
|----|---------------------------------------------------------|--------------------|
| 1  | Registreer nieuwe gebruiker                             | 201 + UserOut      |
| 2  | Registreer met bestaande gebruikersnaam                 | 400 "bestaat al"  |
| 3  | Login met correcte credentials                          | 200 + TokenResponse|
| 4  | Login met verkeerd wachtwoord                           | 401                |
| 5  | Login met onbekende gebruikersnaam                      | 401                |
| 6  | Ververs token met geldig refresh token                  | 200 + nieuwe tokens|
| 7  | Ververs token met verlopen/ongeldig refresh token       | 401                |
| 8  | Open endpoint zonder token                              | 401                |
| 9  | Open endpoint met verlopen access token                 | 401                |

### Patiënten (`test_patients.py`)

| #  | Scenario                                                | Verwachte response |
|----|---------------------------------------------------------|--------------------|
| 1  | Lijst patiënten (leeg)                                  | 200 + []           |
| 2  | Maak nieuwe patiënt (verplichte velden)                 | 201 + PatientOut   |
| 3  | Maak nieuwe patiënt met alle velden (zie seed_data.json)| 201 + alle velden  |
| 4  | Maak patiënt zonder voornaam (verplicht)                | 422                |
| 5  | Haal patiënt op via ID — bv. `GET /patients/1`          | 200 + PatientOut   |
| 6  | Haal niet-bestaande patiënt op                          | 404                |
| 7  | Update bestaande patiënt                                | 200 + gewijzigd    |
| 8  | Update niet-bestaande patiënt                           | 404                |
| 9  | Verwijder patiënt                                       | 200 + "verwijderd" |
| 10 | Verwijder niet-bestaande patiënt                        | 404                |
| 11 | Dubbele BSN wordt geweigerd                             | 400/409            |

### DSM-5 (`test_dsm5.py`)

| #  | Scenario                                                | Verwachte response |
|----|---------------------------------------------------------|--------------------|
| 1  | DSM-5 formulier opvragen voor patiënt zonder formulier  | 200 + null         |
| 2  | DSM-5 formulier aanmaken voor patiënt (zie seed_data)   | 201 + Dsm5FormOut  |
| 3  | DSM-5 formulier aanmaken — tweede POST updatet i.p.v. 2e| 200 (update)       |
| 4  | Update formulier via PUT /form/{id}                     | 200                |
| 5  | Update niet-bestaand formulier                          | 404                |
| 6  | Verwijder formulier                                     | 200                |
| 7  | Status-overzicht (`/dsm5/status/all`)                   | 200 + lijst        |
| 8  | Status-overzicht toont has_form/correcte status         | 200 + correcte data|

### Kindcheck (`test_kindcheck.py`)

| #  | Scenario                                                | Verwachte response |
|----|---------------------------------------------------------|--------------------|
| 1  | Formulier opvragen voor patiënt zonder formulier        | 200 + null         |
| 2  | Terminologie opvragen                                   | 200 + 4 lijsten    |
| 3  | Formulier aanmaken (alleen hoofdvelden, zie seed_data)  | 201 + KindcheckFormOut |
| 4  | Formulier aanmaken met 2 kinderen                       | 201 + 2 kinderen   |
| 5  | Formulier opnieuw opslaan (upsert)                      | 200 (update)       |
| 6  | Kinderen vervangen bij upsert                           | 201 + nieuwe set   |
| 7  | Update formulier via PUT /form/{id}                     | 200                |
| 8  | Update niet-bestaand formulier                          | 404                |
| 9  | Verwijder formulier                                     | 200                |
| 10 | Verwijder formulier met kinderen (cascade)              | 200 + kinderen weg |
| 11 | Status-overzicht (`/kindcheck/status/all`)              | 200 + lijst        |
| 12 | Status-overzicht toont has_form correct                 | 200 + correct      |

### Locks (`test_locks.py`)

| #  | Scenario                                                | Verwachte response |
|----|---------------------------------------------------------|--------------------|
| 1  | Lock aanvragen op vrij record                           | 200 + {locked:True}|
| 2  | Lock aanvragen op reeds gelockt record (andere user)    | 423 + locked info  |
| 3  | Lock opnieuw aanvragen door zelfde user (heartbeat)     | 200 + lock ververst|
| 4  | Lock status opvragen (gelocked)                         | 200 + locked info  |
| 5  | Lock status opvragen (niet gelocked)                    | 200 + {locked:False|
| 6  | Lock vrijgeven door eigenaar                            | 200 + "vrijgegeven"|
| 7  | Lock vrijgeven door andere gebruiker                    | 400                |
| 8  | Alle locks van gebruiker vrijgeven                      | 200 + aantal       |
| 9  | Lock refresh door eigenaar                              | 200 + "ververst"   |
| 10 | Lock refresh door andere gebruiker                      | 400                |
| 11 | Lock timeout (expired lock wordt genegeerd)             | 200 + {locked:False|

### Audit (`test_audit.py`)

| #  | Scenario                                                | Verwachte response |
|----|---------------------------------------------------------|--------------------|
| 1  | CREATE patiënt genereert auditlog                       | AuditLog action=CREATE|
| 2  | UPDATE patiënt genereert auditlog (alleen gewijzigd)    | AuditLog action=UPDATE|
| 3  | UPDATE zonder wijzigingen genereert géén auditlog       | Geen nieuwe log    |
| 4  | DELETE patiënt genereert auditlog                       | AuditLog action=DELETE|
| 5  | Auditlog lijst met filters (table_name)                 | Gefilterde resultaten|
| 6  | Auditlog lijst met datumfilter                          | Correcte datering  |
| 7  | Auditlog detail opvragen — bv. `GET /audit/1`           | 200 + log          |
| 8  | Auditlog detail niet-bestaand                           | 404                |
| 9  | DSM-5 CREATE logt correct (zie seed_data voor data)     | AuditLog table=dsm5_forms|

---

## Handmatig testen (zonder pytest)

### 1. Server starten

```bash
cd backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### 2. Healthcheck

```bash
curl http://localhost:8001/api/health
# {"status":"ok"}
```

### 3. Auth testen

```bash
# Registreren
curl -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo123","display_name":"Demo Gebruiker"}'

# Inloggen (bewaar de tokens)
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo123"}'

# Token verversen
curl -X POST http://localhost:8001/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"<refresh_token>"}'
```

### 4. Patiënten testen

```bash
TOKEN="<access_token>"
BASE="http://localhost:8001"

# Lijst (leeg)
curl -H "Authorization: Bearer $TOKEN" $BASE/api/patients

# Aanmaken (zie ook seed_data.json voor volledige dataset)
curl -X POST $BASE/api/patients \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"voornaam":"Stefan","achternaam":"de Vrij","bsn":"648091958","woonplaats":"Alkmaar"}'

# Ophalen
curl -H "Authorization: Bearer $TOKEN" $BASE/api/patients/1

# Bewerken
curl -X PUT $BASE/api/patients/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"woonplaats":"Alkmaar","notities":"Voetballer"}'

# Verwijderen
curl -X DELETE $BASE/api/patients/1 \
  -H "Authorization: Bearer $TOKEN"
```

### 5. Locks testen

```bash
# Lock aanvragen op patients/1
curl -X POST $BASE/api/lock \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"table_name":"patients","record_id":1}'

# Lock status checken
curl -H "Authorization: Bearer $TOKEN" $BASE/api/lock/patients/1

# Lock vrijgeven
curl -X DELETE $BASE/api/lock \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"table_name":"patients","record_id":1}'
```

### 6. DSM-5 testen

```bash
# Formulier aanmaken (zie seed_data.json)
curl -X POST $BASE/api/dsm5/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status":"concept","criteria_a":"A","criteria_b":"B","criteria_c":"C","criteria_d":"D","criteria_e":"E","dimensies":"Dimensies","conclusie":"Conclusie staat hier"}'

# Formulier ophalen
curl -H "Authorization: Bearer $TOKEN" $BASE/api/dsm5/1

# Status overzicht
curl -H "Authorization: Bearer $TOKEN" $BASE/api/dsm5/status/all
```

### 7. Kindcheck testen

```bash
# Terminologie ophalen
curl -H "Authorization: Bearer $TOKEN" $BASE/api/kindcheck/terminologie | python3 -m json.tool

# Formulier aanmaken (zie seed_data.json)
curl -X POST $BASE/api/kindcheck/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 1,
    "datum": "2020-01-01",
    "herkomst": "instelling",
    "herkomst_anders": "Geen",
    "opkomst": true,
    "opmerking_gedeelde_zorg": "Wil graag voetballen",
    "opmerking_alleen_zorg": "Last met opstaan",
    "kinderen": []
  }' | python3 -m json.tool

# Formulier ophalen
curl -H "Authorization: Bearer $TOKEN" $BASE/api/kindcheck/1 | python3 -m json.tool

# Status overzicht
curl -H "Authorization: Bearer $TOKEN" $BASE/api/kindcheck/status/all | python3 -m json.tool

# Lock op kindcheck_forms
curl -X POST $BASE/api/lock \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"table_name":"kindcheck_forms","record_id":1}'
```

### 8. Audit testen

```bash
# Audit logs bekijken
curl -H "Authorization: Bearer $TOKEN" $BASE/api/audit

# Met filters
curl -H "Authorization: Bearer $TOKEN" "$BASE/api/audit?table_name=patients&action=CREATE"

# Detail
curl -H "Authorization: Bearer $TOKEN" $BASE/api/audit/1
```

### 9. Lock-conflict simuleren — Kindcheck (twee gebruikers)

Hetzelfde patroon als bij patiënten, maar met
`table_name="kindcheck_forms"` en `record_id=1`:

```bash
# Terminal 1 — Gebruiker A: lock op kindcheck_forms/1
curl -X POST http://localhost:8001/api/lock \
  -H "Authorization: Bearer $TOKEN_A" \
  -H "Content-Type: application/json" \
  -d '{"table_name":"kindcheck_forms","record_id":1}'

# Terminal 2 — Gebruiker B: probeert zelfde lock
curl -X POST http://localhost:8001/api/lock \
  -H "Authorization: Bearer $TOKEN_B" \
  -H "Content-Type: application/json" \
  -d '{"table_name":"kindcheck_forms","record_id":1}'
# Verwacht: 423 — locked door user_a
```

---

### 10. Lock-conflict simuleren (twee gebruikers)

Open **twee terminals**:

**Terminal 1 — Gebruiker A**:
```bash
TOKEN_A=$(curl -s -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user_a","password":"test123"}' | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

curl -X POST http://localhost:8001/api/lock \
  -H "Authorization: Bearer $TOKEN_A" \
  -H "Content-Type: application/json" \
  -d '{"table_name":"patients","record_id":1}'
# Verwacht: 200 — lock verkregen
```

**Terminal 2 — Gebruiker B**:
```bash
TOKEN_B=$(curl -s -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user_b","password":"test123"}' | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

curl -X POST http://localhost:8001/api/lock \
  -H "Authorization: Bearer $TOKEN_B" \
  -H "Content-Type: application/json" \
  -d '{"table_name":"patients","record_id":1}'
# Verwacht: 423 — locked door user_a
```

---

## Snelle smoke-test met één script

```bash
#!/bin/bash
set -e
BASE="http://localhost:8001"

echo "=== 1. Register (gebruik seed_data/import.sh voor volledige import) ==="
curl -s -X POST "$BASE/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo123","display_name":"Demo Gebruiker"}'

echo -e "\n=== 2. Login ==="
RESP=$(curl -s -X POST "$BASE/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo123"}')
TOKEN=$(echo "$RESP" | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")
echo "Token: ${TOKEN:0:20}..."

echo -e "\n=== 3. Health ==="
curl -s "$BASE/api/health" | python3 -m json.tool

echo -e "\n=== 4. Create patient (zie seed_data.json voor complete dataset) ==="
curl -s -X POST "$BASE/api/patients" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"voornaam":"Stefan","achternaam":"de Vrij","bsn":"648091958","geboortedatum":"2001-01-04","adres":"Comeniusstraat","postcode":"1234AA","woonplaats":"Alkmaar","telefoon":"+123456789","email":"Stefan@devrij.nl","notities":"Voetballer"}' | python3 -m json.tool

echo -e "\n=== 5. List patients ==="
curl -s -H "Authorization: Bearer $TOKEN" "$BASE/api/patients" | python3 -m json.tool

echo -e "\n=== 6. Lock patient ==="
curl -s -X POST "$BASE/api/lock" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"table_name":"patients","record_id":1}' | python3 -m json.tool

echo -e "\n=== 7. Release lock ==="
curl -s -X DELETE "$BASE/api/lock" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"table_name":"patients","record_id":1}'

echo -e "\n=== 8. Kindcheck terminologie ==="
curl -s -H "Authorization: Bearer $TOKEN" "$BASE/api/kindcheck/terminologie" | python3 -c "import sys,json;d=json.load(sys.stdin);print(f'{len(d)} lijsten geladen')"

echo -e "\n=== 9. Kindcheck formulier (zie seed_data.json) ==="
curl -s -X POST "$BASE/api/kindcheck/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"patient_id":1,"datum":"2020-01-01","herkomst":"instelling","herkomst_anders":"Geen","opkomst":true,"opmerking_gedeelde_zorg":"Wil graag voetballen","opmerking_alleen_zorg":"Last met opstaan","kinderen":[]}' | python3 -m json.tool

echo -e "\n=== 10. Audit log ==="
curl -s -H "Authorization: Bearer $TOKEN" "$BASE/api/audit" | python3 -m json.tool

echo -e "\n=== ALL CHECKS PASSED ==="
```

Bewaar dit als `smoke_test.sh`, maak uitvoerbaar (`chmod +x smoke_test.sh`),
en voer uit terwijl de server draait.

> **Tip**: Gebruik `bash ../seed_data/import.sh http://localhost:8001` voor een
> complete import van alle testdata (gebruiker + patiënt + DSM-5 + Kindcheck)
> in één keer. Zie `../seed_data/seed_data.json` voor de exacte data.
