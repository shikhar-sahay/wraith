from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Registry:
    commands: Dict[str, str] = field(default_factory=dict)
    downloads: List[dict] = field(default_factory=list)
    reverse_shells: List[dict] = field(default_factory=list)

    def register_command(self, name: str, output: str) -> None:
        self.commands[name] = output

    def record_download(self, url: str, path: str) -> None:
        self.downloads.append({"url": url, "path": path})

    def record_reverse_shell(self, payload: str) -> None:
        self.reverse_shells.append({"payload": payload})
