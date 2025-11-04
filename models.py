# models.py
from pydantic import BaseModel, Field
from typing import Literal

class BaseEntity(BaseModel):
    """Базовая модель для всех Сущностей."""
    value: str = Field(..., description="Значение сущности")

    @property
    def entity_type(self) -> str:
        """Автоматически возвращает имя класса как 'тип'."""
        return self.__class__.__name__

class Domain(BaseEntity): pass
class Subdomain(BaseEntity): pass
class IPAddress(BaseEntity): pass
class Email(BaseEntity): pass
class Username(BaseEntity): pass
class URL(BaseEntity): pass
class Port(BaseEntity): value: int
class Service(BaseEntity): pass
class Technology(BaseEntity): pass
class GPSLocation(BaseEntity): pass