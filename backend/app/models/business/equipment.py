from sqlalchemy import Column, String, Date, ForeignKey, DateTime, Text, Numeric, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import TenantModel
import uuid


class Equipment(TenantModel):
    """
    设备模型，存储在租户schema
    """
    
    __tablename__ = 'equipments'
    
    # 设备信息
    name = Column(String(255), nullable=False)
    model = Column(String(255))
    serial_number = Column(String(255), unique=True)
    description = Column(Text)
    purchase_date = Column(Date)
    warranty_expiry = Column(Date)
    
    # 设备状态
    status = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # 维护信息
    last_maintenance_date = Column(Date)
    next_maintenance_date = Column(Date)
    
    def __init__(self, name, status, model=None, serial_number=None, description=None, 
                 purchase_date=None, warranty_expiry=None, is_active=True,
                 last_maintenance_date=None, next_maintenance_date=None):
        """
        初始化设备
        :param name: 设备名称
        :param status: 状态
        :param model: 型号
        :param serial_number: 序列号
        :param description: 描述
        :param purchase_date: 购买日期
        :param warranty_expiry: 保修到期日
        :param is_active: 是否激活
        :param last_maintenance_date: 上次维护日期
        :param next_maintenance_date: 下次维护日期
        """
        self.name = name
        self.status = status
        self.model = model
        self.serial_number = serial_number
        self.description = description
        self.purchase_date = purchase_date
        self.warranty_expiry = warranty_expiry
        self.is_active = is_active
        self.last_maintenance_date = last_maintenance_date
        self.next_maintenance_date = next_maintenance_date
    
    def __repr__(self):
        return f'<Equipment {self.name}>' 