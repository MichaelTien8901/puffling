from puffin.data import YFinanceProvider
from puffin.portfolio import MeanVarianceOptimizer, compute_stats, generate_tearsheet


class PortfolioService:
    def __init__(self):
        self.provider = YFinanceProvider()

    def optimize(self, symbols: list[str], start: str, end: str, method: str = "mean_variance") -> dict:
        data = self.provider.get_data(symbols, start=start, end=end)
        returns = data["Close"].pct_change().dropna()
        if method == "mean_variance":
            optimizer = MeanVarianceOptimizer()
            weights = optimizer.optimize(returns)
        else:
            from puffin.portfolio import risk_parity_weights
            weights = risk_parity_weights(returns)
        return {"weights": dict(zip(symbols, weights.tolist())), "method": method}

    def tearsheet(self, returns_data: list[float]) -> dict:
        import pandas as pd
        returns = pd.Series(returns_data)
        stats = compute_stats(returns)
        return stats
