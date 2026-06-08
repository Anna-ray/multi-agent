import uuid
from typing import Dict, Any
from .base_agent import Agent
from services.featherless_client import FeatherlessClient

class IntakeAgent(Agent):
    """Detects incoming escalations and classifies urgency using Featherless.

    Behaviors:
    - Accepts raw escalation input (e.g., ticket text) via `handle_message` or polling in `run`.
    - Calls Featherless to classify urgency/priority and attaches metadata.
    - Emits an 'escalation.created' message on the Band.
    """

    def __init__(self, name: str, band_client, featherless: FeatherlessClient):
        super().__init__(name, band_client)
        self.classifier = featherless

    def ingest(self, source: str, content: str):
        escalation_id = str(uuid.uuid4())
        urgency = self.classifier.classify(content)
        message = {
            "escalation_id": escalation_id,
            "source": source,
            "content": content,
            "urgency": urgency,
        }
        self.send_message("escalation.created", message)
        return escalation_id

    def handle_message(self, message: Dict[str, Any]):
        # Intake may also respond to manual triggers
        payload = message.get("payload", {})
        src = payload.get("source", "unknown")
        content = payload.get("content", "")
        self.ingest(src, content)
