from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import PurePosixPath
from typing import Dict, List, Optional, Tuple


@dataclass
class FakeFilesystem:
    root: str = "/"
    entries: Dict[str, List[str]] = field(default_factory=dict)
    files: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.entries = {
            "/": ["home", "tmp", "var", "etc", "usr", "opt", "root"],
            "/home": ["admin"],
            "/home/admin": [".bash_history", ".ssh"],
            "/tmp": [],
            "/var": ["www", "log"],
            "/var/www": ["html"],
            "/etc": ["ssh", "cron.d"],
            "/usr": ["bin", "sbin", "local"],
            "/root": [],
        }
        self.files = {
            "/etc/hostname": "db-prod-01\n",
            "/etc/os-release": "PRETTY_NAME=\"Ubuntu 22.04 LTS\"\n",
        }

    def mkdir(self, path: str) -> str:
        normalized = self._normalize(path)
        if normalized == "/":
            return "mkdir: cannot create directory '/': File exists"
        parent = str(PurePosixPath(normalized).parent)
        if parent not in self.entries:
            self.entries[parent] = []
        if normalized in self.entries or normalized in self.files:
            return f"mkdir: cannot create directory '{normalized}': File exists"
        self.entries[normalized] = []
        self.entries.setdefault(parent, []).append(PurePosixPath(normalized).name)
        return ""

    def touch(self, path: str) -> str:
        normalized = self._normalize(path)
        self.entries.setdefault(normalized, [])
        self.files.setdefault(normalized, "")
        return ""

    def write(self, path: str, content: str) -> str:
        normalized = self._normalize(path)
        self.touch(normalized)
        self.files[normalized] = content
        return ""

    def cat(self, path: str) -> Optional[str]:
        normalized = self._normalize(path)
        return self.files.get(normalized)

    def ls(self, path: str) -> str:
        normalized = self._normalize(path)
        entries = self.entries.get(normalized, [])
        if not entries and normalized not in self.entries and normalized not in self.files:
            return ""
        return "\n".join(entries) if entries else ""

    def remove(self, path: str) -> str:
        normalized = self._normalize(path)
        if normalized in self.files:
            del self.files[normalized]
        if normalized in self.entries:
            del self.entries[normalized]
        parent = str(PurePosixPath(normalized).parent)
        if parent in self.entries:
            name = PurePosixPath(normalized).name
            self.entries[parent] = [item for item in self.entries[parent] if item != name]
        return ""

    def exists(self, path: str) -> bool:
        normalized = self._normalize(path)
        return normalized in self.entries or normalized in self.files

    def _normalize(self, path: str) -> str:
        if not path or path == ".":
            return "/"
        if path.startswith("~"):
            path = "/home/admin" + path[1:]
        if not path.startswith("/"):
            path = "/" + path
        normalized = PurePosixPath(path)
        return str(normalized)
