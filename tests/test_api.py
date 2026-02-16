def test_health(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_settings_crud(client):
    # Set
    res = client.put("/api/settings/", json={"key": "theme", "value": "dark"})
    assert res.status_code == 200

    # Get
    res = client.get("/api/settings/theme")
    assert res.status_code == 200
    assert res.json()["value"] == "dark"

    # List
    res = client.get("/api/settings/")
    assert res.status_code == 200
    assert "theme" in res.json()

    # Delete
    res = client.delete("/api/settings/theme")
    assert res.status_code == 200


def test_strategies_crud(client):
    # Create
    res = client.post("/api/strategies/", json={"name": "test", "strategy_type": "momentum", "params": {}})
    assert res.status_code == 200
    config_id = res.json()["id"]

    # List
    res = client.get("/api/strategies/")
    assert res.status_code == 200
    assert len(res.json()) == 1

    # Delete
    res = client.delete(f"/api/strategies/{config_id}")
    assert res.status_code == 200


def test_model_types(client):
    res = client.get("/api/models/types")
    assert res.status_code == 200
    types = res.json()
    assert "ml" in types
    assert "deep" in types
    assert "ensembles" in types
    assert "rl" in types


def test_unknown_route(client):
    res = client.get("/api/nonexistent")
    assert res.status_code == 404
