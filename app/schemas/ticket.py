from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class TicketBase(BaseModel):
    name: str
    desc: Optional[str] = None
    type: Optional[str] = None
    price: float
    discount: float = 1.0
    total: int = 0
    remain: int = 0
    expire_date: Optional[date] = None
    return_policy: Optional[str] = None
    is_valid: bool = True
    sight_id: int

class TicketResponse(TicketBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes= True
