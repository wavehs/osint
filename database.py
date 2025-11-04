from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
import datetime
from sqlalchemy.future import select

DATABASE_URL = "sqlite+aiosqlite:///investigations.db"

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()

class Investigation(Base):
    __tablename__ = "investigations"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    start_time = Column(DateTime, default=datetime.datetime.utcnow)

class Entity(Base):
    __tablename__ = "entities"
    id = Column(Integer, primary_key=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id"))
    type = Column(String)
    value = Column(String)
    status = Column(String, default="QUEUED")  # QUEUED, PROCESSING, DONE, FAILED
    source_transform_name = Column(String, nullable=True)

class TransformResult(Base):
    __tablename__ = "transform_results"
    id = Column(Integer, primary_key=True)
    entity_id = Column(Integer, ForeignKey("entities.id"))
    transform_name = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    raw_output_file = Column(String, nullable=True)
    success = Column(Boolean)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def create_investigation(name: str) -> int:
    async with async_session() as session:
        async with session.begin():
            investigation = Investigation(name=name)
            session.add(investigation)
            await session.flush()
            return investigation.id

async def add_entity(investigation_id: int, entity_type: str, entity_value: str, status: str = "QUEUED", source: str = None) -> Entity:
    async with async_session() as session:
        async with session.begin():
            entity = Entity(
                investigation_id=investigation_id,
                type=entity_type,
                value=entity_value,
                status=status,
                source_transform_name=source
            )
            session.add(entity)
            await session.flush()
            return entity

async def get_next_queued_entity():
    async with async_session() as session:
        result = await session.execute(
            select(Entity).where(Entity.status == "QUEUED").limit(1)
        )
        return result.scalars().first()

async def set_entity_status(entity_id: int, status: str):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(Entity).where(Entity.id == entity_id))
            entity = result.scalars().first()
            if entity:
                entity.status = status

async def add_entity_if_not_exists(investigation_id: int, entity_type: str, entity_value: str, source: str):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(Entity).where(Entity.investigation_id == investigation_id, Entity.value == entity_value)
            )
            existing_entity = result.scalars().first()
            if not existing_entity:
                await add_entity(investigation_id, entity_type, entity_value, source=source)
