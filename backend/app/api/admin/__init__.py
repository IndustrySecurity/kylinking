from flask import Blueprint

admin_bp = Blueprint('admin', __name__)

from app.api.admin import routes 
from app.api.admin import modules
from app.api.admin import organizations

# 注册模块管理相关的路由
admin_bp.register_blueprint(modules.bp, url_prefix='/modules')

# 注册组织管理相关的路由
admin_bp.register_blueprint(organizations.bp, url_prefix='') 