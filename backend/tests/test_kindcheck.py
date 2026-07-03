import pytest


class TestKindcheck:
    async def test_terminologie(self, client, auth_headers):
        resp = await client.get("/api/kindcheck/terminologie", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "herkomst" in data
        assert "kleinstiefpleeg" in data
        assert "kind_soort" in data
        assert "kind_zorg" in data
        assert len(data["herkomst"]) >= 4

    async def test_get_form_no_patient(self, client, auth_headers):
        resp = await client.get("/api/kindcheck/99999", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() is None

    async def test_create_form_basic(self, client, auth_headers, test_patient):
        pid = test_patient["id"]
        resp = await client.post(f"/api/kindcheck/{pid}", json={
            "patient_id": pid,
            "datum": "2020-01-01",
            "herkomst": "instelling",
            "herkomst_anders": "Geen",
            "opkomst": True,
            "opmerking_gedeelde_zorg": "Wil graag voetballen",
            "opmerking_alleen_zorg": "Last met opstaan",
            "kinderen": [],
        }, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["patient_id"] == pid
        assert data["herkomst"] == "instelling"
        assert data["opkomst"] is True
        assert data["kinderen"] == []

    async def test_create_form_with_children(self, client, auth_headers, test_patient):
        pid = test_patient["id"]
        resp = await client.post(f"/api/kindcheck/{pid}", json={
            "patient_id": pid,
            "datum": "2020-01-01",
            "herkomst": "thuis",
            "opkomst": True,
            "kinderen": [
                {"kind_naam": "Anna", "kind_soort": "eigen", "kind_gebdat": "2020-03-15", "kind_afhankelijk": True, "kind_zorg": "gedeelde_zorg"},
                {"kind_naam": "Bart", "kind_soort": "eigen", "kind_gebdat": "2022-07-01", "kind_afhankelijk": True, "kind_zorg": "gedeelde_zorg"},
            ],
        }, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert len(data["kinderen"]) == 2

    async def test_create_form_upsert(self, client, auth_headers, test_patient):
        pid = test_patient["id"]
        resp1 = await client.post(f"/api/kindcheck/{pid}", json={
            "patient_id": pid,
            "herkomst": "thuis",
            "opkomst": True,
            "kinderen": [],
        }, headers=auth_headers)
        assert resp1.status_code == 201
        form_id = resp1.json()["id"]
        resp2 = await client.post(f"/api/kindcheck/{pid}", json={
            "patient_id": pid,
            "herkomst": "instelling",
            "opkomst": False,
            "opmerking_gedeelde_zorg": "Bijgewerkt",
            "kinderen": [
                {"kind_naam": "Kees", "kind_soort": "eigen"},
            ],
        }, headers=auth_headers)
        assert resp2.status_code == 201
        assert resp2.json()["id"] == form_id
        assert resp2.json()["herkomst"] == "instelling"
        assert resp2.json()["opkomst"] is False
        assert len(resp2.json()["kinderen"]) == 1

    async def test_update_form_via_put(self, client, auth_headers, test_patient):
        pid = test_patient["id"]
        create_resp = await client.post(f"/api/kindcheck/{pid}", json={
            "patient_id": pid,
            "herkomst": "thuis",
            "opkomst": True,
            "kinderen": [],
        }, headers=auth_headers)
        form_id = create_resp.json()["id"]
        resp = await client.put(f"/api/kindcheck/form/{form_id}", json={
            "herkomst": "instelling",
            "opmerking_gedeelde_zorg": "Geüpdatet via PUT",
        }, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["herkomst"] == "instelling"

    async def test_update_form_not_found(self, client, auth_headers):
        resp = await client.put("/api/kindcheck/form/99999", json={
            "herkomst": "thuis",
        }, headers=auth_headers)
        assert resp.status_code == 404

    async def test_delete_form(self, client, auth_headers, test_patient):
        pid = test_patient["id"]
        create_resp = await client.post(f"/api/kindcheck/{pid}", json={
            "patient_id": pid,
            "herkomst": "thuis",
            "opkomst": True,
            "kinderen": [],
        }, headers=auth_headers)
        form_id = create_resp.json()["id"]
        resp = await client.delete(f"/api/kindcheck/form/{form_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert "verwijderd" in resp.json()["detail"]
        get_resp = await client.get(f"/api/kindcheck/{pid}", headers=auth_headers)
        assert get_resp.json() is None

    async def test_delete_form_cascades_children(self, client, auth_headers, test_patient):
        pid = test_patient["id"]
        create_resp = await client.post(f"/api/kindcheck/{pid}", json={
            "patient_id": pid,
            "herkomst": "thuis",
            "kinderen": [
                {"kind_naam": "Kind1"},
                {"kind_naam": "Kind2"},
            ],
        }, headers=auth_headers)
        form_id = create_resp.json()["id"]
        await client.delete(f"/api/kindcheck/form/{form_id}", headers=auth_headers)
        get_resp = await client.get(f"/api/kindcheck/{pid}", headers=auth_headers)
        assert get_resp.json() is None

    async def test_status_all(self, client, auth_headers, test_patient):
        pid = test_patient["id"]
        await client.post(f"/api/kindcheck/{pid}", json={
            "patient_id": pid,
            "herkomst": "thuis",
            "opkomst": True,
            "kinderen": [],
        }, headers=auth_headers)
        resp = await client.get("/api/kindcheck/status/all", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 1
        match = [p for p in data if p["patient_id"] == pid]
        assert len(match) == 1
        assert match[0]["has_form"] is True

    async def test_create_form_without_auth(self, client, test_patient):
        pid = test_patient["id"]
        resp = await client.post(f"/api/kindcheck/{pid}", json={
            "patient_id": pid,
            "herkomst": "thuis",
        })
        assert resp.status_code == 401

    async def test_terminologie_without_auth(self, client):
        resp = await client.get("/api/kindcheck/terminologie")
        assert resp.status_code == 401
