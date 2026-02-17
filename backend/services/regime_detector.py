import numpy as np
import pandas as pd


class RegimeDetector:
    """Detects market regime changes using rolling volatility and trend metrics."""

    def compute_volatility_ratio(
        self, data: pd.DataFrame, short: int = 20, long: int = 60
    ) -> float | None:
        """Compute ratio of short-term to long-term realized volatility."""
        if len(data) < long:
            return None
        returns = data["Close"].pct_change().dropna()
        short_vol = returns.iloc[-short:].std() * np.sqrt(252)
        long_vol = returns.iloc[-long:].std() * np.sqrt(252)
        if long_vol == 0:
            return None
        return short_vol / long_vol

    def compute_trend_strength(self, data: pd.DataFrame, window: int = 20) -> float | None:
        """Compute normalized linear regression slope of recent close prices."""
        if len(data) < window:
            return None
        closes = data["Close"].iloc[-window:].values
        x = np.arange(window, dtype=float)
        x_mean = x.mean()
        y_mean = closes.mean()
        slope = np.sum((x - x_mean) * (closes - y_mean)) / np.sum((x - x_mean) ** 2)
        # Normalize by mean price
        if y_mean == 0:
            return None
        return slope / y_mean

    def detect_regime_change(self, data: pd.DataFrame, config) -> list[dict]:
        """Check for regime changes based on config thresholds.

        Args:
            data: OHLCV DataFrame
            config: LiveAdaptationConfig (or object with vol_ratio_high, vol_ratio_low)

        Returns:
            List of regime change events (may be empty)
        """
        events = []

        vol_ratio = self.compute_volatility_ratio(data)
        if vol_ratio is not None:
            if vol_ratio > config.vol_ratio_high:
                events.append({
                    "type": "high_volatility",
                    "value": vol_ratio,
                    "threshold": config.vol_ratio_high,
                })
            elif vol_ratio < config.vol_ratio_low:
                events.append({
                    "type": "low_volatility",
                    "value": vol_ratio,
                    "threshold": config.vol_ratio_low,
                })

        trend = self.compute_trend_strength(data)
        if trend is not None:
            # Check for trend reversal by comparing current vs previous window
            if len(data) >= 40:  # Need enough data for two windows
                prev_trend = self.compute_trend_strength(
                    data.iloc[:-20], window=20
                )
                if prev_trend is not None and (trend * prev_trend < 0):
                    events.append({
                        "type": "trend_reversal",
                        "value": trend,
                        "previous": prev_trend,
                    })

        return events
