# modules/base_transform.py
from abc import ABC, abstractmethod
from typing import List
from models import BaseEntity
from sqlalchemy.orm import Session
from config import OUTPUT_DIR
import aiofiles
import os

class BaseTransform(ABC):
    """Абстрактный базовый класс для всех 'Трансформов'."""

    # Имя (должно быть уникальным)
    transform_name = "BaseTransform"
    # Тип Pydantic-модели на вход (напр., Domain)
    input_type = BaseEntity

    def __init__(self, entity: BaseEntity, session: Session, investigation_id: int):
        self.entity = entity
        self.session = session # Сессия БД для записи результатов
        self.investigation_id = investigation_id

        # Создаем директорию для логов, если ее нет
        self.output_dir = OUTPUT_DIR / str(self.investigation_id)
        os.makedirs(self.output_dir, exist_ok=True)

        # Уникальное имя файла для лога
        self.output_file = self.output_dir / f"{entity.value.replace('://', '_').replace('/', '_')}_{self.transform_name}.log"

    @abstractmethod
    async def run(self) -> str:
        """
        Метод для запуска внешнего инструмента (через subprocess).
        Должен вернуть СЫРОЙ текстовый вывод.
        """
        pass

    @abstractmethod
    def parse(self, raw_output: str) -> List[BaseEntity]:
        """
        Метод для парсинга сырого вывода.
        Должен вернуть список НОВЫХ Pydantic-моделей (Сущностей).
        """
        pass

    async def save_raw_output(self, raw_output: str):
        """Вспомогательная функция для сохранения сырого лога."""
        async with aiofiles.open(self.output_file, 'w', encoding='utf-8') as f:
            await f.write(raw_output)
