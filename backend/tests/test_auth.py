import pytest


class TestAuth:
    async def test_register_new_user(self, client):
        resp = await client.post("/api/auth/register", json={
            "username": "newuser",
            "password": "secret123",
            "display_name": "Nieuwe Gebruiker",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "newuser"
        assert data["display_name"] == "Nieuwe Gebruiker"
        assert "id" in data

    async def test_register_duplicate_username(self, client, demo_user):
        resp = await client.post("/api/auth/register", json={
            "username": "demo",
            "password": "demo123",
            "display_name": "Demo Gebruiker",
        })
        assert resp.status_code == 400
        assert "bestaat" in resp.json()["detail"]

    async def test_login_correct(self, client, demo_user):
        resp = await client.post("/api/auth/login", json={
            "username": "demo",
            "password": "demo123",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password(self, client, demo_user):
        resp = await client.post("/api/auth/login", json={
            "username": "demo",
            "password": "wrongpass",
        })
        assert resp.status_code == 401

    async def test_login_unknown_user(self, client):
        resp = await client.post("/api/auth/login", json={
            "username": "nobody",
            "password": "irrelevant",
        })
        assert resp.status_code == 401

    async def test_refresh_token_valid(self, client, demo_user):
        login_resp = await client.post("/api/auth/login", json={
            "username": "demo",
            "password": "demo123",
        })
        refresh_token = login_resp.json()["refresh_token"]
        resp = await client.post("/api/auth/refresh", json={
            "refresh_token": refresh_token,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data

    async def test_refresh_token_invalid(self, client):
        resp = await client.post("/api/auth/refresh", json={
            "refresh_token": "invalid_token_here",
        })
        assert resp.status_code == 401

    async def test_endpoint_without_token(self, client):
        resp = await client.get("/api/patients")
        assert resp.status_code == 401
        assert "Niet geauthenticeerd" in resp.json()["detail"]

    async def test_endpoint_with_invalid_token(self, client):
        resp = await client.get("/api/patients", headers={
            "Authorization": "Bearer invalid_token"
        })
        assert resp.status_code == 401
