from typing import Optional

from pydantic import BaseModel


class PaymentModel(BaseModel):
    id: Optional[str]=None
    amount: float
    user_id: str
    package_id: str
    payment_intent_id:Optional[str]=None
    instance_id:Optional[str]=None
