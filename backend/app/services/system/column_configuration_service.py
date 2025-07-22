import logging
from app.services.base_service import TenantAwareService
from app.models.column_configuration import ColumnConfiguration
import uuid


class ColumnConfigurationService(TenantAwareService):
    """列配置服务"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)
    
    def get_column_config(self, page_name, config_type):
        """获取列配置"""
        try:
            config = ColumnConfiguration.get_config(page_name, config_type)
            return config.to_dict() if config else None
        except Exception as e:
            self.logger.error(f"获取列配置失败: {str(e)}")
            raise ValueError(f"获取列配置失败: {str(e)}")
    
    def save_column_config(self, page_name, config_type, config_data, user_id):
        """保存列配置"""
        try:
            # 验证用户权限 - 只有管理员可以保存配置
            if not self._is_admin_user(user_id):
                raise ValueError("只有管理员可以保存列配置")
            
            config = ColumnConfiguration.save_config(page_name, config_type, config_data, user_id)
            return config.to_dict()
        except Exception as e:
            self.logger.error(f"保存列配置失败: {str(e)}")
            raise ValueError(f"保存列配置失败: {str(e)}")
    
    def delete_column_config(self, page_name, config_type, user_id):
        """删除列配置"""
        try:
            # 验证用户权限 - 只有管理员可以删除配置
            if not self._is_admin_user(user_id):
                raise ValueError("只有管理员可以删除列配置")
            
            config = ColumnConfiguration.delete_config(page_name, config_type)
            return config.to_dict() if config else None
        except Exception as e:
            self.logger.error(f"删除列配置失败: {str(e)}")
            raise ValueError(f"删除列配置失败: {str(e)}")
    
    def get_all_configs(self, page_name=None):
        """获取所有配置"""
        try:
            query = self.session.query(ColumnConfiguration).filter(ColumnConfiguration.is_enabled == True)
            if page_name:
                query = query.filter(ColumnConfiguration.page_name == page_name)
            
            configs = query.all()
            return [config.to_dict() for config in configs]
        except Exception as e:
            self.logger.error(f"获取所有配置失败: {str(e)}")
            raise ValueError(f"获取所有配置失败: {str(e)}")
    
    def _is_admin_user(self, user_id):
        """检查用户是否为管理员"""
        try:
            from app.models.user import User, Role
            user = self.session.query(User).filter(User.id == uuid.UUID(user_id)).first()
            if not user:
                self.logger.warning(f"用户不存在: {user_id}")
                return False
            
            # 首先检查用户的直接管理员标志
            if user.is_admin or user.is_superadmin:
                self.logger.info(f"用户 {user.email} 是管理员 (is_admin={user.is_admin}, is_superadmin={user.is_superadmin})")
                return True
            
            # 检查用户角色
            admin_roles = ['admin', 'super_admin', '系统管理员', '管理员']
            user_roles = [role.name for role in user.roles]  # 使用 role.name 而不是 role.role_name
            
            self.logger.info(f"用户 {user.email} 的角色: {user_roles}")
            
            is_admin = any(role in admin_roles for role in user_roles)
            self.logger.info(f"用户 {user.email} 管理员检查结果: {is_admin}")
            
            return is_admin
        except Exception as e:
            self.logger.error(f"检查用户权限失败: {str(e)}")
            return False


def get_column_configuration_service(tenant_id: str = None, schema_name: str = None) -> ColumnConfigurationService:
    """获取列配置服务实例"""
    return ColumnConfigurationService(tenant_id=tenant_id, schema_name=schema_name) 