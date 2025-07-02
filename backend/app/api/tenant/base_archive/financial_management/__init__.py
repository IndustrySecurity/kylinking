# -*- coding: utf-8 -*-
"""
财务管理模块API
包含币别、税率、账户管理等财务相关功能
"""

from flask import Blueprint

# 创建财务管理模块主蓝图
financial_management_bp = Blueprint('financial_management', __name__)

# ==================== 财务基础数据 ====================
from .currency import bp as currency_bp
from .tax_rate import bp as tax_rate_bp
from .account_management import bp as account_management_bp
from .payment_method import bp as payment_method_bp
from .settlement_method import bp as settlement_method_bp

# 注册各个API蓝图
financial_management_bp.register_blueprint(currency_bp, url_prefix='/currencies')
financial_management_bp.register_blueprint(tax_rate_bp, url_prefix='/tax-rates')
financial_management_bp.register_blueprint(account_management_bp, url_prefix='/account-management')
financial_management_bp.register_blueprint(payment_method_bp, url_prefix='/payment-methods')
financial_management_bp.register_blueprint(settlement_method_bp, url_prefix='/settlement-methods')

@financial_management_bp.route('/health', methods=['GET'])
def health_check():
    """财务管理模块健康检查"""
    return {
        'status': 'ok',
        'message': '财务管理模块API运行正常',
        'modules': [
            'currencies',         # 币别管理
            'tax_rates',         # 税率管理
            'account_management', # 账户管理
            'payment_methods',    # 付款方式管理
            'settlement_methods'  # 结算方式管理
        ]
    } 