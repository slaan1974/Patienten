import pytest


class TestLocks:
    async def test_acquire_lock_free(self, client, auth_headers):
        resp = await client.post("/api/lock", json={
            "table_name": "patients",
            "record_id": 1,
        }, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["locked"] is True

    async def test_acquire_lock_conflict(self, client, auth_headers, second_headers):
        resp1 = await client.post("/api/lock", json={
            "table_name": "patients",
            "record_id": 1,
        }, headers=auth_headers)
        assert resp1.status_code == 200
        resp2 = await client.post("/api/lock", json={
            "table_name": "patients",
            "record_id": 1,
        }, headers=second_headers)
        assert resp2.status_code == 423

    async def test_acquire_lock_same_user_heartbeat(self, client, auth_headers):
        resp1 = await client.post("/api/lock", json={
            "table_name": "patients",
            "record_id": 1,
        }, headers=auth_headers)
        assert resp1.status_code == 200
        resp2 = await client.post("/api/lock", json={
            "table_name": "patients",
            "record_id": 1,
        }, headers=auth_headers)
        assert resp2.status_code == 200
        assert resp2.json()["locked"] is True

    async def test_lock_status_locked(self, client, auth_headers):
        await client.post("/api/lock", json={
            "table_name": "patients",
            "record_id": 1,
        }, headers=auth_headers)
        resp = await client.get("/api/lock/patients/1", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["locked"] is True
        assert "locked_by" in data
        assert "locked_at" in data
        assert "expires_at" in data

    async def test_lock_status_unlocked(self, client, auth_headers):
        resp = await client.get("/api/lock/patients/1", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["locked"] is False

    async def test_release_lock_owner(self, client, auth_headers):
        await client.post("/api/lock", json={
            "table_name": "patients",
            "record_id": 1,
        }, headers=auth_headers)
        resp = await client.request("DELETE", "/api/lock", json={
            "table_name": "patients",
            "record_id": 1,
        }, headers=auth_headers)
        assert resp.status_code == 200
        assert "vrijgegeven" in resp.json()["detail"]
        status = await client.get("/api/lock/patients/1", headers=auth_headers)
        assert status.json()["locked"] is False

    async def test_release_lock_not_owner(self, client, auth_headers, second_headers):
        await client.post("/api/lock", json={
            "table_name": "patients",
            "record_id": 1,
        }, headers=auth_headers)
        resp = await client.request("DELETE", "/api/lock", json={
            "table_name": "patients",
            "record_id": 1,
        }, headers=second_headers)
        assert resp.status_code == 400

    async def test_release_all_locks(self, client, auth_headers):
        await client.post("/api/lock", json={
            "table_name": "patients",
            "record_id": 1,
        }, headers=auth_headers)
        await client.post("/api/lock", json={
            "table_name": "patients",
            "record_id": 2,
        }, headers=auth_headers)
        resp = await client.post("/api/lock/release-all", headers=auth_headers)
        assert resp.status_code == 200
        assert "2" in resp.json()["detail"]

    async def test_refresh_lock_owner(self, client, auth_headers):
        await client.post("/api/lock", json={
            "table_name": "patients",
            "record_id": 1,
        }, headers=auth_headers)
        resp = await client.post("/api/lock/refresh", json={
            "table_name": "patients",
            "record_id": 1,
        }, headers=auth_headers)
        assert resp.status_code == 200
        assert "ververst" in resp.json()["detail"]

    async def test_refresh_lock_not_owner(self, client, auth_headers, second_headers):
        await client.post("/api/lock", json={
            "table_name": "patients",
            "record_id": 1,
        }, headers=auth_headers)
        resp = await client.post("/api/lock/refresh", json={
            "table_name": "patients",
            "record_id": 1,
        }, headers=second_headers)
        assert resp.status_code == 400
