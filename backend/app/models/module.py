from sqlalchemy import Column, String, Boolean, ForeignKey, Text, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import SystemModel, BaseModel
from app.extensions import db


class SystemModule(SystemModel):
    """
    系统模块模型 - 定义系统中所有可用的功能模块
    存储在system schema
    """
    
    __tablename__ = 'system_modules'
    
    # 模块基本信息
    name = Column(String(100), nullable=False, unique=True)  # 模块名称，如 'production_planning'
    display_name = Column(String(255), nullable=False)  # 显示名称，如 '生产计划管理'
    description = Column(Text)  # 模块描述
    category = Column(String(100))  # 模块分类，如 'production', 'quality', 'inventory'
    
    # 模块配置
    version = Column(String(20), default='1.0.0')  # 模块版本
    icon = Column(String(255))  # 模块图标
    sort_order = Column(Integer, default=0)  # 排序顺序
    is_core = Column(Boolean, default=False)  # 是否为核心模块（核心模块不能禁用）
    is_active = Column(Boolean, default=True)  # 模块是否激活
    
    # 模块依赖关系（JSON格式存储依赖的模块列表）
    dependencies = Column(JSON, default=list)  # 依赖的模块列表
    
    # 默认配置（JSON格式存储模块的默认配置）
    default_config = Column(JSON, default=dict)
    
    # 关联关系
    tenant_modules = relationship("TenantModule", back_populates="module", cascade="all, delete-orphan")
    module_fields = relationship("ModuleField", back_populates="module", cascade="all, delete-orphan")
    
    def __init__(self, name, display_name, description=None, category=None, 
                 version='1.0.0', icon=None, sort_order=0, is_core=False, 
                 dependencies=None, default_config=None):
        self.name = name
        self.display_name = display_name
        self.description = description
        self.category = category
        self.version = version
        self.icon = icon
        self.sort_order = sort_order
        self.is_core = is_core
        self.dependencies = dependencies or []
        self.default_config = default_config or {}
    
    def __repr__(self):
        return f'<SystemModule {self.name}>'


class ModuleField(SystemModel):
    """
    模块字段定义 - 定义每个模块中可配置的字段
    存储在system schema
    """
    
    __tablename__ = 'module_fields'
    
    # 关联模块
    module_id = Column(UUID(as_uuid=True), ForeignKey('system_modules.id'), nullable=False)
    
    # 字段信息
    field_name = Column(String(100), nullable=False)  # 字段名称，如 'planned_start_date'
    display_name = Column(String(255), nullable=False)  # 显示名称，如 '计划开始日期'
    field_type = Column(String(50), nullable=False)  # 字段类型：string, number, date, boolean, select, etc.
    description = Column(Text)  # 字段描述
    
    # 字段配置
    is_required = Column(Boolean, default=False)  # 是否必填字段
    is_system_field = Column(Boolean, default=False)  # 是否系统字段（系统字段不能禁用）
    is_configurable = Column(Boolean, default=True)  # 是否可配置
    sort_order = Column(Integer, default=0)  # 字段排序
    
    # 字段验证规则（JSON格式）
    validation_rules = Column(JSON, default=dict)  # 验证规则
    field_options = Column(JSON, default=dict)  # 字段选项（如下拉列表的选项）
    default_value = Column(JSON)  # 默认值
    
    # 关联关系
    module = relationship("SystemModule", back_populates="module_fields")
    tenant_field_configs = relationship("TenantFieldConfig", back_populates="field", cascade="all, delete-orphan")
    
    def __init__(self, module_id, field_name, display_name, field_type, 
                 description=None, is_required=False, is_system_field=False, 
                 is_configurable=True, sort_order=0, validation_rules=None, 
                 field_options=None, default_value=None):
        self.module_id = module_id
        self.field_name = field_name
        self.display_name = display_name
        self.field_type = field_type
        self.description = description
        self.is_required = is_required
        self.is_system_field = is_system_field
        self.is_configurable = is_configurable
        self.sort_order = sort_order
        self.validation_rules = validation_rules or {}
        self.field_options = field_options or {}
        self.default_value = default_value
    
    def __repr__(self):
        return f'<ModuleField {self.field_name}>'


class TenantModule(SystemModel):
    """
    租户模块配置 - 控制每个租户启用的模块及其配置
    存储在system schema
    """
    
    __tablename__ = 'tenant_modules'
    
    # 关联租户和模块
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id'), nullable=False)
    module_id = Column(UUID(as_uuid=True), ForeignKey('system_modules.id'), nullable=False)
    
    # 模块状态
    is_enabled = Column(Boolean, default=True)  # 是否启用
    is_visible = Column(Boolean, default=True)  # 是否在菜单中显示
    
    # 自定义配置（JSON格式）
    custom_config = Column(JSON, default=dict)  # 租户自定义的模块配置
    custom_permissions = Column(JSON, default=dict)  # 自定义权限配置
    
    # 配置元数据
    configured_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))  # 配置者
    configured_at = Column(db.DateTime, default=db.func.now())  # 配置时间
    
    # 关联关系
    tenant = relationship("Tenant")
    module = relationship("SystemModule", back_populates="tenant_modules")
    configured_by_user = relationship("User")
    
    # 添加唯一约束
    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'module_id', name='uq_tenant_module'),
    )
    
    def __init__(self, tenant_id, module_id, is_enabled=True, is_visible=True, 
                 custom_config=None, custom_permissions=None, configured_by=None):
        self.tenant_id = tenant_id
        self.module_id = module_id
        self.is_enabled = is_enabled
        self.is_visible = is_visible
        self.custom_config = custom_config or {}
        self.custom_permissions = custom_permissions or {}
        self.configured_by = configured_by
    
    def __repr__(self):
        return f'<TenantModule {self.tenant_id}-{self.module_id}>'


class TenantFieldConfig(SystemModel):
    """
    租户字段配置 - 控制每个租户对模块字段的配置
    存储在system schema
    """
    
    __tablename__ = 'tenant_field_configs'
    
    # 关联租户和字段
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id'), nullable=False)
    field_id = Column(UUID(as_uuid=True), ForeignKey('module_fields.id'), nullable=False)
    
    # 字段配置
    is_enabled = Column(Boolean, default=True)  # 是否启用该字段
    is_visible = Column(Boolean, default=True)  # 是否显示该字段
    is_required = Column(Boolean, default=False)  # 是否必填
    is_readonly = Column(Boolean, default=False)  # 是否只读
    
    # 自定义配置
    custom_label = Column(String(255))  # 自定义字段标签
    custom_placeholder = Column(String(255))  # 自定义占位符
    custom_help_text = Column(Text)  # 自定义帮助文本
    custom_validation_rules = Column(JSON, default=dict)  # 自定义验证规则
    custom_options = Column(JSON, default=dict)  # 自定义选项
    custom_default_value = Column(JSON)  # 自定义默认值
    
    # 显示配置
    display_order = Column(Integer, default=0)  # 显示顺序
    column_width = Column(Integer)  # 列宽度（百分比）
    field_group = Column(String(100))  # 字段分组
    
    # 配置元数据
    configured_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    configured_at = Column(db.DateTime, default=db.func.now())
    
    # 关联关系
    tenant = relationship("Tenant")
    field = relationship("ModuleField", back_populates="tenant_field_configs")
    configured_by_user = relationship("User")
    
    # 添加唯一约束
    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'field_id', name='uq_tenant_field'),
    )
    
    def __init__(self, tenant_id, field_id, is_enabled=True, is_visible=True, 
                 is_required=False, is_readonly=False, custom_label=None,
                 custom_placeholder=None, custom_help_text=None,
                 custom_validation_rules=None, custom_options=None,
                 custom_default_value=None, display_order=0, column_width=None,
                 field_group=None, configured_by=None):
        self.tenant_id = tenant_id
        self.field_id = field_id
        self.is_enabled = is_enabled
        self.is_visible = is_visible
        self.is_required = is_required
        self.is_readonly = is_readonly
        self.custom_label = custom_label
        self.custom_placeholder = custom_placeholder
        self.custom_help_text = custom_help_text
        self.custom_validation_rules = custom_validation_rules or {}
        self.custom_options = custom_options or {}
        self.custom_default_value = custom_default_value
        self.display_order = display_order
        self.column_width = column_width
        self.field_group = field_group
        self.configured_by = configured_by
    
    def __repr__(self):
        return f'<TenantFieldConfig {self.tenant_id}-{self.field_id}>'


class TenantExtension(SystemModel):
    """
    租户扩展配置 - 支持租户间的差异化扩展
    存储在system schema
    """
    
    __tablename__ = 'tenant_extensions'
    
    # 关联租户
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id'), nullable=False)
    
    # 扩展信息
    extension_type = Column(String(100), nullable=False)  # 扩展类型：custom_field, custom_workflow, custom_report, etc.
    extension_name = Column(String(255), nullable=False)  # 扩展名称
    extension_key = Column(String(100), nullable=False)  # 扩展唯一标识
    
    # 扩展配置
    extension_config = Column(JSON, default=dict)  # 扩展配置数据
    extension_schema = Column(JSON, default=dict)  # 扩展数据结构定义
    extension_metadata = Column(JSON, default=dict)  # 扩展元数据
    
    # 状态
    is_active = Column(Boolean, default=True)
    
    # 关联模块（可选）
    module_id = Column(UUID(as_uuid=True), ForeignKey('system_modules.id'))
    
    # 配置元数据
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # 关联关系
    tenant = relationship("Tenant")
    module = relationship("SystemModule")
    created_by_user = relationship("User")
    
    # 添加唯一约束
    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'extension_key', name='uq_tenant_extension'),
    )
    
    def __init__(self, tenant_id, extension_type, extension_name, extension_key,
                 extension_config=None, extension_schema=None, extension_metadata=None,
                 is_active=True, module_id=None, created_by=None):
        self.tenant_id = tenant_id
        self.extension_type = extension_type
        self.extension_name = extension_name
        self.extension_key = extension_key
        self.extension_config = extension_config or {}
        self.extension_schema = extension_schema or {}
        self.extension_metadata = extension_metadata or {}
        self.is_active = is_active
        self.module_id = module_id
        self.created_by = created_by
    
    def __repr__(self):
        return f'<TenantExtension {self.extension_key}>' 