from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import SystemModel
from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
import uuid


# 用户角色关联表
user_roles = Table(
    'user_roles',
    SystemModel.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('system.users.id', ondelete='CASCADE'), primary_key=True),
    Column('role_id', UUID(as_uuid=True), ForeignKey('system.roles.id', ondelete='CASCADE'), primary_key=True),
    Column('created_at', DateTime, nullable=False, default=db.func.now()),
    schema='system'
)


class User(SystemModel):
    """
    用户模型，存储在system schema
    """
    
    __tablename__ = 'users'
    
    # 关联租户
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('system.tenants.id'), nullable=True)
    
    # 用户信息
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    
    # 状态
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    is_superadmin = Column(Boolean, default=False, nullable=False)
    
    # 最后登录时间
    last_login_at = Column(DateTime, nullable=True)
    
    # 关联关系
    tenant = relationship("Tenant", back_populates="users")
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    
    def __init__(self, email, password, first_name=None, last_name=None, tenant_id=None, 
                 is_active=True, is_admin=False, is_superadmin=False):
        """
        初始化用户
        :param email: 用户邮箱
        :param password: 明文密码
        :param first_name: 名
        :param last_name: 姓
        :param tenant_id: 租户ID
        :param is_active: 是否激活
        :param is_admin: 是否是管理员
        :param is_superadmin: 是否是超级管理员
        """
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.first_name = first_name
        self.last_name = last_name
        self.tenant_id = tenant_id
        self.is_active = is_active
        self.is_admin = is_admin
        self.is_superadmin = is_superadmin
    
    def check_password(self, password):
        """
        验证密码
        :param password: 明文密码
        :return: 是否匹配
        """
        return check_password_hash(self.password_hash, password)
    
    def set_password(self, password):
        """
        设置密码
        :param password: 明文密码
        """
        self.password_hash = generate_password_hash(password)
    
    def update_last_login(self):
        """
        更新最后登录时间
        """
        self.last_login_at = db.func.now()
        db.session.commit()
    
    def get_full_name(self):
        """
        获取用户全名
        :return: 用户全名
        """
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email
    
    def has_permission(self, permission_name):
        """
        检查用户是否拥有指定权限
        :param permission_name: 权限名称
        :return: 是否拥有权限
        """
        # 超级管理员拥有所有权限
        if self.is_superadmin:
            return True
        
        # 遍历用户的所有角色
        for role in self.roles:
            # 遍历角色的所有权限
            for permission in role.permissions:
                if permission.name == permission_name:
                    return True
        
        return False
    
    def __repr__(self):
        return f'<User {self.email}>'


class Role(SystemModel):
    """
    角色模型，存储在system schema
    """
    
    __tablename__ = 'roles'
    
    # 关联租户
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('system.tenants.id'), nullable=True)
    
    # 角色信息
    name = Column(String(100), nullable=False)
    description = Column(String(255))
    
    # 关联关系
    tenant = relationship("Tenant", back_populates="roles")
    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", secondary="system.role_permissions", back_populates="roles")
    
    def __init__(self, name, description=None, tenant_id=None):
        """
        初始化角色
        :param name: 角色名称
        :param description: 角色描述
        :param tenant_id: 租户ID
        """
        self.name = name
        self.description = description
        self.tenant_id = tenant_id
    
    def __repr__(self):
        return f'<Role {self.name}>'


# 角色权限关联表
role_permissions = Table(
    'role_permissions',
    SystemModel.metadata,
    Column('role_id', UUID(as_uuid=True), ForeignKey('system.roles.id', ondelete='CASCADE'), primary_key=True),
    Column('permission_id', UUID(as_uuid=True), ForeignKey('system.permissions.id', ondelete='CASCADE'), primary_key=True),
    Column('created_at', DateTime, nullable=False, default=db.func.now()),
    schema='system'
)


class Permission(SystemModel):
    """
    权限模型，存储在system schema
    """
    
    __tablename__ = 'permissions'
    
    # 权限信息
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(255))
    
    # 关联关系
    roles = relationship("Role", secondary="system.role_permissions", back_populates="permissions")
    
    def __init__(self, name, description=None):
        """
        初始化权限
        :param name: 权限名称
        :param description: 权限描述
        """
        self.name = name
        self.description = description
    
    def __repr__(self):
        return f'<Permission {self.name}>' 