from importlib import resources
from pathlib import Path
from typing import Generator

import litellm

litellm.suppress_debug_info = True

REFERENCES_DIR = Path(__file__).parent / "data" / "references"

# Priority order: most critical first.
# (filename, display_name, size_kb)
REFERENCE_FILES = [
    # Priority order: most critical first.
    # Atlas e Planilha VTN são os únicos com dados de mercado reais —
    # sem eles o agente opera apenas com conhecimento de treinamento do LLM.
    ("nbr-14653-3-imoveis-rurais.md",       "ABNT NBR 14653-3 — Imóveis Rurais",             84),
    ("bacen-resolucao-4676-2018.md",         "Resolução BACEN nº 4.676/2018 — LTV/Garantias",  37),
    ("atlas-mercado-terras-2025.md",         "Atlas do Mercado de Terras INCRA 2025",          422),
    ("planilha-vtn-2025.md",                 "Planilha VTN 2025 — INCRA (por município)",      224),
    ("nbr-14653-1-procedimentos-gerais.md",  "ABNT NBR 14653-1 — Procedimentos Gerais",         32),
    ("nbr-14653-4-empreendimentos.md",       "ABNT NBR 14653-4 — Empreendimentos",              51),
    ("nbr-14653-6-recursos-naturais.md",     "ABNT NBR 14653-6 — Recursos Naturais",            38),
]

# KB budget per model family.
# Markdown de tabelas tokeniza eficientemente (~3,5 chars/token em PT).
# Claude 200K → budget 770 KB carrega os 4 docs core (767 KB total).
CONTEXT_BUDGET_KB = {
    "claude":  770,   # 200K ctx  → carrega NBR14653-3 + BACEN + Atlas + Planilha VTN
    "gpt-4o":  380,   # 128K ctx  → carrega NBR14653-3 + BACEN + Planilha VTN + NBR14653-1
    "gemini":  380,   # conservador para manter custo baixo
    "groq":    130,   # 32K–128K dependendo do modelo
    "default": 200,
}


def _budget_for(model: str) -> int:
    m = model.lower()
    for key, kb in CONTEXT_BUDGET_KB.items():
        if key in m:
            return kb
    return CONTEXT_BUDGET_KB["default"]


def load_references(model: str) -> tuple[str, list[str]]:
    """Load reference documents up to the model's context budget.

    Returns (combined_text, list_of_loaded_display_names).
    """
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
            f"\n\n---\n"
            f"## BASE DE CONHECIMENTO: {display_name}\n\n"
            f"{content}"
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


class TerraValAgent:
    def __init__(self, model: str) -> None:
        self.model = model
        skill = _load_skill()
        refs_text, self.loaded_refs = load_references(model)
        self.system_prompt = skill + refs_text
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
