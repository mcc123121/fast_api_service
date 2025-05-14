# app/routes/sights.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_db, get_redis
from app.models.sight import Sight
from app.schemas.sight import SightResponse, SightListResponse
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
from app.utils.logger import get_logger, log_execution_time

logger = get_logger("app.routers.sights")

router = APIRouter(
    prefix="/api/sight",
    tags=["sights"],
    responses={404: {"description": "Not found"}},
)

async def get_Info_from_redis(redis, cache_key):
    """从Redis获取信息"""
    cached = await redis.get(cache_key)
    if cached:
        try:
            cached_data = json.loads(cached)
            return ResponseModel(code=200, data=cached_data)
        except Exception as e:
            print(f"Error parsing cached data: {str(e)}")
            return None
    return None

@router.get("/detail/{sight_id}/",response_model=ResponseModel)
@log_execution_time()
async def get_sight_detail(
    sight_id : int,
    db:AsyncSession = Depends(get_async_db),
    redis=Depends(get_redis),
):
    """获取景点详情信息"""
    cache_key = f"sight:detail:{sight_id}"
    cached_response = await get_Info_from_redis(redis, cache_key)
    if cached_response:
        return cached_response

    try:
        sight = await get_sight_by_id_async(db,sight_id=sight_id)
        if not sight:
            raise HTTPException(status_code=404,detail="Sight not found")

        try:
            sight_data = SightResponse.model_validate(sight)

            # 只有在成功处理数据后才缓存
            try:
                # 直接将Pydantic模型序列化为JSON字符串
                json_data = sight_data.model_dump_json()
                await redis.set(
                    cache_key,
                    json_data,
                    ex=3600,
                )
            except Exception as e:
                logger.error(f"Error caching sight detail {sight_id}: {str(e)}")

            return ResponseModel(code=200,data=sight_data)
        except Exception as e:
            logger.error(f"Error processing sight detail {sight_id}: {str(e)}")
            raise HTTPException(status_code=500,detail=f"Error processing sight data: {str(e)}")

    except Exception as e:
        logger.error(f"Unexpected error in get_sight_detail: {str(e)}")
        raise HTTPException(status_code=500,detail=str(e))


@router.get("/list/",response_model=ResponseModel)
async def get_sight_list(
    page:int = Query(1,ge=1),
    page_size:int = Query(10,ge=1,le=100),
    db:AsyncSession = Depends(get_async_db),
    redis=Depends(get_redis),
):
    cache_key = f"sight:list:{page}:{page_size}"
    cached_response = await get_Info_from_redis(redis, cache_key)
    if cached_response:
        return cached_response

    try:
        skip = (page - 1) * page_size
        sights = await get_sight_async(db,skip=skip,limit=page_size)
        total = await count_sights_async(db)
        total_pages = math.ceil(total / page_size)

        # 更详细的错误处理
        sights_data = []
        for sight in sights:
            try:
                sight_data = SightResponse.model_validate(sight)
                sights_data.append(sight_data)
            except Exception as e:
                # 记录具体的验证错误，但继续处理其他景点
                logger.error(f"Error validating sight {sight.id}: {str(e)}")
                continue

        pagination = {
            "total": total,
            "page_size": page_size,
            "current_page": page,
            "total_pages": total_pages,
        }
        response_data = {
            "data": sights_data,
            "pagination": pagination,
        }

        # 只有在成功处理所有数据后才缓存
        if sights_data:
            try:
                # 将Pydantic模型转换为字典
                json_data = {
                    "data": [sight.model_dump_json() for sight in sights_data],
                    "pagination": pagination
                }
                await redis.set(
                    cache_key,
                    json_data,
                    ex=3600,
                )
            except Exception as e:
                logger.error(f"Error caching data: {str(e)}")

        return ResponseModel(code=200,data=response_data)
    except Exception as e:
        logger.error(f"Unexpected error in get_sight_list: {str(e)}")
        raise HTTPException(status_code=500,detail=str(e))

@router.get("/hot/list/",response_model=ResponseModel)
async def get_hot_sight_list(
    db:AsyncSession = Depends(get_async_db),
    redis=Depends(get_redis),
):
    cache_key = "sight:hot:list"
    cached_response = await get_Info_from_redis(redis, cache_key)
    if cached_response:
        return cached_response

    try:
        hot_sights = await get_hot_sights_async(db)

        # 更详细的错误处理
        hot_sights_data = []
        for sight in hot_sights:
            try:
                sight_data = SightResponse.model_validate(sight)
                hot_sights_data.append(sight_data)
            except Exception as e:
                # 记录具体的验证错误，但继续处理其他景点
                logger.error(f"Error validating hot sight {sight.id}: {str(e)}")
                continue

        # 只有在成功处理所有数据后才缓存
        if hot_sights_data:
            try:
                # 将Pydantic模型转换为字典
                json_data = [sight.model_dump_json() for sight in hot_sights_data]
                await redis.set(
                    cache_key,
                    json_data,
                    ex=3600,
                )
            except Exception as e:
                logger.error(f"Error caching hot sights data: {str(e)}")

        return ResponseModel(code=200,data=hot_sights_data)
    except Exception as e:
        logger.error(f"Unexpected error in get_hot_sight_list: {str(e)}")
        raise HTTPException(status_code=500,detail=str(e))


@router.get("/fine/list/",response_model=ResponseModel)
async def get_fine_sight_list(
    db:AsyncSession = Depends(get_async_db),
    redis=Depends(get_redis)
):
    cache_key = "sight:fine:list"
    cached_response = await get_Info_from_redis(redis, cache_key)
    if cached_response:
        return cached_response

    try:
        fine_sights = await get_fine_sights_async(db)

        # 更详细的错误处理
        fine_sights_data = []
        for sight in fine_sights:
            try:
                sight_data = SightResponse.model_validate(sight)
                fine_sights_data.append(sight_data)
            except Exception as e:
                logger.error(f"Error validating fine sight {sight.id}: {str(e)}")
                continue
        if fine_sights_data:
            try:
                # 将Pydantic模型转换为字典
                json_data = [sight.model_dump_json() for sight in fine_sights_data]
                await redis.set(
                    cache_key,
                    json_data,
                    ex=3600,
                )
            except Exception as e:
                logger.error(f"Error caching fine sights data: {str(e)}")

        return ResponseModel(code=200,data=fine_sights_data)
    except Exception as e:
        logger.error(f"Unexpected error in get_fine_sight_list: {str(e)}")
        raise HTTPException(status_code=500,detail=str(e))

@router.get("/search/",response_model=ResponseModel)
async def search_sights(
    keyword:str = Query(...,min_length=1),
    page:int = Query(1,ge=1),
    page_size:int = Query(4,ge=1,le=100),
    db:AsyncSession = Depends(get_async_db),
    redis=Depends(get_redis),
):
    """搜索景点"""
    cache_key = f"sight:search:{keyword}:{page}:{page_size}"
    cached_response = await get_Info_from_redis(redis, cache_key)
    if cached_response:
        return cached_response

    try:
        skip = (page - 1) * page_size
        sights = await search_sights_async(db,keyword=keyword,skip=skip,limit=page_size)
        total = await count_search_sights_async(db,keyword=keyword)
        total_pages = math.ceil(total / page_size)

        # 更详细的错误处理
        sights_data = []
        for sight in sights:
            try:
                sight_data = SightResponse.model_validate(sight)
                sights_data.append(sight_data)
            except Exception as e:
                # 记录具体的验证错误，但继续处理其他景点
                logger.error(f"Error validating search sight {sight.id}: {str(e)}")
                continue

        # 只有在成功处理所有数据后才缓存
        if sights_data:
            try:
                # 将Pydantic模型转换为字典
                json_data = {
                    "data": [sight.model_dump_json() for sight in sights_data],
                    "pagination": pagination
                }
                await redis.set(
                    cache_key,
                    json_data,
                    ex=3600,
                )
            except Exception as e:
                logger.error(f"Error caching search data: {str(e)}")

        pagination = {
            "total": total,
            "page_size": page_size,
            "current_page": page,
            "total_pages": total_pages,
        }
        response_data = {
            "data": sights_data,
            "pagination": pagination,
        }
        return ResponseModel(code=200,data=response_data)

    except Exception as e:
        logger.error(f"Unexpected error in search_sights: {str(e)}")
        raise HTTPException(status_code=500,detail=str(e))