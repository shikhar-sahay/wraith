from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class MachinePersona:
    hostname: str = "db-prod-01"
    os_name: str = "Ubuntu"
    os_version: str = "22.04 LTS"
    cpu_cores: int = 16
    memory_gb: int = 64
    disk_gb: int = 500
    services: List[str] = None

    def __post_init__(self) -> None:
        if self.services is None:
            self.services = ["mysql", "redis", "docker", "cron", "nginx", "ssh"]

    def banner(self) -> str:
        return (
            f"Welcome to {self.hostname}\n"
            f"{self.os_name} {self.os_version} \n"
            f"{self.cpu_cores} CPU cores | {self.memory_gb} GB RAM | {self.disk_gb} GB SSD"
        )

    def motd(self) -> str:
        return "Last login: unknown from 203.0.113.10 on pts/0"
