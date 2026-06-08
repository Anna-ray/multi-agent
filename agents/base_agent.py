from abc import ABC, abstractmethod
from typing import Any, Dict

class Agent(ABC):
    """Base class for all agents. Agents interact via a BandClient passed on construction.

    Subclasses should implement handle_message and optionally run (for background tasks).
    """

    def __init__(self, name: str, band_client):
        self.name = name
        self.band = band_client

    @abstractmethod
    def handle_message(self, message: Dict[str, Any]):
        raise NotImplementedError

    def send_message(self, channel: str, message: Dict[str, Any]):
        """Helper to publish messages onto the Band hub."""
        envelope = {"from": self.name, "payload": message}
        self.band.publish(channel, envelope)

    def run(self):
        """Optional long-running process for the agent (e.g., polling)."""
        pass
