# app/routes/sights.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_db, get_redis
from app.sight.models import Sight
from app.sight.schemas import SightResponse, SightListResponse
from app.sight.response import ResponseModel
from app.sight.services import (
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
from datetime import datetime
from app.utils.logger import get_logger, log_execution_time
from app.sight.schemas import SightCreate, SightUpdate
from app.sight.services import create_sight_async, update_sight_async, delete_sight_async
from app.dependencies import get_current_user, get_sight_admin, TokenData

# 自定义JSON编码器，处理datetime对象
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

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
            # 尝试解析缓存的JSON数据
            cached_data = json.loads(cached)
            logger.info(f"Successfully retrieved data from Redis cache: {cache_key}")
            return ResponseModel(code=200, data=cached_data)
        except Exception as e:
            # 使用logger而不是print，记录更详细的错误信息
            logger.error(f"Error parsing cached data for key {cache_key}: {str(e)}")
            # 删除可能损坏的缓存
            await redis.delete(cache_key)
            logger.info(f"Deleted potentially corrupted cache for key: {cache_key}")
            return None
    logger.info(f"No cache found for key: {cache_key}")
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
                # 将Pydantic模型转换为字典，然后序列化为JSON字符串，使用自定义编码器处理datetime
                json_str = json.dumps(
                    sight_data.model_dump(),
                    cls=DateTimeEncoder
                )
                await redis.set(
                    cache_key,
                    json_str,
                    ex=3600,
                )
                logger.info(f"Successfully cached sight detail for ID {sight_id}")
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
    page_size:int = Query(6,ge=1,le=100),
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
                # 将Pydantic模型转换为字典，然后序列化为JSON字符串，使用自定义编码器处理datetime
                response_data = {
                    "data": [sight.model_dump() for sight in sights_data],
                    "pagination": pagination
                }
                json_str = json.dumps(
                    response_data,
                    cls=DateTimeEncoder
                )
                await redis.set(
                    cache_key,
                    json_str,
                    ex=3600,
                )
                logger.info(f"Successfully cached sight list data, page: {page}, count: {len(sights_data)}")
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
                # 将Pydantic模型转换为JSON字符串，使用自定义编码器处理datetime
                json_str = json.dumps(
                    [sight.model_dump() for sight in hot_sights_data],
                    cls=DateTimeEncoder
                )
                await redis.set(
                    cache_key,
                    json_str,
                    ex=3600,
                )
                logger.info(f"Successfully cached hot sights data, count: {len(hot_sights_data)}")
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
                # 将Pydantic模型转换为JSON字符串，使用自定义编码器处理datetime
                json_str = json.dumps(
                    [sight.model_dump() for sight in fine_sights_data],
                    cls=DateTimeEncoder
                )
                await redis.set(
                    cache_key,
                    json_str,
                    ex=3600,
                )
                logger.info(f"Successfully cached fine sights data, count: {len(fine_sights_data)}")
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

        pagination = {
            "total": total,
            "page_size": page_size,
            "current_page": page,
            "total_pages": total_pages,
        }

        # 只有在成功处理所有数据后才缓存
        if sights_data:
            try:
                # 将Pydantic模型转换为JSON字符串，使用自定义编码器处理datetime
                response_data = {
                    "data": [sight.model_dump() for sight in sights_data],
                    "pagination": pagination
                }
                json_str = json.dumps(
                    response_data,
                    cls=DateTimeEncoder
                )
                await redis.set(
                    cache_key,
                    json_str,
                    ex=3600,
                )
                logger.info(f"Successfully cached search data for keyword '{keyword}', count: {len(sights_data)}")
            except Exception as e:
                logger.error(f"Error caching search data: {str(e)}")

        response_data = {
            "data": sights_data,
            "pagination": pagination,
        }
        return ResponseModel(code=200,data=response_data)

    except Exception as e:
        logger.error(f"Unexpected error in search_sights: {str(e)}")
        raise HTTPException(status_code=500,detail=str(e))


@router.post("/create/", response_model=ResponseModel)
async def create_sight(
    sight_data: SightCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: TokenData = Depends(get_sight_admin)
):

    try:
        new_sight = await create_sight_async(db, sight_data)
        sight_response = SightResponse.model_validate(new_sight)

        # 清除相关缓存
        redis = await get_redis()
        await redis.delete("sight:list:*")

        return ResponseModel(code=200, message="景点创建成功", data=sight_response)
    except Exception as e:
        logger.error(f"Error creating sight: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建景点失败: {str(e)}")



@router.put("/update/{sight_id}/", response_model=ResponseModel)
async def update_sight(
    sight_id: int,
    sight_data: SightUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: TokenData = Depends(get_sight_admin)
):

    try:
        updated_sight = await update_sight_async(db, sight_id, sight_data)
        if not updated_sight:
            raise HTTPException(status_code=404, detail="景点不存在")

        sight_response = SightResponse.model_validate(updated_sight)

        # 清除相关缓存
        redis = await get_redis()
        await redis.delete(f"sight:detail:{sight_id}")
        await redis.delete("sight:list:*")
        await redis.delete("sight:hot:list")
        await redis.delete("sight:fine:list")

        return ResponseModel(code=200, message="景点更新成功", data=sight_response)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating sight {sight_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新景点失败: {str(e)}")

# 添加删除景点的API端点
@router.delete("/delete/{sight_id}/", response_model=ResponseModel)
async def delete_sight(
    sight_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: TokenData = Depends(get_sight_admin)
):
    """删除景点（需要景点管理员权限）"""
    try:
        success = await delete_sight_async(db, sight_id)
        if not success:
            raise HTTPException(status_code=404, detail="景点不存在")

        # 清除相关缓存
        redis = await get_redis()
        await redis.delete(f"sight:detail:{sight_id}")
        await redis.delete("sight:list:*")
        await redis.delete("sight:hot:list")
        await redis.delete("sight:fine:list")

        return ResponseModel(code=200, message="景点删除成功")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting sight {sight_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除景点失败: {str(e)}")

# 添加清除缓存的API端点
@router.post("/clear-cache/", response_model=ResponseModel)
async def clear_cache(
    redis=Depends(get_redis),
):
    """清除所有景点相关的缓存"""
    try:
        # 清除所有景点相关的缓存
        await redis.delete("sight:hot:list")
        await redis.delete("sight:fine:list")

        # 清除列表缓存
        keys = await redis.keys("sight:list:*")
        if keys:
            await redis.delete(*keys)

        # 清除详情缓存
        detail_keys = await redis.keys("sight:detail:*")
        if detail_keys:
            await redis.delete(*detail_keys)

        # 清除搜索缓存
        search_keys = await redis.keys("sight:search:*")
        if search_keys:
            await redis.delete(*search_keys)

        logger.info("Successfully cleared all sight caches")
        return ResponseModel(code=200, message="所有景点缓存已清除")
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        raise HTTPException(status_code=500, detail=f"清除缓存失败: {str(e)}")