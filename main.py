# main.py
import asyncio
import questionary
from rich.console import Console
from rich.panel import Panel

# Импорты из нашего проекта
from database import create_db_and_tables, SessionLocal, Investigation, Entity, EntityStatus
from models import (
    Domain, IPAddress, Username, Subdomain, Port, Service,
    Technology, GPSLocation, Email, URL, BaseEntity
)
from engine import InvestigationEngine

# Импорты наших модулей
from modules.domain_transforms import Sublist3rTransform
from modules.ip_transforms import NmapTransform
# (Здесь мы будем добавлять новые модули)

# --- 1. Собираем ВСЕ наши модули ---
ALL_TRANSFORMS = [
    Sublist3rTransform,
    NmapTransform,
    # SherlockTransform, (добавим в след. задаче)
]

# --- 2. Определяем, какие "семена" (seeds) мы принимаем ---
SEED_ENTITY_TYPES = {
    "Domain": Domain,
    "IPAddress": IPAddress,
    "Username": Username,
}

console = Console()

def show_banner():
    """Показывает этический баннер."""
    banner = Panel(
        "[bold red]ВНИМАНИЕ![/bold red] Этот инструмент предназначен для образовательных и [bold green]оборонительных (Blue Team)[/bold green] целей, например, для аудита [bold]собственной[/bold] инфраструктуры. Несанкционированное сканирование чужих систем незаконно. Автор не несет ответственности за неправомерное использование.",
        title="ЭТИЧЕСКОЕ ПРЕДУПРЕЖДЕНИЕ",
        border_style="red",
        width=80
    )
    console.print(banner)

async def start_new_investigation():
    """Запускает мастер создания нового расследования."""

    # --- Шаг 1: Запрос у пользователя ---
    investigation_name = await questionary.text("Название расследования (напр., 'my-company-audit'):").ask_async()
    if not investigation_name:
        investigation_name = "Новое расследование"

    seed_type_name = await questionary.select(
        "Тип начальной 'сущности':",
        choices=list(SEED_ENTITY_TYPES.keys())
    ).ask_async()

    seed_value = await questionary.text(f"Введите {seed_type_name}:").ask_async()
    if not seed_value:
        console.print("[red]Значение не может быть пустым.[/red]")
        return

    # --- Шаг 2: Создание в БД ---
    session = SessionLocal()

    # 2.1. Создаем Расследование
    new_investigation = Investigation(name=investigation_name)
    session.add(new_investigation)
    session.commit()
    session.refresh(new_investigation)

    investigation_id = new_investigation.id

    # 2.2. Создаем "семенную" Сущность
    seed_entity = Entity(
        investigation_id=investigation_id,
        type=seed_type_name,
        value=seed_value,
        status=EntityStatus.QUEUED, # Ставим в очередь
        source_transform_name="Seed"
    )
    session.add(seed_entity)
    session.commit()
    session.close()

    console.print(f"\n[bold green]Расследование '{investigation_name}' (ID: {investigation_id}) создано.[/bold green]")
    console.print(f"Начальная сущность: ({seed_type_name}) {seed_value}")

    # --- Шаг 3: Запуск Движка ---
    engine = InvestigationEngine(investigation_id=investigation_id)
    engine.register_transforms(ALL_TRANSFORMS)

    await engine.start()

async def main_menu():
    """Главное меню программы."""
    show_banner()

    # (Здесь в будущем можно добавить "Посмотреть старые расследования")
    action = await questionary.select(
        "Выберите действие:",
        choices=["Начать новое расследование", "Выход"]
    ).ask_async()

    if action == "Начать новое расследование":
        await start_new_investigation()
    else:
        console.print("[bold]До свидания![/bold]")

if __name__ == "__main__":
    # 1. Убедимся, что БД и таблицы существуют
    create_db_and_tables()

    # 2. Запускаем асинхронное TUI
    try:
        asyncio.run(main_menu())
    except KeyboardInterrupt:
        console.print("\n[bold red]Выход по нажатию Ctrl+C...[/bold red]")
