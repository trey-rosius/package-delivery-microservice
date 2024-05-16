from datetime import datetime
from enum import Enum

from pydantic import BaseModel, UUID4


class PackageStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    PICK_UP_REQUEST = "pick-up-request"
    IN_TRANSIT = "in-transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    DAMAGED = "damaged"

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
    deliveryAgentId: str
    createdAt: datetime
    updatedAt: datetime
