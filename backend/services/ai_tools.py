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
        "description": "Place a trading order (requires user confirmation)",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {"type": "string"},
                "side": {"type": "string", "enum": ["buy", "sell"]},
                "qty": {"type": "number"},
                "order_type": {"type": "string", "enum": ["market", "limit"]},
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
        return BrokerService(db).submit_order(args["symbol"], args["side"], args["qty"], args.get("order_type", "market"))

    elif tool_name == "check_risk":
        from backend.services.risk_service import RiskService
        return RiskService().portfolio_risk(args["symbols"], args["weights"], args["start"], args["end"])

    return {"error": f"Unknown tool: {tool_name}"}
