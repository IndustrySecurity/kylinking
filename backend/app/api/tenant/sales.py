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


@sales_bp.route('/sales-orders/<order_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_sales_order(order_id):
    """删除销售订单"""
    try:
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


@sales_bp.route('/sales-orders/<order_id>/approve', methods=['POST'])
@jwt_required()
@tenant_required
def approve_sales_order(order_id):
    """审批销售订单"""
    try:
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
        
        user_id = get_jwt_identity()
        result = sales_order_service.cancel_sales_order(
            order_id=order_id,
            user_id=user_id,
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


@sales_bp.route('/taxes/options', methods=['GET'])
@jwt_required()
@tenant_required
def get_tax_options():
    """获取税收选项"""
    try:
        # 使用税收服务获取启用的税收列表
        from app.services.package_method_service import TaxRateService
        
        tax_rates = TaxRateService.get_enabled_tax_rates()
        
        # 转换为选项格式
        options = []
        for tax_rate in tax_rates:
            options.append({
                'value': tax_rate['id'],
                'label': tax_rate['tax_name'],
                'rate': tax_rate['tax_rate']
            })
        
        return jsonify({
            'success': True,
            'data': options
        })
        
    except Exception as e:
        return jsonify({'error': f'获取税收选项失败: {str(e)}'}), 500


@sales_bp.route('/customers/<customer_id>/details', methods=['GET'])
@jwt_required()
@tenant_required
def get_customer_details(customer_id):
    """获取客户详细信息用于自动填充订单表单"""
    try:
        from app.models.basic_data import CustomerManagement, CustomerContact, CustomerAffiliatedCompany
        from app.extensions import db
        
        # 获取客户基本信息
        customer = db.session.query(CustomerManagement).filter_by(id=customer_id).first()
        if not customer:
            return jsonify({'error': '客户不存在'}), 404
        
        # 获取客户联系人信息（第一个联系人）
        contact = db.session.query(CustomerContact).filter_by(
            customer_id=customer_id
        ).order_by(CustomerContact.sort_order.asc()).first()
        
        # 获取归属公司信息（第一个归属公司）
        affiliated_company = db.session.query(CustomerAffiliatedCompany).filter_by(
            customer_id=customer_id
        ).order_by(CustomerAffiliatedCompany.sort_order.asc()).first()
        
        # 构建返回数据
        result = {
            'customer_code': customer.customer_code,
            'customer_name': customer.customer_name,
            'contact_person_id': str(contact.id) if contact else None,
            'phone': contact.mobile if contact else '',
            'mobile': contact.mobile if contact else '',
            'payment_method_id': str(customer.payment_method_id) if customer.payment_method_id else None,
            'delivery_method': str(customer.package_method_id) if customer.package_method_id else None,
            'contact_method': contact.mobile if contact else '',
            'salesperson_id': str(customer.salesperson_id) if customer.salesperson_id else None,
            'company_id': affiliated_company.affiliated_company if affiliated_company else '',
            'tax_rate_id': str(customer.tax_rate_id) if customer.tax_rate_id else None,
            'tax_rate': float(customer.tax_rate) if customer.tax_rate else 0.0
        }
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': f'获取客户详情失败: {str(e)}'}), 500


@sales_bp.route('/customers/<customer_id>/contacts', methods=['GET'])
@jwt_required()
@tenant_required
def get_customer_contacts(customer_id):
    """获取客户联系人列表"""
    try:
        from app.models.basic_data import CustomerContact
        from app.extensions import db
        
        contacts = db.session.query(CustomerContact).filter_by(
            customer_id=customer_id
        ).order_by(CustomerContact.sort_order.asc()).all()
        
        contact_list = []
        for c in contacts:
            landline_value = getattr(c, 'landline', None) or getattr(c, 'mobile', None)
            contact_list.append({
                'id': c.id,
                'contact_name': getattr(c, 'contact_name', None),
                'mobile': getattr(c, 'mobile', None),
                'landline': landline_value,
                'fax': getattr(c, 'fax', None),
                'email': getattr(c, 'email', None),
                'position': getattr(c, 'position', None)
            })
        
        return jsonify({
            'success': True,
            'data': contact_list
        })
        
    except Exception as e:
        return jsonify({'error': f'获取客户联系人失败: {str(e)}'}), 500


@sales_bp.route('/products/<product_id>/details', methods=['GET'])
@jwt_required()
@tenant_required
def get_product_details(product_id):
    """获取产品详细信息用于自动填充订单明细表单"""
    try:
        from app.models.basic_data import Product, Unit, Currency, TaxRate, BagType
        from app.extensions import db
        
        # 获取产品基本信息
        product = db.session.query(Product).filter_by(id=product_id).first()
        if not product:
            return jsonify({'error': '产品不存在'}), 404
        
        # 获取相关的关联数据
        currency = db.session.query(Currency).filter_by(currency_code=product.currency).first() if product.currency else None
        bag_type = db.session.query(BagType).filter_by(id=product.bag_type_id).first() if product.bag_type_id else None
        
        # 组装返回数据
        product_data = {
            # 基本产品信息
            'product_code': product.product_code,
            'product_name': product.product_name,
            'specification': product.specification,
            
            # 单位信息
            'unit': product.base_unit,
            'sales_unit_id': None,  # 销售单位ID，根据产品自动填入
            
            # 价格信息
            'unit_price': float(product.standard_price) if product.standard_price else 0,  # 单价
            'standard_cost': float(product.standard_cost) if product.standard_cost else 0,  # 标准成本
            'currency_id': currency.id if currency else None,  # 币种ID
            
            # 库存信息
            'usable_inventory': float(product.safety_stock) if product.safety_stock else 0,  # 可用库存
            'min_order_qty': float(product.min_order_qty) if product.min_order_qty else 1,  # 最小订单量
            'max_order_qty': float(product.max_order_qty) if product.max_order_qty else None,  # 最大订单量
            
            # 生产信息
            'production_small_quantity': float(product.min_order_qty) if product.min_order_qty else 0,  # 生产最小数
            'production_large_quantity': float(product.max_order_qty) if product.max_order_qty else 0,  # 生产最大数
            'lead_time': product.lead_time if product.lead_time else 0,  # 生产周期
            
            # 技术参数
            'thickness': float(product.thickness) if product.thickness else None,  # 厚度
            'width': float(product.width) if product.width else None,  # 宽度
            'length': float(product.length) if product.length else None,  # 长度
            'material_type': product.material_type,  # 材料类型
            
            # 包装信息
            'net_weight': float(product.net_weight) if product.net_weight else None,  # 净重
            'gross_weight': float(product.gross_weight) if product.gross_weight else None,  # 毛重
            'conversion_rate': float(product.conversion_rate) if product.conversion_rate else 1,  # 换算率
            
            # 质量信息
            'quality_standard': product.quality_standard,  # 质量标准
            'inspection_method': product.inspection_method,  # 检验方法
            'storage_condition': product.storage_condition,  # 存储条件
            'shelf_life': product.shelf_life,  # 保质期
            
            # 袋型信息
            'bag_type_id': str(product.bag_type_id) if product.bag_type_id else None,  # 袋型ID
            'bag_type_name': bag_type.bag_type_name if bag_type else None,  # 袋型名称
            
            # 客户信息
            'customer_id': str(product.customer_id) if product.customer_id else None,  # 客户ID
            'salesperson_id': str(product.salesperson_id) if product.salesperson_id else None,  # 业务员ID
            
            # 其他业务字段
            'material_info': product.material_info,  # 材料信息
            'compound_quantity': product.compound_quantity,  # 复合量
            'is_compound_needed': product.is_compound_needed,  # 需要复合
            'is_inspection_needed': product.is_inspection_needed,  # 检验手续
            'is_packaging_needed': product.is_packaging_needed,  # 包装
            
            # 自定义字段
            'custom_fields': product.custom_fields or {}
        }
        
        return jsonify({
            'success': True,
            'data': product_data
        })
        
    except Exception as e:
        return jsonify({'error': f'获取产品详情失败: {str(e)}'}), 500