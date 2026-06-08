import threading
from typing import Callable, Dict, Any, List

class BandClient:
    """Abstract Band client interface. Implement publish/subscribe in production.

    For development an in-memory client is provided below (publish/subscribe within the process).
    """

    def publish(self, channel: str, message: Dict[str, Any]):
        raise NotImplementedError

    def subscribe(self, channel: str, handler: Callable[[Dict[str, Any]], None]):
        raise NotImplementedError


class InMemoryBandClient(BandClient):
    """A simple in-process pub/sub used for demos and tests.

    - Maintains a registry of channel -> handlers.
    - When publish is called, it delivers a message to all handlers on that channel in separate threads.
    - Attaches a `topic` field to the message for agents that need it.
    """

    def __init__(self):
        self._handlers = {}  # channel -> list of handlers
        self._lock = threading.Lock()

    def publish(self, channel: str, message: Dict[str, Any]):
        # Enrich with topic for convenience
        envelope = {"topic": channel, **message}
        handlers = []
        with self._lock:
            handlers = list(self._handlers.get(channel, []))
            # also deliver to wildcard listeners registered under '*'
            handlers += list(self._handlers.get("*", []))

        for h in handlers:
            # deliver in background thread to avoid blocking publisher
            threading.Thread(target=h, args=(envelope,), daemon=True).start()

    def subscribe(self, channel: str, handler: Callable[[Dict[str, Any]], None]):
        with self._lock:
            self._handlers.setdefault(channel, []).append(handler)
