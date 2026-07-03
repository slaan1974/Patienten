import pytest


class TestPatients:
    async def test_list_patients_empty(self, client, auth_headers):
        resp = await client.get("/api/patients", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_create_patient_minimal(self, client, auth_headers):
        resp = await client.post("/api/patients", json={
            "voornaam": "Jan",
            "achternaam": "Jansen",
        }, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["voornaam"] == "Jan"
        assert data["achternaam"] == "Jansen"
        assert "id" in data

    async def test_create_patient_all_fields(self, client, auth_headers):
        resp = await client.post("/api/patients", json={
            "voornaam": "Stefan",
            "achternaam": "de Vrij",
            "geboortedatum": "2001-01-04",
            "bsn": "648091958",
            "adres": "Comeniusstraat",
            "postcode": "1234AA",
            "woonplaats": "Alkmaar",
            "telefoon": "+123456789",
            "email": "stefan@devrij.nl",
            "notities": "Voetballer",
        }, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["voornaam"] == "Stefan"
        assert data["bsn"] == "648091958"
        assert data["woonplaats"] == "Alkmaar"

    async def test_create_patient_missing_voornaam(self, client, auth_headers):
        resp = await client.post("/api/patients", json={
            "achternaam": "Jansen",
        }, headers=auth_headers)
        assert resp.status_code == 422

    async def test_create_patient_duplicate_bsn(self, client, auth_headers):
        await client.post("/api/patients", json={
            "voornaam": "Eerste",
            "achternaam": "Persoon",
            "bsn": "123456789",
        }, headers=auth_headers)
        resp = await client.post("/api/patients", json={
            "voornaam": "Tweede",
            "achternaam": "Persoon",
            "bsn": "123456789",
        }, headers=auth_headers)
        assert resp.status_code == 409

    async def test_get_patient_by_id(self, client, auth_headers, test_patient):
        pid = test_patient["id"]
        resp = await client.get(f"/api/patients/{pid}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == pid

    async def test_get_patient_not_found(self, client, auth_headers):
        resp = await client.get("/api/patients/99999", headers=auth_headers)
        assert resp.status_code == 404

    async def test_update_patient(self, client, auth_headers, test_patient):
        pid = test_patient["id"]
        resp = await client.put(f"/api/patients/{pid}", json={
            "woonplaats": "Amsterdam",
            "notities": "Bijgewerkt",
        }, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["woonplaats"] == "Amsterdam"
        assert data["notities"] == "Bijgewerkt"

    async def test_update_patient_not_found(self, client, auth_headers):
        resp = await client.put("/api/patients/99999", json={
            "woonplaats": "Test",
        }, headers=auth_headers)
        assert resp.status_code == 404

    async def test_delete_patient(self, client, auth_headers, test_patient):
        pid = test_patient["id"]
        resp = await client.delete(f"/api/patients/{pid}", headers=auth_headers)
        assert resp.status_code == 200
        assert "verwijderd" in resp.json()["detail"]
        get_resp = await client.get(f"/api/patients/{pid}", headers=auth_headers)
        assert get_resp.status_code == 404

    async def test_delete_patient_not_found(self, client, auth_headers):
        resp = await client.delete("/api/patients/99999", headers=auth_headers)
        assert resp.status_code == 404

    async def test_list_patients_after_create(self, client, auth_headers, test_patient):
        resp = await client.get("/api/patients", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 1
        assert any(p["id"] == test_patient["id"] for p in data)
