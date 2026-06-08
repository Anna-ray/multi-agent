from abc import ABC, abstractmethod
from typing import Any
from messages.models import MessageEnvelope


class Agent(ABC):
    """Base class for all agents. Agents interact via a BandClient passed on construction.

    Subclasses should implement handle_message and optionally run (for background tasks).
    Messages delivered to agents will be MessageEnvelope instances (validated at bus boundary).
    """

    def __init__(self, name: str, band_client):
        self.name = name
        self.band = band_client

    @abstractmethod
    def handle_message(self, message: MessageEnvelope):
        raise NotImplementedError

    def send_message(self, topic: str, payload: dict):
        """Helper to publish messages onto the Band hub.

        This method builds a well-formed MessageEnvelope-compatible dict so the BandClient
        validator can enforce schema contracts.
        """
        envelope = {
            "source": self.name,
            "topic": topic,
            "payload": payload,
        }
        self.band.publish(topic, envelope)

    def run(self):
        """Optional long-running process for the agent (e.g., polling)."""
        pass
