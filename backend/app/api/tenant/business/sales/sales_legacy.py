"""
销售订单相关API (Legacy版本 - 待移除)
"""
from flask import Blueprint, request, jsonify, g
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.api.tenant.routes import tenant_required
from app.services import (
    CustomerService,
    DeliveryNoticeService,
    InventoryService,
    MaterialService,
    SalesOrderService,
    TaxRateService
)

sales_legacy_bp = Blueprint('sales_legacy', __name__)

# 服务实例将在每个请求中动态创建，以确保正确的租户上下文


@sales_legacy_bp.route('/sales-orders', methods=['GET'])
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
            filters['start_date'] = datetime.fromisoformat(request.args.get('start_date'))
        if request.args.get('end_date'):
            filters['end_date'] = datetime.fromisoformat(request.args.get('end_date'))
        
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


@sales_legacy_bp.route('/sales-orders', methods=['POST'])
@jwt_required()
@tenant_required
def create_sales_order():
    """创建销售订单"""
    try:
        # 创建服务实例
        sales_order_service = SalesOrderService()
        
        data = request.get_json()
        
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


@sales_legacy_bp.route('/sales-orders/<order_id>', methods=['GET'])
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


@sales_legacy_bp.route('/sales-orders/<order_id>', methods=['PUT'])
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


@sales_legacy_bp.route('/sales-orders/<order_id>', methods=['DELETE'])
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


@sales_legacy_bp.route('/sales-orders/<order_id>/approve', methods=['POST'])
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


@sales_legacy_bp.route('/sales-orders/<order_id>/cancel', methods=['POST'])
@jwt_required()
@tenant_required
def cancel_sales_order(order_id):
    """取消销售订单"""
    try:
        # 创建服务实例
        sales_order_service = SalesOrderService()
        
        data = request.get_json()
        reason = data.get('reason') if data else None
        
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


@sales_legacy_bp.route('/sales-orders/<order_id>/calculate-total', methods=['GET'])
@jwt_required()
@tenant_required
def calculate_order_total(order_id):
    """计算订单总额"""
    try:
        # 创建服务实例
        sales_order_service = SalesOrderService()
        
        result = sales_order_service.calculate_order_total(order_id=order_id)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@sales_legacy_bp.route('/sales-orders/statistics', methods=['GET'])
@jwt_required()
@tenant_required
def get_order_statistics():
    """获取订单统计"""
    try:
        # 创建服务实例
        sales_order_service = SalesOrderService()
        
        # 获取查询参数
        filters = {}
        if request.args.get('start_date'):
            filters['start_date'] = datetime.fromisoformat(request.args.get('start_date'))
        if request.args.get('end_date'):
            filters['end_date'] = datetime.fromisoformat(request.args.get('end_date'))
        
        result = sales_order_service.get_order_statistics(filters=filters)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@sales_legacy_bp.route('/customers/options', methods=['GET'])
@jwt_required()
@tenant_required
def get_customer_options():
    """获取客户选项"""
    try:
        # 创建服务实例
        customer_service = CustomerService()
        
        result = customer_service.get_customer_options()
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@sales_legacy_bp.route('/products/options', methods=['GET'])
@jwt_required()
@tenant_required
def get_product_options():
    """获取产品选项"""
    try:
        # 使用现有的服务获取产品选项
        from app.services.base_archive.base_data.product_management_service import ProductManagementService
        product_service = ProductManagementService()
        
        result = product_service.get_product_options()
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@sales_legacy_bp.route('/materials/options', methods=['GET'])
@jwt_required()
@tenant_required
def get_material_options():
    """获取材料选项"""
    try:
        # 创建服务实例
        material_service = MaterialService()
        
        result = material_service.get_material_options()
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@sales_legacy_bp.route('/products/<product_id>/inventory', methods=['GET'])
@jwt_required()
@tenant_required
def get_product_inventory(product_id):
    """获取产品库存信息"""
    try:
        # 创建服务实例
        inventory_service = InventoryService()
        
        result = inventory_service.get_product_inventory(product_id=product_id)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@sales_legacy_bp.route('/taxes/options', methods=['GET'])
@jwt_required()
@tenant_required
def get_tax_options():
    """获取税率选项"""
    try:
        # 创建服务实例
        tax_rate_service = TaxRateService()
        
        result = tax_rate_service.get_tax_rate_options()
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@sales_legacy_bp.route('/customers/<customer_id>/details', methods=['GET'])
@jwt_required()
@tenant_required
def get_customer_details(customer_id):
    """获取客户详情"""
    try:
        # 创建服务实例
        customer_service = CustomerService()
        
        result = customer_service.get_customer_details(customer_id=customer_id)
        
        if not result:
            return jsonify({'error': '客户不存在'}), 404
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@sales_legacy_bp.route('/customers/<customer_id>/contacts', methods=['GET'])
@jwt_required()
@tenant_required
def get_customer_contacts(customer_id):
    """获取客户联系人"""
    try:
        # 创建服务实例
        customer_service = CustomerService()
        
        result = customer_service.get_customer_contacts(customer_id=customer_id)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@sales_legacy_bp.route('/products/<product_id>/details', methods=['GET'])
@jwt_required()
@tenant_required
def get_product_details(product_id):
    """获取产品详情"""
    try:
        # 使用现有的服务获取产品详情
        from app.services.base_archive.base_data.product_management_service import ProductManagementService
        product_service = ProductManagementService()
        
        result = product_service.get_product_details(product_id=product_id)
        
        if not result:
            return jsonify({'error': '产品不存在'}), 404
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@sales_legacy_bp.route('/delivery-notices', methods=['GET'])
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


@sales_legacy_bp.route('/delivery-notices', methods=['POST'])
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


@sales_legacy_bp.route('/delivery-notices/<notice_id>', methods=['GET'])
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


@sales_legacy_bp.route('/delivery-notices/<notice_id>', methods=['PUT'])
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


@sales_legacy_bp.route('/delivery-notices/<notice_id>', methods=['DELETE'])
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


@sales_legacy_bp.route('/delivery-notices/<notice_id>/confirm', methods=['POST'])
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
            'message': '送货通知确认成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'确认失败: {str(e)}'}), 500


@sales_legacy_bp.route('/delivery-notices/<notice_id>/ship', methods=['POST'])
@jwt_required()
@tenant_required
def ship_delivery_notice(notice_id):
    """发货送货通知"""
    try:
        # 创建服务实例
        delivery_notice_service = DeliveryNoticeService()
        
        data = request.get_json()
        shipping_info = data.get('shipping_info') if data else {}
        
        user_id = get_jwt_identity()
        result = delivery_notice_service.ship_delivery_notice(
            notice_id=notice_id,
            user_id=user_id,
            shipping_info=shipping_info
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


@sales_legacy_bp.route('/delivery-notices/<notice_id>/complete', methods=['POST'])
@jwt_required()
@tenant_required
def complete_delivery_notice(notice_id):
    """完成送货通知"""
    try:
        # 创建服务实例
        delivery_notice_service = DeliveryNoticeService()
        
        data = request.get_json()
        completion_info = data.get('completion_info') if data else {}
        
        user_id = get_jwt_identity()
        result = delivery_notice_service.complete_delivery_notice(
            notice_id=notice_id,
            user_id=user_id,
            completion_info=completion_info
        )
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '送货完成'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'完成失败: {str(e)}'}), 500 