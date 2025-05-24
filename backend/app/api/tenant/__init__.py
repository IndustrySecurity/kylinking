from flask import Blueprint

tenant_bp = Blueprint('tenant', __name__)

from app.api.tenant import routes 
from app.api.tenant import modules
from app.api.tenant import basic_data

# 注册模块管理相关的路由
tenant_bp.register_blueprint(modules.bp)

# 注册基础档案管理相关的路由
tenant_bp.register_blueprint(basic_data.bp, url_prefix='/basic-data') 