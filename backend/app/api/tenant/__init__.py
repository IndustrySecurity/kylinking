from flask import Blueprint

tenant_bp = Blueprint('tenant', __name__)

from app.api.tenant import routes
from app.api.tenant import modules

# 注册模块管理相关的路由
tenant_bp.register_blueprint(modules.bp) 