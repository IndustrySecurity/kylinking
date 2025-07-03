"""
产品入库管理 API

提供产品入库的完整管理功能：
- 产品入库列表查询和创建
- 产品入库详情获取和更新
- 产品入库删除和状态管理
- 产品入库审核、执行、取消流程
- 产品入库明细管理
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.api.tenant.routes import tenant_required
import logging

# 设置蓝图
bp = Blueprint('product_inbound', __name__)
logger = logging.getLogger(__name__)

# ==================== 产品入库管理 ====================

@bp.route('/product-inbound-orders', methods=['GET'])
@jwt_required()
@tenant_required
def get_product_inbound_orders():
    """获取产品入库单列表"""
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        page_size = min(int(request.args.get('page_size', 20)), 100)
        order_number = request.args.get('order_number')
        warehouse_id = request.args.get('warehouse_id')
        supplier_id = request.args.get('supplier_id')
        status = request.args.get('status')
        approval_status = request.args.get('approval_status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 获取当前用户和租户信息
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        if not tenant_id:
            return jsonify({'error': '租户信息缺失'}), 400
        
        # 获取产品入库单列表
        from app.services.business.inventory.product_inbound_service import ProductInboundService
        service = ProductInboundService()
        result = service.get_product_inbound_order_list(
            warehouse_id=warehouse_id,
            status=status,
            approval_status=approval_status,
            start_date=start_date,
            end_date=end_date,
            search=order_number,
            page=page,
            page_size=page_size
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f"获取产品入库单列表失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/product-inbound-orders/<order_id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_product_inbound_order(order_id):
    """获取产品入库单详情"""
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        from app.services.business.inventory.product_inbound_service import ProductInboundService
        service = ProductInboundService()
        order = service.get_product_inbound_order_by_id(order_id)
        
        if not order:
            return jsonify({'error': '产品入库单不存在'}), 404
        
        return jsonify({
            'success': True,
            'data': order
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"获取产品入库单详情失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/product-inbound-orders', methods=['POST'])
@jwt_required()
@tenant_required
def create_product_inbound_order():
    """创建产品入库单"""
    try:
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        if not data.get('warehouse_id'):
            return jsonify({'error': '仓库ID不能为空'}), 400
        
        from app.services.business.inventory.product_inbound_service import ProductInboundService
        service = ProductInboundService()
        order = service.create_product_inbound_order(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': order,
            'message': '产品入库单创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"创建产品入库单失败: {str(e)}")
        return jsonify({'error': str(e)}), 500
