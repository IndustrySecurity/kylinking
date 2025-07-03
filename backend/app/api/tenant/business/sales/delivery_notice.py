# -*- coding: utf-8 -*-
# type: ignore
# pyright: reportGeneralTypeIssues=false
# pyright: reportAttributeAccessIssue=false
# pyright: reportOptionalMemberAccess=false
"""
送货通知管理API路由
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.tenant.routes import tenant_required
from app.services import DeliveryNoticeService

bp = Blueprint('delivery_notice', __name__)


@bp.route('/delivery-notices', methods=['GET'])
@jwt_required()
@tenant_required
def get_delivery_notices():
    """获取送货通知列表"""
    try:
        # 创建服务实例
        delivery_notice_service = DeliveryNoticeService()
        
        # 获取查询参数
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        
        # 构建过滤条件
        filters = {}
        if request.args.get('sales_order_id'):
            filters['sales_order_id'] = request.args.get('sales_order_id')
        if request.args.get('customer_id'):
            filters['customer_id'] = request.args.get('customer_id')
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        if request.args.get('start_date'):
            filters['start_date'] = datetime.fromisoformat(request.args.get('start_date'))
        if request.args.get('end_date'):
            filters['end_date'] = datetime.fromisoformat(request.args.get('end_date'))
        
        result = delivery_notice_service.get_delivery_notice_list(
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


@bp.route('/delivery-notices', methods=['POST'])
@jwt_required()
@tenant_required
def create_delivery_notice():
    """创建送货通知"""
    try:
        # 创建服务实例
        delivery_notice_service = DeliveryNoticeService()
        
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('sales_order_id'):
            return jsonify({'error': '销售订单ID不能为空'}), 400
        
        # 处理日期字段
        if data.get('delivery_date'):
            data['delivery_date'] = datetime.fromisoformat(data['delivery_date'].replace('Z', '+00:00'))
        
        user_id = get_jwt_identity()
        result = delivery_notice_service.create_delivery_notice(
            notice_data=data,
            user_id=user_id
        )
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '送货通知创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'创建失败: {str(e)}'}), 500


@bp.route('/delivery-notices/<notice_id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_delivery_notice_detail(notice_id):
    """获取送货通知详情"""
    try:
        # 创建服务实例
        delivery_notice_service = DeliveryNoticeService()
        
        result = delivery_notice_service.get_delivery_notice_detail(notice_id=notice_id)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/delivery-notices/<notice_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_delivery_notice(notice_id):
    """更新送货通知"""
    try:
        # 创建服务实例
        delivery_notice_service = DeliveryNoticeService()
        
        data = request.get_json()
        
        # 处理日期字段
        if data.get('delivery_date'):
            data['delivery_date'] = datetime.fromisoformat(data['delivery_date'].replace('Z', '+00:00'))
        
        user_id = get_jwt_identity()
        result = delivery_notice_service.update_delivery_notice(
            notice_id=notice_id,
            notice_data=data,
            user_id=user_id
        )
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '送货通知更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'更新失败: {str(e)}'}), 500


@bp.route('/delivery-notices/<notice_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_delivery_notice(notice_id):
    """删除送货通知"""
    try:
        # 创建服务实例
        delivery_notice_service = DeliveryNoticeService()
        
        user_id = get_jwt_identity()
        success = delivery_notice_service.delete_delivery_notice(
            notice_id=notice_id,
            user_id=user_id
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': '送货通知删除成功'
            })
        else:
            return jsonify({'error': '删除失败'}), 500
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'删除失败: {str(e)}'}), 500


@bp.route('/delivery-notices/<notice_id>/confirm', methods=['POST'])
@jwt_required()
@tenant_required
def confirm_delivery_notice(notice_id):
    """确认送货通知"""
    try:
        # 创建服务实例
        delivery_notice_service = DeliveryNoticeService()
        
        user_id = get_jwt_identity()
        result = delivery_notice_service.confirm_delivery_notice(
            notice_id=notice_id,
            user_id=user_id
        )
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '送货通知已确认'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'确认失败: {str(e)}'}), 500


@bp.route('/delivery-notices/<notice_id>/ship', methods=['POST'])
@jwt_required()
@tenant_required
def ship_delivery_notice(notice_id):
    """发货"""
    try:
        # 创建服务实例
        delivery_notice_service = DeliveryNoticeService()
        
        data = request.get_json()
        tracking_number = data.get('tracking_number') if data else None
        
        user_id = get_jwt_identity()
        result = delivery_notice_service.ship_delivery_notice(
            notice_id=notice_id,
            user_id=user_id,
            tracking_number=tracking_number
        )
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '发货成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'发货失败: {str(e)}'}), 500


@bp.route('/delivery-notices/<notice_id>/complete', methods=['POST'])
@jwt_required()
@tenant_required
def complete_delivery_notice(notice_id):
    """完成送货"""
    try:
        # 创建服务实例
        delivery_notice_service = DeliveryNoticeService()
        
        user_id = get_jwt_identity()
        result = delivery_notice_service.complete_delivery_notice(
            notice_id=notice_id,
            user_id=user_id
        )
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '送货已完成'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'完成失败: {str(e)}'}), 500 