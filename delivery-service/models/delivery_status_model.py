from datetime import datetime

from pydantic import BaseModel


class Address(BaseModel):
    city: str
    street: str
    zip: str
    country: str


class Geolocation(BaseModel):
    lat: float
    long: float


class DeliveryStatusModel(BaseModel):
    packageId: str
    deliveryAgentId: str
    senderId: str
    destinationAddress: Address
    status: str
    currentPackageGeolocation: Geolocation
    createdAt: datetime
