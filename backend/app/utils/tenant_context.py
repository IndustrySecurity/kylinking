from flask import g, current_app
from sqlalchemy import event, text
from sqlalchemy.orm import Session
from functools import wraps
import threading

# 线程本地存储，用于存储当前租户上下文
_thread_local = threading.local()


class TenantContext:
    """
    租户上下文，用于管理多租户数据库操作
    """
    
    def set_schema(self, schema_name):
        """
        设置当前线程的schema
        :param schema_name: schema名称
        """
        _thread_local.schema_name = schema_name
    
    def get_schema(self):
        """
        获取当前线程的schema
        :return: schema名称
        """
        return getattr(_thread_local, 'schema_name', current_app.config['DEFAULT_SCHEMA'])


# SQLAlchemy事件监听器，用于在执行SQL前设置schema
@event.listens_for(Session, "before_flush")
def before_flush(session, flush_context, instances):
    """
    在SQLAlchemy提交前更新schema搜索路径
    :param session: SQLAlchemy会话
    :param flush_context: 刷新上下文
    :param instances: 实例列表
    """
    schema_name = getattr(_thread_local, 'schema_name', current_app.config['DEFAULT_SCHEMA'])
    
    # 设置当前会话的schema搜索路径
    # 只有当schema不是默认的public时才需要设置
    if schema_name != 'public':
        current_app.logger.info(f"Setting search_path to {schema_name} in before_flush")
        session.execute(text(f'SET search_path TO {schema_name}, public'))


@event.listens_for(Session, "after_begin")
def after_begin(session, transaction, connection):
    """
    在事务开始后设置schema搜索路径
    """
    schema_name = getattr(_thread_local, 'schema_name', current_app.config['DEFAULT_SCHEMA'])
    
    if schema_name != 'public':
        current_app.logger.info(f"Setting search_path to {schema_name} in after_begin")
        connection.execute(text(f'SET search_path TO {schema_name}, public'))


def tenant_context_required(f):
    """
    装饰器，确保函数在正确的租户上下文中执行
    :param f: 要装饰的函数
    :return: 装饰后的函数
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # 获取当前请求的schema
        schema_name = g.schema_name if hasattr(g, 'schema_name') else current_app.config['DEFAULT_SCHEMA']
        
        # 在函数执行前设置schema
        tenant_context = TenantContext()
        tenant_context.set_schema(schema_name)
        
        # 执行原函数
        result = f(*args, **kwargs)
        
        # 恢复默认schema
        tenant_context.set_schema(current_app.config['DEFAULT_SCHEMA'])
        
        return result
    
    return decorated 