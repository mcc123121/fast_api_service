from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, func
from sqlalchemy.orm import selectinload
from app.sight.models import Sight,SightProfile
from typing import List, Optional
from app.sight.schemas import SightCreate, SightUpdate

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

#实现创建新景点的异步函数
async def create_sight_async(db: AsyncSession, sight_data: SightCreate) -> Sight:
    """
    创建新景点及其详情
    """
    # 创建新景点对象
    new_sight = Sight(
        name=sight_data.name,
        desc=sight_data.desc,
        main_img=sight_data.main_img,
        banner_img=sight_data.banner_img,
        content=sight_data.content,
        score=sight_data.score,
        min_price=sight_data.min_price,
        province=sight_data.province,
        city=sight_data.city,
        area=sight_data.area,
        town=sight_data.town,
        is_top=sight_data.is_top,
        is_hot=sight_data.is_hot,
        is_valid=sight_data.is_valid
    )

    # 添加到数据库并刷新以获取ID
    db.add(new_sight)
    await db.flush()

    #创建景点详情对象
    profile_data = sight_data.profile
    new_profile = SightProfile(
        img=profile_data.img,
        address=profile_data.address,
        explain=profile_data.explain,
        open_time=profile_data.open_time,
        tel=profile_data.tel,
        level=profile_data.level,
        tags=profile_data.tags,
        attention=profile_data.attention,
        location=profile_data.location,
        sight_id=new_sight.id  
    )
    db.add(new_profile)
    await db.commit()
    await db.refresh(new_sight)
    
    # 手动加载关系
    query = (
        select(Sight)
        .options(
            selectinload(Sight.profile),
            selectinload(Sight.tickets)
        )
        .where(Sight.id == new_sight.id)
    )
    result = await db.execute(query)
    created_sight = result.scalars().first()

    if not created_sight:
        created_sight = new_sight  # 如果找不到，就返回原始对象

    return created_sight

#实现更新景点信息的异步函数
async def update_sight_async(db: AsyncSession, sight_id: int, sight_data: SightUpdate) -> Optional[Sight]:
    """
    更新景点信息及其详情
    """
    # 获取要更新的景点
    sight = await get_sight_by_id_async(db, sight_id)
    if not sight:
        return None
    
    # 更新景点属性
    update_data = sight_data.model_dump(exclude={"profile"}, exclude_unset=True)
    for key, value in update_data.items():
        setattr(sight, key, value)
    
    # 如果提供了景点详情更新数据
    if sight_data.profile:
        # 确保景点详情存在
        if sight.profile:
            # 更新现有景点详情
            profile_update_data = sight_data.profile.model_dump(exclude_unset=True)
            for key, value in profile_update_data.items():
                setattr(sight.profile, key, value)
        else:

            profile_data = sight_data.profile.model_dump(exclude_unset=True)
            new_profile = SightProfile(sight_id=sight_id, **profile_data)
            db.add(new_profile)
    
    # 提交更改
    await db.commit()
    await db.refresh(sight)
    
    # 获取完整的景点对象，包括关系
    updated_sight = await get_sight_by_id_async(db, sight_id)
    
    return updated_sight

#通过景点id删除景点和景点详情
async def delete_sight_async(db: AsyncSession, sight_id: int) -> None:
    """
    删除景点及其详情
    """
    # 获取要删除的景点
    sight = await get_sight_by_id_async(db, sight_id)
    if not sight:
        return False
    try:
        #先删除关联的景点详情
        if sight.profile:
            await db.delete(sight.profile)
            await db.flush()

        await db.delete(sight)
        await db.commit()
        return True
    except Exception as e:
        await db.rollback()
        raise e

