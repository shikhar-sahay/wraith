from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class SessionIdentity:
    session_id: str
    attacker_ip: str
    client: str
    started_at: str
    cwd: str = "/home/admin"
    user: str = "admin"
    hostname: str = "db-prod-01"
    root_mode: bool = False
    sudo_attempts: int = 0
    history: List[str] = field(default_factory=list)
    environment: Dict[str, str] = field(
        default_factory=lambda: {
            "HOSTNAME": "db-prod-01",
            "USER": "admin",
            "HOME": "/home/admin",
            "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
            "SHELL": "/bin/bash",
            "TERM": "xterm-256color",
        }
    )
    filesystem: Dict[str, List[str]] = field(default_factory=dict)
