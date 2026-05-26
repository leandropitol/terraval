import json
import os
from pathlib import Path

CONFIG_DIR = Path.home() / ".terraval"
CONFIG_FILE = CONFIG_DIR / "config.json"

PROVIDERS = {
    "1": {
        "name": "Anthropic (Claude)",
        "key": "anthropic",
        "models": {
            "1": ("claude-sonnet-4-6",          "Claude Sonnet 4.6  — recomendado (Recommended)"),
            "2": ("claude-opus-4-7",             "Claude Opus 4.7    — mais capaz, mais lento"),
            "3": ("claude-haiku-4-5-20251001",   "Claude Haiku 4.5   — rápido e econômico"),
        },
        "default_model": "claude-sonnet-4-6",
        "env_var": "ANTHROPIC_API_KEY",
        "key_url": "https://console.anthropic.com/",
    },
    "2": {
        "name": "OpenAI",
        "key": "openai",
        "models": {
            "1": ("gpt-4o",      "GPT-4o      — recomendado"),
            "2": ("gpt-4o-mini", "GPT-4o Mini — econômico"),
            "3": ("o3-mini",     "o3-mini     — raciocínio avançado"),
        },
        "default_model": "gpt-4o",
        "env_var": "OPENAI_API_KEY",
        "key_url": "https://platform.openai.com/api-keys",
    },
    "3": {
        "name": "Google Gemini",
        "key": "gemini",
        "models": {
            "1": ("gemini/gemini-2.0-flash", "Gemini 2.0 Flash — rápido"),
            "2": ("gemini/gemini-2.5-pro",   "Gemini 2.5 Pro   — mais capaz"),
        },
        "default_model": "gemini/gemini-2.0-flash",
        "env_var": "GEMINI_API_KEY",
        "key_url": "https://aistudio.google.com/apikey",
    },
    "4": {
        "name": "Groq  (ultra-rápido, plano gratuito disponível)",
        "key": "groq",
        "models": {
            "1": ("groq/llama-3.3-70b-versatile", "Llama 3.3 70B — recomendado"),
            "2": ("groq/llama-3.1-8b-instant",    "Llama 3.1 8B  — ultra-rápido"),
        },
        "default_model": "groq/llama-3.3-70b-versatile",
        "env_var": "GROQ_API_KEY",
        "key_url": "https://console.groq.com/keys",
    },
    "5": {
        "name": "OpenRouter  (200+ modelos com uma chave só)",
        "key": "openrouter",
        "models": {
            "1": ("openrouter/anthropic/claude-sonnet-4-5", "Claude Sonnet via OpenRouter"),
            "2": ("openrouter/openai/gpt-4o",               "GPT-4o via OpenRouter"),
            "3": ("openrouter/google/gemini-2.0-flash-001", "Gemini 2.0 Flash via OpenRouter"),
        },
        "default_model": "openrouter/anthropic/claude-sonnet-4-5",
        "env_var": "OPENROUTER_API_KEY",
        "key_url": "https://openrouter.ai/keys",
    },
}


def load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_config(config: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")


def is_configured(config: dict) -> bool:
    return bool(config.get("model") and config.get("api_key"))


def get_litellm_model(config: dict) -> str:
    return config.get("model", "claude-sonnet-4-6")


def apply_api_key(config: dict) -> None:
    provider_key = config.get("provider", "anthropic")
    api_key = config.get("api_key", "")
    for p in PROVIDERS.values():
        if p["key"] == provider_key:
            os.environ[p["env_var"]] = api_key
            # OpenRouter also needs this header
            if provider_key == "openrouter":
                os.environ["OPENROUTER_API_KEY"] = api_key
            return
