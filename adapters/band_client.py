import threading
from typing import Callable, Dict, Any
from messages.models import MessageEnvelope, TOPIC_PAYLOAD_MODELS

class BandClient:
    """Abstract Band client interface. Implement publish/subscribe in production.

    All messages MUST be MessageEnvelope-compatible. Implementations should validate
    at the boundary so that every delivered message conforms to the declared contract.
    """

    def publish(self, topic: str, message: Dict[str, Any]):
        raise NotImplementedError

    def subscribe(self, topic: str, handler: Callable[[MessageEnvelope], None]):
        raise NotImplementedError


class InMemoryBandClient(BandClient):
    """A simple in-process pub/sub used for demos and tests.

    - Validates outgoing messages against MessageEnvelope and topic payload models
    - Maintains a registry of topic -> handlers
    - When publish is called, it delivers a MessageEnvelope instance to all handlers
    - Supports wildcard subscriptions under topic="*"
    """

    def __init__(self):
        self._handlers: Dict[str, list[Callable[[MessageEnvelope], None]]] = {}
        self._lock = threading.Lock()

    def publish(self, topic: str, message: Dict[str, Any]):
        # Build the envelope shape expected by the system. If the user supplied a
        # full envelope already, we respect its fields but ensure required ones exist.
        if isinstance(message, MessageEnvelope):
            envelope_obj = message
        else:
            # Ensure message contains payload dict
            envelope_payload = message.get("payload") if isinstance(message, dict) else None
            # Compose an envelope dict
            env = {
                "source": message.get("source", "unknown") if isinstance(message, dict) else "unknown",
                "topic": topic,
                "payload": envelope_payload if envelope_payload is not None else (message if isinstance(message, dict) else {}),
            }
            # Validate against MessageEnvelope model
            envelope_obj = MessageEnvelope.model_validate(env)

        # Validate payload schema for the topic if a model exists
        payload_model = TOPIC_PAYLOAD_MODELS.get(topic)
        if payload_model:
            try:
                payload_model.model_validate(envelope_obj.payload)
            except Exception as e:
                # For safety, do not deliver invalid messages. Raise to surface errors during development.
                raise ValueError(f"Payload validation failed for topic '{topic}': {e}") from e

        # Deliver to subscribers
        handlers = []
        with self._lock:
            handlers = list(self._handlers.get(topic, []))
            handlers += list(self._handlers.get("*", []))

        for h in handlers:
            threading.Thread(target=h, args=(envelope_obj,), daemon=True).start()

    def subscribe(self, topic: str, handler: Callable[[MessageEnvelope], None]):
        with self._lock:
            self._handlers.setdefault(topic, []).append(handler)
