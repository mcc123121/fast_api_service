# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from app.sight.router import router as sight_router
from app.tickets.router import router as tickets_router
# from app.auth import router as auth_router
from app.database import  get_redis,create_async_db_pool,close_async_db_pool
from app.utils.logger import setup_logger


async def lifespan(app: FastAPI):
    # Startup event
    logger.info("redis and db startup...")  # 记录启动日志
    app.state.redis = await get_redis()
    app.state.db_pool = await create_async_db_pool()  # 创建连接池

    yield  # 应用运行期间

    # Shutdown event
    logger.info("redis and db shutdown...")
    await app.state.redis.close()
    await close_async_db_pool()


app = FastAPI(
    title="旅游系统API",
    description="旅游系统的FastAPI后端",
    version="0.1.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境中应该限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#设置logger
logger = setup_logger()

# 注册路由
app.include_router(tickets_router)
app.include_router(sight_router)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def root():
    return {"message": "欢迎使用旅游系统API"}

from fastapi.responses import FileResponse
import os

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(os.path.join("app", "static", "favicon.ico"))



