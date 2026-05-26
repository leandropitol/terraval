# 🌾 TerraVal

**Agente CLI especialista em Avaliações de Imóveis Rurais**

Co-piloto técnico para engenheiros avaliadores, peritos judiciais e analistas de crédito rural. Fundamentado na **ABNT NBR 14653**, no **Atlas do Mercado de Terras INCRA 2025** e na **Resolução BACEN nº 4.676/2018**.

Funciona com qualquer chave de API: **Anthropic**, **OpenAI**, **Google Gemini**, **Groq** ou **OpenRouter**.

---

## Instalação

### Windows (CMD ou PowerShell)
```cmd
pip install git+https://github.com/leandropitol/terraval.git
```

### Linux / macOS
```bash
curl -fsSL https://raw.githubusercontent.com/leandropitol/terraval/main/install.sh | bash
```

### Windows (PowerShell — one-liner)
```powershell
iwr https://raw.githubusercontent.com/leandropitol/terraval/main/install.ps1 | iex
```

> **Requisito:** Python 3.10 ou superior — [python.org/downloads](https://www.python.org/downloads/)

---

## Início rápido

```bash
# 1. Configurar provedor e API key (feito uma única vez)
terraval setup

# 2. Iniciar o agente
terraval
```

Na primeira execução sem `setup`, o assistente de configuração abre automaticamente.

---

## Provedores suportados

| # | Provedor | Modelos disponíveis | Obter chave |
|---|---|---|---|
| 1 | **Anthropic** (recomendado) | Claude Sonnet 4.6, Opus 4.7, Haiku 4.5 | [console.anthropic.com](https://console.anthropic.com/) |
| 2 | **OpenAI** | GPT-4o, GPT-4o Mini, o3-mini | [platform.openai.com](https://platform.openai.com/api-keys) |
| 3 | **Google Gemini** | Gemini 2.0 Flash, Gemini 2.5 Pro | [aistudio.google.com](https://aistudio.google.com/apikey) |
| 4 | **Groq** *(plano gratuito)* | Llama 3.3 70B, Llama 3.1 8B | [console.groq.com](https://console.groq.com/keys) |
| 5 | **OpenRouter** *(200+ modelos)* | Claude, GPT, Gemini e mais | [openrouter.ai/keys](https://openrouter.ai/keys) |

Trocar de provedor a qualquer momento: `terraval setup`

---

## Comandos no terminal

| Comando | Ação |
|---|---|
| `/ajuda`  | Lista todos os comandos disponíveis |
| `/limpar` | Limpa o histórico da conversa atual |
| `/modelo` | Exibe o modelo e provedor ativos |
| `/config` | Reconfigura provedor e API key |
| `/sair`   | Encerra o TerraVal |

---

## Exemplos de uso

```
▶ Avalie uma fazenda de 800 ha em pecuária extensiva em Unaí/MG. Região com
  histórico de R$ 9.000 a R$ 14.000/ha. Elabore o laudo completo com campo
  de arbítrio e disclaimer CREA.

▶ Tenho 12 amostras de transações: [lista de R$/ha]. Aplique Box Plot,
  elimine outliers e calcule o VTN homogeneizado.

▶ Qual o grau de fundamentação e precisão com 10 dados tratados por fatores
  de homogeneização, sem regressão?

▶ Calcule o VTI de uma fazenda com VTN de R$ 4.200.000, pastagem formada
  (180 ha × R$ 1.800/ha), sede (R$ 320.000 CRN, Ross-Heidecke 60%) e
  passivo ambiental de R$ 180.000 em APP degradada.

▶ Qual o LTV máximo para garantia de R$ 3,5M numa operação SFI? Qual o
  valor máximo financiável?
```

---

## O que o TerraVal cobre

**Metodologias (NBR 14653-3):**
- Método Comparativo Direto de Dados de Mercado (MCDDM)
- Método Evolutivo → VTI = VTN + VBR + VBNR + AA − PA
- Método da Capitalização da Renda (florestas, arrendamento)

**Tratamento estatístico:**
- Box Plot para eliminação de outliers
- Regressão Linear Múltipla com comprovação de pressupostos (Shapiro-Wilk, Durbin-Watson, VIF)
- Fatores de homogeneização (Fonte, Localização, Capacidade de Uso, Área)

**Compliance e resultados:**
- Grau de Fundamentação (I, II ou III)
- Grau de Precisão (coeficiente de variação)
- Campo de Arbítrio ± 15%
- Análise LTV conforme Resolução BACEN nº 4.676/2018
- Disclaimer obrigatório CONFEA/CREA/ART

---

## Configuração salva

As configurações ficam em `~/.terraval/config.json` (Linux/macOS) ou `%USERPROFILE%\.terraval\config.json` (Windows). Nenhuma chave é enviada a servidores externos — tudo vai direto para o provedor escolhido.

---

## Estrutura do projeto

```
terraval/
├── pyproject.toml
├── install.sh          ← Linux/macOS
├── install.ps1         ← Windows PowerShell
└── terraval/
    ├── cli.py          ← interface de terminal (rich + typer)
    ├── agent.py        ← loop de conversa com streaming (litellm)
    ├── config.py       ← gerenciamento de ~/.terraval/config.json
    └── data/
        └── SKILL.md    ← system prompt (5 módulos NBR 14653)
```

---

## Desenvolvido por

**Leandro Pitol**  
Baseado na ABNT NBR 14653 (partes 1, 3, 4, 5 e 6), Atlas do Mercado de Terras INCRA 2025 e Resolução BACEN nº 4.676/2018.

Skill fonte: [leandropitol/claude-skills](https://github.com/leandropitol/claude-skills/tree/main/skills/avaliacao-rural)

---

*Este agente é uma ferramenta de suporte técnico. Laudos com validade legal exigem vistoria presencial, validação e assinatura de profissional habilitado no CREA com emissão de ART.*
