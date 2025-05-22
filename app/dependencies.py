# app/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Optional
import time

# 配置
SECRET_KEY = "django-insecure-1234567890abcdefghijklmnopqrstuvwxyz"  # 替换为Django中的实际SECRET_KEY
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class TokenData(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None
    user_type: Optional[str] = None
    exp: Optional[int] = None

    class Config:
        extra = "allow"  # 允许额外的字段

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # 从payload中获取声明
        user_id = payload.get("user_id")
        username = payload.get("username")
        user_type = payload.get("user_type")
        exp = payload.get("exp")

        # 如果没有user_id，尝试从token_type和jti中提取
        if user_id is None and "token_type" in payload and payload["token_type"] == "access":
            # 这是一个access token，可以使用其他字段
            if "user" in payload:
                user_id = payload["user"]

        # 确保至少有username和user_type
        if username is None or user_type is None:
            print("Missing required claims: username or user_type")
            raise credentials_exception

        # 检查令牌是否过期
        if exp is None or time.time() > exp:
            raise credentials_exception

        # 创建TokenData对象，包含所有必要的字段
        token_data_dict = {
            "user_id": user_id,
            "username": username,
            "user_type": user_type,
            "exp": exp
        }

        # 添加payload中的其他字段
        for key, value in payload.items():
            if key not in token_data_dict:
                token_data_dict[key] = value

        token_data = TokenData(**token_data_dict)
    except JWTError as e:
        print(f"JWT decode error: {str(e)}")  # 添加这行来打印具体的JWT错误
        raise credentials_exception

    return token_data

async def get_sight_admin(current_user: TokenData = Depends(get_current_user)):
    if current_user.user_type != "sight_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user