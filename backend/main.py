from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.core.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Puffling", version="0.1.0", lifespan=lifespan)


@app.get("/api/health")
def health():
    return {"status": "ok"}


from backend.api.routes import data, factors, strategies, backtest, portfolio, models, ai, broker, risk, monitor, settings  # noqa: E402

app.include_router(data.router, prefix="/api/data", tags=["data"])
app.include_router(factors.router, prefix="/api/factors", tags=["factors"])
app.include_router(strategies.router, prefix="/api/strategies", tags=["strategies"])
app.include_router(backtest.router, prefix="/api/backtest", tags=["backtest"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["portfolio"])
app.include_router(models.router, prefix="/api/models", tags=["models"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])
app.include_router(broker.router, prefix="/api/broker", tags=["broker"])
app.include_router(risk.router, prefix="/api/risk", tags=["risk"])
app.include_router(monitor.router, prefix="/api/monitor", tags=["monitor"])
app.include_router(settings.router, prefix="/api/settings", tags=["settings"])

from backend.api.ws import prices, backtest_ws, trades, ai_chat  # noqa: E402

app.include_router(prices.router, tags=["ws"])
app.include_router(backtest_ws.router, tags=["ws"])
app.include_router(trades.router, tags=["ws"])
app.include_router(ai_chat.router, tags=["ws"])
