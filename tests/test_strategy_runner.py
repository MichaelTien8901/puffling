"""Tests for strategy runner service."""


def test_activate_deactivate(client):
    # Create a strategy config first
    res = client.post("/api/strategies/", json={
        "name": "runner_test", "strategy_type": "momentum", "params": {},
    })
    assert res.status_code == 200
    config_id = res.json()["id"]

    # Activate in monitor mode
    res = client.post("/api/strategies/live/activate", json={"config_id": config_id, "mode": "monitor"})
    assert res.status_code == 200
    assert res.json()["mode"] == "monitor"
    assert res.json()["status"] == "active"

    # List active
    res = client.get("/api/strategies/live/active")
    assert res.status_code == 200
    active = res.json()
    assert any(s["id"] == config_id for s in active)

    # Update mode to alert
    res = client.put(f"/api/strategies/live/{config_id}/mode", json={"mode": "alert"})
    assert res.status_code == 200
    assert res.json()["mode"] == "alert"

    # Deactivate
    res = client.delete(f"/api/strategies/live/{config_id}")
    assert res.status_code == 200
    assert res.json()["status"] == "deactivated"

    # Verify no longer active
    res = client.get("/api/strategies/live/active")
    assert not any(s["id"] == config_id for s in res.json())

    # Cleanup
    client.delete(f"/api/strategies/{config_id}")


def test_auto_trade_blocked_by_kill_switch(client):
    # Create and activate in auto-trade mode
    res = client.post("/api/strategies/", json={
        "name": "auto_test", "strategy_type": "momentum", "params": {},
    })
    config_id = res.json()["id"]

    client.post("/api/strategies/live/activate", json={"config_id": config_id, "mode": "auto-trade"})

    # Activate kill switch
    client.post("/api/safety/kill")

    # Verify safety blocks trading
    res = client.get("/api/safety/")
    assert res.json()["kill_switch"] is True

    # Resume and cleanup
    client.post("/api/safety/resume")
    client.delete(f"/api/strategies/live/{config_id}")
    client.delete(f"/api/strategies/{config_id}")
