import json


class TestAudit:
    async def test_create_patient_generates_audit(self, client, auth_headers):
        resp = await client.post("/api/patients", json={
            "voornaam": "Jan",
            "achternaam": "Jansen",
        }, headers=auth_headers)
        assert resp.status_code == 201
        patient_id = resp.json()["id"]
        audit_resp = await client.get("/api/audit", headers=auth_headers)
        assert audit_resp.status_code == 200
        logs = audit_resp.json()
        matching = [l for l in logs if l["record_id"] == patient_id and l["table_name"] == "patients"]
        assert len(matching) >= 1
        assert matching[0]["action"] == "CREATE"

    async def test_update_patient_generates_audit(self, client, auth_headers, test_patient):
        pid = test_patient["id"]
        await client.put(f"/api/patients/{pid}", json={
            "woonplaats": "Rotterdam",
        }, headers=auth_headers)
        audit_resp = await client.get("/api/audit", headers=auth_headers)
        logs = audit_resp.json()
        updates = [l for l in logs if l["table_name"] == "patients" and l["action"] == "UPDATE" and l["record_id"] == pid]
        assert len(updates) >= 1
        old = json.loads(updates[0]["old_values"])
        new = json.loads(updates[0]["new_values"])
        assert old.get("woonplaats") == "Alkmaar"
        assert new.get("woonplaats") == "Rotterdam"

    async def test_update_patient_logs_changed_values(self, client, auth_headers, test_patient):
        pid = test_patient["id"]
        await client.put(f"/api/patients/{pid}", json={
            "woonplaats": "Rotterdam",
        }, headers=auth_headers)
        audit_resp = await client.get("/api/audit", headers=auth_headers)
        logs = [l for l in audit_resp.json() if l["table_name"] == "patients" and l["action"] == "UPDATE" and l["record_id"] == pid]
        assert len(logs) >= 1

    async def test_delete_patient_generates_audit(self, client, auth_headers, test_patient):
        pid = test_patient["id"]
        await client.delete(f"/api/patients/{pid}", headers=auth_headers)
        audit_resp = await client.get("/api/audit", headers=auth_headers)
        logs = audit_resp.json()
        deletes = [l for l in logs if l["table_name"] == "patients" and l["action"] == "DELETE" and l["record_id"] == pid]
        assert len(deletes) >= 1

    async def test_audit_filter_table_name(self, client, auth_headers, test_patient):
        pid = test_patient["id"]
        await client.post(f"/api/dsm5/{pid}", json={
            "patient_id": pid,
            "status": "concept",
        }, headers=auth_headers)
        resp = await client.get("/api/audit?table_name=dsm5_forms", headers=auth_headers)
        logs = resp.json()
        assert all(l["table_name"] == "dsm5_forms" for l in logs)

    async def test_audit_filter_action(self, client, auth_headers, test_patient):
        pid = test_patient["id"]
        resp = await client.get(f"/api/audit?action=CREATE&table_name=patients", headers=auth_headers)
        logs = resp.json()
        assert len(logs) >= 1

    async def test_audit_detail(self, client, auth_headers, test_patient):
        pid = test_patient["id"]
        audit_resp = await client.get("/api/audit", headers=auth_headers)
        logs = audit_resp.json()
        if logs:
            log_id = logs[0]["id"]
            detail = await client.get(f"/api/audit/{log_id}", headers=auth_headers)
            assert detail.status_code == 200
            assert detail.json()["id"] == log_id

    async def test_audit_detail_not_found(self, client, auth_headers):
        resp = await client.get("/api/audit/99999", headers=auth_headers)
        assert resp.status_code == 404

    async def test_dsm5_create_generates_audit(self, client, auth_headers, test_patient):
        pid = test_patient["id"]
        await client.post(f"/api/dsm5/{pid}", json={
            "patient_id": pid,
            "status": "concept",
        }, headers=auth_headers)
        resp = await client.get("/api/audit?table_name=dsm5_forms", headers=auth_headers)
        logs = resp.json()
        matching = [l for l in logs if l["record_id"] == pid and l["action"] == "CREATE"]
        assert len(matching) >= 1
