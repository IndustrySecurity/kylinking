from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from app.models.module import (
    SystemModule, ModuleField, TenantModule, 
    TenantFieldConfig, TenantExtension
)
from app.models.tenant import Tenant
from app.models.user import User
from app.extensions import db
import uuid


class ModuleService:
    """模块管理服务"""
    
    @staticmethod
    def create_system_module(
        name: str,
        display_name: str,
        description: Optional[str] = None,
        category: Optional[str] = None,
        version: str = '1.0.0',
        icon: Optional[str] = None,
        sort_order: int = 0,
        is_core: bool = False,
        dependencies: Optional[List[str]] = None,
        default_config: Optional[Dict] = None
    ) -> SystemModule:
        """创建系统模块"""
        module = SystemModule(
            name=name,
            display_name=display_name,
            description=description,
            category=category,
            version=version,
            icon=icon,
            sort_order=sort_order,
            is_core=is_core,
            dependencies=dependencies,
            default_config=default_config
        )
        
        db.session.add(module)
        db.session.commit()
        return module
    
    @staticmethod
    def add_module_field(
        module_id: str,
        field_name: str,
        display_name: str,
        field_type: str,
        description: Optional[str] = None,
        is_required: bool = False,
        is_system_field: bool = False,
        is_configurable: bool = True,
        sort_order: int = 0,
        validation_rules: Optional[Dict] = None,
        field_options: Optional[Dict] = None,
        default_value: Any = None
    ) -> ModuleField:
        """为模块添加字段定义"""
        field = ModuleField(
            module_id=uuid.UUID(module_id),
            field_name=field_name,
            display_name=display_name,
            field_type=field_type,
            description=description,
            is_required=is_required,
            is_system_field=is_system_field,
            is_configurable=is_configurable,
            sort_order=sort_order,
            validation_rules=validation_rules,
            field_options=field_options,
            default_value=default_value
        )
        
        db.session.add(field)
        db.session.commit()
        return field
    
    @staticmethod
    def get_available_modules(tenant_id: Optional[str] = None) -> List[Dict]:
        """获取可用的模块列表"""
        query = db.session.query(SystemModule).filter(SystemModule.is_active == True)
        modules = query.order_by(SystemModule.sort_order).all()
        
        result = []
        for module in modules:
            module_data = {
                'id': str(module.id),
                'name': module.name,
                'display_name': module.display_name,
                'description': module.description,
                'category': module.category,
                'version': module.version,
                'icon': module.icon,
                'is_core': module.is_core,
                'dependencies': module.dependencies,
                'default_config': module.default_config
            }
            
            # 如果指定了租户，添加租户配置信息
            if tenant_id:
                tenant_module = db.session.query(TenantModule).filter(
                    TenantModule.tenant_id == uuid.UUID(tenant_id),
                    TenantModule.module_id == module.id
                ).first()
                
                if tenant_module:
                    module_data.update({
                        'is_enabled': tenant_module.is_enabled,
                        'is_visible': tenant_module.is_visible,
                        'custom_config': tenant_module.custom_config,
                        'custom_permissions': tenant_module.custom_permissions
                    })
                else:
                    module_data.update({
                        'is_enabled': False,
                        'is_visible': True,
                        'custom_config': {},
                        'custom_permissions': {}
                    })
            
            result.append(module_data)
        
        return result
    
    @staticmethod
    def configure_tenant_module(
        tenant_id: str,
        module_id: str,
        is_enabled: bool = True,
        is_visible: bool = True,
        custom_config: Optional[Dict] = None,
        custom_permissions: Optional[Dict] = None,
        configured_by: Optional[str] = None
    ) -> TenantModule:
        """配置租户模块"""
        # 检查是否已存在配置
        existing = db.session.query(TenantModule).filter(
            TenantModule.tenant_id == uuid.UUID(tenant_id),
            TenantModule.module_id == uuid.UUID(module_id)
        ).first()
        
        if existing:
            # 更新现有配置
            existing.is_enabled = is_enabled
            existing.is_visible = is_visible
            existing.custom_config = custom_config or {}
            existing.custom_permissions = custom_permissions or {}
            if configured_by:
                existing.configured_by = uuid.UUID(configured_by)
            existing.configured_at = db.func.now()
            
            db.session.commit()
            return existing
        else:
            # 创建新配置
            tenant_module = TenantModule(
                tenant_id=uuid.UUID(tenant_id),
                module_id=uuid.UUID(module_id),
                is_enabled=is_enabled,
                is_visible=is_visible,
                custom_config=custom_config,
                custom_permissions=custom_permissions,
                configured_by=uuid.UUID(configured_by) if configured_by else None
            )
            
            db.session.add(tenant_module)
            db.session.commit()
            return tenant_module
    
    @staticmethod
    def get_module_fields(module_id: str, tenant_id: Optional[str] = None) -> List[Dict]:
        """获取模块字段列表"""
        query = db.session.query(ModuleField).filter(
            ModuleField.module_id == uuid.UUID(module_id)
        ).order_by(ModuleField.sort_order)
        
        fields = query.all()
        result = []
        
        for field in fields:
            field_data = {
                'id': str(field.id),
                'field_name': field.field_name,
                'display_name': field.display_name,
                'field_type': field.field_type,
                'description': field.description,
                'is_required': field.is_required,
                'is_system_field': field.is_system_field,
                'is_configurable': field.is_configurable,
                'validation_rules': field.validation_rules,
                'field_options': field.field_options,
                'default_value': field.default_value
            }
            
            # 如果指定了租户，添加租户字段配置
            if tenant_id:
                tenant_config = db.session.query(TenantFieldConfig).filter(
                    TenantFieldConfig.tenant_id == uuid.UUID(tenant_id),
                    TenantFieldConfig.field_id == field.id
                ).first()
                
                if tenant_config:
                    field_data.update({
                        'is_enabled': tenant_config.is_enabled,
                        'is_visible': tenant_config.is_visible,
                        'is_required_override': tenant_config.is_required,
                        'is_readonly': tenant_config.is_readonly,
                        'custom_label': tenant_config.custom_label,
                        'custom_placeholder': tenant_config.custom_placeholder,
                        'custom_help_text': tenant_config.custom_help_text,
                        'custom_validation_rules': tenant_config.custom_validation_rules,
                        'custom_options': tenant_config.custom_options,
                        'custom_default_value': tenant_config.custom_default_value,
                        'display_order': tenant_config.display_order,
                        'column_width': tenant_config.column_width,
                        'field_group': tenant_config.field_group
                    })
                else:
                    field_data.update({
                        'is_enabled': True,
                        'is_visible': True,
                        'is_required_override': field.is_required,
                        'is_readonly': False,
                        'custom_label': None,
                        'custom_placeholder': None,
                        'custom_help_text': None,
                        'custom_validation_rules': {},
                        'custom_options': {},
                        'custom_default_value': None,
                        'display_order': field.sort_order,
                        'column_width': None,
                        'field_group': None
                    })
            
            result.append(field_data)
        
        return result
    
    @staticmethod
    def configure_tenant_field(
        tenant_id: str,
        field_id: str,
        is_enabled: bool = True,
        is_visible: bool = True,
        is_required: Optional[bool] = None,
        is_readonly: bool = False,
        custom_label: Optional[str] = None,
        custom_placeholder: Optional[str] = None,
        custom_help_text: Optional[str] = None,
        custom_validation_rules: Optional[Dict] = None,
        custom_options: Optional[Dict] = None,
        custom_default_value: Any = None,
        display_order: int = 0,
        column_width: Optional[int] = None,
        field_group: Optional[str] = None,
        configured_by: Optional[str] = None
    ) -> TenantFieldConfig:
        """配置租户字段"""
        # 检查是否已存在配置
        existing = db.session.query(TenantFieldConfig).filter(
            TenantFieldConfig.tenant_id == uuid.UUID(tenant_id),
            TenantFieldConfig.field_id == uuid.UUID(field_id)
        ).first()
        
        # 获取原始字段信息
        field = db.session.query(ModuleField).get(uuid.UUID(field_id))
        if not field:
            raise ValueError("Field not found")
        
        # 如果字段不可配置且不是系统字段，不允许配置
        if not field.is_configurable and not field.is_system_field:
            raise ValueError("Field is not configurable")
        
        # 如果没有提供is_required，使用字段默认值
        if is_required is None:
            is_required = field.is_required
        
        if existing:
            # 更新现有配置
            existing.is_enabled = is_enabled
            existing.is_visible = is_visible
            existing.is_required = is_required
            existing.is_readonly = is_readonly
            existing.custom_label = custom_label
            existing.custom_placeholder = custom_placeholder
            existing.custom_help_text = custom_help_text
            existing.custom_validation_rules = custom_validation_rules or {}
            existing.custom_options = custom_options or {}
            existing.custom_default_value = custom_default_value
            existing.display_order = display_order
            existing.column_width = column_width
            existing.field_group = field_group
            if configured_by:
                existing.configured_by = uuid.UUID(configured_by)
            existing.configured_at = db.func.now()
            
            db.session.commit()
            return existing
        else:
            # 创建新配置
            config = TenantFieldConfig(
                tenant_id=uuid.UUID(tenant_id),
                field_id=uuid.UUID(field_id),
                is_enabled=is_enabled,
                is_visible=is_visible,
                is_required=is_required,
                is_readonly=is_readonly,
                custom_label=custom_label,
                custom_placeholder=custom_placeholder,
                custom_help_text=custom_help_text,
                custom_validation_rules=custom_validation_rules,
                custom_options=custom_options,
                custom_default_value=custom_default_value,
                display_order=display_order,
                column_width=column_width,
                field_group=field_group,
                configured_by=uuid.UUID(configured_by) if configured_by else None
            )
            
            db.session.add(config)
            db.session.commit()
            return config


class TenantExtensionService:
    """租户扩展服务"""
    
    @staticmethod
    def create_extension(
        tenant_id: str,
        extension_type: str,
        extension_name: str,
        extension_key: str,
        extension_config: Optional[Dict] = None,
        extension_schema: Optional[Dict] = None,
        extension_metadata: Optional[Dict] = None,
        module_id: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> TenantExtension:
        """创建租户扩展"""
        extension = TenantExtension(
            tenant_id=uuid.UUID(tenant_id),
            extension_type=extension_type,
            extension_name=extension_name,
            extension_key=extension_key,
            extension_config=extension_config,
            extension_schema=extension_schema,
            extension_metadata=extension_metadata,
            module_id=uuid.UUID(module_id) if module_id else None,
            created_by=uuid.UUID(created_by) if created_by else None
        )
        
        db.session.add(extension)
        db.session.commit()
        return extension
    
    @staticmethod
    def get_tenant_extensions(
        tenant_id: str,
        extension_type: Optional[str] = None,
        module_id: Optional[str] = None
    ) -> List[Dict]:
        """获取租户扩展列表"""
        query = db.session.query(TenantExtension).filter(
            TenantExtension.tenant_id == uuid.UUID(tenant_id),
            TenantExtension.is_active == True
        )
        
        if extension_type:
            query = query.filter(TenantExtension.extension_type == extension_type)
        
        if module_id:
            query = query.filter(TenantExtension.module_id == uuid.UUID(module_id))
        
        extensions = query.all()
        
        result = []
        for ext in extensions:
            result.append({
                'id': str(ext.id),
                'extension_type': ext.extension_type,
                'extension_name': ext.extension_name,
                'extension_key': ext.extension_key,
                'extension_config': ext.extension_config,
                'extension_schema': ext.extension_schema,
                'extension_metadata': ext.extension_metadata,
                'module_id': str(ext.module_id) if ext.module_id else None,
                'created_at': ext.created_at.isoformat() if ext.created_at else None
            })
        
        return result
    
    @staticmethod
    def update_extension(
        extension_id: str,
        extension_config: Optional[Dict] = None,
        extension_schema: Optional[Dict] = None,
        extension_metadata: Optional[Dict] = None,
        is_active: Optional[bool] = None
    ) -> TenantExtension:
        """更新租户扩展"""
        extension = db.session.query(TenantExtension).get(uuid.UUID(extension_id))
        if not extension:
            raise ValueError("Extension not found")
        
        if extension_config is not None:
            extension.extension_config = extension_config
        
        if extension_schema is not None:
            extension.extension_schema = extension_schema
        
        if extension_metadata is not None:
            extension.extension_metadata = extension_metadata
        
        if is_active is not None:
            extension.is_active = is_active
        
        extension.updated_at = db.func.now()
        db.session.commit()
        return extension


class TenantConfigService:
    """租户配置服务 - 综合管理租户的模块和字段配置"""
    
    @staticmethod
    def get_tenant_config_summary(tenant_id: str) -> Dict:
        """获取租户配置概要"""
        # 获取已启用的模块
        enabled_modules = db.session.query(TenantModule).filter(
            TenantModule.tenant_id == uuid.UUID(tenant_id),
            TenantModule.is_enabled == True
        ).count()
        
        # 获取总模块数
        total_modules = db.session.query(SystemModule).filter(
            SystemModule.is_active == True
        ).count()
        
        # 获取自定义字段配置数
        custom_field_configs = db.session.query(TenantFieldConfig).filter(
            TenantFieldConfig.tenant_id == uuid.UUID(tenant_id)
        ).count()
        
        # 获取扩展数
        extensions = db.session.query(TenantExtension).filter(
            TenantExtension.tenant_id == uuid.UUID(tenant_id),
            TenantExtension.is_active == True
        ).count()
        
        return {
            'enabled_modules': enabled_modules,
            'total_modules': total_modules,
            'custom_field_configs': custom_field_configs,
            'extensions': extensions,
            'module_coverage': round((enabled_modules / total_modules) * 100, 2) if total_modules > 0 else 0
        }
    
    @staticmethod
    def initialize_tenant_modules(tenant_id: str, user_id: str) -> Dict:
        """为新租户初始化默认模块配置"""
        # 获取所有核心模块
        core_modules = db.session.query(SystemModule).filter(
            SystemModule.is_active == True,
            SystemModule.is_core == True
        ).all()
        
        initialized_count = 0
        for module in core_modules:
            # 检查是否已存在配置
            existing = db.session.query(TenantModule).filter(
                TenantModule.tenant_id == uuid.UUID(tenant_id),
                TenantModule.module_id == module.id
            ).first()
            
            if not existing:
                tenant_module = TenantModule(
                    tenant_id=uuid.UUID(tenant_id),
                    module_id=module.id,
                    is_enabled=True,
                    is_visible=True,
                    custom_config=module.default_config,
                    configured_by=uuid.UUID(user_id)
                )
                db.session.add(tenant_module)
                initialized_count += 1
        
        db.session.commit()
        
        return {
            'initialized_modules': initialized_count,
            'total_core_modules': len(core_modules)
        }
    
    @staticmethod
    def export_tenant_config(tenant_id: str) -> Dict:
        """导出租户配置"""
        # 导出模块配置
        tenant_modules = db.session.query(TenantModule).filter(
            TenantModule.tenant_id == uuid.UUID(tenant_id)
        ).all()
        
        modules_config = []
        for tm in tenant_modules:
            modules_config.append({
                'module_name': tm.module.name,
                'is_enabled': tm.is_enabled,
                'is_visible': tm.is_visible,
                'custom_config': tm.custom_config,
                'custom_permissions': tm.custom_permissions
            })
        
        # 导出字段配置
        field_configs = db.session.query(TenantFieldConfig).filter(
            TenantFieldConfig.tenant_id == uuid.UUID(tenant_id)
        ).all()
        
        fields_config = []
        for fc in field_configs:
            fields_config.append({
                'module_name': fc.field.module.name,
                'field_name': fc.field.field_name,
                'is_enabled': fc.is_enabled,
                'is_visible': fc.is_visible,
                'is_required': fc.is_required,
                'is_readonly': fc.is_readonly,
                'custom_label': fc.custom_label,
                'custom_placeholder': fc.custom_placeholder,
                'custom_help_text': fc.custom_help_text,
                'custom_validation_rules': fc.custom_validation_rules,
                'custom_options': fc.custom_options,
                'custom_default_value': fc.custom_default_value,
                'display_order': fc.display_order,
                'column_width': fc.column_width,
                'field_group': fc.field_group
            })
        
        # 导出扩展配置
        extensions = TenantExtensionService().get_tenant_extensions(tenant_id)
        
        return {
            'tenant_id': tenant_id,
            'modules': modules_config,
            'fields': fields_config,
            'extensions': extensions,
            'exported_at': db.func.now().scalar().isoformat()
        } 