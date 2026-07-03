import pytest


class TestDsm5:
    async def test_get_form_no_patient(self, client, auth_headers):
        resp = await client.get("/api/dsm5/99999", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() is None

    async def test_create_form(self, client, auth_headers, test_patient):
        pid = test_patient["id"]
        resp = await client.post(f"/api/dsm5/{pid}", json={
            "patient_id": pid,
            "status": "concept",
            "criteria_a": "A",
            "criteria_b": "B",
            "criteria_c": "C",
            "criteria_d": "D",
            "criteria_e": "E",
            "dimensies": "Dimensies",
            "conclusie": "Conclusie staat hier",
        }, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["patient_id"] == pid
        assert data["status"] == "concept"
        assert data["criteria_a"] == "A"

    async def test_create_form_then_upsert(self, client, auth_headers, test_patient):
        pid = test_patient["id"]
        resp1 = await client.post(f"/api/dsm5/{pid}", json={
            "patient_id": pid,
            "status": "concept",
        }, headers=auth_headers)
        assert resp1.status_code == 201
        form_id = resp1.json()["id"]
        resp2 = await client.post(f"/api/dsm5/{pid}", json={
            "patient_id": pid,
            "status": "definitief",
            "conclusie": "Bijgewerkt",
        }, headers=auth_headers)
        assert resp2.status_code == 201
        assert resp2.json()["id"] == form_id
        assert resp2.json()["status"] == "definitief"
        assert resp2.json()["conclusie"] == "Bijgewerkt"

    async def test_update_form_via_put(self, client, auth_headers, test_patient):
        pid = test_patient["id"]
        create_resp = await client.post(f"/api/dsm5/{pid}", json={
            "patient_id": pid,
            "status": "concept",
        }, headers=auth_headers)
        form_id = create_resp.json()["id"]
        resp = await client.put(f"/api/dsm5/form/{form_id}", json={
            "status": "definitief",
            "conclusie": "Geüpdatet via PUT",
        }, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["status"] == "definitief"
        assert resp.json()["conclusie"] == "Geüpdatet via PUT"

    async def test_update_form_not_found(self, client, auth_headers):
        resp = await client.put("/api/dsm5/form/99999", json={
            "status": "definitief",
        }, headers=auth_headers)
        assert resp.status_code == 404

    async def test_delete_form(self, client, auth_headers, test_patient):
        pid = test_patient["id"]
        create_resp = await client.post(f"/api/dsm5/{pid}", json={
            "patient_id": pid,
            "status": "concept",
        }, headers=auth_headers)
        form_id = create_resp.json()["id"]
        resp = await client.delete(f"/api/dsm5/form/{form_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert "verwijderd" in resp.json()["detail"]
        get_resp = await client.get(f"/api/dsm5/{pid}", headers=auth_headers)
        assert get_resp.json() is None

    async def test_status_all(self, client, auth_headers, test_patient):
        pid = test_patient["id"]
        await client.post(f"/api/dsm5/{pid}", json={
            "patient_id": pid,
            "status": "concept",
        }, headers=auth_headers)
        resp = await client.get("/api/dsm5/status/all", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 1
        match = [p for p in data if p["patient_id"] == pid]
        assert len(match) == 1
        assert match[0]["has_form"] is True
        assert match[0]["form_status"] == "concept"
