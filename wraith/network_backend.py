from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class NetworkBackend:
    blocked_domains: List[str] = field(default_factory=lambda: ["example.com", "127.0.0.1"])

    def simulate_fetch(self, target: str) -> str:
        if target.startswith("http://") or target.startswith("https://"):
            return f"[simulated] fetched {target}"
        return f"[simulated] resolved {target}"
