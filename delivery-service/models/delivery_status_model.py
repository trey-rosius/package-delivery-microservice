from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class Address(BaseModel):
    city: str
    street: str
    zip: str
    country: str


class Geolocation(BaseModel):
    lat: float
    long: float

class DeliveryStatus(str,Enum):
    IN_PROGRESS = "IN_PROGRESS"
    DELIVERED = "DELIVERED"
    DELAYED = "DELAYED"





class DeliveryStatusModel(BaseModel):
    packageId: str
    deliveryAgentId: str
    senderId: str
    destinationAddress: Address
    status: DeliveryStatus
    currentPackageGeolocation: Geolocation
    createdAt: datetime
