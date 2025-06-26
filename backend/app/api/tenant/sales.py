"""
销售订单相关API
"""
from flask import Blueprint, request, jsonify, g
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from .routes import tenant_required
from app.services.sales_order_service import SalesOrderService
from app.services.customer_service import CustomerService
from app.services.basic_data_service import BasicDataService

sales_bp = Blueprint('sales', __name__)

# 创建服务实例
sales_order_service = SalesOrderService()
customer_service = CustomerService()
basic_data_service = BasicDataService()


@sales_bp.route('/sales-orders', methods=['GET'])
@jwt_required()
@tenant_required
def get_sales_orders():
    """获取销售订单列表"""
    try:
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


@sales_bp.route('/sales-orders', methods=['POST'])
@jwt_required()
@tenant_required
def create_sales_order():
    """创建销售订单"""
    try:
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
        
        result = sales_order_service.create_sales_order(
            user_id=g.user_id,
            order_data=data
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


@sales_bp.route('/sales-orders/<order_id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_sales_order_detail(order_id):
    """获取销售订单详情"""
    try:
        result = sales_order_service.get_sales_order_detail(order_id=order_id)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@sales_bp.route('/sales-orders/<order_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_sales_order(order_id):
    """更新销售订单"""
    try:
        data = request.get_json()
        
        # 处理日期字段
        if data.get('order_date'):
            data['order_date'] = datetime.fromisoformat(data['order_date'].replace('Z', '+00:00'))
        if data.get('internal_delivery_date'):
            data['internal_delivery_date'] = datetime.fromisoformat(data['internal_delivery_date'].replace('Z', '+00:00'))
        if data.get('contract_date'):
            data['contract_date'] = datetime.fromisoformat(data['contract_date'].replace('Z', '+00:00'))
        
        result = sales_order_service.update_sales_order(
            user_id=g.user_id,
            order_id=order_id,
            order_data=data
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


@sales_bp.route('/sales-orders/<order_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_sales_order(order_id):
    """删除销售订单"""
    try:
        # 由于服务类没有 delete_by_id 方法，我们需要先获取订单然后删除
        # 这里暂时返回未实现的错误
        return jsonify({'error': '删除功能暂未实现'}), 501
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'删除失败: {str(e)}'}), 500


@sales_bp.route('/sales-orders/<order_id>/approve', methods=['POST'])
@jwt_required()
@tenant_required
def approve_sales_order(order_id):
    """审批销售订单"""
    try:
        result = sales_order_service.approve_sales_order(
            user_id=g.user_id,
            order_id=order_id
        )
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '销售订单审批成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'审批失败: {str(e)}'}), 500


@sales_bp.route('/sales-orders/<order_id>/cancel', methods=['POST'])
@jwt_required()
@tenant_required
def cancel_sales_order(order_id):
    """取消销售订单"""
    try:
        data = request.get_json()
        reason = data.get('reason') if data else None
        
        result = sales_order_service.cancel_sales_order(
            user_id=g.user_id,
            order_id=order_id,
            reason=reason
        )
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '销售订单取消成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'取消失败: {str(e)}'}), 500


@sales_bp.route('/sales-orders/<order_id>/calculate-total', methods=['GET'])
@jwt_required()
@tenant_required
def calculate_order_total(order_id):
    """计算订单总额"""
    try:
        result = sales_order_service.calculate_order_total(order_id=order_id)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@sales_bp.route('/sales-orders/statistics', methods=['GET'])
@jwt_required()
@tenant_required
def get_order_statistics():
    """获取订单统计"""
    try:
        # 构建过滤条件
        filters = {}
        if request.args.get('start_date'):
            filters['start_date'] = datetime.fromisoformat(request.args.get('start_date'))
        if request.args.get('end_date'):
            filters['end_date'] = datetime.fromisoformat(request.args.get('end_date'))
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        
        result = sales_order_service.get_order_statistics(filters=filters)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@sales_bp.route('/customers/options', methods=['GET'])
@jwt_required()
@tenant_required
def get_customer_options():
    """获取客户选项"""
    try:
        # 使用客户服务获取客户列表
        result = customer_service.get_list(page=1, per_page=1000, enabled_only=True)
        
        # 转换为选项格式
        options = []
        for customer in result['customers']:
            options.append({
                'label': customer['customer_name'],
                'value': customer['id'],
                'customer_code': customer['customer_code']
            })
        
        return jsonify({
            'success': True,
            'data': options
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@sales_bp.route('/products/options', methods=['GET'])
@jwt_required()
@tenant_required
def get_product_options():
    """获取产品选项"""
    try:
        # 使用基础数据服务中的ProductService获取产品列表
        from app.services.basic_data_service import ProductService
        result = ProductService.get_products(page=1, per_page=1000, status='active')
        
        # 转换为选项格式，包含更多产品信息
        options = []
        for product in result['products']:
            options.append({
                'label': f"{product['product_code']} - {product['product_name']}",
                'value': product['id'],
                'product_code': product['product_code'],
                'product_name': product['product_name'],
                'unit': product.get('unit', ''),
                'unit_name': product.get('unit_name', ''),
                'specification': product.get('specification', ''),
                'unit_price': product.get('unit_price', 0),
                'category': product.get('category', ''),
                'material_structure': product.get('material_structure', ''),
                'printing_requirements': product.get('printing_requirements', '')
            })
        
        return jsonify({
            'success': True,
            'data': options
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@sales_bp.route('/materials/options', methods=['GET'])
@jwt_required()
@tenant_required
def get_material_options():
    """获取材料选项"""
    try:
        # 使用材料服务获取材料列表
        from app.services.material_management_service import MaterialService
        result = MaterialService.get_materials(page=1, page_size=1000, is_enabled=True)
        
        # 转换为选项格式
        options = []
        for material in result['items']:
            options.append({
                'label': f"{material['material_code']} - {material['material_name']}",
                'value': material['id'],
                'material_code': material['material_code'],
                'material_name': material['material_name'],
                'unit_name': material.get('unit_name', ''),
                'specification_model': material.get('specification_model', '')
            })
        
        return jsonify({
            'success': True,
            'data': options
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@sales_bp.route('/products/<product_id>/inventory', methods=['GET'])
@jwt_required()
@tenant_required
def get_product_inventory(product_id):
    """获取产品库存信息"""
    try:
        from app.services.inventory_service import InventoryService
        from app.extensions import db
        
        inventory_service = InventoryService(db.session)
        inventory_service._set_schema()
        
        # 获取产品的可用库存
        inventory = inventory_service.get_product_inventory(product_id)
        
        return jsonify({
            'success': True,
            'data': {
                'product_id': product_id,
                'available_quantity': inventory.get('available_quantity', 0),
                'total_quantity': inventory.get('total_quantity', 0),
                'reserved_quantity': inventory.get('reserved_quantity', 0)
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取产品库存失败: {str(e)}'
        }), 500 