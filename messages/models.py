from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, Optional, Literal
from pydantic import BaseModel, Field
import uuid


# Core envelope model used at the Band boundary
class MessageEnvelope(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str
    topic: str
    payload: Dict[str, Any]


# Domain message models (typed payloads)
class EscalationCreated(BaseModel):
    escalation_id: str
    source: str
    content: str
    urgency: Dict[str, Any]  # e.g. {"level": "high", "score": 0.95}


class EscalationTask(BaseModel):
    escalation_id: str
    action: str
    assigned_to: str
    urgency: Literal["low", "medium", "high", "critical"] | str


class AnalysisCompleted(BaseModel):
    escalation_id: str
    root_cause: str
    confidence: float
    evidence: list[str] = []
    ai_analysis: Optional[Dict[str, Any]] = None


class DecisionRequest(BaseModel):
    escalation_id: str
    context: Dict[str, Any]
    request: str


class DecisionMade(BaseModel):
    escalation_id: str
    recommendation: str
    rationale: str
    confidence: float
    analyses_count: int


# Topic -> payload model mapping used by the BandClient validator
TOPIC_PAYLOAD_MODELS: Dict[str, type] = {
    "escalation.created": EscalationCreated,
    "escalation.task": EscalationTask,
    "analysis.completed": AnalysisCompleted,
    "decision.request": DecisionRequest,
    "decision.made": DecisionMade,
}
