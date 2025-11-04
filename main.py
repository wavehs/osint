import asyncio
import questionary
from rich.console import Console
from rich.panel import Panel
import database
from engine import InvestigationEngine
import models

console = Console()

def print_banner():
    banner = """
    ██████╗ ███████╗██╗███╗   ██╗████████╗
    ██╔══██╗██╔════╝██║████╗  ██║╚══██╔══╝
    ██████╔╝███████╗██║██╔██╗ ██║   ██║
    ██╔══██╗╚════██║██║██║╚██╗██║   ██║
    ██║  ██║███████║██║██║ ╚████║   ██║
    ╚═╝  ╚═╝╚══════╝╚═╝╚═╝  ╚═══╝   ╚═╝

    -- An Automated OSINT Investigation Framework --
    """
    console.print(Panel.fit(banner, style="bold blue"))
    console.print(Panel.fit(
        "[bold red]ETHICAL USE NOTICE:[/bold red]\n"
        "This tool is intended for professional and authorized security analysis only. "
        "Unauthorized use against systems or individuals is illegal and unethical. "
        "By using this tool, you agree to do so responsibly and in accordance with all applicable laws.",
        title="Disclaimer",
        border_style="red"
    ))


async def start_new_investigation():
    name = await questionary.text("Investigation Name (e.g., 'my-company-audit'):").ask_async()
    if not name: return

    entity_type = await questionary.select(
        "Seed Entity Type:",
        choices=["Domain", "IPAddress", "Username"]
    ).ask_async()
    if not entity_type: return

    value = await questionary.text(f"Enter {entity_type}:").ask_async()
    if not value: return

    await database.init_db()
    investigation_id = await database.create_investigation(name)

    # Convert string type to Pydantic model class
    model_class = getattr(models, entity_type)
    seed_entity_model = model_class(value=value)

    await database.add_entity(investigation_id, entity_type, value, status="QUEUED")

    engine = InvestigationEngine(investigation_id)

    console.print(f"\n[bold green]Starting investigation '{name}'...[/bold green]")
    await engine.start(seed_entity_model)
    console.print(f"[bold blue]Investigation '{name}' complete![/bold blue]")


async def view_results():
    investigations = await database.get_all_investigations()
    if not investigations:
        console.print("\n[bold yellow]No investigations found.[/bold yellow]")
        return

    choices = [f"{inv.id}: {inv.name} ({inv.start_time.strftime('%Y-%m-%d %H:%M')})" for inv in investigations]

    selected_investigation_str = await questionary.select(
        "Select an investigation to view:",
        choices=choices
    ).ask_async()

    if not selected_investigation_str:
        return

    investigation_id = int(selected_investigation_str.split(":")[0])

    entities = await database.get_entities_for_investigation(investigation_id)

    from rich.table import Table
    table = Table(title=f"Results for Investigation {investigation_id}")
    table.add_column("ID", style="dim")
    table.add_column("Type", style="cyan")
    table.add_column("Value", style="green")
    table.add_column("Source Transform", style="yellow")
    table.add_column("Status", style="magenta")

    for entity in entities:
        table.add_row(
            str(entity.id),
            entity.type,
            entity.value,
            entity.source_transform_name or "Seed",
            entity.status
        )

    console.print(table)


async def main():
    while True:
        print_banner()
        choice = await questionary.select(
            "Main Menu:",
            choices=[
                "Start New Investigation",
                "View Results (by ID)",
                "Exit"
            ]
        ).ask_async()

        if choice == "Start New Investigation":
            await start_new_investigation()
        elif choice == "View Results (by ID)":
            await view_results()
        elif choice == "Exit" or choice is None:
            break

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Exiting...[/bold yellow]")
