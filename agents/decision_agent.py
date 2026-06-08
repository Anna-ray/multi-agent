from typing import Dict, Any
from .base_agent import Agent
from services.ai_ml_client import AiMlClient

class DecisionAgent(Agent):
    """Synthesizes analysis into executive-level recommendations using AI/ML APIs.

    - Receives 'decision.request' and 'analysis.completed' messages.
    - Aggregates context and calls AI/ML service to produce a precise recommendation.
    - Emits 'decision.made' message with structured recommendation and rationale.
    """

    def __init__(self, name: str, band_client, ai_client: AiMlClient):
        super().__init__(name, band_client)
        self.ai = ai_client
        # Simple in-memory store to gather analyses
        self._analyses = {}

    def handle_message(self, message: Dict[str, Any]):
        topic = message.get("topic")
        payload = message.get("payload", {})

        if topic == "analysis.completed":
            esc_id = payload.get("escalation_id")
            self._analyses.setdefault(esc_id, []).append(payload)

        if topic == "decision.request":
            esc_id = payload.get("escalation_id")
            context = payload.get("context", {})
            analyses = self._analyses.get(esc_id, [])
            # Synthesize recommendation
            recommendation = self.ai.synthesize_recommendation(esc_id, context, analyses)
            self.send_message("decision.made", recommendation)
