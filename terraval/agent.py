from importlib import resources
from pathlib import Path
from typing import Generator

REFERENCES_DIR = Path(__file__).parent / "data" / "references"

REFERENCE_FILES = [
    # Priority order: most critical first.
    # Atlas e Planilha VTN são os únicos com dados de mercado reais.
    ("nbr-14653-3-imoveis-rurais.md",       "ABNT NBR 14653-3 — Imóveis Rurais",             84),
    ("bacen-resolucao-4676-2018.md",         "Resolução BACEN nº 4.676/2018 — LTV/Garantias",  37),
    ("atlas-mercado-terras-2025.md",         "Atlas do Mercado de Terras INCRA 2025",          422),
    ("planilha-vtn-2025.md",                 "Planilha VTN 2025 — INCRA (por município)",      224),
    ("nbr-14653-1-procedimentos-gerais.md",  "ABNT NBR 14653-1 — Procedimentos Gerais",         32),
    ("nbr-14653-4-empreendimentos.md",       "ABNT NBR 14653-4 — Empreendimentos",              51),
    ("nbr-14653-6-recursos-naturais.md",     "ABNT NBR 14653-6 — Recursos Naturais",            38),
]

# KB budget per model family.
# Calibrado empiricamente: texto técnico BR com tabelas ≈ 436 tokens/KB.
# Claude 200K  → 770 KB  ≈ 336K tokens (seguro)
# GPT-4o 128K  → 200 KB  ≈  87K tokens + 10 KB SKILL + ~20K conversa = ~123K (seguro)
# Gemini 1M    → 380 KB  ≈ 166K tokens (seguro)
# Llama 128K   → 110 KB  ≈  48K tokens (seguro)
CONTEXT_BUDGET_KB = {
    "claude":  770,
    "gpt-4o":  200,
    "gemini":  380,
    "llama":   110,
    "default": 160,
}


def _budget_for(model: str) -> int:
    m = model.lower()
    for key, kb in CONTEXT_BUDGET_KB.items():
        if key in m:
            return kb
    return CONTEXT_BUDGET_KB["default"]


def load_references(model: str) -> tuple[str, list[str]]:
    budget_kb = _budget_for(model)
    used_kb = 0
    blocks: list[str] = []
    loaded: list[str] = []

    for filename, display_name, size_kb in REFERENCE_FILES:
        path = REFERENCES_DIR / filename
        if not path.exists():
            continue
        if used_kb + size_kb > budget_kb:
            continue
        content = path.read_text(encoding="utf-8")
        blocks.append(
            f"\n\n---\n## BASE DE CONHECIMENTO: {display_name}\n\n{content}"
        )
        loaded.append(display_name)
        used_kb += size_kb

    return "".join(blocks), loaded


def _load_skill() -> str:
    try:
        ref = resources.files("terraval.data").joinpath("SKILL.md")
        return ref.read_text(encoding="utf-8")
    except Exception:
        return (Path(__file__).parent / "data" / "SKILL.md").read_text(encoding="utf-8")


def _make_client(provider_info: dict, api_key: str):
    sdk = provider_info["sdk"]
    if sdk == "anthropic":
        from anthropic import Anthropic
        return Anthropic(api_key=api_key)
    else:
        from openai import OpenAI
        kwargs = {"api_key": api_key}
        if provider_info.get("base_url"):
            kwargs["base_url"] = provider_info["base_url"]
        return OpenAI(**kwargs)


class TerraValAgent:
    def __init__(self, model: str, provider_info: dict, api_key: str) -> None:
        self.model = model
        self.sdk = provider_info["sdk"]
        self.client = _make_client(provider_info, api_key)
        skill = _load_skill()
        refs_text, self.loaded_refs = load_references(model)
        self.system_prompt = skill + refs_text
        self.history: list[dict] = []
        self.last_response: str = ""

    def clear_history(self) -> None:
        self.history = []
        self.last_response = ""

    def chat(self, user_message: str) -> Generator[str, None, None]:
        self.history.append({"role": "user", "content": user_message})
        full_response = ""

        if self.sdk == "anthropic":
            with self.client.messages.stream(
                model=self.model,
                max_tokens=4096,
                system=self.system_prompt,
                messages=self.history,
            ) as stream:
                for delta in stream.text_stream:
                    full_response += delta
                    yield delta
        else:
            messages = [{"role": "system", "content": self.system_prompt}, *self.history]
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=4096,
                stream=True,
            )
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                if delta:
                    full_response += delta
                    yield delta

        self.last_response = full_response
        self.history.append({"role": "assistant", "content": full_response})
