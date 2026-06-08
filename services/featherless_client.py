import os
import requests
from typing import Dict

class FeatherlessClient:
    """Wrapper around Featherless classification API.

    This is a placeholder. Replace endpoint and payload according to your org's Featherless contract.
    """

    def __init__(self, api_key: str = None, endpoint: str = None):
        self.api_key = api_key or os.getenv("FEATHERLESS_API_KEY")
        self.endpoint = endpoint or os.getenv("FEATHERLESS_ENDPOINT", "https://api.featherless.example/v1/classify")

    def classify(self, text: str) -> Dict[str, str]:
        # Example return: {"level": "high", "score": 0.97}
        if not self.api_key:
            # Fallback heuristic for demos
            score = min(1.0, max(0.0, len(text) / 500))
            level = "low"
            if score > 0.7:
                level = "high"
            elif score > 0.4:
                level = "medium"
            return {"level": level, "score": score}

        payload = {"text": text}
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        try:
            resp = requests.post(self.endpoint, json=payload, headers=headers, timeout=5)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return {"level": "unknown", "score": 0.0}
