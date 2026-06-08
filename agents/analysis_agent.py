from typing import Dict, Any
import os
import json

from agents.base_agent import Agent
from messages.models import MessageEnvelope, AnalysisCompleted


class AnalysisAgent(Agent):
    """Performs structured analysis of cryptographic/anomaly payloads and emits analysis.completed.

    This agent transforms a raw escalation into a validated AnalysisCompleted payload.
    """

    def __init__(self, name: str, band_client):
        super().__init__(name, band_client)

    def handle_message(self, message: MessageEnvelope):
        payload = message.payload
        # Expect payload to include escalation_id and content
        escalation_id = payload.get("escalation_id") or payload.get("id") or "unknown"
        content = payload.get("content", "")

        # Simulated structured evaluation (deterministic for the demo)
        analysis = {
            "escalation_id": escalation_id,
            "root_cause": "HSM entropy starvation under peak Kyber-1024 load",
            "confidence": 0.98,
            "evidence": [
                "hsm-metric:entropy-degradation",
                "hsm-logs:kyber-1024-latency-spike",
                "gateway:cross-border-clearing-errors"
            ],
            "ai_analysis": {
                "severity": "critical",
                "severity_level": 5,
                "financial_exposure_per_minute": 120000,
                "summary": (
                    "Entropy degradation and key-generation latency spike detected in HSM "
                    "during post-quantum Kyber-1024 handshakes across the cross-border clearing gateway."
                ),
                "recommended_attention": ["security", "infrastructure", "network"]
            }
        }

        # Validate against AnalysisCompleted model
        AnalysisCompleted.model_validate(analysis)

        # Publish validated analysis
        self.send_message("analysis.completed", analysis)


from adapters.band_client import InMemoryBandClient
from messages.models import IncidentRoomCreated, NodeTelemetry
from datetime import datetime
import uuid

class CoordinationAgent(Agent):
    """Creates incident rooms and routes telemetry to organizational nodes.

    - Listens for analysis.completed and creates incident room
    - Routes sub-payloads to network/security/infrastructure telemetry topics
    """

    def __init__(self, name: str, band_client):
        super().__init__(name, band_client)

    def handle_message(self, message: MessageEnvelope):
        payload = message.payload
        esc_id = payload.get("escalation_id")

        # Create dedicated incident room
        room_name = f"PQC-CRISIS-ROOM-HSM-01"
        room_payload = {
            "room_id": str(uuid.uuid4()),
            "room_name": room_name,
            "escalation_id": esc_id,
            "created_by": self.name,
            "participants": ["network_team", "security_team", "infra_team"]
        }
        # Validate and publish
        IncidentRoomCreated.model_validate(room_payload)
        self.send_message("incident.room.created", room_payload)

        # Route telemetry sub-payloads (simulate extracting metrics)
        telemetry_samples = [
            {"node": "network", "metric": "packet_drop_rate", "value": "0.12"},
            {"node": "security", "metric": "hsm_entropy_level", "value": "0.02"},
            {"node": "infrastructure", "metric": "hsm_keygen_latency_ms", "value": "1200"},
        ]

        for sample in telemetry_samples:
            telemetry = {
                "escalation_id": esc_id,
                "node": sample["node"],
                "metric": sample["metric"],
                "value": sample["value"],
                "timestamp": datetime.utcnow()
            }
            NodeTelemetry.model_validate(telemetry)
            self.send_message("node.telemetry", telemetry)


from typing import Dict, Any, List
from services.ai_ml_client import AiMlClient
from messages.models import DecisionMade, DecisionDetails

class DecisionAgent(Agent):
    """Synthesizes analysis and coordination context into executive mitigation decisions.

    Produces both a compact DecisionMade message and a richer DecisionDetails record.
    """

    def __init__(self, name: str, band_client, ai_client: AiMlClient = None):
        super().__init__(name, band_client)
        self.ai = ai_client
        self._analyses: Dict[str, List[Dict[str, Any]]] = {}

    def handle_message(self, message: MessageEnvelope):
        topic = message.topic
        payload = message.payload
        esc_id = payload.get("escalation_id")

        # Accumulate analyses if they arrive
        if topic == "analysis.completed":
            self._analyses.setdefault(esc_id, []).append(payload)

        # When an incident room is created, or a decision request comes, synthesize
        if topic in ("incident.room.created", "decision.request"):
            analyses = self._analyses.get(esc_id, [])

            # Construct executive recommendation
            recommendation_text = (
                "Execute an emergency fallback to a secure classical hybrid elliptic-curve "
                "cryptography (ECDH fallback mechanism) to immediately clear the transaction backlog "
                "while logging the temporary regulatory compliance variance."
            )

            # Build detailed risk matrix
            risk_matrix = {
                "risks": [
                    {"id": "R1", "description": "Temporary compliance variance", "likelihood": "medium", "impact": "high", "mitigation": "document decision, notify regulators"},
                    {"id": "R2", "description": "Residual cryptographic downgrade risk", "likelihood": "low", "impact": "critical", "mitigation": "limit fallback window, enable strict logging"},
                    {"id": "R3", "description": "Transaction throughput loss during switchover", "likelihood": "high", "impact": "medium", "mitigation": "staged rollout, monitor throughput"},
                ],
                "summary": {
                    "overall_risk": "high",
                    "recommended_confidence": 0.92
                }
            }

            details_payload = {
                "escalation_id": esc_id,
                "action_item": "Execute emergency ECDH fallback and clear backlog",
                "mitigation_steps": [
                    "Activate ECDH fallback configuration on clearing gateway",
                    "Throttle non-critical transaction types to preserve capacity",
                    "Notify regulators and affected partners with interim variance report",
                    "Capture full packet and HSM logs for forensic review"
                ],
                "risk_matrix": risk_matrix,
                "recommended_by": self.name,
            }

            # Validate and publish rich decision details
            DecisionDetails.model_validate(details_payload)
            self.send_message("decision.details", details_payload)

            decision_payload = {
                "escalation_id": esc_id,
                "recommendation": recommendation_text,
                "rationale": "Automated synthesis based on high-confidence HSM entropy degradation signals and financial exposure.",
                "confidence": float(details_payload["risk_matrix"]["summary"]["recommended_confidence"]),
                "analyses_count": len(analyses),
            }

            DecisionMade.model_validate(decision_payload)
            self.send_message("decision.made", decision_payload)


import os
import json
from messages.models import MessageEnvelope

class AuditAgent(Agent):
    """Records a legally-defensible append-only JSON ledger of system events and decisions.

    The ledger is written to disk with an fsync after each append to ensure durability.
    """

    def __init__(self, name: str, band_client, ledger_path: str = "audit_ledger.jsonl"):
        super().__init__(name, band_client)
        self.ledger_path = ledger_path
        # Ensure file exists
        open(self.ledger_path, "a").close()

    def _append(self, record: Dict[str, Any]):
        # Write atomically and fsync to ensure durability for legal defensibility
        with open(self.ledger_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
            fh.flush()
            try:
                os.fsync(fh.fileno())
            except Exception:
                # If fsync unsupported in environment, proceed but warn
                pass

    def handle_message(self, message: MessageEnvelope):
        # Normalize envelope to dict
        envelope = message.model_dump()
        entry = {
            "recorded_at": datetime.utcnow().isoformat() + "Z",
            "agent": self.name,
            "envelope": envelope
        }
        self._append(entry)
