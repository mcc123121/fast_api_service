# app/schemas/sight.py

from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class SightProfileBase(BaseModel):
    img: str
    address: str
    explain: Optional[str] = None
    open_time: str
    tel: str
    level: Optional[str] = None
    tags: Optional[str] = None
    attention: Optional[str] = None
    location: Optional[str] = None

class SightProfileResponse(SightProfileBase):
    id: int
    sight_id: int

    model_config = {
        "from_attributes": True,
    }

class TicketBase(BaseModel):
    id: int
    name: str
    desc: Optional[str] = None
    type: Optional[str] = None
    price: float
    discount: float
    total: int
    remain: int
    expire_date: Optional[str] = None  
    return_policy: Optional[str] = None
    is_valid: bool
    created_at: datetime
    updated_at: datetime

class TicketResponse(TicketBase):
    model_config = {
        "from_attributes": True,
    }

class SightBase(BaseModel):
    name: str
    desc: str
    main_img: str
    banner_img: str
    content: str
    score: float = 5.0
    min_price: float = 0
    province: str
    city: str
    area: Optional[str] = None
    town: Optional[str] = None
    is_top: bool = False
    is_hot: bool = False
    is_valid: bool = True

class SightCreate(SightBase):
    profile:SightProfileBase

class SightResponse(SightBase):
    id: int
    created_at: datetime
    updated_at: datetime
    profile: Optional[SightProfileResponse] = None
    tickets: List[TicketResponse]  

    model_config = {
        "from_attributes": True,
    }

class SightListResponse(BaseModel):
    data: List[SightResponse]
    pagination: Optional[Dict[str, Any]] = None

class SightUpdate(BaseModel):
    name: Optional[str] = None
    desc: Optional[str] = None
    main_img: Optional[str] = None
    banner_img: Optional[str] = None
    content: Optional[str] = None
    score: Optional[float] = None
    min_price: Optional[float] = None
    province: Optional[str] = None
    city: Optional[str] = None
    area: Optional[str] = None
    town: Optional[str] = None
    is_top: Optional[bool] = None
    is_hot: Optional[bool] = None
    is_valid: Optional[bool] = None

    
class SightProfileUpdate(BaseModel):
    img: Optional[str] = None
    address: Optional[str] = None
    explain: Optional[str] = None
    open_time: Optional[str] = None
    tel: Optional[str] = None
    level: Optional[str] = None
    tags: Optional[str] = None
    attention: Optional[str] = None
    location: Optional[str] = None