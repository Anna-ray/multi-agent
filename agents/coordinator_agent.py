from typing import Dict, Any
from .base_agent import Agent
from messages.models import MessageEnvelope, EscalationTask

class CoordinatorAgent(Agent):
    """Listens for escalations and coordinates specialist tasks.

    - Receives 'escalation.created' messages.
    - Based on urgency, it creates tasks for Specialist Agents and requests Decision Agent involvement.
    - Emits 'escalation.task' messages describing work to be done.
    """

    def __init__(self, name: str, band_client):
        super().__init__(name, band_client)

    def handle_message(self, message: MessageEnvelope):
        payload = message.payload
        escalation_id = payload.get("escalation_id")
        urgency_level = payload.get("urgency", {}).get("level", "low") if payload.get("urgency") else "low"

        # Mobilize teams: choose number of specialists or priority path
        task_payload = {
            "escalation_id": escalation_id,
            "action": "analyze_root_cause",
            "assigned_to": "specialist_pool",
            "urgency": urgency_level,
        }
        # Validate task payload
        EscalationTask.model_validate(task_payload)
        self.send_message("escalation.task", task_payload)

        # Request decision synthesis in parallel
        decision_request = {
            "escalation_id": escalation_id,
            "context": payload,
            "request": "synthesize_recommendation",
        }
        self.send_message("decision.request", decision_request)
