from puffin.risk import fixed_fractional, kelly_criterion, volatility_based


class RiskService:
    def position_size(self, method: str, **kwargs) -> dict:
        if method == "fixed_fractional":
            size = fixed_fractional(**kwargs)
        elif method == "kelly":
            size = kelly_criterion(**kwargs)
        elif method == "volatility":
            size = volatility_based(**kwargs)
        else:
            raise ValueError(f"Unknown sizing method: {method}")
        return {"method": method, "position_size": float(size)}

    def portfolio_risk(self, symbols: list[str], weights: list[float], start: str, end: str) -> dict:
        from puffin.data import YFinanceProvider
        from puffin.risk import PortfolioRiskManager
        provider = YFinanceProvider()
        data = provider.get_data(symbols, start=start, end=end)
        returns = data["Close"].pct_change().dropna()
        manager = PortfolioRiskManager()
        risk = manager.assess(returns, weights)
        return {"risk": risk}
