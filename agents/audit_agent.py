from typing import Dict, Any
from .base_agent import Agent
import json
from messages.models import MessageEnvelope


class AuditAgent(Agent):
    """Listens to Band messages and records them for traceability.

    - Subscribes broadly and writes JSONL events to an audit.log file.
    - Ensures every action is time-stamped and attributed. Messages arriving here are
      validated MessageEnvelope instances produced by the BandClient.
    """

    def __init__(self, name: str, band_client, audit_path: str = "audit.log"):
        super().__init__(name, band_client)
        self.audit_path = audit_path

    def _record(self, event: Dict[str, Any]):
        with open(self.audit_path, "a") as fh:
            fh.write(json.dumps(event) + "\n")

    def handle_message(self, message: MessageEnvelope):
        # message is a validated MessageEnvelope
        event = {
            "agent": self.name,
            "envelope": message.model_dump(),
        }
        self._record(event)
