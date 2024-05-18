from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, UUID4


class PackageStatus(str, Enum):
    PENDING = "PENDING"
    ASSIGNED = "ASSIGNED"
    PICK_UP_REQUEST = "PICK_UP_REQUEST"
    IN_TRANSIT = "IN_TRANSIT"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    DAMAGED = "DAMAGED"


class TransactionAddress(BaseModel):
    city: str
    street: str
    zip: int
    country: str
    latitude: float
    longitude: float


class PackageType(str, Enum):
    FOOD = "FOOD"
    MEDICATION = "MEDICATION"
    ELECTRONICS = "ELECTRONICS"
    FURNITURE = "FURNITURE"
    FASHION = "FASHION"
    BEAUTY = "BEAUTY"
    OTHER = "OTHER"


class PackageDeliveryMode(str, Enum):
    NORMAL = "NORMAL"
    EXPRESS = "EXPRESS"
    PRO = "PRO"


class PackageModel(BaseModel):
    id: str
    packageName: str
    packageDescription: str
    pickupAddress: TransactionAddress
    deliveryAddress: TransactionAddress
    packageStatus: PackageStatus
    packageType: PackageType
    deliveryMode: PackageDeliveryMode
    senderId: str
    deliveryAgentId: Optional[str] = None
    createdAt: int
    updatedAt: Optional[int] =None
