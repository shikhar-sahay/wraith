from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass
class SessionRandomizer:
    seed: int

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)

    def choice(self, values: list[str]) -> str:
        return self._rng.choice(values)

    def randint(self, low: int, high: int) -> int:
        return self._rng.randint(low, high)
