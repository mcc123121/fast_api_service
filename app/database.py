from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from typing import AsyncGenerator
import aioredis

# 同步数据库URL - 使用Django的数据库
DATABASE_URL = "mysql+pymysql://root:mc253831@127.0.0.1:3306/fast_api_trip"

# 异步数据库URL (注意使用aiomysql) - 使用Django的数据库
ASYNC_DATABASE_URL = "mysql+aiomysql://root:mc253831@127.0.0.1:3306/fast_api_trip"

# 同步引擎和会话
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 异步引擎和会话
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    pool_size=10,  
    max_overflow=20,  
    pool_timeout=30,  
    pool_recycle=1800,  
    pool_pre_ping=True,  
    echo=False,  
)


AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# 同步数据库依赖
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 异步数据库依赖
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# 异步数据库连接池
async def create_async_db_pool():

    return AsyncSessionLocal

#关闭数据库连接池
async def close_async_db_pool():
    '''关闭数据库连接池'''
    await async_engine.dispose()

async def get_redis():
    '''获取Redis连接'''
    redis_client = await aioredis.from_url("redis://localhost:6379/0",password="mcc20040225", encoding="utf-8", decode_responses=True)
    return redis_client
    