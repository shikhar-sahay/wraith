from __future__ import annotations

from typing import Dict, List


def sample_users() -> List[str]:
    return ["admin", "postgres", "root"]


def sample_processes() -> List[Dict[str, str]]:
    return [
        {"pid": "123", "cmd": "sshd: admin [priv]"},
        {"pid": "456", "cmd": "python3 /opt/agent.py"},
        {"pid": "789", "cmd": "/usr/sbin/nginx"},
    ]
