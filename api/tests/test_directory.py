def test_facility_search(client, directory_data) -> None:
    response = client.get("/api/v1/facilities?city=Dallas&state=TX")
    assert response.status_code == 200
    assert response.json()[0]["facility_name"] == "ZambeCare Dallas Clinic"


def test_provider_search(client, directory_data) -> None:
    response = client.get("/api/v1/providers?specialty=PRIMARY_CARE")
    assert response.status_code == 200
    assert response.json()[0]["last_name"] == "Testdoctor"


def test_provider_search_by_city(client, directory_data) -> None:
    match = client.get("/api/v1/providers?city=Dallas")
    assert match.status_code == 200
    assert [p["last_name"] for p in match.json()] == ["Testdoctor"]

    miss = client.get("/api/v1/providers?city=Nowhere")
    assert miss.status_code == 200
    assert miss.json() == []
