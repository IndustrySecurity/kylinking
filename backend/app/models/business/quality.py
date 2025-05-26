from sqlalchemy import Column, String, Date, ForeignKey, DateTime, Text, Numeric, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import TenantModel
import uuid


class QualityInspection(TenantModel):
    """
    质量检查模型，存储在租户schema
    """
    
    __tablename__ = 'quality_inspections'
    
    # 关联生产记录
    production_record_id = Column(UUID(as_uuid=True), ForeignKey('production_records.id', ondelete='CASCADE'), nullable=False)
    
    # 检查信息
    inspection_date = Column(DateTime, nullable=False)
    inspector = Column(UUID(as_uuid=True), nullable=False)
    status = Column(String(50), nullable=False)
    result = Column(String(50), nullable=False)
    notes = Column(Text)
    
    # 关联关系
    production_record = relationship("ProductionRecord", back_populates="quality_inspections")
    
    def __init__(self, production_record_id, inspection_date, inspector, status, result, notes=None):
        """
        初始化质量检查
        :param production_record_id: 生产记录ID
        :param inspection_date: 检查日期
        :param inspector: 检查员ID
        :param status: 状态
        :param result: 结果
        :param notes: 备注
        """
        self.production_record_id = production_record_id
        self.inspection_date = inspection_date
        self.inspector = inspector
        self.status = status
        self.result = result
        self.notes = notes
    
    def __repr__(self):
        return f'<QualityInspection {self.id}>' 