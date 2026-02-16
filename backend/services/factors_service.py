from puffin.data import YFinanceProvider
from puffin.factors import compute_all_factors, TechnicalIndicators


class FactorsService:
    def __init__(self):
        self.provider = YFinanceProvider()

    def compute(self, symbols: list[str], start: str, end: str, factor_types: list[str] | None = None) -> dict:
        data = self.provider.get_data(symbols, start=start, end=end)
        factors = compute_all_factors(data)
        return {"factors": factors.reset_index().to_dict(orient="records")}

    def get_library(self) -> dict:
        from puffin.factors import ALPHA_LIBRARY
        return {"alphas": list(ALPHA_LIBRARY.keys())}

    def risk_factors(self, symbols: list[str], start: str, end: str, n_components: int = 5) -> dict:
        from puffin.unsupervised import MarketPCA, extract_risk_factors
        data = self.provider.get_data(symbols, start=start, end=end)
        returns = data["Close"].pct_change().dropna()
        factors = extract_risk_factors(returns, n_components=n_components)
        return {"risk_factors": factors}

    def cluster_assets(self, symbols: list[str], start: str, end: str, method: str = "kmeans") -> dict:
        from puffin.unsupervised import cluster_assets
        data = self.provider.get_data(symbols, start=start, end=end)
        returns = data["Close"].pct_change().dropna()
        clusters = cluster_assets(returns, method=method)
        return {"clusters": clusters}
