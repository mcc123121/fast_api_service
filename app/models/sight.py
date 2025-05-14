
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Sight(Base):
    """景点基础信息表"""
    __tablename__ = "sight"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), nullable=False)  # 景点名称
    desc = Column(String(256), nullable=False)  # 景点简介
    main_img = Column(String(256), nullable=False)  # 主图
    banner_img = Column(String(256), nullable=False)  # 轮播图
    content = Column(Text, nullable=False)  # 景点详细内容
    score = Column(Float, default=5.0)  # 评分
    min_price = Column(Float, default=0)  # 最低价格
    province = Column(String(32), nullable=False)  # 省份
    city = Column(String(32), nullable=False)  # 城市
    area = Column(String(32), nullable=True)  # 区域
    town = Column(String(32), nullable=True)  # 镇/街道
    is_top = Column(Boolean, default=False)  # 是否精选
    is_hot = Column(Boolean, default=False)  # 是否热门
    is_valid = Column(Boolean, default=True)  # 是否有效
    created_at = Column(DateTime, default=func.now())  # 创建时间
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())  # 更新时间

    # 关系
    profile = relationship("SightProfile", back_populates="sight", uselist=False)
    tickets = relationship("Ticket", back_populates="sight")


class SightProfile(Base):
    """景点详细信息表"""
    __tablename__ = "sight_profile"

    id = Column(BigInteger, primary_key=True, index=True)
    img = Column(String(256), nullable=False)  # 图片
    address = Column(String(256), nullable=False)  # 地址
    explain = Column(String(1024), nullable=True)  # 说明
    open_time = Column(String(256), nullable=False)  # 开放时间
    tel = Column(String(32), nullable=False)  # 电话
    level = Column(String(32), nullable=True)  # 景点等级
    tags = Column(String(256), nullable=True)  # 标签
    attention = Column(Text, nullable=True)  # 注意事项
    location = Column(String(256), nullable=True)  # 位置
    sight_id = Column(BigInteger, ForeignKey("sight.id"), unique=True, nullable=False)  # 关联的景点ID

    # 关系
    sight = relationship("Sight", back_populates="profile")