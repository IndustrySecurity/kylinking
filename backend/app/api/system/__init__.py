from flask import Blueprint

# 创建系统主蓝图
system_bp = Blueprint('system', __name__)

@system_bp.route('/health', methods=['GET'])
def system_health():
    """系统API健康检查"""
    return {
        'status': 'ok',
        'message': '系统API模块运行正常',
        'modules': ['column_configuration']
    }

# 注册子蓝图
try:
    from .column_configuration import column_config_bp
    
    # 注册子蓝图
    system_bp.register_blueprint(column_config_bp, url_prefix='/column-config')
    
    print("✅ 系统子蓝图注册成功")
    
except Exception as e:
    print(f"❌ 系统子蓝图注册失败: {e}")

# 为统一导入方式提供别名
bp = system_bp 