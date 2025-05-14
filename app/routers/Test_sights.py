# app/routers/sights.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_db, get_redis
from app.models.sight import Sight
from app.schemas.sight import SightResponse
from app.schemas.response import ResponseModel
from app.services.sight import (
    get_sight_by_id_async,
    get_sight_async,
    count_sights_async,
    get_hot_sights_async,
    get_fine_sights_async,
    search_sights_async,
    count_search_sights_async,
)
from typing import List
import math
import json

router = APIRouter(
    prefix="/api/sight",
    tags=["sights"],
    responses={404: {"description": "Not found"}},
)

@router.get("/detail/{sight_id}/", response_model=ResponseModel[SightResponse])
async def get_sight_detail(
    sight_id: int,
    db: AsyncSession = Depends(get_async_db),
    redis=Depends(get_redis),
):
    """获取景点详情"""
    cache_key = f"sight:detail:{sight_id}"
    cached = await redis.get(cache_key)
    if cached:
        return ResponseModel(code=200, data=json.loads(cached))

    try:
        sight = await get_sight_by_id_async(db, sight_id=sight_id)
        if not sight:
            raise HTTPException(status_code=404, detail="Sight not found")

        sight_data = SightResponse.model_validate(sight)

        # 写入缓存
        await redis.set(
            cache_key,
            json.dumps(sight_data.model_dump(), default=str),
            ex=3600,
        )

        return ResponseModel(code=200, data=sight_data)
    except Exception as e:
        print(f"Error in get_sight_detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list/", response_model=ResponseModel[List[SightResponse]])
async def get_sight_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_async_db),
):
    """获取景点列表（分页）"""
    try:
        skip = (page - 1) * page_size
        sights_orm = await get_sight_async(db, skip=skip, limit=page_size)
        total = await count_sights_async(db)
        total_pages = math.ceil(total / page_size)

        # 使用 Pydantic 模型转换 ORM 列表
        sights = [SightResponse.model_validate(sight) for sight in sights_orm]

        pagination = {
            "total": total,
            "page_size": page_size,
            "current_page": page,
            "total_pages": total_pages,
        }

        return ResponseModel(code=200, data=sights, pagination=pagination)
    except Exception as e:
        print(f"Error in get_sight_list: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hot/list/", response_model=ResponseModel[List[SightResponse]])
async def get_hot_sight_list(db: AsyncSession = Depends(get_async_db)):
    """获取热门景点列表"""
    try:
        sights_orm = await get_hot_sights_async(db)
        sights = [SightResponse.model_validate(sight) for sight in sights_orm]
        return ResponseModel(code=200, data=sights)
    except Exception as e:
        print(f"Error in get_hot_sight_list: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fine/list/", response_model=ResponseModel[List[SightResponse]])
async def get_fine_sight_list(db: AsyncSession = Depends(get_async_db)):
    """获取精选景点列表"""
    try:
        sights_orm = await get_fine_sights_async(db)
        sights = [SightResponse.model_validate(sight) for sight in sights_orm]
        return ResponseModel(code=200, data=sights)
    except Exception as e:
        print(f"Error in get_fine_sight_list: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/", response_model=ResponseModel[List[SightResponse]])
async def search_sights(
    keyword: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(4, ge=1, le=100),
    db: AsyncSession = Depends(get_async_db),
):
    """搜索景点（分页）"""
    try:
        skip = (page - 1) * page_size
        sights_orm = await search_sights_async(db, keyword=keyword, skip=skip, limit=page_size)
        total = await count_search_sights_async(db, keyword=keyword)
        total_pages = math.ceil(total / page_size)

        sights = [SightResponse.model_validate(sight) for sight in sights_orm]

        pagination = {
            "total": total,
            "page_size": page_size,
            "current_page": page,
            "total_pages": total_pages,
        }

        return ResponseModel(code=200, data=sights, pagination=pagination)
    except Exception as e:
        print(f"Error in search_sights: {e}")
        raise HTTPException(status_code=500, detail=str(e))