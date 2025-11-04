# database.py
import datetime
import enum
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Enum as DBEnum
from sqlalchemy.orm import sessionmaker, relationship, DeclarativeBase
from config import BASE_DIR

# --- Конфигурация БД ---
DATABASE_URL = f"sqlite:///{BASE_DIR / 'investigations.db'}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

# --- Перечисление для статусов ---
class EntityStatus(enum.Enum):
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    DONE = "DONE"
    FAILED = "FAILED"

# --- Модель 1: Расследование ---
class Investigation(Base):
    __tablename__ = "investigations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    entities = relationship("Entity", back_populates="investigation")

# --- Модель 2: Сущность ---
class Entity(Base):
    __tablename__ = "entities"
    id = Column(Integer, primary_key=True, index=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id"))
    type = Column(String, index=True)  # "Domain", "IPAddress"
    value = Column(String, index=True) # "google.com", "8.8.8.8"
    status = Column(DBEnum(EntityStatus), default=EntityStatus.QUEUED)
    source_transform_name = Column(String, nullable=True) # Откуда взялась
    investigation = relationship("Investigation", back_populates="entities")
    results = relationship("TransformResult", back_populates="entity")

# --- Модель 3: Результат Трансформа ---
class TransformResult(Base):
    __tablename__ = "transform_results"
    id = Column(Integer, primary_key=True, index=True)
    entity_id = Column(Integer, ForeignKey("entities.id"))
    transform_name = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    success = Column(String, default="UNKNOWN") # "SUCCESS" or "FAILED"
    raw_output_file = Column(String, nullable=True)
    entity = relationship("Entity", back_populates="results")

# --- Функция для создания таблиц ---
def create_db_and_tables():
    Base.metadata.create_all(bind=engine)