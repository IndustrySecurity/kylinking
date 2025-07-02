# -*- coding: utf-8 -*-
"""
通用装饰器模块
"""

from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt


def tenant_required(fn):
    """
    装饰器，确保用户有对应的租户
    """
    @jwt_required()
    @wraps(fn)  # 添加functools.wraps保留原始函数名称
    def tenant_wrapper(*args, **kwargs):
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        if not tenant_id:
            return jsonify({"message": "No tenant associated with user"}), 403
        
        return fn(*args, **kwargs)
    
    return tenant_wrapper 