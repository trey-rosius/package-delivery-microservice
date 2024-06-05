from enum import Enum
from typing import Optional

from pydantic import BaseModel


class Status(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    FAILED = "FAILED"
    SUCCESS = "SUCCESS"
    CANCELLED = "CANCELLED"


class PaymentModel(BaseModel):
    id: Optional[str] = None
    amount: int
    user_id: str
    package_id: str
    status: Optional[Status] = None
    payment_intent_id: Optional[str] = None
    instance_id: Optional[str] = None
