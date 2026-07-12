from __future__ import annotations

from .server import FakeShellServer


class BeelzebubAdapter:
    def __init__(self, telemetry_dir: str | None = None) -> None:
        self.server = FakeShellServer(telemetry_dir=telemetry_dir)
        self.sessions: dict[str, object] = {}

    def get_or_create_session(self, attacker_ip: str, client: str) -> object:
        session_key = f"{attacker_ip}:{client}"
        if session_key not in self.sessions:
            self.sessions[session_key] = self.server.create_session(attacker_ip, client)
        return self.sessions[session_key]

    def handle(self, attacker_ip: str, client: str, command: str) -> str:
        session = self.get_or_create_session(attacker_ip, client)
        return session.handle_command(command)
