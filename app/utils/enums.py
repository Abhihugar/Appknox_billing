from enum import Enum


class PlanEnum(Enum):
    BASIC = "Basic"
    PRO = "Pro"
    ENTERPRISE = "Enterprise"


class SubscriptionStatus(Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class InvoiceStatus(Enum):
    unpaid = "unpaid"
    paid = "paid"
    overdue = "overdue"
    
    
class PaymentStatus(Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"