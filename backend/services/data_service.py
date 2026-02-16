from puffin.data import YFinanceProvider


class DataService:
    def __init__(self):
        self.provider = YFinanceProvider()

    def get_ohlcv(self, symbol: str, start: str, end: str, interval: str = "1d") -> dict:
        df = self.provider.get_data(symbol, start=start, end=end, interval=interval)
        return {
            "symbol": symbol,
            "interval": interval,
            "data": df.reset_index().to_dict(orient="records"),
        }

    def get_symbols(self) -> list[str]:
        return self.provider.list_symbols() if hasattr(self.provider, "list_symbols") else []
