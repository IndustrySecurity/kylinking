"""
产品盘点管理 API

提供产品盘点的完整管理功能：
- 产品盘点计划列表查询和创建
- 产品盘点计划详情获取和删除
- 产品盘点记录管理
- 产品盘点流程控制（开始、完成）
- 产品盘点库存调整
- 产品盘点统计分析
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.tenant.routes import tenant_required
from app.services.business.inventory.product_count_service import ProductCountService
import logging

# 设置蓝图
bp = Blueprint('product_count', __name__)
logger = logging.getLogger(__name__)

# ==================== 产品盘点计划管理 ====================

@bp.route('/product-count-plans', methods=['GET'])
@jwt_required()
@tenant_required
def get_product_count_plans():
    """获取成品盘点计划列表"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        
        # 筛选条件
        filters = {}
        if request.args.get('warehouse_id'):
            filters['warehouse_id'] = request.args.get('warehouse_id')
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        if request.args.get('count_person_id'):
            filters['count_person_id'] = request.args.get('count_person_id')
        if request.args.get('start_date'):
            filters['start_date'] = request.args.get('start_date')
        if request.args.get('end_date'):
            filters['end_date'] = request.args.get('end_date')
        if request.args.get('search'):
            filters['search'] = request.args.get('search')
        
        productcount_service = ProductCountService()
        result = productcount_service.get_count_plans(page, page_size, **filters)
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f"获取成品盘点计划列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"获取盘点计划列表失败: {str(e)}"
        }), 500


@bp.route('/product-count-plans', methods=['POST'])
@jwt_required()
@tenant_required
def create_product_count_plan():
    """创建成品盘点计划"""
    try:
        data = request.get_json()
        
        # 验证必需字段
        required_fields = ['warehouse_id', 'count_person_id', 'count_date']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'message': f'缺少必需字段: {field}'
                }), 400
        
        user_id = get_jwt_identity()
        productcount_service = ProductCountService()
        result = productcount_service.create_count_plan(data, user_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '盘点计划创建成功'
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"创建成品盘点计划失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"创建盘点计划失败: {str(e)}"
        }), 500


@bp.route('/product-count-plans/<plan_id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_product_count_plan(plan_id):
    """获取成品盘点计划详情"""
    try:
        productcount_service = ProductCountService()
        result = productcount_service.get_count_plan(plan_id)
        return jsonify({
            'success': True,
            'data': result
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 404
    except Exception as e:
        logger.error(f"获取成品盘点计划详情失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"获取盘点计划详情失败: {str(e)}"
        }), 500


@bp.route('/product-count-plans/<plan_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_product_count_plan(plan_id):
    """删除成品盘点计划"""
    try:
        user_id = get_jwt_identity()
        productcount_service = ProductCountService()
        result = productcount_service.delete_count_plan(plan_id, user_id)
        
        return jsonify({
            'success': True,
            'data': {"deleted": result},
            'message': '盘点计划删除成功'
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"删除成品盘点计划失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"删除盘点计划失败: {str(e)}"
        }), 500


# ==================== 产品盘点记录管理 ====================

@bp.route('/product-count-plans/<plan_id>/records', methods=['GET'])
@jwt_required()
@tenant_required
def get_product_count_records(plan_id):
    """获取成品盘点记录列表"""
    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 50, type=int)
        
        productcount_service = ProductCountService()
        result = productcount_service.get_count_records(plan_id, page, page_size)
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f"获取成品盘点记录失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"获取盘点记录失败: {str(e)}"
        }), 500


@bp.route('/product-count-plans/<plan_id>/records/<record_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_product_count_record(plan_id, record_id):
    """更新成品盘点记录"""
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        
        productcount_service = ProductCountService()
        result = productcount_service.update_count_record(plan_id, record_id, data, user_id)
        return jsonify({
            'success': True,
            'data': result,
            'message': '盘点记录更新成功'
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"更新成品盘点记录失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"更新盘点记录失败: {str(e)}"
        }), 500


# ==================== 产品盘点流程控制 ====================

@bp.route('/product-count-plans/<plan_id>/start', methods=['POST'])
@jwt_required()
@tenant_required
def start_product_count_plan(plan_id):
    """开始成品盘点计划"""
    try:
        user_id = get_jwt_identity()
        productcount_service = ProductCountService()
        result = productcount_service.start_count_plan(plan_id, user_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '盘点计划已开始'
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"开始成品盘点计划失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"开始盘点计划失败: {str(e)}"
        }), 500


@bp.route('/product-count-plans/<plan_id>/complete', methods=['POST'])
@jwt_required()
@tenant_required
def complete_product_count_plan(plan_id):
    """完成成品盘点计划"""
    try:
        user_id = get_jwt_identity()
        productcount_service = ProductCountService()
        result = productcount_service.complete_count_plan(plan_id, user_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '盘点计划已完成'
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"完成成品盘点计划失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"完成盘点计划失败: {str(e)}"
        }), 500


# ==================== 产品盘点库存调整 ====================

@bp.route('/product-count-plans/<plan_id>/adjust', methods=['POST'])
@jwt_required()
@tenant_required
def adjust_product_inventory(plan_id):
    """根据成品盘点结果调整库存"""
    try:
        data = request.get_json() or {}
        record_ids = data.get('record_ids', [])
        
        user_id = get_jwt_identity()
        productcount_service = ProductCountService()
        result = productcount_service.adjust_inventory(plan_id, record_ids, user_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': result.get('message', '库存调整成功')
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"调整成品库存失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"调整库存失败: {str(e)}"
        }), 500


# ==================== 产品盘点统计和分析 ====================

@bp.route('/product-count-plans/<plan_id>/statistics', methods=['GET'])
@jwt_required()
@tenant_required
def get_product_count_statistics(plan_id):
    """获取成品盘点统计信息"""
    try:
        productcount_service = ProductCountService()
        result = productcount_service.get_count_statistics(plan_id)
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f"获取成品盘点统计信息失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"获取统计信息失败: {str(e)}"
        }), 500


@bp.route('/warehouses/<warehouse_id>/product-inventory', methods=['GET'])
@jwt_required()
@tenant_required
def get_warehouse_product_inventory(warehouse_id):
    """获取仓库成品库存"""
    try:
        productcount_service = ProductCountService()
        result = productcount_service.get_warehouse_product_inventory(warehouse_id)
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f"获取仓库成品库存失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"获取成品库存失败: {str(e)}"
        }), 500 