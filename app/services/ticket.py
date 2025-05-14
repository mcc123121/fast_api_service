from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.ticket import Ticket
from typing import List, Optional

async def get_ticket_async(db: AsyncSession, ticket_id: int) -> Optional[Ticket]:
    """
    根据ID获取门票信息
    """
    query = select(Ticket).where(Ticket.id == ticket_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_tickets_async(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Ticket]:
    """
    获取门票列表
    """
    query = select(Ticket).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_tickets_by_sight_async(db: AsyncSession, sight_id: int) -> List[Ticket]:
    """
    根据景点ID获取门票列表
    """
    query = select(Ticket).where(Ticket.sight_id == sight_id)
    result = await db.execute(query)
    return result.scalars().all()
