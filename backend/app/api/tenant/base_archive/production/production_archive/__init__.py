# -*- coding: utf-8 -*-
"""
生产档案API模块初始化
"""

from flask import Blueprint

# 创建生产档案主蓝图
production_archive_bp = Blueprint('production_archive', __name__)

# 导入各个API模块
from .bag_type import bp as bag_type_bp
from .warehouse import bp as warehouse_bp  
from .process import bp as process_bp
from .package_method import bp as package_method_bp
from .color_card import bp as color_card_bp
from .delivery_method import bp as delivery_method_bp
from .unit import bp as unit_bp
from .specification import bp as specification_bp
from .loss_type import bp as loss_type_bp

# 注册各个API蓝图
production_archive_bp.register_blueprint(bag_type_bp, url_prefix='/bag-types')
production_archive_bp.register_blueprint(warehouse_bp, url_prefix='/warehouses')
production_archive_bp.register_blueprint(process_bp, url_prefix='/processes')
production_archive_bp.register_blueprint(package_method_bp, url_prefix='/package-methods')
production_archive_bp.register_blueprint(color_card_bp, url_prefix='/color-cards')
production_archive_bp.register_blueprint(delivery_method_bp, url_prefix='/delivery-methods')
production_archive_bp.register_blueprint(unit_bp, url_prefix='/units')
production_archive_bp.register_blueprint(specification_bp, url_prefix='/specifications')
production_archive_bp.register_blueprint(loss_type_bp, url_prefix='/loss-types') 