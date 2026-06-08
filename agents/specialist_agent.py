from typing import Dict, Any
from .base_agent import Agent
from services.ai_ml_client import AiMlClient
from messages.models import MessageEnvelope, AnalysisCompleted


class SpecialistAgent(Agent):
    """Analyzes escalations and collects evidence.

    - Receives 'escalation.task' messages.
    - Performs domain-specific analysis (placeholder) and emits 'analysis.completed'.
    """

    def __init__(self, name: str, band_client, ai_client: AiMlClient = None):
        super().__init__(name, band_client)
        self.ai = ai_client

    def analyze(self, escalation_id: str, context: Dict[str, Any]):
        # Placeholder for real analysis. Optionally use AI to extract likely root causes.
        summary = {
            "escalation_id": escalation_id,
            "root_cause": "investigate_logs",
            "confidence": 0.6,
            "evidence": ["log-snippet-1", "related-ticket-42"],
        }
        # If AI client is available, run a deep analysis
        if self.ai:
            prompt = (
                f"Analyze escalation {escalation_id}: {context.get('content','')[:500]}"
            )
            ai_analysis = self.ai.analyze(prompt)
            summary["ai_analysis"] = ai_analysis

        # Validate analysis payload
        AnalysisCompleted.model_validate(summary)
        self.send_message("analysis.completed", summary)
        return summary

    def handle_message(self, message: MessageEnvelope):
        payload = message.payload
        if payload.get("action") == "analyze_root_cause":
            self.analyze(payload.get("escalation_id"), payload)
