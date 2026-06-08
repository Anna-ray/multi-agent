import time
import threading
import logging

from adapters.band_client import InMemoryBandClient
from services.featherless_client import FeatherlessClient
from services.ai_ml_client import AiMlClient
from agents.intake_agent import IntakeAgent
from agents.analysis_agent import AnalysisAgent, CoordinationAgent, DecisionAgent, AuditAgent


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def main():
    band = InMemoryBandClient()

    featherless = FeatherlessClient()
    ai_client = AiMlClient()

    # Instantiate agents
    intake = IntakeAgent("intake-1", band, featherless)
    analysis = AnalysisAgent("analysis-1", band)
    coordination = CoordinationAgent("coordination-1", band)
    decision = DecisionAgent("decision-1", band, ai_client)
    audit = AuditAgent("audit-1", band)

    # Wire up subscriptions
    band.subscribe("escalation.created", analysis.handle_message)
    band.subscribe("analysis.completed", coordination.handle_message)
    band.subscribe("analysis.completed", decision.handle_message)
    band.subscribe("incident.room.created", decision.handle_message)
    band.subscribe("decision.request", decision.handle_message)

    # Audit subscribes to everything
    band.subscribe("*", audit.handle_message)

    # Target PQC Flash-Crash payload
    payload = (
        "Entropy degradation and key-generation latency spike detected in HSM (Hardware Security Modules) "
        "during post-quantum Kyber-1024 handshakes across the cross-border clearing gateway."
    )

    logging.info("Starting Project Nexavara MVP pipeline demo")

    # Start the demo run in a background thread so pub/sub is non-blocking
    def produce():
        intake.ingest(source="monitoring-hub", content=payload)

    threading.Thread(target=produce, daemon=True).start()

    # Allow time for async processing to complete
    time.sleep(3)

    logging.info("Demo complete. Audit ledger path: audit_ledger.jsonl")


if __name__ == "__main__":
    main()
