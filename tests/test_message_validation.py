import pytest
from messages.models import MessageEnvelope, EscalationCreated
from adapters.band_client import InMemoryBandClient

def test_valid_message_delivery():
    client = InMemoryBandClient()
    received_messages = []

    # Subscribe a dummy handler to the topic
    client.subscribe("escalation.created", lambda msg: received_messages.append(msg))

    # 1. Create the raw payload dictionary matching EscalationCreated's contract
    payload_data = {
        "escalation_id": "ESC-123",
        "details": "Critical issue",
        "source": "IntakeAgent",
        "content": "System anomaly",
        "urgency": {"level": "high"}  # Urgency must be a dictionary
    }

    # 2. Construct the envelope providing the top-level 'source' field 
    # and passing the payload as a clean dictionary
    envelope = MessageEnvelope(
        topic="escalation.created",
        source="IntakeAgent",
        payload=payload_data
    )

    # Publish to the event bus
    client.publish("escalation.created", envelope)

    # Assertions
    assert len(received_messages) == 1
    
    # Duck-typing check to support either object attribute or dictionary key access
    msg_payload = received_messages[0].payload
    if hasattr(msg_payload, "escalation_id"):
        assert msg_payload.escalation_id == "ESC-123"
    else:
        assert msg_payload["escalation_id"] == "ESC-123"

def test_invalid_message_raises_value_error():
    client = InMemoryBandClient()

    # Attempt to publish a completely malformed envelope or missing required fields
    # This triggers a ValidationError caught by the bus boundary validation layer
    with pytest.raises(ValueError):
        client.publish("escalation.created", {"topic": "escalation.created", "payload": {}})