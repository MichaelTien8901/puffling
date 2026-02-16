"""End-to-end smoke test: verify app starts, basic flows work."""


def test_app_starts_and_health(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_full_strategy_flow(client):
    # Create a strategy config
    res = client.post("/api/strategies/", json={
        "name": "e2e_momentum",
        "strategy_type": "momentum",
        "params": {"short_window": 10, "long_window": 30},
    })
    assert res.status_code == 200
    strategy_id = res.json()["id"]

    # List strategies
    res = client.get("/api/strategies/")
    assert res.status_code == 200
    assert any(s["name"] == "e2e_momentum" for s in res.json())

    # Cleanup
    res = client.delete(f"/api/strategies/{strategy_id}")
    assert res.status_code == 200


def test_settings_roundtrip(client):
    client.put("/api/settings/", json={"key": "paper_trading", "value": True})
    res = client.get("/api/settings/paper_trading")
    assert res.json()["value"] is True
    client.delete("/api/settings/paper_trading")


def test_model_types_available(client):
    res = client.get("/api/models/types")
    assert res.status_code == 200
    data = res.json()
    assert "ensembles" in data
    assert "deep" in data
    assert "rl" in data


def test_factor_library_available(client):
    res = client.get("/api/factors/library")
    assert res.status_code == 200
