from __future__ import annotations

from dataclasses import dataclass


@dataclass
class InputLayer:
    prompt: str = "$ "

    def render_prompt(self, user: str, hostname: str, cwd: str) -> str:
        if user == "root":
            prompt = f"root@{hostname}:#"
        else:
            prompt = f"{user}@{hostname}:{cwd}$"
        return prompt
