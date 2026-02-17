import json
from datetime import datetime, timedelta
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from backend.services.regime_detector import RegimeDetector
from backend.services.live_adapter_service import LiveAdapterService


# --- 6.1 RegimeDetector unit tests ---

def _make_ohlcv(n: int, base_price: float = 100.0, volatility: float = 0.01) -> pd.DataFrame:
    """Generate synthetic OHLCV data."""
    np.random.seed(42)
    returns = np.random.normal(0, volatility, n)
    prices = base_price * np.exp(np.cumsum(returns))
    return pd.DataFrame({
        "Open": prices * 0.999,
        "High": prices * 1.005,
        "Low": prices * 0.995,
        "Close": prices,
        "Volume": np.random.randint(1000, 10000, n),
    })


def test_volatility_ratio_normal():
    detector = RegimeDetector()
    data = _make_ohlcv(100, volatility=0.01)
    ratio = detector.compute_volatility_ratio(data)
    assert ratio is not None
    # With constant volatility, ratio should be close to 1.0
    assert 0.5 < ratio < 2.0


def test_volatility_ratio_insufficient_data():
    detector = RegimeDetector()
    data = _make_ohlcv(30)
    ratio = detector.compute_volatility_ratio(data, long=60)
    assert ratio is None


def test_trend_strength():
    detector = RegimeDetector()
    # Create uptrending data
    n = 30
    prices = np.linspace(100, 120, n)
    data = pd.DataFrame({
        "Open": prices * 0.999,
        "High": prices * 1.005,
        "Low": prices * 0.995,
        "Close": prices,
        "Volume": np.ones(n) * 5000,
    })
    trend = detector.compute_trend_strength(data)
    assert trend is not None
    assert trend > 0  # Uptrend


def test_trend_strength_downtrend():
    detector = RegimeDetector()
    n = 30
    prices = np.linspace(120, 100, n)
    data = pd.DataFrame({
        "Open": prices * 0.999,
        "High": prices * 1.005,
        "Low": prices * 0.995,
        "Close": prices,
        "Volume": np.ones(n) * 5000,
    })
    trend = detector.compute_trend_strength(data)
    assert trend is not None
    assert trend < 0  # Downtrend


def test_detect_regime_high_volatility():
    detector = RegimeDetector()
    # Create data with high recent volatility
    calm = _make_ohlcv(60, volatility=0.005)
    volatile = _make_ohlcv(20, base_price=float(calm["Close"].iloc[-1]), volatility=0.04)
    data = pd.concat([calm, volatile], ignore_index=True)

    config = SimpleNamespace(vol_ratio_high=1.5, vol_ratio_low=0.5)
    events = detector.detect_regime_change(data, config)
    vol_events = [e for e in events if e["type"] == "high_volatility"]
    assert len(vol_events) >= 1


def test_detect_regime_no_change():
    detector = RegimeDetector()
    data = _make_ohlcv(100, volatility=0.01)
    config = SimpleNamespace(vol_ratio_high=1.5, vol_ratio_low=0.5)
    events = detector.detect_regime_change(data, config)
    # With stable volatility, no regime change expected
    vol_events = [e for e in events if e["type"] in ("high_volatility", "low_volatility")]
    assert len(vol_events) == 0


# --- 6.2 LiveAdapterService unit tests ---

def test_cap_params_within_limits():
    current = {"short_window": 10, "long_window": 50}
    proposed = {"short_window": 12, "long_window": 55}
    grid = {"short_window": [5, 10, 15, 20], "long_window": [20, 50, 80, 100]}
    capped, was_capped = LiveAdapterService.cap_params(current, proposed, grid, 25.0)
    assert was_capped is False
    assert capped["short_window"] == 12
    assert capped["long_window"] == 55


def test_cap_params_exceeds_limits():
    current = {"short_window": 5}
    proposed = {"short_window": 20}
    grid = {"short_window": [5, 10, 15, 20]}
    # Max change = 25% of range (15) = 3.75, so 5 + 3.75 = 8.75 → rounded to 9
    capped, was_capped = LiveAdapterService.cap_params(current, proposed, grid, 25.0)
    assert was_capped is True
    assert capped["short_window"] == 9  # 5 + round(3.75)


def test_cap_params_non_numeric():
    current = {"ma_type": "sma"}
    proposed = {"ma_type": "ema"}
    grid = {"ma_type": ["sma", "ema"]}
    capped, was_capped = LiveAdapterService.cap_params(current, proposed, grid, 25.0)
    assert was_capped is False
    assert capped["ma_type"] == "ema"


def _create_strategy_and_config(db):
    """Helper to create a strategy + adaptation config with valid FK."""
    from backend.models.user import User
    from backend.models.strategy_config import StrategyConfig
    from backend.models.live_adaptation import LiveAdaptationConfig

    # Ensure default user exists
    user = db.query(User).filter(User.id == "default").first()
    if not user:
        db.add(User(id="default", name="Default User"))
        db.commit()

    strategy = StrategyConfig(
        user_id="default", name="test_cooldown", strategy_type="momentum",
        params=json.dumps({"short_window": 10}),
    )
    db.add(strategy)
    db.commit()
    db.refresh(strategy)

    config = LiveAdaptationConfig(
        user_id="default", strategy_id=strategy.id, schedule="0 2 * * SAT",
        cooldown_days=7, status="active",
    )
    db.add(config)
    db.commit()
    db.refresh(config)
    return config


def test_cooldown_check_no_events(client):
    """Cooldown returns False when no events exist."""
    from backend.core.database import SessionLocal

    db = SessionLocal()
    try:
        config = _create_strategy_and_config(db)
        svc = LiveAdapterService(db)
        assert svc.check_cooldown(config) is False
    finally:
        db.close()


def test_cooldown_check_active(client):
    """Cooldown returns True when a recent event exists."""
    from backend.core.database import SessionLocal
    from backend.models.live_adaptation import AdaptationEvent

    db = SessionLocal()
    try:
        config = _create_strategy_and_config(db)

        event = AdaptationEvent(
            config_id=config.id, trigger_type="scheduled",
            proposed_params="{}", status="applied",
            created_at=datetime.utcnow() - timedelta(days=2),
        )
        db.add(event)
        db.commit()

        svc = LiveAdapterService(db)
        assert svc.check_cooldown(config) is True
    finally:
        db.close()


def test_cooldown_check_expired(client):
    """Cooldown returns False when event is older than cooldown_days."""
    from backend.core.database import SessionLocal
    from backend.models.live_adaptation import AdaptationEvent

    db = SessionLocal()
    try:
        config = _create_strategy_and_config(db)

        event = AdaptationEvent(
            config_id=config.id, trigger_type="scheduled",
            proposed_params="{}", status="applied",
            created_at=datetime.utcnow() - timedelta(days=10),
        )
        db.add(event)
        db.commit()

        svc = LiveAdapterService(db)
        assert svc.check_cooldown(config) is False
    finally:
        db.close()


# --- 6.3 API tests ---

def test_create_adaptation(client):
    # First create a strategy
    client.post("/api/strategies/", json={
        "name": "test_adapt", "strategy_type": "momentum", "params": {"short_window": 10},
    })
    strategies = client.get("/api/strategies/").json()
    strategy_id = strategies[0]["id"]

    resp = client.post("/api/optimize/live", json={
        "strategy_id": strategy_id,
        "schedule": "0 2 * * SAT",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "active"
    assert data["strategy_id"] == strategy_id


def test_list_adaptations(client):
    # Create a strategy + adaptation
    client.post("/api/strategies/", json={
        "name": "test_list", "strategy_type": "momentum", "params": {},
    })
    strategies = client.get("/api/strategies/").json()
    strategy_id = strategies[0]["id"]
    client.post("/api/optimize/live", json={
        "strategy_id": strategy_id,
        "schedule": "0 2 * * SAT",
    })

    resp = client.get("/api/optimize/live")
    assert resp.status_code == 200
    configs = resp.json()
    assert len(configs) >= 1
    assert configs[0]["status"] == "active"


def test_stop_adaptation(client):
    client.post("/api/strategies/", json={
        "name": "test_stop", "strategy_type": "momentum", "params": {},
    })
    strategies = client.get("/api/strategies/").json()
    strategy_id = strategies[0]["id"]
    create_resp = client.post("/api/optimize/live", json={
        "strategy_id": strategy_id,
        "schedule": "0 2 * * SAT",
    })
    config_id = create_resp.json()["id"]

    resp = client.delete(f"/api/optimize/live/{config_id}")
    assert resp.status_code == 200
    assert resp.json()["status"] == "stopped"


def test_stop_nonexistent_adaptation(client):
    resp = client.delete("/api/optimize/live/999")
    assert resp.status_code == 404


def test_adaptation_history_empty(client):
    client.post("/api/strategies/", json={
        "name": "test_hist", "strategy_type": "momentum", "params": {},
    })
    strategies = client.get("/api/strategies/").json()
    strategy_id = strategies[0]["id"]
    create_resp = client.post("/api/optimize/live", json={
        "strategy_id": strategy_id,
        "schedule": "0 2 * * SAT",
    })
    config_id = create_resp.json()["id"]

    resp = client.get(f"/api/optimize/live/{config_id}/history")
    assert resp.status_code == 200
    assert resp.json() == []


def test_adaptation_history_not_found(client):
    resp = client.get("/api/optimize/live/999/history")
    assert resp.status_code == 404
