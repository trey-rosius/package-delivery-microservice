
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, UUID4


class UserType(str,Enum):
    CUSTOMER="customer"
    ADMIN ="admin"
    DELIVERY_AGENT = "delivery_agent"

'''


'''
class Address(BaseModel):
    street: str
    city: str
    zip: int
    country: str


class Geolocation(BaseModel):
    lat: float
    long: float


class UserModel(BaseModel):
    id: UUID4
    email: EmailStr
    username: str
    first_name: str
    last_name: str
    address: Address
    profilePicUrl: str
    geolocation: Geolocation
    is_active: bool
    is_admin: bool
    user_type: UserType
    created_at: str
    updated_at: Optional[str]
