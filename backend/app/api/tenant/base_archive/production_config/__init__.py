# -*- coding: utf-8 -*-
"""
生产配置模块API
包含计算参数、计算方案、油墨选项、报价运费等生产配置功能
"""

from flask import Blueprint

# 创建生产配置模块主蓝图
production_config_bp = Blueprint('production_config', __name__)

# ==================== 计算配置 ====================
from .calculation_parameter import bp as calculation_parameter_bp
from .calculation_scheme import bp as calculation_scheme_bp

# ==================== 油墨配置 ====================
from .ink_option import bp as ink_option_bp

# ==================== 报价配置 ====================
from .quote_freight import bp as quote_freight_bp
from .quote_ink import bp as quote_ink_bp
from .quote_material import bp as quote_material_bp
from .quote_accessory import bp as quote_accessory_bp
from .quote_loss import bp as quote_loss_bp
from .bag_related_formula import bp as bag_related_formula_bp

# 注册各个API蓝图
production_config_bp.register_blueprint(calculation_parameter_bp, url_prefix='/calculation-parameters')
production_config_bp.register_blueprint(calculation_scheme_bp, url_prefix='/calculation-schemes')
production_config_bp.register_blueprint(ink_option_bp, url_prefix='/ink-options')
production_config_bp.register_blueprint(quote_freight_bp, url_prefix='/quote-freights')
production_config_bp.register_blueprint(quote_ink_bp, url_prefix='/quote-inks')
production_config_bp.register_blueprint(quote_material_bp, url_prefix='/quote-materials')
production_config_bp.register_blueprint(quote_accessory_bp, url_prefix='/quote-accessories')
production_config_bp.register_blueprint(quote_loss_bp, url_prefix='/quote-losses')
production_config_bp.register_blueprint(bag_related_formula_bp, url_prefix='/bag-related-formulas')

@production_config_bp.route('/health', methods=['GET'])
def health_check():
    """生产配置模块健康检查"""
    return {
        'status': 'ok',
        'message': '生产配置模块API运行正常',
        'modules': [
            'calculation_parameters',  # 计算参数
            'calculation_schemes',     # 计算方案
            'ink_options',            # 油墨选项
            'quote_freights',         # 报价运费
            'quote_inks',             # 报价油墨
            'quote_materials',        # 报价材料
            'quote_accessories',      # 报价配件
            'quote_losses',           # 报价损耗
            'bag_related_formulas'    # 袋型相关公式
        ]
    } 