# -*- coding: utf-8 -*-
"""
数据库工具函数
"""

from flask_jwt_extended import get_jwt_identity
import uuid


def get_current_user_id():
    """获取当前用户ID"""
    try:
        current_user_id = get_jwt_identity()
        if current_user_id:
            return uuid.UUID(current_user_id)
        return None
    except Exception:
        # 如果无法获取用户ID，返回默认值或抛出异常
        # 在迁移等场景下，可能没有JWT上下文
        return uuid.uuid4()  # 返回一个默认UUID


def get_current_tenant_id():
    """获取当前租户ID"""
    try:
        from flask_jwt_extended import get_jwt
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        if tenant_id:
            return uuid.UUID(tenant_id)
        return None
    except Exception:
        return None 