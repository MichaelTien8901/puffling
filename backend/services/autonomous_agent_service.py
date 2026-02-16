import json
import logging
from datetime import datetime

from sqlalchemy.orm import Session

from backend.models.agent_log import AgentLog
from backend.services.ai_tools import AI_TOOL_SCHEMAS, execute_tool

logger = logging.getLogger(__name__)

# Connected WebSocket clients for agent activity streaming
agent_connections: list = []


class AutonomousAgentService:
    def __init__(self, db: Session):
        self.db = db

    def run(self, user_id: str, max_api_calls: int = 10) -> dict:
        api_calls = 0
        actions_taken = []

        # Step 1: Gather context
        context = self._gather_context(user_id)
        self._stream_activity({"step": "gather_context", "status": "done"})

        # Step 2: Analyze via LLM
        api_calls += 1
        analysis = self._analyze(context, user_id)
        self._stream_activity({"step": "analyze", "status": "done"})

        # Step 3: Produce report
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "context_summary": {k: type(v).__name__ for k, v in context.items()},
            "analysis": analysis.get("response", ""),
            "tool_calls": analysis.get("tool_calls", []),
        }

        # Step 4: Extract suggestions
        suggestions = analysis.get("suggestions", [])
        report["suggestions"] = suggestions

        # Step 5: Execute actions if auto-trade enabled
        from backend.services.settings_service import SettingsService
        settings_svc = SettingsService(self.db)
        auto_trade = settings_svc.get(user_id, "auto_trade_enabled")

        if auto_trade:
            from backend.services.safety_service import SafetyService
            safety = SafetyService(self.db)
            for suggestion in suggestions:
                if api_calls >= max_api_calls:
                    report["budget_exhausted"] = True
                    break
                if suggestion.get("action") == "trade" and safety.can_trade(user_id):
                    result = execute_tool("place_order", suggestion.get("params", {}), user_id, self.db)
                    actions_taken.append({"action": suggestion, "result": result})
                    self._stream_activity({"step": "execute", "action": suggestion})

        report["actions_taken"] = actions_taken

        # Persist log
        log = AgentLog(
            user_id=user_id,
            report=json.dumps(report),
            actions_taken=json.dumps(actions_taken),
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        self._stream_activity({"step": "complete", "log_id": log.id})

        return {"log_id": log.id, "report": report}

    def _gather_context(self, user_id: str) -> dict:
        context = {}
        try:
            from backend.services.broker_service import BrokerService
            broker = BrokerService(self.db)
            context["positions"] = broker.get_positions()
        except Exception:
            context["positions"] = []

        try:
            from backend.services.alert_service import AlertService
            alert_svc = AlertService(self.db)
            history = alert_svc.get_history(user_id, limit=10)
            context["recent_alerts"] = [{"message": h.message, "time": str(h.triggered_at)} for h in history]
        except Exception:
            context["recent_alerts"] = []

        try:
            from backend.services.strategy_runner_service import StrategyRunnerService
            runner = StrategyRunnerService(self.db)
            context["active_strategies"] = runner.get_active(user_id)
        except Exception:
            context["active_strategies"] = []

        return context

    def _analyze(self, context: dict, user_id: str) -> dict:
        prompt = f"""You are an autonomous trading agent. Analyze the current portfolio and market conditions.

Current portfolio positions: {json.dumps(context.get('positions', []))}
Active strategies: {json.dumps(context.get('active_strategies', []))}
Recent alerts: {json.dumps(context.get('recent_alerts', []))}

Provide:
1. A brief market analysis
2. Portfolio assessment
3. Any suggested actions (buy/sell/rebalance)

Be conservative and risk-aware."""

        try:
            from puffin.ai import ClaudeProvider
            provider = ClaudeProvider()
            response = provider.generate(prompt)
            return {"response": response, "suggestions": [], "tool_calls": []}
        except Exception as e:
            logger.error(f"Agent LLM call failed: {e}")
            return {"response": f"Analysis unavailable: {e}", "suggestions": []}

    def _stream_activity(self, data: dict):
        import asyncio
        for ws in agent_connections[:]:
            try:
                asyncio.get_event_loop().create_task(
                    ws.send_text(json.dumps(data))
                )
            except Exception:
                agent_connections.remove(ws)

    def get_logs(self, user_id: str, limit: int = 20) -> list[AgentLog]:
        return (
            self.db.query(AgentLog)
            .filter(AgentLog.user_id == user_id)
            .order_by(AgentLog.run_at.desc())
            .limit(limit)
            .all()
        )
