from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import SystemModel


class Tenant(SystemModel):
    """
    租户模型，存储在system schema
    """
    
    __tablename__ = 'tenants'
    
    # 租户名称
    name = Column(String(255), nullable=False)
    
    # 租户唯一标识，用于URL和域名
    slug = Column(String(100), nullable=False, unique=True)
    
    # 租户数据库schema
    schema_name = Column(String(63), nullable=False, unique=True)
    
    # 自定义域名
    domain = Column(String(255), unique=True)
    
    # 联系信息
    contact_email = Column(String(255), nullable=False)
    contact_phone = Column(String(50))
    
    # 是否激活
    is_active = Column(Boolean, default=True, nullable=False)
    
    # users 关联关系现在通过 User.tenant 的 backref 建立
    
    def __init__(self, name, slug, schema_name, contact_email, domain=None, contact_phone=None, is_active=True):
        """
        初始化租户
        :param name: 租户名称
        :param slug: 租户唯一标识
        :param schema_name: 数据库schema名称
        :param contact_email: 联系邮箱
        :param domain: 自定义域名
        :param contact_phone: 联系电话
        :param is_active: 是否激活
        """
        self.name = name
        self.slug = slug
        self.schema_name = schema_name
        self.contact_email = contact_email
        self.domain = domain
        self.contact_phone = contact_phone
        self.is_active = is_active
    
    def __repr__(self):
        return f'<Tenant {self.name}>' 