# app/models/ticket.py
from sqlalchemy import Column, Integer, String, Numeric, Boolean, Text, ForeignKey, Float, Date, DateTime, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Ticket(Base):
    """
    门票模型，对应Django中的sight_ticket表
    """
    __tablename__ = "sight_ticket"

    id = Column(Integer, primary_key=True, index=True)
    sight_id = Column(Integer, ForeignKey("sight.id"), index=True)  # 关联的景点ID
    name = Column(String(128))  # 门票名称
    desc = Column(String(256), nullable=True)  # 门票描述
    type = Column(String(32), nullable=True)  # 门票类型
    price = Column(Float)  # 价格
    discount = Column(Float, default=1.0)  # 折扣
    total = Column(Integer, default=0)  # 总数量
    remain = Column(Integer, default=0)  # 剩余数量
    expire_date = Column(Date, nullable=True)  # 有效期
    return_policy = Column(String(256), nullable=True)  # 退票政策
    is_valid = Column(Boolean, default=True)  # 是否有效
    created_at = Column(DateTime, default=func.now())  # 创建时间
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())  # 修改时间

    # 关系
    sight = relationship("Sight", back_populates="tickets")