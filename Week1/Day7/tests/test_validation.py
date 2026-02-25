def test_create_item_validation_error_returns_400(client):
    # invalid: empty name + negative price
    payload = {"name": "", "price": -1, "in_stock": True}
    r = client.post("/items", json=payload)
    assert r.status_code == 400
    body = r.json()
    assert body["error_type"] == "validation_error"
