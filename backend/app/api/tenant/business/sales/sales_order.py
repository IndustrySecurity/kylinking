# -*- coding: utf-8 -*-
"""
销售订单管理API路由
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.tenant.routes import tenant_required
from app.services import (
    CustomerService,
    SalesOrderService
)
from app.models.business.sales import SalesOrder

bp = Blueprint('sales_order', __name__)


@bp.route('/sales-orders', methods=['GET'])
@jwt_required()
@tenant_required
def get_sales_orders():
    """获取销售订单列表"""
    try:
        # 创建服务实例
        sales_order_service = SalesOrderService()
        
        # 获取查询参数
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        
        # 构建过滤条件
        filters = {}
        if request.args.get('order_number'):
            filters['order_number'] = request.args.get('order_number')
        if request.args.get('customer_id'):
            filters['customer_id'] = request.args.get('customer_id')
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        if request.args.get('salesperson_id'):
            filters['salesperson_id'] = request.args.get('salesperson_id')
        if request.args.get('start_date'):
            start_date = request.args.get('start_date')
            if start_date:
                filters['start_date'] = datetime.fromisoformat(start_date)
        if request.args.get('end_date'):
            end_date = request.args.get('end_date')
            if end_date:
                filters['end_date'] = datetime.fromisoformat(end_date)
        
        result = sales_order_service.get_sales_order_list(
            page=page,
            page_size=page_size,
            filters=filters
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/sales-orders', methods=['POST'])
@jwt_required()
@tenant_required
def create_sales_order():
    """创建销售订单"""
    try:
        # 创建服务实例
        sales_order_service = SalesOrderService()
        
        data = request.get_json()
        
        if not data.get('order_number'):
            data['order_number'] = SalesOrder.generate_order_number()

        # 验证必填字段
        if not data.get('customer_id'):
            return jsonify({'error': '客户ID不能为空'}), 400

        # 处理日期字段
        if data.get('order_date'):
            data['order_date'] = datetime.fromisoformat(data['order_date'].replace('Z', '+00:00'))
        if data.get('internal_delivery_date'):
            data['internal_delivery_date'] = datetime.fromisoformat(data['internal_delivery_date'].replace('Z', '+00:00'))
        if data.get('contract_date'):
            data['contract_date'] = datetime.fromisoformat(data['contract_date'].replace('Z', '+00:00'))
        
        user_id = get_jwt_identity()
        result = sales_order_service.create_sales_order(
            order_data=data,
            user_id=user_id
        )
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '销售订单创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'创建失败: {str(e)}'}), 500


@bp.route('/sales-orders/<order_id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_sales_order_detail(order_id):
    """获取销售订单详情"""
    try:
        # 创建服务实例
        sales_order_service = SalesOrderService()
        
        result = sales_order_service.get_sales_order_detail(order_id=order_id)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/sales-orders/<order_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_sales_order(order_id):
    """更新销售订单"""
    try:
        # 创建服务实例
        sales_order_service = SalesOrderService()
        
        data = request.get_json()
        
        # 处理日期字段
        if data.get('order_date'):
            data['order_date'] = datetime.fromisoformat(data['order_date'].replace('Z', '+00:00'))
        if data.get('internal_delivery_date'):
            data['internal_delivery_date'] = datetime.fromisoformat(data['internal_delivery_date'].replace('Z', '+00:00'))
        if data.get('contract_date'):
            data['contract_date'] = datetime.fromisoformat(data['contract_date'].replace('Z', '+00:00'))
        
        user_id = get_jwt_identity()
        result = sales_order_service.update_sales_order(
            order_id=order_id,
            order_data=data,
            user_id=user_id
        )
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '销售订单更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'更新失败: {str(e)}'}), 500


@bp.route('/sales-orders/<order_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_sales_order(order_id):
    """删除销售订单"""
    try:
        # 创建服务实例
        sales_order_service = SalesOrderService()
        
        user_id = get_jwt_identity()
        success = sales_order_service.delete_sales_order(
            order_id=order_id,
            user_id=user_id
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': '销售订单删除成功'
            })
        else:
            return jsonify({'error': '删除失败'}), 500
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'删除失败: {str(e)}'}), 500


@bp.route('/sales-orders/<order_id>/approve', methods=['POST'])
@jwt_required()
@tenant_required
def approve_sales_order(order_id):
    """审批销售订单"""
    try:
        # 创建服务实例
        sales_order_service = SalesOrderService()
        
        user_id = get_jwt_identity()
        result = sales_order_service.approve_sales_order(
            order_id=order_id,
            user_id=user_id
        )
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '销售订单审批成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'审批失败: {str(e)}'}), 500


@bp.route('/sales-orders/<order_id>/cancel', methods=['POST'])
@jwt_required()
@tenant_required
def cancel_sales_order(order_id):
    """取消销售订单"""
    try:
        # 创建服务实例
        sales_order_service = SalesOrderService()
        
        data = request.get_json() or {}
        reason = data.get('reason', '')
        
        user_id = get_jwt_identity()
        result = sales_order_service.cancel_sales_order(
            order_id=order_id,
            user_id=user_id,
            reason=reason
        )
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '销售订单已取消'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'取消失败: {str(e)}'}), 500



# ==================== 获取未全部安排发货的销售订单选项 ====================

@bp.route('/sales-orders/unscheduled-options', methods=['GET'])
@jwt_required()
@tenant_required
def get_unscheduled_sales_order_options():
    """按客户筛选，仅返回还有未安排发货产品的销售订单(剩余数量>0)"""
    try:
        customer_id = request.args.get('customer_id')
        if not customer_id:
            return jsonify({'success': True, 'data': []})

        from sqlalchemy.orm import joinedload
        from app.models.business.sales import SalesOrder, SalesOrderDetail
        from app.extensions import db

        query = db.session.query(SalesOrder).options(joinedload(SalesOrder.order_details))\
            .filter(SalesOrder.customer_id == customer_id)

        results = []
        for order in query.all():
            remaining = 0
            for d in order.order_details:
                remaining += max((d.order_quantity or 0) - (d.scheduled_delivery_quantity or 0), 0)
            if remaining > 0:
                results.append({
                    'value': str(order.id),
                    'label': f"{order.order_number}",
                    'remaining_quantity': float(remaining)
                })

        return jsonify({'success': True, 'data': results})
    except Exception as e:
        print(f"获取未安排销售订单选项失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500 