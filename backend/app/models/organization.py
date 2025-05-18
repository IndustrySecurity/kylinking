from sqlalchemy import Column, String, Text, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import SystemModel
from app.models.user import organization_users
from app.extensions import db
import uuid


class Organization(SystemModel):
    """
    组织模型，存储在system schema
    表示租户内的组织架构，如部门、团队等
    """
    
    __tablename__ = 'organizations'
    
    # 关联租户
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    
    # 父组织ID
    parent_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id', ondelete='CASCADE'), nullable=True)
    
    # 组织信息
    name = Column(String(100), nullable=False)
    code = Column(String(50), nullable=False)  # 组织代码，唯一标识
    description = Column(Text, nullable=True)
    
    # 组织层级
    level = Column(Integer, default=1)
    
    # 关系
    children = relationship("Organization", 
                          backref=db.backref('parent', remote_side='Organization.id'),
                          cascade="all, delete-orphan")
    # 使用字符串引用User模型
    users = relationship("User", secondary=organization_users, back_populates="organizations")
    
    def __init__(self, name, code, tenant_id, parent_id=None, description=None, level=1):
        """
        初始化组织
        :param name: 组织名称
        :param code: 组织代码
        :param tenant_id: 租户ID
        :param parent_id: 父组织ID
        :param description: 组织描述
        :param level: 组织层级
        """
        self.name = name
        self.code = code
        self.tenant_id = tenant_id
        self.parent_id = parent_id
        self.description = description
        self.level = level
    
    def __repr__(self):
        return f'<Organization {self.name}>' 