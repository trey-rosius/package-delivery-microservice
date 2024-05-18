from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, UUID4


class UserType(str, Enum):
    CUSTOMER = "CUSTOMER"
    ADMIN = "ADMIN"
    DELIVERY_AGENT = "DELIVERY_AGENT"


'''


'''


class Address(BaseModel):
    street: str
    city: str
    zip: int
    country: str


class Geolocation(BaseModel):
    latitude: float
    longitude: float


class UserModel(BaseModel):
    id: str
    email: EmailStr
    username: str
    first_name: str
    last_name: str
    address: Optional[Address]
    profile_pic_url: Optional[str]
    geolocation: Geolocation
    is_active: bool
    is_admin: bool
    phone_number: str
    user_type: UserType
    created_at: int
    updated_at: Optional[int]
