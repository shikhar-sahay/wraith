from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


class TelemetryLogger:
    def __init__(self, output_dir: str | None = None) -> None:
        self.output_dir = Path(output_dir or "logs/telemetry")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def log_event(self, entry: Dict[str, Any]) -> None:
        entry = dict(entry)
        entry.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
        path = self.output_dir / "events.jsonl"
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry) + "\n")

    def log_session_ended(
        self,
        session_id: str,
        attacker_ip: str,
        client: str,
        duration_seconds: float,
        commands: int,
    ) -> None:
        self.log_event(
            {
                "event": "session_ended",
                "session_id": session_id,
                "attacker_ip": attacker_ip,
                "client": client,
                "duration_seconds": duration_seconds,
                "commands": commands,
            }
        )
