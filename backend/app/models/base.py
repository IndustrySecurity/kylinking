from sqlalchemy import Column, DateTime, func, text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.extensions import db
from flask import current_app, g
import uuid


class BaseModel(db.Model):
    """
    所有模型的基类，提供通用字段和方法
    """
    
    __abstract__ = True
    
    # 默认使用UUID作为主键
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 创建和更新时间 - 使用数据库服务器时间
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    @classmethod
    def get_by_id(cls, id):
        """
        根据ID获取记录
        :param id: 记录ID
        :return: 记录对象
        """
        return cls.query.filter_by(id=id).first()
    
    def save(self):
        """
        保存记录到数据库
        """
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self):
        """
        从数据库删除记录
        """
        db.session.delete(self)
        db.session.commit()
        return self
    
    def to_dict(self):
        """
        将模型转换为字典
        :return: 字典
        """
        result = {}
        for c in self.__table__.columns:
            value = getattr(self, c.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            elif isinstance(value, uuid.UUID):
                value = str(value)
            result[c.name] = value
        return result


class SystemModel(BaseModel):
    """
    系统级模型的基类，用于存储在system schema中
    """
    
    __abstract__ = True
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    @classmethod
    def __declare_last__(cls):
        """
        在声明完成后设置schema
        """
        if not cls.__table__.schema:
            cls.__table__.schema = current_app.config['SYSTEM_SCHEMA']


class TenantModel(BaseModel):
    """
    租户级模型的基类，表示存储在租户schema中的实体
    """
    
    __abstract__ = True
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    @classmethod
    def get_schema(cls):
        """
        获取当前租户的schema
        :return: schema名称
        """
        from app.utils.tenant_context import TenantContext
        tenant_context = TenantContext()
        return tenant_context.get_schema() 