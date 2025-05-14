from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, func
from sqlalchemy.orm import selectinload
from app.sight.models import Sight
from typing import List, Optional


async def get_sight_by_id_async(db: AsyncSession, sight_id: int) -> Optional[Sight]:
    """
    根据ID获取景点信息
    """
    query = (
        select(Sight)
        .options(
            selectinload(Sight.profile),
            selectinload(Sight.tickets)
        )
        .where(Sight.id == sight_id)
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_sight_async(db:AsyncSession,skip:int = 0,limit: int = 100) -> List[Sight]:
    """
    获取景点列表
    """
    query = select(Sight).options(selectinload(Sight.profile),
                                  selectinload(Sight.tickets)
    ).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_hot_sights_async(db:AsyncSession,skip:int = 0,limit: int = 10) -> List[Sight]:
    """
    获取热门景点列表
    """
    query = select(Sight).options(selectinload(Sight.profile),
                                  selectinload(Sight.tickets)
                                  ).where(Sight.is_hot == True).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_fine_sights_async(db:AsyncSession,skip:int = 0,limit: int = 3) -> List[Sight]:
    """
    获取精选景点列表
    """
    query = select(Sight).options(selectinload(Sight.profile),
                                  selectinload(Sight.tickets)
                                  ).where(Sight.is_top == True).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def search_sights_async(db:AsyncSession,keyword: str,skip:int = 0,limit: int = 100) -> List[Sight]:
    """
    搜索景点
    """
    query = select(Sight).options(selectinload(Sight.profile),
                                  selectinload(Sight.tickets)
                                  ).where(
        or_(
            Sight.name.contains(keyword),
            Sight.province.contains(keyword),
            Sight.city.contains(keyword),
            Sight.area.contains(keyword)
        )
    ).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def count_sights_async(db:AsyncSession) -> int:
    """
    获取景点总数
    """
    query = select(func.count()).select_from(Sight)
    result = await db.execute(query)
    return result.scalar_one()

async def count_search_sights_async(db:AsyncSession,keyword: str) -> int:
    """
    获取搜索景点总数
    """
    query = select(func.count()).select_from(Sight).where(
        or_(
            Sight.name.contains(keyword),
            Sight.province.contains(keyword),
            Sight.city.contains(keyword),
            Sight.area.contains(keyword)
        )
    )
    result = await db.execute(query)
    return result.scalar_one()