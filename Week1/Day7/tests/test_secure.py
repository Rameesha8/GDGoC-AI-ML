def test_secure_data_401_without_key(client):
    r = client.get("/secure-data")
    assert r.status_code == 401


def test_secure_data_200_with_key(client):
    r = client.get("/secure-data", headers={"X-API-Key": "test-key"})
    assert r.status_code == 200
    assert r.json()["secret_data"] == "approved"
