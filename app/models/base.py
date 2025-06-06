from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    Integer,
    select,
    String,
)
from sqlalchemy import delete as sqlalchemy_delete
from sqlalchemy import update as sqlalchemy_update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import (
    DeclarativeBase,
    declared_attr,
    mapped_column,
    Mapped,
)


class Base(DeclarativeBase):
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, index=True
    )


class TimestampMixin:
    created_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(tz=timezone.utc)
    )
    updated_on: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, onupdate=datetime.now(tz=timezone.utc)
    )


class CRUDMixin:
    @classmethod
    async def create(cls, session: AsyncSession, **kwargs):
        db_entry: cls = cls(**kwargs)
        try:
            session.add(db_entry)
            await session.flush()
            return db_entry
        except IntegrityError as ex:
            print(f"Duplicate Data: {ex}")
            raise Exception("Data already exists")
        except Exception as e:
            print(f"Exception: {e}")
            raise Exception("Database error")

    @classmethod
    async def update(cls, session: AsyncSession, id, **kwargs):
        query = (
            sqlalchemy_update(cls)
            .where(cls.id == id)
            .values(**kwargs)
            .execution_options(synchronize_session="fetch")
        )
        await session.execute(query)
        try:
            await session.commit()
        except Exception as e:
            await session.rollback()
            print(f"Error while updating: {e}")
            raise Exception("Database error")

    @classmethod
    async def get(cls, session: AsyncSession, id):
        query = select(cls).where(cls.id == id)
        results = await session.execute(query)
        item = results.scalars().first()
        if item is None:
            raise Exception(f"Invalid {cls.__name__.lower()} ID")
        return item

    @classmethod
    async def get_all(cls, session: AsyncSession, offset=None, limit=None):
        if offset and limit is not None:
            query = select(cls).offset(offset).limit(limit)
        else:
            query = select(cls)
        results = await session.execute(query)
        print(f"Results: {results}")
        items = results.scalars().all()
        print(f"Items: {items}")
        return items

    @classmethod
    async def delete(cls, session: AsyncSession, id):
        query = sqlalchemy_delete(cls).where(cls.id == id)
        await session.execute(query)
        try:
            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            print(f"Error while deleting: {e}")
            raise Exception("Database error")
