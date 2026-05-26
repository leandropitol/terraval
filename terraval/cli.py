import typer
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich import box

from .exporter import save_report
from .agent import TerraValAgent
from .config import (
    PROVIDERS,
    is_configured,
    load_config,
    save_config,
    get_provider_info,
)

app = typer.Typer(
    name="terraval",
    help="Agente CLI especialista em Avaliações de Imóveis Rurais — NBR 14653 · Atlas INCRA 2025 · BACEN 4.676/2018",
    add_completion=False,
)
console = Console()


# ── UI helpers ────────────────────────────────────────────────────────────────

def print_banner(model: str, loaded_refs: list[str]) -> None:
    docs_line = "\n".join(f"  [green]✓[/green] [dim]{r}[/dim]" for r in loaded_refs)
    console.print()
    console.print(Panel.fit(
        "[bold green]🌾  TerraVal[/bold green]  [dim]—  Especialista em Avaliações de Imóveis Rurais[/dim]\n"
        "[dim]NBR 14653  ·  Atlas INCRA 2025  ·  BACEN Res. 4.676/2018[/dim]\n\n"
        f"[dim]Modelo:[/dim] [cyan]{model}[/cyan]\n\n"
        f"[dim]Documentos carregados:[/dim]\n{docs_line}\n\n"
        "[dim][bold]/ajuda[/bold] para comandos  │  [bold]/sair[/bold] para encerrar[/dim]",
        border_style="green",
        padding=(0, 2),
    ))
    console.print()


def print_help() -> None:
    t = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    t.add_column(style="green bold")
    t.add_column()
    t.add_row("/ajuda",        "Mostra esta mensagem")
    t.add_row("/salvar",       "Salva o último laudo em .docx e .pdf")
    t.add_row("/salvar docx",  "Salva somente em Word (.docx)")
    t.add_row("/salvar pdf",   "Salva somente em PDF")
    t.add_row("/salvar md",    "Salva somente em Markdown (.md)")
    t.add_row("/limpar",       "Limpa o histórico da conversa atual")
    t.add_row("/modelo",       "Exibe o modelo e provedor ativos")
    t.add_row("/config",       "Reconfigura provedor e API key")
    t.add_row("/sair",         "Encerra o TerraVal")
    console.print(Panel(t, title="[bold]Comandos[/bold]", border_style="dim", padding=(0, 1)))

    e = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    e.add_column(style="dim")
    for ex in [
        "Avalie uma fazenda de 500 ha em pecuária extensiva em Unaí/MG",
        "Tenho 10 amostras de R$/ha — aplique Box Plot e homogeneização",
        "Calcule o LTV máximo para garantia de R$ 3,2M com operação de R$ 1,8M",
        "Qual o grau de fundamentação com 12 dados tratados por fatores?",
        "Monte o Módulo 5 completo com campo de arbítrio e disclaimer CREA",
    ]:
        e.add_row(f'"{ex}"')
    console.print(Panel(e, title="[bold]Exemplos[/bold]", border_style="dim", padding=(0, 1)))
    console.print()


# ── Setup wizard ──────────────────────────────────────────────────────────────

def run_setup() -> dict:
    console.print()
    console.print(Panel(
        "[bold]Configuração inicial do TerraVal[/bold]\n"
        "[dim]Configuração salva em [cyan]~/.terraval/config.json[/cyan][/dim]",
        border_style="yellow", padding=(0, 2),
    ))
    console.print()

    console.print("[bold]1. Escolha o provedor LLM:[/bold]\n")
    for k, p in PROVIDERS.items():
        console.print(f"   [green]{k}[/green]  {p['name']}")

    console.print()
    while True:
        choice = Prompt.ask("[bold]Provedor[/bold]", default="1")
        if choice in PROVIDERS:
            break
        console.print("[red]  Opção inválida — digite um número de 1 a 5.[/red]")

    prov = PROVIDERS[choice]
    console.print()

    console.print(f"[bold]2. Modelo ({prov['name']}):[/bold]\n")
    for k, (mid, desc) in prov["models"].items():
        console.print(f"   [green]{k}[/green]  {desc}")

    console.print()
    model_choice = Prompt.ask("[bold]Modelo[/bold]", default="1")
    if model_choice not in prov["models"]:
        model_choice = "1"
    model_id, _ = prov["models"][model_choice]

    console.print()
    console.print(f"[bold]3. API Key — {prov['name']}[/bold]")
    console.print(f"   [dim]Obtenha em: [link={prov['key_url']}]{prov['key_url']}[/link][/dim]")
    console.print("   [dim]No CMD: cole com clique direito do mouse[/dim]\n")
    api_key = Prompt.ask("[bold]Cole sua API Key[/bold]")

    config = {
        "provider": prov["key"],
        "model":    model_id,
        "api_key":  api_key,
    }
    save_config(config)

    console.print()
    console.print("[bold green]✓  Configuração salva.[/bold green]  Execute [bold]terraval[/bold] para começar.\n")
    return config


# ── Commands ──────────────────────────────────────────────────────────────────

@app.command()
def setup():
    """Configura (ou reconfigura) o provedor LLM e a API key."""
    run_setup()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """Inicia o agente TerraVal no terminal."""
    if ctx.invoked_subcommand is not None:
        return

    config = load_config()
    if not is_configured(config):
        console.print("[yellow]Nenhuma configuração encontrada.[/yellow]")
        config = run_setup()

    provider_info = get_provider_info(config)
    model = config["model"]
    api_key = config["api_key"]

    agent = TerraValAgent(model=model, provider_info=provider_info, api_key=api_key)
    print_banner(model, agent.loaded_refs)

    while True:
        try:
            user_input = Prompt.ask("[bold green]▶[/bold green]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Encerrando TerraVal...[/dim]")
            break

        text = user_input.strip()
        if not text:
            continue

        cmd = text.lower()

        if cmd in ("/sair", "/exit", "/quit", "exit", "quit"):
            console.print("[dim]Encerrando TerraVal...[/dim]")
            break

        elif cmd == "/ajuda":
            print_help()
            continue

        elif cmd.startswith("/salvar"):
            if not agent.last_response:
                console.print("[yellow]Nenhum laudo gerado ainda. Faça uma pergunta primeiro.[/yellow]\n")
                continue
            parts = cmd.split()
            fmts = parts[1:] if len(parts) > 1 else ["docx", "pdf"]
            fmts = [f for f in fmts if f in {"docx", "pdf", "md"}] or ["docx", "pdf"]
            console.print(f"[dim]Salvando em {', '.join(f.upper() for f in fmts)}...[/dim]")
            try:
                saved = save_report(agent.last_response, fmts)
                for fmt, path in saved.items():
                    console.print(f"  [green]✓[/green] [bold]{fmt.upper()}[/bold] → [cyan]{path}[/cyan]")
            except Exception as e:
                console.print(f"[red]Erro ao salvar: {e}[/red]")
            console.print()
            continue

        elif cmd == "/limpar":
            agent.clear_history()
            console.print("[dim]Histórico limpo.[/dim]\n")
            continue

        elif cmd == "/modelo":
            console.print(f"[dim]Modelo ativo: [bold cyan]{model}[/bold cyan][/dim]\n")
            continue

        elif cmd == "/config":
            config = run_setup()
            provider_info = get_provider_info(config)
            model = config["model"]
            api_key = config["api_key"]
            agent = TerraValAgent(model=model, provider_info=provider_info, api_key=api_key)
            print_banner(model, agent.loaded_refs)
            continue

        # ── Stream response ────────────────────────────────────────────────
        console.print()
        try:
            full = ""
            with Live(console=console, refresh_per_second=12, vertical_overflow="visible") as live:
                for delta in agent.chat(text):
                    full += delta
                    live.update(Markdown(full))
        except Exception as e:
            console.print(f"[red]Erro: {e}[/red]")

        console.print()
