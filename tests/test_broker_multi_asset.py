"""Tests for multi-asset order support (options, futures, forex, non-US stocks)."""
from unittest.mock import MagicMock, patch

from backend.services.broker_service import BrokerService, _pending_orders


def test_submit_options_order(client):
    """Submit an options order with expiry, strike, right."""
    res = client.post("/api/broker/order", json={
        "symbol": "AAPL",
        "side": "buy",
        "qty": 1,
        "order_type": "limit",
        "asset_type": "OPT",
        "expiry": "20260320",
        "strike": 200.0,
        "right": "C",
        "multiplier": "100",
        "limit_price": 5.50,
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "pending_confirmation"
    assert "type=OPT" in data["summary"]
    assert "exp=20260320" in data["summary"]
    assert "strike=200.0" in data["summary"]
    assert "right=C" in data["summary"]
    assert "limit=5.5" in data["summary"]


def test_submit_futures_order(client):
    """Submit a futures order with expiry and multiplier."""
    res = client.post("/api/broker/order", json={
        "symbol": "ES",
        "side": "buy",
        "qty": 2,
        "order_type": "market",
        "asset_type": "FUT",
        "expiry": "20260620",
        "multiplier": "50",
        "exchange": "CME",
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "pending_confirmation"
    assert "type=FUT" in data["summary"]
    assert "exp=20260620" in data["summary"]
    assert "exch=CME" in data["summary"]


def test_submit_forex_order(client):
    """Submit a forex order with pair_currency."""
    res = client.post("/api/broker/order", json={
        "symbol": "USD",
        "side": "buy",
        "qty": 100000,
        "order_type": "market",
        "asset_type": "CASH",
        "pair_currency": "JPY",
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "pending_confirmation"
    assert "type=CASH" in data["summary"]
    assert "pair=JPY" in data["summary"]


def test_submit_non_us_stock_order(client):
    """Submit a non-US stock order with exchange and currency."""
    res = client.post("/api/broker/order", json={
        "symbol": "SAP",
        "side": "buy",
        "qty": 10,
        "order_type": "limit",
        "exchange": "IBIS",
        "currency": "EUR",
        "limit_price": 180.0,
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "pending_confirmation"
    assert "exch=IBIS" in data["summary"]
    assert "ccy=EUR" in data["summary"]


def test_simple_stock_order_unchanged(client):
    """A plain stock order still works with default spec fields."""
    res = client.post("/api/broker/order", json={
        "symbol": "MSFT",
        "side": "buy",
        "qty": 5,
        "order_type": "market",
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "pending_confirmation"
    assert data["summary"] == "buy 5.0 MSFT (market)"


def test_confirm_options_order_uses_contract_spec(db):
    """Confirming a non-STK order calls submit_order_with_spec."""
    svc = BrokerService(db)
    # Create a user first
    from backend.models.user import User
    user = User(id="test-user", name="Test")
    db.add(user)
    db.commit()

    # Submit options order
    result = svc.submit_order(
        symbol="AAPL", side="buy", qty=1, order_type="limit",
        asset_type="OPT", expiry="20260320", strike=200.0, right="C",
        multiplier="100", limit_price=5.50,
    )
    order_id = result["order_id"]

    # Mock the broker
    mock_broker = MagicMock()
    mock_broker.submit_order_with_spec.return_value = "mock-order-123"

    with patch.object(svc, "_get_broker", return_value=mock_broker):
        confirm_result = svc.confirm_order(order_id, "test-user")

    assert confirm_result["status"] == "submitted"
    mock_broker.submit_order_with_spec.assert_called_once()
    # Verify ContractSpec was passed
    call_args = mock_broker.submit_order_with_spec.call_args
    spec = call_args[0][1]  # second positional arg
    assert spec.asset_type == "OPT"
    assert spec.strike == 200.0
    assert spec.right == "C"


def test_confirm_stock_order_uses_submit_order(db):
    """Confirming a plain STK order calls submit_order (not with_spec)."""
    svc = BrokerService(db)
    from backend.models.user import User
    user = User(id="test-user2", name="Test2")
    db.add(user)
    db.commit()

    result = svc.submit_order(symbol="MSFT", side="buy", qty=5, order_type="market")
    order_id = result["order_id"]

    mock_broker = MagicMock()
    mock_broker.submit_order.return_value = "mock-order-456"

    with patch.object(svc, "_get_broker", return_value=mock_broker):
        confirm_result = svc.confirm_order(order_id, "test-user2")

    assert confirm_result["status"] == "submitted"
    mock_broker.submit_order.assert_called_once()
    mock_broker.submit_order_with_spec.assert_not_called()


def test_needs_contract_spec_logic():
    """_needs_contract_spec returns True for non-default specs."""
    svc = BrokerService.__new__(BrokerService)
    assert svc._needs_contract_spec({"asset_type": "OPT"}) is True
    assert svc._needs_contract_spec({"exchange": "TSE"}) is True
    assert svc._needs_contract_spec({"currency": "EUR"}) is True
    assert svc._needs_contract_spec({"asset_type": "STK", "exchange": "SMART", "currency": "USD"}) is False
    assert svc._needs_contract_spec({}) is False
