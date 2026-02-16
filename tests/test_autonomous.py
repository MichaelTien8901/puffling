"""Tests for autonomous trading features."""


def test_scheduler_crud(client):
    # Create
    res = client.post("/api/scheduler/", json={
        "job_type": "market_scan",
        "schedule": "0 9 * * 1-5",
        "config": {"strategy_type": "momentum", "symbols": ["SPY"]},
    })
    assert res.status_code == 200
    job_id = res.json()["id"]

    # List
    res = client.get("/api/scheduler/")
    assert res.status_code == 200
    assert len(res.json()) >= 1

    # Update
    res = client.put(f"/api/scheduler/{job_id}", json={"enabled": False})
    assert res.status_code == 200

    # Delete
    res = client.delete(f"/api/scheduler/{job_id}")
    assert res.status_code == 200


def test_portfolio_goals_crud(client):
    # Create
    res = client.post("/api/portfolio/goals/", json={
        "name": "balanced",
        "target_weights": {"SPY": 0.6, "AGG": 0.3, "GLD": 0.1},
        "drift_threshold": 0.05,
        "rebalance_mode": "alert",
    })
    assert res.status_code == 200
    goal_id = res.json()["id"]

    # List
    res = client.get("/api/portfolio/goals/")
    assert res.status_code == 200
    assert len(res.json()) >= 1

    # Get drift
    res = client.get(f"/api/portfolio/goals/{goal_id}/drift")
    assert res.status_code == 200
    assert "drift" in res.json()

    # Update
    res = client.put(f"/api/portfolio/goals/{goal_id}", json={"drift_threshold": 0.03})
    assert res.status_code == 200

    # Delete
    res = client.delete(f"/api/portfolio/goals/{goal_id}")
    assert res.status_code == 200


def test_alerts_crud(client):
    # Create
    res = client.post("/api/alerts/", json={
        "alert_type": "price",
        "condition": {"symbol": "AAPL", "above": 200},
    })
    assert res.status_code == 200
    alert_id = res.json()["id"]

    # List
    res = client.get("/api/alerts/")
    assert res.status_code == 200
    assert len(res.json()) >= 1

    # Disable
    res = client.put(f"/api/alerts/{alert_id}", json={"enabled": False})
    assert res.status_code == 200

    # History
    res = client.get("/api/alerts/history")
    assert res.status_code == 200

    # Delete
    res = client.delete(f"/api/alerts/{alert_id}")
    assert res.status_code == 200


def test_safety_controls(client):
    # Get defaults
    res = client.get("/api/safety/")
    assert res.status_code == 200
    safety = res.json()
    assert safety["paper_trading"] is True
    assert safety["kill_switch"] is False

    # Activate kill switch
    res = client.post("/api/safety/kill")
    assert res.status_code == 200
    assert "kill_switch_active" in res.json()["status"]

    # Verify kill switch is on
    res = client.get("/api/safety/")
    assert res.json()["kill_switch"] is True

    # Resume
    res = client.post("/api/safety/resume")
    assert res.status_code == 200

    # Update settings
    res = client.put("/api/safety/", json={"max_daily_trades": 5})
    assert res.status_code == 200


def test_safety_service_can_trade(db):
    from backend.models.user import User
    from backend.services.safety_service import SafetyService

    db.add(User(id="default", name="Test"))
    db.commit()

    svc = SafetyService(db)

    # Default: can trade (paper mode)
    assert svc.can_trade("default") is True

    # Kill switch blocks trading
    svc.activate_kill_switch("default")
    assert svc.can_trade("default") is False

    # Resume allows trading
    svc.deactivate_kill_switch("default")
    assert svc.can_trade("default") is True
