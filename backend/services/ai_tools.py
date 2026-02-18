AI_TOOL_SCHEMAS = [
    {
        "name": "get_market_data",
        "description": "Fetch OHLCV market data for a symbol over a date range",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {"type": "string", "description": "Ticker symbol (e.g., AAPL)"},
                "start": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                "end": {"type": "string", "description": "End date (YYYY-MM-DD)"},
            },
            "required": ["symbol", "start", "end"],
        },
    },
    {
        "name": "run_backtest",
        "description": "Run a backtest with a given strategy on symbols over a date range",
        "parameters": {
            "type": "object",
            "properties": {
                "strategy_type": {"type": "string", "description": "Strategy name (e.g., momentum)"},
                "symbols": {"type": "array", "items": {"type": "string"}, "description": "List of symbols"},
                "start": {"type": "string"},
                "end": {"type": "string"},
                "params": {"type": "object", "description": "Strategy parameters"},
            },
            "required": ["strategy_type", "symbols", "start", "end"],
        },
    },
    {
        "name": "analyze_sentiment",
        "description": "Analyze sentiment of financial text using NLP lexicons",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to analyze"},
            },
            "required": ["text"],
        },
    },
    {
        "name": "compute_factors",
        "description": "Compute alpha factors for given symbols",
        "parameters": {
            "type": "object",
            "properties": {
                "symbols": {"type": "array", "items": {"type": "string"}},
                "start": {"type": "string"},
                "end": {"type": "string"},
            },
            "required": ["symbols", "start", "end"],
        },
    },
    {
        "name": "optimize_portfolio",
        "description": "Optimize portfolio weights for given symbols",
        "parameters": {
            "type": "object",
            "properties": {
                "symbols": {"type": "array", "items": {"type": "string"}},
                "start": {"type": "string"},
                "end": {"type": "string"},
                "method": {"type": "string", "enum": ["mean_variance", "risk_parity"]},
            },
            "required": ["symbols", "start", "end"],
        },
    },
    {
        "name": "place_order",
        "description": "Place a trading order (requires user confirmation). Supports stocks, options, futures, forex, and non-US stocks.",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {"type": "string"},
                "side": {"type": "string", "enum": ["buy", "sell"]},
                "qty": {"type": "number"},
                "order_type": {"type": "string", "enum": ["market", "limit", "stop", "stop_limit"]},
                "asset_type": {"type": "string", "enum": ["STK", "OPT", "FUT", "CASH"], "description": "Asset type (default STK)"},
                "exchange": {"type": "string", "description": "Exchange (default SMART)"},
                "currency": {"type": "string", "description": "Currency (default USD)"},
                "expiry": {"type": "string", "description": "Expiry YYYYMMDD for options/futures"},
                "strike": {"type": "number", "description": "Strike price for options"},
                "right": {"type": "string", "enum": ["C", "P"], "description": "Call or Put for options"},
                "multiplier": {"type": "string", "description": "Contract multiplier"},
                "pair_currency": {"type": "string", "description": "Second currency for forex (e.g. JPY)"},
                "limit_price": {"type": "number", "description": "Limit price for limit/stop_limit orders"},
                "stop_price": {"type": "number", "description": "Stop price for stop/stop_limit orders"},
                "time_in_force": {"type": "string", "enum": ["DAY", "GTC", "IOC", "FOK"]},
            },
            "required": ["symbol", "side", "qty"],
        },
    },
    {
        "name": "check_risk",
        "description": "Check portfolio risk metrics",
        "parameters": {
            "type": "object",
            "properties": {
                "symbols": {"type": "array", "items": {"type": "string"}},
                "weights": {"type": "array", "items": {"type": "number"}},
                "start": {"type": "string"},
                "end": {"type": "string"},
            },
            "required": ["symbols", "weights", "start", "end"],
        },
    },
    {
        "name": "get_position_size",
        "description": "Calculate position size using a given method (fixed_fractional, kelly, volatility)",
        "parameters": {
            "type": "object",
            "properties": {
                "method": {"type": "string", "enum": ["fixed_fractional", "kelly", "volatility"]},
                "params": {"type": "object", "description": "Method-specific parameters"},
            },
            "required": ["method", "params"],
        },
    },
    {
        "name": "get_account_info",
        "description": "Get current broker account info (equity, cash, buying power)",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
]


def execute_tool(tool_name: str, args: dict, user_id: str, db) -> dict:
    if tool_name == "get_market_data":
        from backend.services.data_service import DataService
        return DataService().get_ohlcv(args["symbol"], args["start"], args["end"])

    elif tool_name == "run_backtest":
        from backend.services.backtest_service import BacktestService
        svc = BacktestService(db)
        return svc.run(user_id, args["strategy_type"], args.get("params", {}), args["symbols"], args["start"], args["end"])

    elif tool_name == "analyze_sentiment":
        from backend.services.ai_service import AIService
        return AIService(db).analyze_sentiment(args["text"])

    elif tool_name == "compute_factors":
        from backend.services.factors_service import FactorsService
        return FactorsService().compute(args["symbols"], args["start"], args["end"])

    elif tool_name == "optimize_portfolio":
        from backend.services.portfolio_service import PortfolioService
        return PortfolioService().optimize(args["symbols"], args["start"], args["end"], args.get("method", "mean_variance"))

    elif tool_name == "place_order":
        from backend.services.broker_service import BrokerService
        return BrokerService(db).submit_order(
            symbol=args["symbol"], side=args["side"], qty=args["qty"],
            order_type=args.get("order_type", "market"),
            asset_type=args.get("asset_type", "STK"),
            exchange=args.get("exchange", "SMART"),
            currency=args.get("currency", "USD"),
            expiry=args.get("expiry"), strike=args.get("strike"),
            right=args.get("right"), multiplier=args.get("multiplier"),
            pair_currency=args.get("pair_currency"),
            limit_price=args.get("limit_price"), stop_price=args.get("stop_price"),
            time_in_force=args.get("time_in_force", "DAY"),
        )

    elif tool_name == "check_risk":
        from backend.services.risk_service import RiskService
        return RiskService().portfolio_risk(args["symbols"], args["weights"], args["start"], args["end"])

    elif tool_name == "get_position_size":
        from backend.services.risk_service import RiskService
        return RiskService().position_size(args["method"], **args.get("params", {}))

    elif tool_name == "get_account_info":
        from backend.services.broker_service import BrokerService
        return BrokerService(db).get_account()

    return {"error": f"Unknown tool: {tool_name}"}
