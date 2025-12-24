#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AUTOMATOR CLI - Command Line Interface
Ferramentas de linha de comando para administração do Automatizador IA
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional
import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.text import Text

# Adiciona src ao path
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent
src_dir = project_root / "src"

for path in [str(project_root), str(src_dir)]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Imports da aplicação
from src.application.services.automation_orchestrator import AutomationOrchestrator
from src.infrastructure.persistence.sqlalchemy_task_repository import SQLAlchemyTaskRepository
from src.infrastructure.external_services.playwright_automation_service import PlaywrightAutomationService
from src.shared.utils.logger import get_logger

# Console Rich
console = Console()

# Logger
logger = get_logger(__name__)


class AutomatorCLI:
    """CLI principal do Automatizador"""

    def __init__(self):
        self.orchestrator: Optional[AutomationOrchestrator] = None

    async def initialize(self):
        """Inicializa serviços"""
        try:
            with console.status("[bold green]Inicializando serviços...") as status:
                # Inicializa repositório e serviços
                task_repo = SQLAlchemyTaskRepository()
                automation_service = PlaywrightAutomationService()

                # Inicializa serviços assíncronos
                await task_repo._ensure_initialized()
                await automation_service._ensure_initialized()

                # Cria orchestrator
                self.orchestrator = AutomationOrchestrator(
                    task_repository=task_repo,
                    automation_service=automation_service
                )

            console.print("[green]✓[/green] Serviços inicializados com sucesso")

        except Exception as e:
            console.print(f"[red]✗[/red] Erro na inicialização: {e}")
            raise

    async def list_tasks(self, status: Optional[str] = None, limit: int = 50):
        """Lista tarefas"""
        if not self.orchestrator:
            await self.initialize()

        try:
            filters = {}
            if status:
                filters["status"] = status
            if limit:
                filters["limit"] = limit

            result = await self.orchestrator.get_tasks(filters)

            if "tasks" in result:
                tasks = result["tasks"]

                if not tasks:
                    console.print("[yellow]Nenhuma tarefa encontrada.[/yellow]")
                    return

                # Cria tabela
                table = Table(title="Tarefas de Automação")
                table.add_column("ID", style="cyan", no_wrap=True)
                table.add_column("Nome", style="white")
                table.add_column("Status", style="green")
                table.add_column("Sucesso", style="blue")
                table.add_column("Criado em", style="magenta")

                for task in tasks:
                    status_color = {
                        "completed": "green",
                        "failed": "red",
                        "running": "yellow",
                        "pending": "blue"
                    }.get(task["status"], "white")

                    table.add_row(
                        task["id"][:8] + "...",
                        task["name"],
                        f"[{status_color}]{task['status']}[/{status_color}]",
                        f"{task['success_rate']:.1f}%",
                        task["created_at"][:10]
                    )

                console.print(table)
                console.print(f"\n[yellow]Total: {len(tasks)} tarefas[/yellow]")

        except Exception as e:
            console.print(f"[red]Erro ao listar tarefas: {e}[/red]")

    async def create_task(self, name: str, url: str, username: str = "", password: str = ""):
        """Cria nova tarefa"""
        if not self.orchestrator:
            await self.initialize()

        try:
            task_data = {
                "id": f"task_{asyncio.get_event_loop().time()}",
                "name": name,
                "url": url,
                "username": username,
                "password": password
            }

            with console.status("[bold green]Criando tarefa...") as status:
                result = await self.orchestrator.create_task(task_data)

            if result["success"]:
                console.print(f"[green]✓[/green] Tarefa criada com sucesso!")
                console.print(f"[cyan]ID:[/cyan] {result['task']['id']}")
                console.print(f"[cyan]Nome:[/cyan] {result['task']['name']}")
            else:
                console.print(f"[red]✗[/red] Erro ao criar tarefa: {result['message']}")

        except Exception as e:
            console.print(f"[red]Erro ao criar tarefa: {e}[/red]")

    async def execute_task(self, task_id: str):
        """Executa uma tarefa"""
        if not self.orchestrator:
            await self.initialize()

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Executando tarefa...", total=None)

                result = await self.orchestrator.execute_task(task_id)

                if result["success"] is not None:
                    if result["success"]:
                        console.print(f"[green]✓[/green] Tarefa executada com sucesso!")
                        console.print(f"[cyan]Tempo:[/cyan] {result.get('execution_time', 0):.2f}s")
                    else:
                        console.print(f"[red]✗[/red] Falha na execução: {result.get('message', 'Erro desconhecido')}")
                else:
                    console.print(f"[red]✗[/red] Erro na execução: {result.get('message', 'Erro interno')}")

        except Exception as e:
            console.print(f"[red]Erro ao executar tarefa: {e}[/red]")

    async def analyze_page(self, url: str):
        """Analisa uma página web"""
        if not self.orchestrator:
            await self.initialize()

        try:
            with console.status("[bold green]Analisando página...") as status:
                result = await self.orchestrator.analyze_webpage(url)

            if result["success"]:
                analysis = result.get("analysis", {})
                recommendations = result.get("recommendations", {})

                console.print("[green]✓[/green] Análise concluída!")

                # Informações básicas
                console.print(f"[cyan]URL:[/cyan] {analysis.get('url')}")
                console.print(f"[cyan]Título:[/cyan] {analysis.get('title', 'N/A')}")
                console.print(f"[cyan]Formulários:[/cyan] {analysis.get('forms_count', 0)}")
                console.print(f"[cyan]Inputs:[/cyan] {analysis.get('inputs_count', 0)}")

                # Recomendações
                if recommendations:
                    console.print("\n[yellow]Recomendações de seletores:[/yellow]")
                    for field, selector in recommendations.items():
                        if selector:
                            console.print(f"  [cyan]{field}:[/cyan] {selector}")

                # Elementos encontrados
                username_fields = analysis.get('potential_username_fields', [])
                password_fields = analysis.get('potential_password_fields', [])
                submit_buttons = analysis.get('potential_submit_buttons', [])

                if username_fields:
                    console.print(f"\n[green]Campos usuário encontrados:[/green] {len(username_fields)}")
                    for field in username_fields[:3]:  # Top 3
                        console.print(f"  • {field.get('selector', 'N/A')} (conf: {field.get('confidence', 0)})")

                if password_fields:
                    console.print(f"\n[green]Campos senha encontrados:[/green] {len(password_fields)}")
                    for field in password_fields[:3]:  # Top 3
                        console.print(f"  • {field.get('selector', 'N/A')} (conf: {field.get('confidence', 0)})")

                if submit_buttons:
                    console.print(f"\n[green]Botões submit encontrados:[/green] {len(submit_buttons)}")
                    for button in submit_buttons[:3]:  # Top 3
                        console.print(f"  • {button.get('selector', 'N/A')} (conf: {button.get('confidence', 0)})")

            else:
                console.print(f"[red]✗[/red] Erro na análise: {result.get('message', 'Erro desconhecido')}")

        except Exception as e:
            console.print(f"[red]Erro na análise: {e}[/red]")

    async def health_check(self):
        """Verifica saúde do sistema"""
        if not self.orchestrator:
            await self.initialize()

        try:
            result = await self.orchestrator.get_system_health()

            if result["status"] == "healthy":
                console.print("[green]✓ Sistema saudável[/green]")
            elif result["status"] == "degraded":
                console.print("[yellow]⚠ Sistema degradado[/yellow]")
            else:
                console.print("[red]✗ Sistema com problemas[/red]")

            # Detalhes dos serviços
            services = result.get("services", {})
            for service_name, status in services.items():
                status_color = "green" if status == "healthy" else "red" if status == "unhealthy" else "yellow"
                console.print(f"  [{status_color}]{service_name}: {status}[/{status_color}]")

        except Exception as e:
            console.print(f"[red]Erro no health check: {e}[/red]")

    async def cleanup(self):
        """Limpa recursos"""
        try:
            if self.orchestrator and hasattr(self.orchestrator.automation_service, 'cleanup'):
                await self.orchestrator.automation_service.cleanup()
            console.print("[green]✓[/green] Recursos liberados")
        except Exception as e:
            console.print(f"[red]Erro na limpeza: {e}[/red]")


# Instância global
cli = AutomatorCLI()


# ===== CLI COMMANDS =====

@click.group()
@click.version_option(version="7.0.0")
def main():
    """Automator IA v7.0 - CLI Tools

    Ferramentas de linha de comando para administração e operação.
    """
    pass


@main.command()
@click.option('--status', help='Filtrar por status (pending, running, completed, failed)')
@click.option('--limit', default=50, help='Limite de resultados')
def tasks(status, limit):
    """Lista tarefas de automação"""
    asyncio.run(cli.list_tasks(status, limit))


@main.command()
@click.argument('name')
@click.argument('url')
@click.option('--username', default='', help='Nome de usuário')
@click.option('--password', default='', help='Senha')
def create(name, url, username, password):
    """Cria nova tarefa de automação"""
    asyncio.run(cli.create_task(name, url, username, password))


@main.command()
@click.argument('task_id')
def execute(task_id):
    """Executa uma tarefa de automação"""
    asyncio.run(cli.execute_task(task_id))


@main.command()
@click.argument('url')
def analyze(url):
    """Analisa uma página web para automação"""
    asyncio.run(cli.analyze_page(url))


@main.command()
def health():
    """Verifica saúde do sistema"""
    asyncio.run(cli.health_check())


@main.command()
@click.option('--force', is_flag=True, help='Força limpeza sem confirmação')
def cleanup(force):
    """Limpa recursos e cache"""
    if not force:
        if not click.confirm('Tem certeza que deseja limpar os recursos?'):
            return

    asyncio.run(cli.cleanup())


if __name__ == '__main__':
    main()
