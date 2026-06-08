# Multi-Agent Escalation Orchestration

This repository contains a scaffold for a customer support escalation orchestration system. It provides five agent classes implemented in Python that coordinate via a Band messaging hub. The design focuses on modularity, traceability, and integration with classification (Featherless) and AI/ML decision services.

IMPORTANT: Message contract layer

This update adds a strict message contract layer using Pydantic models. Every message published to the Band is validated at the bus boundary. The models live in `messages/models.py` and include:

- MessageEnvelope: the canonical envelope with id, timestamp, source, topic, and payload.
- Typed payload models for: EscalationCreated, EscalationTask, AnalysisCompleted, DecisionRequest, DecisionMade.

The in-memory Band client (`adapters/band_client.py`) enforces these contracts in development: it validates the envelope shape and the payload schema for each registered topic before delivering messages to subscribers.

Why this matters

Strongly-typed message contracts prevent schema drift, make audit logs reliable, and make agent interactions deterministic. Implementing contracts first establishes a stable foundation for further work (CI, production Band adapter, observability).

Running the demo

1. Install requirements: `pip install -r requirements.txt`
2. Run: `python examples/run_pipeline.py`
3. Check `audit.log` for recorded, validated messages.

Next recommended steps

1. Add more domain models and tighten payload fields (replace Dict[str, Any] with explicit shapes where possible).
2. Add unit tests that intentionally send invalid envelopes to confirm the Band client rejects them.
3. Add CI to run tests and linting on PRs.

