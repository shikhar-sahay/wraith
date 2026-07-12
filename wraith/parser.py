from __future__ import annotations

import shlex
from dataclasses import dataclass
from typing import List


@dataclass
class ParsedCommand:
    command: str
    args: List[str]
    raw: str


class CommandParser:
    @staticmethod
    def parse(raw: str) -> ParsedCommand:
        if not raw.strip():
            return ParsedCommand(command="", args=[], raw=raw)
        parts = shlex.split(raw, posix=True)
        return ParsedCommand(command=parts[0], args=parts[1:], raw=raw)
