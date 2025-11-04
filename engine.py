# engine.py
import asyncio
from typing import List, Type
from sqlalchemy.orm import Session
from database import Entity, EntityStatus, TransformResult, SessionLocal
from models import BaseEntity
from modules.base_transform import BaseTransform
from rich.console import Console

console = Console()

class InvestigationEngine:
    def __init__(self, investigation_id: int):
        self.investigation_id = investigation_id
        self.session: Session = SessionLocal()
        # Карта "маршрутизации": Какой тип -> какими модулями проверять
        self.transform_map: dict[str, List[Type[BaseTransform]]] = {}

    def register_transforms(self, transforms: List[Type[BaseTransform]]):
        """Регистрирует 'карту' модуль->тип."""
        for transform in transforms:
            input_type_name = transform.input_type.__name__
            if input_type_name not in self.transform_map:
                self.transform_map[input_type_name] = []
            self.transform_map[input_type_name].append(transform)

        console.print(f"[bold blue]Движок: Зарегистрированы трансформы:[/bold blue] {self.transform_map.keys()}")

    async def _get_next_queued_entity(self) -> Entity | None:
        """Получает 1 сущность из очереди в БД."""
        entity = self.session.query(Entity).filter(
            Entity.investigation_id == self.investigation_id,
            Entity.status == EntityStatus.QUEUED
        ).first()
        return entity

    async def _run_transform(self, transform_class: Type[BaseTransform], db_entity: Entity):
        """Полный цикл запуска одного модуля для одной сущности."""
        transform_name = transform_class.transform_name
        console.print(f"[grey50]  -> Запуск [bold]{transform_name}[/bold] для {db_entity.value}...[/grey50]")

        # 1. Создаем Pydantic-модель из БД-модели
        # (pydantic.from_orm может быть сложным, пока сделаем просто)
        # Учитываем, что у Port value - это int
        entity_value = int(db_entity.value) if transform_class.input_type == "Port" else db_entity.value
        pydantic_entity = transform_class.input_type(value=entity_value)

        transform_instance = transform_class(
            entity=pydantic_entity,
            session=self.session,
            investigation_id=self.investigation_id
        )

        db_result = TransformResult(
            entity_id=db_entity.id,
            transform_name=transform_name,
            raw_output_file=str(transform_instance.output_file)
        )

        try:
            # 2. ЗАПУСК
            raw_output = await transform_instance.run()
            await transform_instance.save_raw_output(raw_output)

            # 3. ПАРСИНГ
            new_pydantic_entities = transform_instance.parse(raw_output)

            # 4. СОХРАНЕНИЕ
            for p_entity in new_pydantic_entities:
                self.add_entity_to_db(p_entity, transform_name)

            db_result.success = "SUCCESS"
            console.print(f"[green]  [+] Успех: [bold]{transform_name}[/bold]. Найдено: {len(new_pydantic_entities)} новых сущностей.[/green]")

        except Exception as e:
            db_result.success = "FAILED"
            console.print(f"[bold red]  [!] ОШИБКА: [bold]{transform_name}[/bold] на {db_entity.value}: {e}[/bold red]")
            await transform_instance.save_raw_output(f"ОШИБКА ВЫПОЛНЕНИЯ: {e}")

        finally:
            self.session.add(db_result)
            self.session.commit()

    def add_entity_to_db(self, p_entity: BaseEntity, source_transform: str):
        """Добавляет новую сущность в БД, если ее еще нет."""
        exists = self.session.query(Entity).filter(
            Entity.investigation_id == self.investigation_id,
            Entity.type == p_entity.entity_type,
            Entity.value == str(p_entity.value) # str() на случай Port(value=80)
        ).first()

        if not exists:
            new_db_entity = Entity(
                investigation_id=self.investigation_id,
                type=p_entity.entity_type,
                value=str(p_entity.value),
                status=EntityStatus.QUEUED,
                source_transform_name=source_transform
            )
            self.session.add(new_db_entity)
            self.session.commit()
            console.print(f"[cyan]    > Новая сущность: ({p_entity.entity_type}) {p_entity.value}[/cyan]")

    async def start(self):
        """Главный цикл 'пивотинга'."""
        console.print(f"[bold green]Запуск расследования #{self.investigation_id}...[/bold green]")

        while True:
            db_entity = await self._get_next_queued_entity()

            if not db_entity:
                console.print("[bold blue]Очередь пуста. Расследование завершено.[/bold blue]")
                break

            # 1. Помечаем как "в работе"
            db_entity.status = EntityStatus.PROCESSING
            self.session.commit()
            console.print(f"\n[bold yellow]Обработка:[/bold yellow] ({db_entity.type}) {db_entity.value}")

            # 2. Находим нужные модули
            transforms_to_run = self.transform_map.get(db_entity.type, [])

            # 3. Запускаем их параллельно
            tasks = [self._run_transform(transform_class, db_entity) for transform_class in transforms_to_run]
            await asyncio.gather(*tasks)

            # 4. Помечаем как "готово"
            db_entity.status = EntityStatus.DONE
            self.session.commit()

        self.session.close()
