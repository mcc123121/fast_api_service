from sqlalchemy import Column,Integer,String,Float,DateTime,ForeignKey,Boolean,Date,BigInteger
from sqlalchemy.sql import func
from app.database import Base
import random
from datetime import datetime

class Order(Base):
    '''订单主表'''
    __tablename__ = 'order'

    id = Column(Integer, primary_key=True, index=True)
    # 订单编号
    order_number = Column(String(32), unique=True, index=True)
    #用ID，关联到Django的UserAUth表
    user_id = Column(Integer,index=True)
    #订单总金额
    total_amount = Column(Float)
    #订单状态:0-待支付 1-已支付 2-已取消
    status = Column(Integer,default=0)
    #联系人姓名
    contact_name = Column(String(32))
    #联系人电话
    contact_phone = Column(String(11))
    #订单备注
    remark = Column(String(256),nullable=True)
    #创建时间
    created_at = Column(DateTime,default=func.now())
    #更新时间
    updated_at = Column(DateTime,default=func.now(),onupdate=func.now())
    #支付时间
    pay_time = Column(DateTime,nullable=True)

    @staticmethod
    def generate_order_number():
        '''生成订单编号,年月日时分秒+4位随机数'''
        now = datetime.now()
        return now.strftime('%Y%m%d%H%M%S') + ''.join(random.choice('0123456789') for _ in range(4))


class OrderItem(Base):
    '''订单项表'''
    __tablename__ = 'order_item'

    id = Column(Integer, primary_key=True, index=True)
    #关联订单的ID
    order_id = Column(Integer, ForeignKey("order.id"), index=True)
    #关联的门票ID
    ticket_id = Column(BigInteger, ForeignKey("sight_ticket.id"), index=True)
    #门票名称
    ticket_name = Column(String(128))
    #购买时的门票单击
    price = Column(Integer)
    #购买数量
    quantity = Column(Integer)
    #小计金额
    amount = Column(Integer)
    #游玩日期
    visit_date = Column(Date)
    #创建时间
    created_at = Column(DateTime,default=func.now())


class Visitor(Base):
    '''游客信息表'''
    __tablename__ = 'visitor'

    id = Column(Integer,primary_key=True,index=True)
    #关联订单的ID
    order_id = Column(Integer,ForeignKey("order.id"),index=True)
    #游客姓名
    name = Column(String(32))
    #身份证号
    id_card = Column(String(18))
    #手机号
    phone = Column(String(11))
    #创建时间
    created_at = Column(DateTime,default=func.now())
