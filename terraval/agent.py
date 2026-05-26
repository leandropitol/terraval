from importlib import resources
from pathlib import Path
from typing import Generator

import litellm

litellm.suppress_debug_info = True


def load_system_prompt() -> str:
    try:
        ref = resources.files("terraval.data").joinpath("SKILL.md")
        return ref.read_text(encoding="utf-8")
    except Exception:
        fallback = Path(__file__).parent / "data" / "SKILL.md"
        return fallback.read_text(encoding="utf-8")


class TerraValAgent:
    def __init__(self, model: str) -> None:
        self.model = model
        self.system_prompt = load_system_prompt()
        self.history: list[dict] = []

    def clear_history(self) -> None:
        self.history = []

    def chat(self, user_message: str) -> Generator[str, None, None]:
        self.history.append({"role": "user", "content": user_message})

        messages = [
            {"role": "system", "content": self.system_prompt},
            *self.history,
        ]

        response = litellm.completion(
            model=self.model,
            messages=messages,
            stream=True,
            max_tokens=4096,
        )

        full_response = ""
        for chunk in response:
            delta = chunk.choices[0].delta.content or ""
            if delta:
                full_response += delta
                yield delta

        self.history.append({"role": "assistant", "content": full_response})
