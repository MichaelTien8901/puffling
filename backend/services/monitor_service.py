from puffin.monitor import TradeLog, PnLTracker, SystemHealth


class MonitorService:
    def __init__(self):
        self.trade_log = TradeLog()
        self.pnl_tracker = PnLTracker()
        self.health = SystemHealth()

    def get_trade_log(self) -> list[dict]:
        records = self.trade_log.get_records()
        return [r.__dict__ for r in records]

    def get_pnl(self) -> dict:
        return self.pnl_tracker.summary()

    def get_health(self) -> dict:
        return self.health.check()
