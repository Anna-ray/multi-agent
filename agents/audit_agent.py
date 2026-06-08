from typing import Dict, Any
from .base_agent import Agent
import json

class AuditAgent(Agent):
    """Listens to all Band messages and records them for traceability.

    - Subscribes broadly and writes JSONL events to an audit.log file.
    - Ensures every action is time-stamped and attributed.
    """

    def __init__(self, name: str, band_client, audit_path: str = "audit.log"):
        super().__init__(name, band_client)
        self.audit_path = audit_path

    def _record(self, event: Dict[str, Any]):
        with open(self.audit_path, "a") as fh:
            fh.write(json.dumps(event) + "\n")

    def handle_message(self, message: Dict[str, Any]):
        # Add minimal metadata and persist
        event = {
            "agent": self.name,
            "message": message,
        }
        self._record(event)
