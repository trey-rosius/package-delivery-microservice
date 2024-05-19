from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class Address(BaseModel):
    city: str
    street: str
    zip: int
    country: str
    latitude: float
    longitude: float


class Geolocation(BaseModel):
    latitude: float
    longitude: float


class DeliveryStatus(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    DELIVERED = "DELIVERED"
    DELAYED = "DELAYED"


class DeliveryStatusModel(BaseModel):
    id:str
    packageId: str
    deliveryAgentId: str
    senderId: str
    destinationAddress: Address
    status: DeliveryStatus
    currentPackageGeolocation: Geolocation
    createdAt: int
    updatedAt: Optional[int] = None
