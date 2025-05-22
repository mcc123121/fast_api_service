# app/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Optional
import time

# 配置
SECRET_KEY = "SECRET_KEY"  # 应该与Django中的SECRET_KEY相同
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class TokenData(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None
    user_type: Optional[str] = None
    exp: Optional[int] = None

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        username = payload.get("username")
        user_type = payload.get("user_type")
        exp = payload.get("exp")
        
        if user_id is None or username is None:
            raise credentials_exception
        
        # 检查令牌是否过期
        if exp is None or time.time() > exp:
            raise credentials_exception
        
        token_data = TokenData(user_id=user_id, username=username, user_type=user_type, exp=exp)
    except JWTError:
        raise credentials_exception
    
    return token_data

async def get_sight_admin(current_user: TokenData = Depends(get_current_user)):
    if current_user.user_type != "sight_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user