from sqlalchemy import (
    Column,
    String,
    Integer,
    ForeignKey,
    select,
    DateTime,
    Numeric,
    Date,
)
from datetime import datetime, timezone
from app.models.base import Base, CRUDMixin, TimestampMixin
from sqlalchemy.orm import relationship


class Subscription(Base, CRUDMixin):
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("plan.id"), nullable=False)

    start_date = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    end_date = Column(DateTime, nullable=True)
    status = Column(String, default="active", nullable=False)

    user = relationship("User", back_populates="subscriptions")
    plan = relationship("Plan", back_populates="subscriptions")
    invoices = relationship(
        "Invoice", back_populates="subscription", cascade="all, delete"
    )


class Plan(Base, CRUDMixin, TimestampMixin):
    name = Column(String, unique=True, nullable=False)
    price = Column(Integer, nullable=False)

    subscriptions = relationship(
        "Subscription", back_populates="plan", cascade="all, delete-orphan"
    )

    @classmethod
    async def get_by_name(cls, session, name: str):
        query = select(cls).where(cls.name == name)
        result = await session.execute(query)
        return result.scalars().first()


class Invoice(Base, CRUDMixin):
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("subscription.id"))
    amount = Column(Numeric)
    issue_date = Column(Date)
    due_date = Column(Date)
    status = Column(String, default="unpaid")

    user = relationship("User", back_populates="invoices")
    subscription = relationship("Subscription", back_populates="invoices")
