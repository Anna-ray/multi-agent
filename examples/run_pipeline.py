import time
import threading

from adapters.band_client import InMemoryBandClient
from services.featherless_client import FeatherlessClient
from services.ai_ml_client import AiMlClient
from agents.intake_agent import IntakeAgent
from agents.coordinator_agent import CoordinatorAgent
from agents.specialist_agent import SpecialistAgent
from agents.decision_agent import DecisionAgent
from agents.audit_agent import AuditAgent


def main():
    band = InMemoryBandClient()

    featherless = FeatherlessClient()
    ai_client = AiMlClient()

    # Instantiate agents
    intake = IntakeAgent("intake-1", band, featherless)
    coordinator = CoordinatorAgent("coordinator-1", band)
    specialist = SpecialistAgent("specialist-1", band, ai_client)
    decision = DecisionAgent("decision-1", band, ai_client)
    audit = AuditAgent("audit-1", band)

    # Wire up subscriptions
    band.subscribe("escalation.created", coordinator.handle_message)
    band.subscribe("escalation.task", specialist.handle_message)
    band.subscribe("analysis.completed", decision.handle_message)
    band.subscribe("decision.request", decision.handle_message)

    # Audit subscribes to everything
    band.subscribe("*", audit.handle_message)

    # Simulate an incoming escalation
    escalation_text = (
        "Customer reports large number of failed payments over the last hour, "
        "error code PAY-502, repeated timeouts while calling payments service."
    )

    def produce():
        intake.ingest(source="ticket-123", content=escalation_text)

    # Run producer in background to show async delivery
    threading.Thread(target=produce, daemon=True).start()

    # Allow a little time for async message processing
    time.sleep(2)

    print("Demo run complete. Check audit.log for recorded events.")


if __name__ == "__main__":
    main()
