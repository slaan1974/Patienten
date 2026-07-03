#!/bin/bash
# ============================================================
# Import seed data voor Patiëntenbeheer
# Gebruik: ./import.sh [base_url]
# Voorbeeld: ./import.sh http://localhost:8001
# ============================================================
set -e

BASE="${1:-http://localhost:8001}"
DIR="$(cd "$(dirname "$0")" && pwd)"
DATA="$DIR/seed_data.json"

if [ ! -f "$DATA" ]; then
  echo "Fout: $DATA niet gevonden"
  exit 1
fi

echo "=== Import seed data naar $BASE ==="
echo ""

# ── 1. Registreer gebruiker ──────────────────────────────────
echo ">>> 1. Gebruiker registreren..."
USERNAME=$(python3 -c "import json; print(json.load(open('$DATA'))['users'][0]['username'])")
PASSWORD=$(python3 -c "import json; print(json.load(open('$DATA'))['users'][0]['password'])")
DISPLAY=$(python3 -c "import json; print(json.load(open('$DATA'))['users'][0]['display_name'])")

REG_RESP=$(curl -s -X POST "$BASE/api/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\",\"display_name\":\"$DISPLAY\"}" 2>&1) || true

if echo "$REG_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('id',''))" 2>/dev/null | grep -q '[0-9]'; then
  echo "   ✅ Gebruiker '$USERNAME' geregistreerd"
elif echo "$REG_RESP" | grep -qi "bestaat"; then
  echo "   ⚠️  Gebruiker '$USERNAME' bestaat al, login gebruiken..."
else
  echo "   ⚠️  Registratie reactie: $REG_RESP"
fi

# ── 2. Login ─────────────────────────────────────────────────
echo ">>> 2. Inloggen..."
LOGIN_RESP=$(curl -s -X POST "$BASE/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}")
TOKEN=$(echo "$LOGIN_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null || echo "")
if [ -z "$TOKEN" ]; then
  echo "   ❌ Login mislukt: $LOGIN_RESP"
  exit 1
fi
echo "   ✅ Token verkregen"

# ── 3. Import patiënten ──────────────────────────────────────
echo ">>> 3. Patiënten importeren..."
NUM_PATIENTS=$(python3 -c "import json; print(len(json.load(open('$DATA'))['patients']))")
for i in $(seq 0 $((NUM_PATIENTS - 1))); do
  PATIENT_DATA=$(python3 -c "
import json
data = json.load(open('$DATA'))
p = data['patients'][$i]
# Verwijder id zodat POST hem zelf toekent
p.pop('id', None)
print(json.dumps(p))
")
  RESP=$(curl -s -X POST "$BASE/api/patients" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "$PATIENT_DATA")
  PID=$(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('id','?'))" 2>/dev/null || echo "?")
  echo "   ✅ Patiënt $i: id=$PID"
done

# If we can't get patient_id from response, try listing
PATIENT_ID=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE/api/patients" \
  | python3 -c "import sys,json; data=json.load(sys.stdin); print(data[0]['id'] if data else '1')" 2>/dev/null || echo "1")
echo "   → Gebruik patient_id=$PATIENT_ID"

# ── 4. Import DSM-5 formulieren ───────────────────────────────
echo ">>> 4. DSM-5 formulieren importeren..."
NUM_DSM5=$(python3 -c "import json; print(len(json.load(open('$DATA')).get('dsm5_forms',[])))")
for i in $(seq 0 $((NUM_DSM5 - 1))); do
  DSM5_DATA=$(python3 -c "
import json
data = json.load(open('$DATA'))
f = data['dsm5_forms'][$i]
f['patient_id'] = $PATIENT_ID
print(json.dumps(f))
")
  RESP=$(curl -s -X POST "$BASE/api/dsm5/$PATIENT_ID" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "$DSM5_DATA")
  FID=$(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('id','?'))" 2>/dev/null || echo "?")
  echo "   ✅ DSM-5 formulier $i: id=$FID"
done

# ── 5. Import Kindcheck formulieren ───────────────────────────
echo ">>> 5. Kindcheck formulieren importeren..."
NUM_KC=$(python3 -c "import json; print(len(json.load(open('$DATA')).get('kindcheck_forms',[])))")
for i in $(seq 0 $((NUM_KC - 1))); do
  KC_DATA=$(python3 -c "
import json
data = json.load(open('$DATA'))
f = data['kindcheck_forms'][$i]
f['patient_id'] = $PATIENT_ID
print(json.dumps(f))
")
  RESP=$(curl -s -X POST "$BASE/api/kindcheck/$PATIENT_ID" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "$KC_DATA")
  KID=$(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('id','?'))" 2>/dev/null || echo "?")
  echo "   ✅ Kindcheck formulier $i: id=$KID"
done

echo ""
echo "=== Import voltooid! ==="
echo ""
echo "Inloggen: http://localhost:8002/login"
echo "  Gebruiker: $USERNAME"
echo "  Wachtwoord: $PASSWORD"
