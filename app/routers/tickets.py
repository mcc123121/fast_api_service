from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_db
from app.models.ticket import Ticket
from app.schemas.ticket import TicketResponse
from app.schemas.response import ResponseModel
from app.services.ticket import get_ticket_async, get_tickets_async, get_tickets_by_sight_async
from typing import List

router = APIRouter(
    prefix="/api/sight",
    tags=["tickets"],
    responses={404: {"description": "Not found"}},
)

@router.get("/ticket/{ticket_id}/", response_model=ResponseModel[TicketResponse])
async def get_ticket_detail(ticket_id: int, db: AsyncSession = Depends(get_async_db)):
    """获取门票详情"""
    ticket = await get_ticket_async(db, ticket_id=ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ResponseModel(code=200, data=ticket)

@router.get("/", response_model=List[TicketResponse])
async def get_tickets(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_async_db)):
    """获取门票列表"""
    tickets = await get_tickets_async(db, skip=skip, limit=limit)
    return tickets

@router.get("/sight/{sight_id}", response_model=List[TicketResponse])
async def get_tickets_by_sight(sight_id: int, db: AsyncSession = Depends(get_async_db)):
    """根据景点ID获取门票列表"""
    tickets = await get_tickets_by_sight_async(db, sight_id=sight_id)
    return tickets
