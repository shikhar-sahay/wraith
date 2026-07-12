from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PrivilegeEscalationSimulator:
    attempts: int = 0

    def next(self, user: str) -> str:
        self.attempts += 1
        if self.attempts == 1:
            return "[sudo] password for admin:"
        if self.attempts == 2:
            return "Sorry, try again."
        return "root@db-prod-01:~#"
