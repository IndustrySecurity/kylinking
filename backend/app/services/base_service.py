"""
基础服务类 - 支持多租户的服务层基类
"""
from typing import Optional, Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy import text
from flask import g, current_app
from app.extensions import db
import logging

logger = logging.getLogger(__name__)


class BaseService:
    """
    多租户支持的基础服务类
    
    提供租户上下文管理、数据库会话管理等基础功能
    所有业务服务类应该继承此类
    """
    
    def __init__(self, tenant_id: Optional[str] = None, schema_name: Optional[str] = None):
        """
        初始化服务
        
        Args:
            tenant_id: 租户ID，如果不提供则从Flask的g对象获取
            schema_name: Schema名称，如果不提供则从Flask的g对象获取
        """
        self.tenant_id = tenant_id or getattr(g, 'tenant_id', None)
        self.schema_name = schema_name or getattr(g, 'schema_name', current_app.config.get('DEFAULT_SCHEMA', 'public'))
        self.db = db
        
        # 添加session属性，直接引用db.session
        self.session = self.db.session
        
        # 设置schema搜索路径
        self._set_schema()
        
        logger.info(f"Initialized {self.__class__.__name__} for tenant: {self.tenant_id}, schema: {self.schema_name}")
    
    def _set_schema(self) -> None:
        """设置当前租户的schema搜索路径"""
        if self.schema_name and self.schema_name != 'public':
            try:
                self.db.session.execute(text(f'SET search_path TO {self.schema_name}, public'))
                logger.debug(f"Set search_path to {self.schema_name} in {self.__class__.__name__}")
            except Exception as e:
                logger.error(f"Failed to set search_path to {self.schema_name}: {e}")
                raise
    
    def get_session(self) -> Session:
        """
        获取数据库会话
        
        Returns:
            SQLAlchemy Session对象
        """
        return self.db.session
    
    def commit(self) -> None:
        """提交事务"""
        try:
            self.db.session.commit()
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Transaction commit failed in {self.__class__.__name__}: {e}")
            raise
    
    def rollback(self) -> None:
        """回滚事务"""
        self.db.session.rollback()
        logger.info(f"Transaction rolled back in {self.__class__.__name__}")
    
    def refresh_schema(self) -> None:
        """刷新schema设置（在租户切换时调用）"""
        self._set_schema()
    
    def validate_tenant_access(self, resource_tenant_id: str) -> bool:
        """
        验证是否有权限访问指定租户的资源
        
        Args:
            resource_tenant_id: 资源所属的租户ID
            
        Returns:
            bool: 是否有权限访问
        """
        if not self.tenant_id:
            logger.warning("No tenant_id set for service instance")
            return False
        
        return self.tenant_id == resource_tenant_id
    
    def get_current_user_id(self) -> Optional[str]:
        """获取当前用户ID"""
        try:
            from flask_jwt_extended import get_jwt_identity
            return get_jwt_identity()
        except Exception:
            return None
    
    def log_operation(self, operation: str, details: Optional[Dict[str, Any]] = None) -> None:
        """
        记录操作日志
        
        Args:
            operation: 操作名称
            details: 操作详情
        """
        user_id = self.get_current_user_id()
        log_data = {
            'tenant_id': self.tenant_id,
            'user_id': user_id,
            'operation': operation,
            'service': self.__class__.__name__,
            'details': details or {}
        }
        logger.info(f"Operation log: {log_data}")


class TenantAwareService(BaseService):
    """
    租户感知服务类 - 为需要严格租户隔离的服务提供额外保护
    """
    
    def __init__(self, tenant_id: Optional[str] = None, schema_name: Optional[str] = None, 
                 strict_tenant_check: bool = True):
        """
        初始化租户感知服务
        
        Args:
            tenant_id: 租户ID
            schema_name: Schema名称
            strict_tenant_check: 是否启用严格的租户检查
        """
        super().__init__(tenant_id, schema_name)
        self.strict_tenant_check = strict_tenant_check
        
        if self.strict_tenant_check and not self.tenant_id:
            raise ValueError("tenant_id is required for strict tenant checking")
    
    def ensure_tenant_isolation(self, query):
        """
        确保查询只返回当前租户的数据
        
        Args:
            query: SQLAlchemy查询对象
            
        Returns:
            修改后的查询对象
        """
        if self.strict_tenant_check and hasattr(query.column_descriptions[0]['type'], 'tenant_id'):
            return query.filter_by(tenant_id=self.tenant_id)
        return query
    
    def create_with_tenant(self, model_class, **kwargs):
        """
        创建带租户信息的模型实例
        
        Args:
            model_class: 模型类
            **kwargs: 模型属性
            
        Returns:
            创建的模型实例
        """
        if hasattr(model_class, 'tenant_id'):
            kwargs['tenant_id'] = self.tenant_id
        
        if hasattr(model_class, 'created_by'):
            kwargs['created_by'] = self.get_current_user_id()
        
        instance = model_class(**kwargs)
        self.db.session.add(instance)
        return instance


# 服务工厂类
class ServiceFactory:
    """服务工厂 - 用于创建和管理服务实例"""
    
    @staticmethod
    def create_service(service_class, tenant_id: Optional[str] = None, 
                      schema_name: Optional[str] = None, **kwargs):
        """
        创建服务实例
        
        Args:
            service_class: 服务类
            tenant_id: 租户ID
            schema_name: Schema名称
            **kwargs: 其他参数
            
        Returns:
            服务实例
        """
        return service_class(tenant_id=tenant_id, schema_name=schema_name, **kwargs)
    
    @staticmethod
    def create_tenant_service(service_class, tenant_id: str, **kwargs):
        """
        创建租户感知服务实例
        
        Args:
            service_class: 服务类
            tenant_id: 租户ID
            **kwargs: 其他参数
            
        Returns:
            服务实例
        """
        from flask import g
        schema_name = getattr(g, 'schema_name', f'tenant_{tenant_id}')
        return service_class(tenant_id=tenant_id, schema_name=schema_name, **kwargs) 