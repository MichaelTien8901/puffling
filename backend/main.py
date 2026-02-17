from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    # Start the background scheduler
    from backend.core.database import SessionLocal
    from backend.services.scheduler_service import SchedulerService
    db = SessionLocal()
    try:
        scheduler_svc = SchedulerService(db)
        scheduler_svc.start()
    finally:
        db.close()
    yield


app = FastAPI(title="Puffling", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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

from backend.api.routes import scheduler, strategy_live, portfolio_goals, alerts, agent, safety, optimize  # noqa: E402

app.include_router(scheduler.router, prefix="/api/scheduler", tags=["scheduler"])
app.include_router(strategy_live.router, prefix="/api/strategies/live", tags=["strategy-live"])
app.include_router(portfolio_goals.router, prefix="/api/portfolio/goals", tags=["portfolio-goals"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
app.include_router(agent.router, prefix="/api/agent", tags=["agent"])
app.include_router(safety.router, prefix="/api/safety", tags=["safety"])
from backend.api.routes import live_adapt  # noqa: E402

app.include_router(live_adapt.router, prefix="/api/optimize", tags=["live-adaptation"])
app.include_router(optimize.router, prefix="/api/optimize", tags=["optimize"])

from backend.api.ws import prices, backtest_ws, trades, ai_chat, alerts_ws, agent_ws, optimize_ws  # noqa: E402

app.include_router(prices.router, tags=["ws"])
app.include_router(backtest_ws.router, tags=["ws"])
app.include_router(trades.router, tags=["ws"])
app.include_router(ai_chat.router, tags=["ws"])
app.include_router(alerts_ws.router, tags=["ws"])
app.include_router(agent_ws.router, tags=["ws"])
app.include_router(optimize_ws.router, tags=["ws"])
