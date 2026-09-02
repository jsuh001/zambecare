from sqlalchemy import select

from app.models.identity import RefreshSession, UserAccount

REGISTER_PAYLOAD = {
    "email": "synthetic.patient@example.com",
    "password": "StrongPass123!",
    "first_name": "Jamie",
    "last_name": "Synthetic",
    "date_of_birth": "1990-05-20",
    "sex_at_birth": "FEMALE",
    "phone": "555-0101",
    "state": "TX",
    "city": "Dallas",
    "postal_code": "75201",
}


def register_and_login(client):
    assert client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD).status_code == 201
    response = client.post(
        "/api/v1/auth/login",
        json={"email": REGISTER_PAYLOAD["email"], "password": REGISTER_PAYLOAD["password"]},
    )
    assert response.status_code == 200
    return response.json()


def test_register_hashes_password(client, db_session) -> None:
    response = client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    assert response.status_code == 201
    assert response.json()["roles"] == ["PATIENT"]
    user = db_session.scalar(select(UserAccount).where(UserAccount.email == REGISTER_PAYLOAD["email"]))
    assert user is not None
    assert user.password_hash != REGISTER_PAYLOAD["password"]
    assert user.password_hash.startswith("$argon2")


def test_duplicate_registration_is_rejected(client) -> None:
    assert client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD).status_code == 201
    response = client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    assert response.status_code == 409


def test_login_profile_refresh_and_logout(client, db_session) -> None:
    tokens = register_and_login(client)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    profile = client.get("/api/v1/patients/me", headers=headers)
    assert profile.status_code == 200
    assert profile.json()["first_name"] == "Jamie"
    assert profile.json()["city"] == "Dallas"
    assert profile.json()["country"] == "United States"

    updated = client.patch(
        "/api/v1/patients/me",
        json={"preferred_language": "French", "city": "Austin", "last_name": "Corrected"},
        headers=headers,
    )
    assert updated.status_code == 200
    assert updated.json()["preferred_language"] == "French"
    assert updated.json()["city"] == "Austin"
    assert updated.json()["last_name"] == "Corrected"

    refreshed = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
    )
    assert refreshed.status_code == 200
    assert refreshed.json()["refresh_token"] != tokens["refresh_token"]

    old_session = db_session.scalar(
        select(RefreshSession).where(RefreshSession.token_hash.is_not(None)).limit(1)
    )
    assert old_session is not None
    assert old_session.revoked_at is not None

    new_refresh = refreshed.json()["refresh_token"]
    assert client.post("/api/v1/auth/logout", json={"refresh_token": new_refresh}).status_code == 204
    assert client.post("/api/v1/auth/refresh", json={"refresh_token": new_refresh}).status_code == 401


def test_incorrect_password_is_rejected(client) -> None:
    client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": REGISTER_PAYLOAD["email"], "password": "WrongPassword123!"},
    )
    assert response.status_code == 401


def test_patient_endpoint_requires_authentication(client) -> None:
    assert client.get("/api/v1/patients/me").status_code == 401


def test_patient_cannot_create_facility(client) -> None:
    tokens = register_and_login(client)
    response = client.post(
        "/api/v1/facilities",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
        json={
            "facility_name": "Unauthorized Facility",
            "facility_type": "CLINIC",
            "address_line_1": "1 Test Road",
            "city": "Dallas",
            "state_code": "TX",
            "postal_code": "75201",
        },
    )
    assert response.status_code == 403
