from flask import Blueprint

tenant_bp = Blueprint('tenant', __name__)

from app.api.tenant import routes 
from app.api.tenant import modules
from app.api.tenant import basic_data
from app.api.tenant import inventory
from app.api.tenant import sales

# 注册模块管理相关的路由
tenant_bp.register_blueprint(modules.bp)

# 注册基础档案管理相关的路由
tenant_bp.register_blueprint(basic_data.bp, url_prefix='/basic-data')

# 注册库存管理相关的路由
tenant_bp.register_blueprint(inventory.bp, url_prefix='/inventory') 

# 注册销售管理相关的路由
tenant_bp.register_blueprint(sales.sales_bp, url_prefix='/sales') 