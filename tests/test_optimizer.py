import json

import pytest

from backend.services.optimizer_service import OptimizerService, DEFAULT_GRIDS, MAX_COMBINATIONS


# --- 6.1 Service tests ---

def test_default_grids_exist():
    svc = OptimizerService.__new__(OptimizerService)
    for strategy_type in ["momentum", "mean_reversion", "stat_arb", "market_making"]:
        grid = svc.get_default_grid(strategy_type)
        assert len(grid) > 0, f"No default grid for {strategy_type}"


def test_grid_size_validation():
    svc = OptimizerService.__new__(OptimizerService)
    # Small grid should pass
    grid = {"a": [1, 2], "b": [3, 4]}
    assert svc.validate_grid_size(grid) == 4

    # Large grid should fail
    grid = {"a": list(range(10)), "b": list(range(10)), "c": list(range(10))}
    with pytest.raises(ValueError, match="exceeds maximum"):
        svc.validate_grid_size(grid)


def test_data_length_validation():
    svc = OptimizerService.__new__(OptimizerService)
    # Sufficient data
    svc.validate_data_length(1260, 5)

    # Insufficient data
    with pytest.raises(ValueError, match="Insufficient data"):
        svc.validate_data_length(800, 5)


def test_expand_grid():
    svc = OptimizerService.__new__(OptimizerService)
    grid = {"a": [1, 2], "b": ["x", "y"]}
    expanded = svc._expand_grid(grid)
    assert len(expanded) == 4
    assert {"a": 1, "b": "x"} in expanded
    assert {"a": 2, "b": "y"} in expanded


def test_default_grid_sizes_within_limit():
    svc = OptimizerService.__new__(OptimizerService)
    for strategy_type, grid in DEFAULT_GRIDS.items():
        total = svc.validate_grid_size(grid)
        assert total <= MAX_COMBINATIONS, f"{strategy_type} default grid too large: {total}"


# --- 6.2 API route tests ---

def test_list_jobs_empty(client):
    resp = client.get("/api/optimize/")
    assert resp.status_code == 200
    assert resp.json() == []


def test_get_job_not_found(client):
    resp = client.get("/api/optimize/999")
    assert resp.status_code == 404


def test_submit_strategy_optimization(client):
    resp = client.post("/api/optimize/strategy", json={
        "strategy_type": "momentum",
        "symbols": ["SPY"],
        "start": "2020-01-01",
        "end": "2024-12-31",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "job_id" in data
    assert data["status"] == "running"
    assert "total_combinations" in data


def test_submit_with_oversized_grid(client):
    resp = client.post("/api/optimize/strategy", json={
        "strategy_type": "momentum",
        "symbols": ["SPY"],
        "start": "2020-01-01",
        "end": "2024-12-31",
        "param_grid": {
            "short_window": list(range(1, 30)),
            "long_window": list(range(30, 60)),
        },
    })
    assert resp.status_code == 400
    assert "exceeds maximum" in resp.json()["detail"]


def test_cancel_nonexistent_job(client):
    resp = client.delete("/api/optimize/999")
    assert resp.status_code == 404


def test_list_jobs_after_submit(client):
    # Submit a job
    client.post("/api/optimize/strategy", json={
        "strategy_type": "momentum",
        "symbols": ["SPY"],
        "start": "2020-01-01",
        "end": "2024-12-31",
    })
    # List should show at least one job
    resp = client.get("/api/optimize/")
    assert resp.status_code == 200
    jobs = resp.json()
    assert len(jobs) >= 1
    assert jobs[0]["strategy_type"] == "momentum"


# --- Sweep / auto-strategy-selection tests ---

def test_build_recommendation():
    svc = OptimizerService.__new__(OptimizerService)
    by_strategy = {
        "momentum": [
            {"mean_sharpe": 1.5, "params": {"short_window": 10}, "sharpe_std": 0.2},
        ],
        "mean_reversion": [
            {"mean_sharpe": 0.8, "params": {"window": 20}, "sharpe_std": 0.5},
        ],
        "stat_arb": [],
        "market_making": [
            {"mean_sharpe": -0.3, "params": {"spread_bps": 10}, "sharpe_std": 0.1},
        ],
    }
    rec = svc._build_recommendation(by_strategy)
    assert rec["strategy_type"] == "momentum"
    assert rec["mean_sharpe"] == 1.5
    assert rec["confidence"] == "high"
    assert rec["recommended"] is True


def test_build_recommendation_low_confidence():
    svc = OptimizerService.__new__(OptimizerService)
    by_strategy = {
        "momentum": [
            {"mean_sharpe": 1.0, "params": {"short_window": 10}, "sharpe_std": 1.2},
        ],
    }
    rec = svc._build_recommendation(by_strategy)
    assert rec["confidence"] == "low"


def test_build_recommendation_negative_sharpe():
    svc = OptimizerService.__new__(OptimizerService)
    by_strategy = {
        "momentum": [
            {"mean_sharpe": -0.5, "params": {"short_window": 10}, "sharpe_std": 0.1},
        ],
    }
    rec = svc._build_recommendation(by_strategy)
    assert rec["recommended"] is False


def test_build_recommendation_empty():
    svc = OptimizerService.__new__(OptimizerService)
    rec = svc._build_recommendation({"momentum": [], "mean_reversion": []})
    assert rec["strategy_type"] is None
    assert rec["confidence"] == "none"


def test_submit_sweep(client):
    resp = client.post("/api/optimize/sweep", json={
        "symbols": ["SPY"],
        "start": "2020-01-01",
        "end": "2024-12-31",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "job_id" in data
    assert data["status"] == "running"
    assert "strategy_types" in data


def test_sweep_job_in_list(client):
    client.post("/api/optimize/sweep", json={
        "symbols": ["SPY"],
        "start": "2020-01-01",
        "end": "2024-12-31",
    })
    resp = client.get("/api/optimize/")
    assert resp.status_code == 200
    jobs = resp.json()
    sweep_jobs = [j for j in jobs if j["job_type"] == "sweep"]
    assert len(sweep_jobs) >= 1
    assert sweep_jobs[0]["strategy_type"] == "all"
