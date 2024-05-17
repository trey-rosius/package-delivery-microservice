from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, UUID4


class PackageStatus(str, Enum):
    PENDING = "PENDING"
    ASSIGNED = "ASSIGNED"
    PICK_UP_REQUEST = "PICK-UP-REQUEST"
    IN_TRANSIT = "IN-TRANSIT"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    DAMAGED = "DAMAGED"

class Location(BaseModel):
    lat: float
    long: float
class TransactionAddress(BaseModel):
    city: str
    street: str
    zip: str
    country: str
    coordinates:Location





class PackageModel(BaseModel):
    id: UUID4
    packageName: str
    packageDescription: str
    pickupAddress: TransactionAddress
    deliveryAddress: TransactionAddress
    packageStatus: PackageStatus
    senderId: str
    deliveryAgentId: Optional[str]
    createdAt: datetime
    updatedAt: Optional[datetime]
