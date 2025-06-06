from sqlalchemy import Column, String, Integer, Boolean, select
from app.models.base import Base, CRUDMixin, TimestampMixin
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship


class User(Base, CRUDMixin, TimestampMixin):
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan", lazy="immediate")
    invoices = relationship("Invoice", back_populates="user", cascade="all, delete-orphan")


    def __repr__(self):
        return f"<User(username={self.username}, email={self.email}, is_active={self.is_active})>"

    @classmethod
    async def get_by_username(cls, session: AsyncSession, username: str):
        q = select(cls).where(cls.username == username)
        f = await session.execute(q)
        return f.scalars().first()

    @classmethod
    async def get_by_email(cls, session: AsyncSession, email: str):
        q = select(cls).where(cls.email == email)
        f = await session.execute(q)
        return f.scalars().first()
