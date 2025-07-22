import os
from flask import Flask, jsonify
from flask_cors import CORS

from app.config import config_by_name
from app.extensions import db, jwt, migrate
from app.middleware.tenant_middleware import TenantMiddleware


def create_app(config_name="development"):
    """
    创建Flask应用实例
    :param config_name: 配置名称
    :return: Flask实例
    """
    app = Flask(__name__)
    
    # 加载配置
    app_config = config_by_name[config_name]
    app.config.from_object(app_config)
    
    # 初始化扩展
    initialize_extensions(app)
    
    # 注册中间件
    register_middleware(app)
    
    # 注册蓝图
    register_blueprints(app)
    
    # 注册错误处理器
    register_error_handlers(app)
    
    # 启用CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # 创建一个基本路由用于健康检查
    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({"status": "healthy"})
    
    return app


def initialize_extensions(app):
    """
    初始化扩展
    :param app: Flask实例
    """
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)


def register_middleware(app):
    """
    注册中间件
    :param app: Flask实例
    """
    app.wsgi_app = TenantMiddleware(app.wsgi_app, app)


def register_blueprints(app):
    """
    注册蓝图
    :param app: Flask实例
    """
    from app.api.auth import auth_bp
    from app.api.admin import admin_bp
    from app.api.tenant import tenant_bp
    from app.api.system import system_bp
    
    # 简化注册，让各个蓝图内部自己处理子蓝图
    try:
        # 只注册主要蓝图
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        app.register_blueprint(admin_bp, url_prefix='/api/admin')
        app.register_blueprint(tenant_bp, url_prefix='/api/tenant')
        app.register_blueprint(system_bp, url_prefix='/api/system')
        
        print("✅ 主要蓝图注册成功")
        
    except Exception as e:
        print(f"❌ 蓝图注册失败: {e}")
        raise


def register_error_handlers(app):
    """
    注册错误处理器
    :param app: Flask实例
    """
    @app.errorhandler(404)
    def handle_404_error(error):
        return jsonify({"error": "Resource not found"}), 404
    
    @app.errorhandler(400)
    def handle_400_error(error):
        return jsonify({"error": str(error)}), 400
    
    @app.errorhandler(500)
    def handle_500_error(error):
        return jsonify({"error": "Internal server error"}), 500 