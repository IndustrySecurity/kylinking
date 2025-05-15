from sqlalchemy import Column, String, Date, ForeignKey, DateTime, Text, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import TenantModel
import uuid


class ProductionPlan(TenantModel):
    """
    生产计划模型，存储在租户schema
    """
    
    __tablename__ = 'production_plans'
    
    # 计划信息
    name = Column(String(255), nullable=False)
    description = Column(Text)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(String(50), nullable=False)
    
    # 创建者
    created_by = Column(UUID(as_uuid=True), nullable=False)
    
    # 关联关系
    production_records = relationship("ProductionRecord", back_populates="plan", cascade="all, delete-orphan")
    
    def __init__(self, name, start_date, end_date, status, created_by, description=None):
        """
        初始化生产计划
        :param name: 计划名称
        :param start_date: 开始日期
        :param end_date: 结束日期
        :param status: 状态
        :param created_by: 创建者ID
        :param description: 描述
        """
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.status = status
        self.created_by = created_by
        self.description = description
    
    def __repr__(self):
        return f'<ProductionPlan {self.name}>'


class ProductionRecord(TenantModel):
    """
    生产记录模型，存储在租户schema
    """
    
    __tablename__ = 'production_records'
    
    # 关联计划和设备
    plan_id = Column(UUID(as_uuid=True), ForeignKey('production_plans.id', ondelete='CASCADE'), nullable=False)
    equipment_id = Column(UUID(as_uuid=True), ForeignKey('equipments.id'), nullable=False)
    
    # 生产信息
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    quantity = Column(Numeric(10, 2), nullable=False)
    status = Column(String(50), nullable=False)
    notes = Column(Text)
    
    # 创建者
    created_by = Column(UUID(as_uuid=True), nullable=False)
    
    # 关联关系
    plan = relationship("ProductionPlan", back_populates="production_records")
    equipment = relationship("Equipment")
    quality_inspections = relationship("QualityInspection", back_populates="production_record", cascade="all, delete-orphan")
    
    def __init__(self, plan_id, equipment_id, start_time, quantity, status, created_by, end_time=None, notes=None):
        """
        初始化生产记录
        :param plan_id: 计划ID
        :param equipment_id: 设备ID
        :param start_time: 开始时间
        :param quantity: 数量
        :param status: 状态
        :param created_by: 创建者ID
        :param end_time: 结束时间
        :param notes: 备注
        """
        self.plan_id = plan_id
        self.equipment_id = equipment_id
        self.start_time = start_time
        self.end_time = end_time
        self.quantity = quantity
        self.status = status
        self.created_by = created_by
        self.notes = notes
    
    def __repr__(self):
        return f'<ProductionRecord {self.id}>' 