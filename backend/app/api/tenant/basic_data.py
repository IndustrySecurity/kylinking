# -*- coding: utf-8 -*-
"""
基础档案管理API路由
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services.basic_data_service import (
    CustomerService, CustomerCategoryService, 
    SupplierService, ProductService,
    TenantFieldConfigIntegrationService
)
from app.services.material_category_service import MaterialCategoryService
from app.models.user import User
from app.extensions import db
import uuid

bp = Blueprint('basic_data', __name__)


@bp.route('/customers', methods=['GET'])
@jwt_required()
def get_customers():
    """获取客户列表"""
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search')
        category_id = request.args.get('category_id')
        status = request.args.get('status')
        
        # 获取当前用户和租户信息
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        if not tenant_id:
            return jsonify({'error': '租户信息缺失'}), 400
        
        # 获取租户字段配置
        field_metadata = TenantFieldConfigIntegrationService.get_field_metadata('basic_data', tenant_id)
        
        # 获取客户列表
        result = CustomerService.get_customers(
            page=page,
            per_page=per_page,
            search=search,
            category_id=category_id,
            status=status,
            tenant_config=field_metadata
        )
        
        # 应用字段配置到每个客户数据
        for customer in result['customers']:
            customer = TenantFieldConfigIntegrationService.apply_field_config(
                customer, 'basic_data', tenant_id
            )
        
        return jsonify({
            'success': True,
            'data': result,
            'field_metadata': field_metadata
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/customers/<customer_id>', methods=['GET'])
@jwt_required()
def get_customer(customer_id):
    """获取客户详情"""
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        customer = CustomerService.get_customer(customer_id)
        
        # 应用字段配置
        if tenant_id:
            customer = TenantFieldConfigIntegrationService.apply_field_config(
                customer, 'basic_data', tenant_id
            )
        
        return jsonify({
            'success': True,
            'data': customer
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/customers', methods=['POST'])
@jwt_required()
def create_customer():
    """创建客户"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        if not data.get('customer_name'):
            return jsonify({'error': '客户名称不能为空'}), 400
        
        customer = CustomerService.create_customer(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': customer,
            'message': '客户创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/customers/<customer_id>', methods=['PUT'])
@jwt_required()
def update_customer(customer_id):
    """更新客户"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        customer = CustomerService.update_customer(customer_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': customer,
            'message': '客户更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/customers/<customer_id>', methods=['DELETE'])
@jwt_required()
def delete_customer(customer_id):
    """删除客户"""
    try:
        CustomerService.delete_customer(customer_id)
        
        return jsonify({
            'success': True,
            'message': '客户删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/customers/<customer_id>/approve', methods=['POST'])
@jwt_required()
def approve_customer(customer_id):
    """审批客户"""
    try:
        current_user_id = get_jwt_identity()
        
        customer = CustomerService.approve_customer(customer_id, current_user_id)
        
        return jsonify({
            'success': True,
            'data': customer,
            'message': '客户审批成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/customers/search', methods=['GET'])
@jwt_required()
def search_customers():
    """客户搜索（简化版）"""
    try:
        search = request.args.get('q', '')
        limit = min(int(request.args.get('limit', 10)), 50)
        
        result = CustomerService.get_customers(
            page=1,
            per_page=limit,
            search=search
        )
        
        # 简化返回数据
        customers = [{
            'id': customer['id'],
            'customer_code': customer['customer_code'],
            'customer_name': customer['customer_name'],
            'contact_person': customer['contact_person'],
            'contact_phone': customer['contact_phone']
        } for customer in result['customers']]
        
        return jsonify({
            'success': True,
            'data': customers
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 客户分类相关API
@bp.route('/categories/customers', methods=['GET'])
@jwt_required()
def get_customer_categories():
    """获取客户分类树"""
    try:
        include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
        
        categories = CustomerCategoryService.get_categories(include_inactive)
        
        return jsonify({
            'success': True,
            'data': categories
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/categories/customers', methods=['POST'])
@jwt_required()
def create_customer_category():
    """创建客户分类"""
    try:
        data = request.get_json()
        
        if not data or not data.get('category_name'):
            return jsonify({'error': '分类名称不能为空'}), 400
        
        category = CustomerCategoryService.create_category(data)
        
        return jsonify({
            'success': True,
            'data': category,
            'message': '分类创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 供应商相关API
@bp.route('/suppliers', methods=['GET'])
@jwt_required()
def get_suppliers():
    """获取供应商列表"""
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search')
        category_id = request.args.get('category_id')
        status = request.args.get('status')
        
        result = SupplierService.get_suppliers(
            page=page,
            per_page=per_page,
            search=search,
            category_id=category_id,
            status=status
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/suppliers', methods=['POST'])
@jwt_required()
def create_supplier():
    """创建供应商"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data.get('supplier_name'):
            return jsonify({'error': '供应商名称不能为空'}), 400
        
        supplier = SupplierService.create_supplier(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': supplier,
            'message': '供应商创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 产品相关API
@bp.route('/products', methods=['GET'])
@jwt_required()
def get_products():
    """获取产品列表"""
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search')
        category_id = request.args.get('category_id')
        status = request.args.get('status')
        product_type = request.args.get('product_type')
        
        result = ProductService.get_products(
            page=page,
            per_page=per_page,
            search=search,
            category_id=category_id,
            status=status,
            product_type=product_type
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/products', methods=['POST'])
@jwt_required()
def create_product():
    """创建产品"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data.get('product_name'):
            return jsonify({'error': '产品名称不能为空'}), 400
        
        product = ProductService.create_product(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': product,
            'message': '产品创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 字段配置相关API
@bp.route('/field-metadata/<module_name>', methods=['GET'])
@jwt_required()
def get_field_metadata(module_name):
    """获取字段元数据"""
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        if not tenant_id:
            return jsonify({'error': '租户信息缺失'}), 400
        
        field_metadata = TenantFieldConfigIntegrationService.get_field_metadata(module_name, tenant_id)
        
        return jsonify({
            'success': True,
            'data': field_metadata
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 数据统计API
@bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_statistics():
    """获取基础档案统计数据"""
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        # 获取统计数据
        from sqlalchemy import func
        from app.models.basic_data import Customer, Supplier, Product
        
        stats = {
            'customers': {
                'total': db.session.query(func.count(Customer.id)).scalar(),
                'active': db.session.query(func.count(Customer.id)).filter(Customer.status == 'active').scalar(),
                'pending': db.session.query(func.count(Customer.id)).filter(Customer.status == 'pending').scalar()
            },
            'suppliers': {
                'total': db.session.query(func.count(Supplier.id)).scalar(),
                'active': db.session.query(func.count(Supplier.id)).filter(Supplier.status == 'active').scalar(),
                'strategic': db.session.query(func.count(Supplier.id)).filter(Supplier.cooperation_level == 'strategic').scalar()
            },
            'products': {
                'total': db.session.query(func.count(Product.id)).scalar(),
                'active': db.session.query(func.count(Product.id)).filter(Product.status == 'active').scalar(),
                'finished': db.session.query(func.count(Product.id)).filter(Product.product_type == 'finished').scalar(),
                'material': db.session.query(func.count(Product.id)).filter(Product.product_type == 'material').scalar()
            }
        }
        
        return jsonify({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===== 包装方式管理 API =====

@bp.route('/package-methods', methods=['GET'])
@jwt_required()
def get_package_methods():
    """获取包装方式列表"""
    try:
        from app.services.package_method_service import PackageMethodService
        
        # 获取查询参数
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 100)), 100)
        search = request.args.get('search')
        enabled_only = request.args.get('enabled_only', 'false').lower() == 'true'
        
        # 获取当前用户和租户信息
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        if not tenant_id:
            return jsonify({'error': '租户信息缺失'}), 400
        
        # 获取包装方式列表
        result = PackageMethodService.get_package_methods(
            page=page,
            per_page=per_page,
            search=search,
            enabled_only=enabled_only
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/package-methods/<package_method_id>', methods=['GET'])
@jwt_required()
def get_package_method(package_method_id):
    """获取包装方式详情"""
    try:
        from app.services.package_method_service import PackageMethodService
        
        package_method = PackageMethodService.get_package_method(package_method_id)
        
        return jsonify({
            'success': True,
            'data': package_method
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/package-methods', methods=['POST'])
@jwt_required()
def create_package_method():
    """创建包装方式"""
    try:
        from app.services.package_method_service import PackageMethodService
        
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        if not data.get('package_name'):
            return jsonify({'error': '包装方式名称不能为空'}), 400
        
        package_method = PackageMethodService.create_package_method(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': package_method,
            'message': '包装方式创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/package-methods/<package_method_id>', methods=['PUT'])
@jwt_required()
def update_package_method(package_method_id):
    """更新包装方式"""
    try:
        from app.services.package_method_service import PackageMethodService
        
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        package_method = PackageMethodService.update_package_method(package_method_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': package_method,
            'message': '包装方式更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/package-methods/<package_method_id>', methods=['DELETE'])
@jwt_required()
def delete_package_method(package_method_id):
    """删除包装方式"""
    try:
        from app.services.package_method_service import PackageMethodService
        
        PackageMethodService.delete_package_method(package_method_id)
        
        return jsonify({
            'success': True,
            'message': '包装方式删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/package-methods/batch', methods=['PUT'])
@jwt_required()
def batch_update_package_methods():
    """批量更新包装方式（用于可编辑表格）"""
    try:
        from app.services.package_method_service import PackageMethodService
        
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not isinstance(data, list):
            return jsonify({'error': '请求数据必须是数组'}), 400
        
        results = PackageMethodService.batch_update_package_methods(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': results,
            'message': f'成功更新 {len(results)} 个包装方式'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===== 送货方式管理 API =====

@bp.route('/delivery-methods', methods=['GET'])
@jwt_required()
def get_delivery_methods():
    """获取送货方式列表"""
    try:
        from app.services.package_method_service import DeliveryMethodService
        
        # 获取查询参数
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 100)), 100)
        search = request.args.get('search')
        enabled_only = request.args.get('enabled_only', 'false').lower() == 'true'
        
        # 获取当前用户和租户信息
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        if not tenant_id:
            return jsonify({'error': '租户信息缺失'}), 400
        
        # 获取送货方式列表
        result = DeliveryMethodService.get_delivery_methods(
            page=page,
            per_page=per_page,
            search=search,
            enabled_only=enabled_only
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/delivery-methods/<delivery_method_id>', methods=['GET'])
@jwt_required()
def get_delivery_method(delivery_method_id):
    """获取送货方式详情"""
    try:
        from app.services.package_method_service import DeliveryMethodService
        
        delivery_method = DeliveryMethodService.get_delivery_method(delivery_method_id)
        
        return jsonify({
            'success': True,
            'data': delivery_method
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/delivery-methods', methods=['POST'])
@jwt_required()
def create_delivery_method():
    """创建送货方式"""
    try:
        from app.services.package_method_service import DeliveryMethodService
        
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        if not data.get('delivery_name'):
            return jsonify({'error': '送货方式名称不能为空'}), 400
        
        delivery_method = DeliveryMethodService.create_delivery_method(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': delivery_method,
            'message': '送货方式创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/delivery-methods/<delivery_method_id>', methods=['PUT'])
@jwt_required()
def update_delivery_method(delivery_method_id):
    """更新送货方式"""
    try:
        from app.services.package_method_service import DeliveryMethodService
        
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        delivery_method = DeliveryMethodService.update_delivery_method(delivery_method_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': delivery_method,
            'message': '送货方式更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/delivery-methods/<delivery_method_id>', methods=['DELETE'])
@jwt_required()
def delete_delivery_method(delivery_method_id):
    """删除送货方式"""
    try:
        from app.services.package_method_service import DeliveryMethodService
        
        DeliveryMethodService.delete_delivery_method(delivery_method_id)
        
        return jsonify({
            'success': True,
            'message': '送货方式删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/delivery-methods/batch', methods=['PUT'])
@jwt_required()
def batch_update_delivery_methods():
    """批量更新送货方式（用于可编辑表格）"""
    try:
        from app.services.package_method_service import DeliveryMethodService
        
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not isinstance(data, list):
            return jsonify({'error': '请求数据必须是数组'}), 400
        
        results = DeliveryMethodService.batch_update_delivery_methods(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': results,
            'message': f'成功更新 {len(results)} 个送货方式'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===== 色卡管理 API =====

@bp.route('/color-cards', methods=['GET'])
@jwt_required()
def get_color_cards():
    """获取色卡列表"""
    try:
        from app.services.package_method_service import ColorCardService
        
        # 获取查询参数
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 100)), 100)
        search = request.args.get('search')
        enabled_only = request.args.get('enabled_only', 'false').lower() == 'true'
        
        # 获取当前用户和租户信息
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        if not tenant_id:
            return jsonify({'error': '租户信息缺失'}), 400
        
        # 获取色卡列表
        result = ColorCardService.get_color_cards(
            page=page,
            per_page=per_page,
            search=search,
            enabled_only=enabled_only
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/color-cards/<color_card_id>', methods=['GET'])
@jwt_required()
def get_color_card(color_card_id):
    """获取色卡详情"""
    try:
        from app.services.package_method_service import ColorCardService
        
        color_card = ColorCardService.get_color_card(color_card_id)
        
        return jsonify({
            'success': True,
            'data': color_card
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/color-cards', methods=['POST'])
@jwt_required()
def create_color_card():
    """创建色卡"""
    try:
        from app.services.package_method_service import ColorCardService
        
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        if not data.get('color_name'):
            return jsonify({'error': '色卡名称不能为空'}), 400
        
        if not data.get('color_value'):
            return jsonify({'error': '色值不能为空'}), 400
        
        color_card = ColorCardService.create_color_card(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': color_card,
            'message': '色卡创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/color-cards/<color_card_id>', methods=['PUT'])
@jwt_required()
def update_color_card(color_card_id):
    """更新色卡"""
    try:
        from app.services.package_method_service import ColorCardService
        
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        color_card = ColorCardService.update_color_card(color_card_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': color_card,
            'message': '色卡更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/color-cards/<color_card_id>', methods=['DELETE'])
@jwt_required()
def delete_color_card(color_card_id):
    """删除色卡"""
    try:
        from app.services.package_method_service import ColorCardService
        
        ColorCardService.delete_color_card(color_card_id)
        
        return jsonify({
            'success': True,
            'message': '色卡删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/color-cards/batch', methods=['PUT'])
@jwt_required()
def batch_update_color_cards():
    """批量更新色卡（用于可编辑表格）"""
    try:
        from app.services.package_method_service import ColorCardService
        
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not isinstance(data, list):
            return jsonify({'error': '请求数据必须是数组'}), 400
        
        results = ColorCardService.batch_update_color_cards(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': results,
            'message': f'成功更新 {len(results)} 个色卡'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 单位管理API
@bp.route('/units', methods=['GET'])
@jwt_required()
def get_units():
    """获取单位列表"""
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search')
        enabled_only = request.args.get('enabled_only', 'false').lower() == 'true'
        
        # 获取当前用户信息
        current_user_id = get_jwt_identity()
        
        # 导入服务
        from app.services.package_method_service import UnitService
        
        # 获取单位列表
        result = UnitService.get_units(
            page=page,
            per_page=per_page,
            search=search,
            enabled_only=enabled_only
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/units/<unit_id>', methods=['GET'])
@jwt_required()
def get_unit(unit_id):
    """获取单位详情"""
    try:
        from app.services.package_method_service import UnitService
        
        unit = UnitService.get_unit(unit_id)
        
        return jsonify({
            'success': True,
            'data': unit
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/units', methods=['POST'])
@jwt_required()
def create_unit():
    """创建单位"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        if not data.get('unit_name'):
            return jsonify({'error': '单位名称不能为空'}), 400
        
        from app.services.package_method_service import UnitService
        
        unit = UnitService.create_unit(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': unit,
            'message': '单位创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/units/<unit_id>', methods=['PUT'])
@jwt_required()
def update_unit(unit_id):
    """更新单位"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        from app.services.package_method_service import UnitService
        
        unit = UnitService.update_unit(unit_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': unit,
            'message': '单位更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/units/<unit_id>', methods=['DELETE'])
@jwt_required()
def delete_unit(unit_id):
    """删除单位"""
    try:
        from app.services.package_method_service import UnitService
        
        UnitService.delete_unit(unit_id)
        
        return jsonify({
            'success': True,
            'message': '单位删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/units/batch', methods=['PUT'])
@jwt_required()
def batch_update_units():
    """批量更新单位"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not isinstance(data, list):
            return jsonify({'error': '请求数据格式错误'}), 400
        
        from app.services.package_method_service import UnitService
        
        results = UnitService.batch_update_units(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': results,
            'message': '批量更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 客户分类管理API
@bp.route('/customer-category-management', methods=['GET'])
@jwt_required()
def get_customer_category_management():
    """获取客户分类列表"""
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search')
        enabled_only = request.args.get('enabled_only', 'false').lower() == 'true'
        
        # 获取当前用户信息
        current_user_id = get_jwt_identity()
        
        # 导入服务
        from app.services.package_method_service import CustomerCategoryManagementService
        
        # 获取客户分类列表
        result = CustomerCategoryManagementService.get_customer_categories(
            page=page,
            per_page=per_page,
            search=search,
            enabled_only=enabled_only
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/customer-category-management/<category_id>', methods=['GET'])
@jwt_required()
def get_customer_category_management_detail(category_id):
    """获取客户分类详情"""
    try:
        from app.services.package_method_service import CustomerCategoryManagementService
        
        category = CustomerCategoryManagementService.get_customer_category(category_id)
        
        return jsonify({
            'success': True,
            'data': category
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/customer-category-management', methods=['POST'])
@jwt_required()
def create_customer_category_management():
    """创建客户分类"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        if not data.get('category_name'):
            return jsonify({'error': '客户分类名称不能为空'}), 400
        
        from app.services.package_method_service import CustomerCategoryManagementService
        
        category = CustomerCategoryManagementService.create_customer_category(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': category,
            'message': '客户分类创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/customer-category-management/<category_id>', methods=['PUT'])
@jwt_required()
def update_customer_category_management(category_id):
    """更新客户分类"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        from app.services.package_method_service import CustomerCategoryManagementService
        
        category = CustomerCategoryManagementService.update_customer_category(category_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': category,
            'message': '客户分类更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/customer-category-management/<category_id>', methods=['DELETE'])
@jwt_required()
def delete_customer_category_management(category_id):
    """删除客户分类"""
    try:
        from app.services.package_method_service import CustomerCategoryManagementService
        
        CustomerCategoryManagementService.delete_customer_category(category_id)
        
        return jsonify({
            'success': True,
            'message': '客户分类删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/customer-category-management/batch', methods=['PUT'])
@jwt_required()
def batch_update_customer_category_management():
    """批量更新客户分类"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not isinstance(data, list):
            return jsonify({'error': '请求数据格式错误'}), 400
        
        from app.services.package_method_service import CustomerCategoryManagementService
        
        results = CustomerCategoryManagementService.batch_update_customer_categories(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': results,
            'message': '批量更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 供应商分类管理API
@bp.route('/supplier-category-management', methods=['GET'])
@jwt_required()
def get_supplier_category_management():
    """获取供应商分类列表"""
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search')
        enabled_only = request.args.get('enabled_only', 'false').lower() == 'true'
        
        # 获取当前用户信息
        current_user_id = get_jwt_identity()
        
        # 导入服务
        from app.services.package_method_service import SupplierCategoryManagementService
        
        # 获取供应商分类列表
        result = SupplierCategoryManagementService.get_supplier_categories(
            page=page,
            per_page=per_page,
            search=search,
            enabled_only=enabled_only
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/supplier-category-management/<category_id>', methods=['GET'])
@jwt_required()
def get_supplier_category_management_detail(category_id):
    """获取供应商分类详情"""
    try:
        from app.services.package_method_service import SupplierCategoryManagementService
        
        category = SupplierCategoryManagementService.get_supplier_category(category_id)
        
        return jsonify({
            'success': True,
            'data': category
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/supplier-category-management', methods=['POST'])
@jwt_required()
def create_supplier_category_management():
    """创建供应商分类"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        if not data.get('category_name'):
            return jsonify({'error': '供应商分类名称不能为空'}), 400
        
        from app.services.package_method_service import SupplierCategoryManagementService
        
        category = SupplierCategoryManagementService.create_supplier_category(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': category,
            'message': '供应商分类创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/supplier-category-management/<category_id>', methods=['PUT'])
@jwt_required()
def update_supplier_category_management(category_id):
    """更新供应商分类"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        from app.services.package_method_service import SupplierCategoryManagementService
        
        category = SupplierCategoryManagementService.update_supplier_category(category_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': category,
            'message': '供应商分类更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/supplier-category-management/<category_id>', methods=['DELETE'])
@jwt_required()
def delete_supplier_category_management(category_id):
    """删除供应商分类"""
    try:
        from app.services.package_method_service import SupplierCategoryManagementService
        
        SupplierCategoryManagementService.delete_supplier_category(category_id)
        
        return jsonify({
            'success': True,
            'message': '供应商分类删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/supplier-category-management/batch', methods=['PUT'])
@jwt_required()
def batch_update_supplier_category_management():
    """批量更新供应商分类"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not isinstance(data, list):
            return jsonify({'error': '请求数据格式错误'}), 400
        
        from app.services.package_method_service import SupplierCategoryManagementService
        
        results = SupplierCategoryManagementService.batch_update_supplier_categories(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': results,
            'message': '批量更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 规格管理API
@bp.route('/specifications', methods=['GET'])
@jwt_required()
def get_specifications():
    """获取规格列表"""
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search')
        enabled_only = request.args.get('enabled_only', 'false').lower() == 'true'
        
        # 获取当前用户信息
        current_user_id = get_jwt_identity()
        
        # 导入服务
        from app.services.package_method_service import SpecificationService
        
        # 获取规格列表
        result = SpecificationService.get_specifications(
            page=page,
            per_page=per_page,
            search=search,
            enabled_only=enabled_only
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/specifications/<spec_id>', methods=['GET'])
@jwt_required()
def get_specification(spec_id):
    """获取规格详情"""
    try:
        from app.services.package_method_service import SpecificationService
        
        specification = SpecificationService.get_specification(spec_id)
        
        return jsonify({
            'success': True,
            'data': specification
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/specifications', methods=['POST'])
@jwt_required()
def create_specification():
    """创建规格"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        if not data.get('spec_name'):
            return jsonify({'error': '规格名称不能为空'}), 400
        
        if not data.get('length') or not data.get('width') or not data.get('roll'):
            return jsonify({'error': '长、宽、卷不能为空'}), 400
        
        from app.services.package_method_service import SpecificationService
        
        specification = SpecificationService.create_specification(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': specification,
            'message': '规格创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/specifications/<spec_id>', methods=['PUT'])
@jwt_required()
def update_specification(spec_id):
    """更新规格"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        from app.services.package_method_service import SpecificationService
        
        specification = SpecificationService.update_specification(spec_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': specification,
            'message': '规格更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/specifications/<spec_id>', methods=['DELETE'])
@jwt_required()
def delete_specification(spec_id):
    """删除规格"""
    try:
        from app.services.package_method_service import SpecificationService
        
        SpecificationService.delete_specification(spec_id)
        
        return jsonify({
            'success': True,
            'message': '规格删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/specifications/batch', methods=['PUT'])
@jwt_required()
def batch_update_specifications():
    """批量更新规格"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not isinstance(data, list):
            return jsonify({'error': '请求数据格式错误'}), 400
        
        from app.services.package_method_service import SpecificationService
        
        results = SpecificationService.batch_update_specifications(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': results,
            'message': '批量更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 币别管理API
@bp.route('/currencies', methods=['GET'])
@jwt_required()
def get_currencies():
    """获取币别列表"""
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search')
        enabled_only = request.args.get('enabled_only', 'false').lower() == 'true'
        
        # 获取当前用户和租户信息
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        if not tenant_id:
            return jsonify({'error': '租户信息缺失'}), 400
        
        # 使用CurrencyService获取币别列表
        from app.services.package_method_service import CurrencyService
        
        result = CurrencyService.get_currencies(
            page=page,
            per_page=per_page,
            search=search,
            enabled_only=enabled_only
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/currencies/enabled', methods=['GET'])
@jwt_required()
def get_enabled_currencies():
    """获取启用的币别列表（用于下拉选择）"""
    try:
        from app.services.package_method_service import CurrencyService
        
        currencies = CurrencyService.get_enabled_currencies()
        
        return jsonify({
            'success': True,
            'data': currencies
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/currencies/<currency_id>', methods=['GET'])
@jwt_required()
def get_currency(currency_id):
    """获取币别详情"""
    try:
        from app.services.package_method_service import CurrencyService
        
        currency = CurrencyService.get_currency(currency_id)
        
        return jsonify({
            'success': True,
            'data': currency
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/currencies', methods=['POST'])
@jwt_required()
def create_currency():
    """创建币别"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        from app.services.package_method_service import CurrencyService
        
        currency = CurrencyService.create_currency(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': currency,
            'message': '币别创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/currencies/<currency_id>', methods=['PUT'])
@jwt_required()
def update_currency(currency_id):
    """更新币别"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        from app.services.package_method_service import CurrencyService
        
        currency = CurrencyService.update_currency(currency_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': currency,
            'message': '币别更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/currencies/<currency_id>', methods=['DELETE'])
@jwt_required()
def delete_currency(currency_id):
    """删除币别"""
    try:
        from app.services.package_method_service import CurrencyService
        
        CurrencyService.delete_currency(currency_id)
        
        return jsonify({
            'success': True,
            'message': '币别删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/currencies/<currency_id>/set-base', methods=['POST'])
@jwt_required()
def set_base_currency(currency_id):
    """设置为本位币"""
    try:
        from app.services.package_method_service import CurrencyService
        
        currency = CurrencyService.set_base_currency(currency_id)
        
        return jsonify({
            'success': True,
            'data': currency,
            'message': '本位币设置成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/currencies/batch', methods=['PUT'])
@jwt_required()
def batch_update_currencies():
    """批量更新币别"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not isinstance(data, list):
            return jsonify({'error': '请求数据格式错误'}), 400
        
        from app.services.package_method_service import CurrencyService
        
        results = CurrencyService.batch_update_currencies(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': results,
            'message': '批量更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 税率管理API
@bp.route('/tax-rates', methods=['GET'])
@jwt_required()
def get_tax_rates():
    """获取税率列表"""
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search')
        enabled_only = request.args.get('enabled_only', 'false').lower() == 'true'
        
        from app.services.package_method_service import TaxRateService
        
        result = TaxRateService.get_tax_rates(
            page=page,
            per_page=per_page,
            search=search,
            enabled_only=enabled_only
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/tax-rates/enabled', methods=['GET'])
@jwt_required()
def get_enabled_tax_rates():
    """获取启用的税率列表（用于下拉选择）"""
    try:
        from app.services.package_method_service import TaxRateService
        
        tax_rates = TaxRateService.get_enabled_tax_rates()
        
        return jsonify({
            'success': True,
            'data': tax_rates
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/tax-rates/<tax_rate_id>', methods=['GET'])
@jwt_required()
def get_tax_rate(tax_rate_id):
    """获取税率详情"""
    try:
        from app.services.package_method_service import TaxRateService
        
        tax_rate = TaxRateService.get_tax_rate(tax_rate_id)
        
        return jsonify({
            'success': True,
            'data': tax_rate
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/tax-rates', methods=['POST'])
@jwt_required()
def create_tax_rate():
    """创建税率"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        from app.services.package_method_service import TaxRateService
        
        tax_rate = TaxRateService.create_tax_rate(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': tax_rate,
            'message': '税率创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/tax-rates/<tax_rate_id>', methods=['PUT'])
@jwt_required()
def update_tax_rate(tax_rate_id):
    """更新税率"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        from app.services.package_method_service import TaxRateService
        
        tax_rate = TaxRateService.update_tax_rate(tax_rate_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': tax_rate,
            'message': '税率更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/tax-rates/<tax_rate_id>', methods=['DELETE'])
@jwt_required()
def delete_tax_rate(tax_rate_id):
    """删除税率"""
    try:
        from app.services.package_method_service import TaxRateService
        
        TaxRateService.delete_tax_rate(tax_rate_id)
        
        return jsonify({
            'success': True,
            'message': '税率删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/tax-rates/<tax_rate_id>/set-default', methods=['POST'])
@jwt_required()
def set_default_tax_rate(tax_rate_id):
    """设置为默认税率"""
    try:
        from app.services.package_method_service import TaxRateService
        
        tax_rate = TaxRateService.set_default_tax_rate(tax_rate_id)
        
        return jsonify({
            'success': True,
            'data': tax_rate,
            'message': '默认税率设置成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/tax-rates/batch', methods=['PUT'])
@jwt_required()
def batch_update_tax_rates():
    """批量更新税率"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not isinstance(data, list):
            return jsonify({'error': '请求数据格式错误'}), 400
        
        from app.services.package_method_service import TaxRateService
        
        results = TaxRateService.batch_update_tax_rates(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': results,
            'message': f'成功处理 {len(results)} 条税率记录'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 结算方式管理API
@bp.route('/settlement-methods', methods=['GET'])
@jwt_required()
def get_settlement_methods():
    """获取结算方式列表"""
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search')
        enabled_only = request.args.get('enabled_only', 'false').lower() == 'true'
        
        from app.services.package_method_service import SettlementMethodService
        
        result = SettlementMethodService.get_settlement_methods(
            page=page,
            per_page=per_page,
            search=search,
            enabled_only=enabled_only
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/settlement-methods/enabled', methods=['GET'])
@jwt_required()
def get_enabled_settlement_methods():
    """获取启用的结算方式列表（用于下拉选择）"""
    try:
        from app.services.package_method_service import SettlementMethodService
        
        settlement_methods = SettlementMethodService.get_enabled_settlement_methods()
        
        return jsonify({
            'success': True,
            'data': settlement_methods
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/settlement-methods/<settlement_method_id>', methods=['GET'])
@jwt_required()
def get_settlement_method(settlement_method_id):
    """获取结算方式详情"""
    try:
        from app.services.package_method_service import SettlementMethodService
        
        settlement_method = SettlementMethodService.get_settlement_method(settlement_method_id)
        
        return jsonify({
            'success': True,
            'data': settlement_method
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/settlement-methods', methods=['POST'])
@jwt_required()
def create_settlement_method():
    """创建结算方式"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        from app.services.package_method_service import SettlementMethodService
        
        settlement_method = SettlementMethodService.create_settlement_method(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': settlement_method,
            'message': '结算方式创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/settlement-methods/<settlement_method_id>', methods=['PUT'])
@jwt_required()
def update_settlement_method(settlement_method_id):
    """更新结算方式"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        from app.services.package_method_service import SettlementMethodService
        
        settlement_method = SettlementMethodService.update_settlement_method(settlement_method_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': settlement_method,
            'message': '结算方式更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/settlement-methods/<settlement_method_id>', methods=['DELETE'])
@jwt_required()
def delete_settlement_method(settlement_method_id):
    """删除结算方式"""
    try:
        from app.services.package_method_service import SettlementMethodService
        
        SettlementMethodService.delete_settlement_method(settlement_method_id)
        
        return jsonify({
            'success': True,
            'message': '结算方式删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/settlement-methods/batch', methods=['PUT'])
@jwt_required()
def batch_update_settlement_methods():
    """批量更新结算方式"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not isinstance(data, list):
            return jsonify({'error': '请求数据格式错误'}), 400
        
        from app.services.package_method_service import SettlementMethodService
        
        results = SettlementMethodService.batch_update_settlement_methods(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': results,
            'message': f'成功处理 {len(results)} 条结算方式记录'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 账户管理API
@bp.route('/account-management', methods=['GET'])
@jwt_required()
def get_accounts():
    """获取账户列表"""
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search')
        enabled_only = request.args.get('enabled_only', 'false').lower() == 'true'
        
        from app.services.package_method_service import AccountManagementService
        
        result = AccountManagementService.get_accounts(
            page=page,
            per_page=per_page,
            search=search,
            enabled_only=enabled_only
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/account-management/enabled', methods=['GET'])
@jwt_required()
def get_enabled_accounts():
    """获取启用的账户列表（用于下拉选择）"""
    try:
        from app.services.package_method_service import AccountManagementService
        
        accounts = AccountManagementService.get_enabled_accounts()
        
        return jsonify({
            'success': True,
            'data': accounts
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/account-management/<account_id>', methods=['GET'])
@jwt_required()
def get_account(account_id):
    """获取账户详情"""
    try:
        from app.services.package_method_service import AccountManagementService
        
        account = AccountManagementService.get_account(account_id)
        
        return jsonify({
            'success': True,
            'data': account
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/account-management', methods=['POST'])
@jwt_required()
def create_account():
    """创建账户"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        from app.services.package_method_service import AccountManagementService
        
        account = AccountManagementService.create_account(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': account,
            'message': '账户创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/account-management/<account_id>', methods=['PUT'])
@jwt_required()
def update_account(account_id):
    """更新账户"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        from app.services.package_method_service import AccountManagementService
        
        account = AccountManagementService.update_account(account_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': account,
            'message': '账户更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/account-management/<account_id>', methods=['DELETE'])
@jwt_required()
def delete_account(account_id):
    """删除账户"""
    try:
        from app.services.package_method_service import AccountManagementService
        
        AccountManagementService.delete_account(account_id)
        
        return jsonify({
            'success': True,
            'message': '账户删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/account-management/batch', methods=['PUT'])
@jwt_required()
def batch_update_accounts():
    """批量更新账户"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not isinstance(data, list):
            return jsonify({'error': '请求数据格式错误'}), 400
        
        from app.services.package_method_service import AccountManagementService
        
        results = AccountManagementService.batch_update_accounts(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': results,
            'message': f'成功处理 {len(results)} 条账户记录'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 付款方式管理API
@bp.route('/payment-methods', methods=['GET'])
@jwt_required()
def get_payment_methods():
    """获取付款方式列表"""
    try:
        from app.services.package_method_service import PaymentMethodService
        
        # 获取查询参数
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search')
        enabled_only = request.args.get('enabled_only', 'false').lower() == 'true'
        
        result = PaymentMethodService.get_payment_methods(
            page=page,
            per_page=per_page,
            search=search,
            enabled_only=enabled_only
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/payment-methods/enabled', methods=['GET'])
@jwt_required()
def get_enabled_payment_methods():
    """获取启用的付款方式列表"""
    try:
        from app.services.package_method_service import PaymentMethodService
        
        payment_methods = PaymentMethodService.get_enabled_payment_methods()
        
        return jsonify({
            'success': True,
            'data': payment_methods
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/payment-methods/<payment_method_id>', methods=['GET'])
@jwt_required()
def get_payment_method(payment_method_id):
    """获取付款方式详情"""
    try:
        from app.services.package_method_service import PaymentMethodService
        
        payment_method = PaymentMethodService.get_payment_method(payment_method_id)
        
        return jsonify({
            'success': True,
            'data': payment_method
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/payment-methods', methods=['POST'])
@jwt_required()
def create_payment_method():
    """创建付款方式"""
    try:
        from app.services.package_method_service import PaymentMethodService
        
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        payment_method = PaymentMethodService.create_payment_method(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': payment_method,
            'message': '付款方式创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/payment-methods/<payment_method_id>', methods=['PUT'])
@jwt_required()
def update_payment_method(payment_method_id):
    """更新付款方式"""
    try:
        from app.services.package_method_service import PaymentMethodService
        
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        payment_method = PaymentMethodService.update_payment_method(payment_method_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': payment_method,
            'message': '付款方式更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/payment-methods/<payment_method_id>', methods=['DELETE'])
@jwt_required()
def delete_payment_method(payment_method_id):
    """删除付款方式"""
    try:
        from app.services.package_method_service import PaymentMethodService
        
        PaymentMethodService.delete_payment_method(payment_method_id)
        
        return jsonify({
            'success': True,
            'message': '付款方式删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/payment-methods/batch', methods=['PUT'])
@jwt_required()
def batch_update_payment_methods():
    """批量更新付款方式"""
    try:
        from app.services.package_method_service import PaymentMethodService
        
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not isinstance(data, list):
            return jsonify({'error': '请求数据格式错误'}), 400
        
        results = PaymentMethodService.batch_update_payment_methods(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': results,
            'message': f'成功处理 {len(results)} 条付款方式记录'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500 

# 油墨选项管理API
@bp.route('/ink-options', methods=['GET'])
@jwt_required()
def get_ink_options():
    """获取油墨选项列表"""
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search')
        enabled_only = request.args.get('enabled_only', 'false').lower() == 'true'
        
        # 获取当前用户信息
        current_user_id = get_jwt_identity()
        
        # 导入服务
        from app.services.package_method_service import InkOptionService
        
        # 获取油墨选项列表
        result = InkOptionService.get_ink_options(
            page=page,
            per_page=per_page,
            search=search,
            enabled_only=enabled_only
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/ink-options/enabled', methods=['GET'])
@jwt_required()
def get_enabled_ink_options():
    """获取启用的油墨选项列表（用于下拉选择）"""
    try:
        from app.services.package_method_service import InkOptionService
        
        options = InkOptionService.get_enabled_ink_options()
        
        return jsonify({
            'success': True,
            'data': options
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/ink-options/<option_id>', methods=['GET'])
@jwt_required()
def get_ink_option(option_id):
    """获取油墨选项详情"""
    try:
        from app.services.package_method_service import InkOptionService
        
        option = InkOptionService.get_ink_option(option_id)
        
        return jsonify({
            'success': True,
            'data': option
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/ink-options', methods=['POST'])
@jwt_required()
def create_ink_option():
    """创建油墨选项"""
    try:
        from app.services.package_method_service import InkOptionService
        
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        if not data.get('option_name'):
            return jsonify({'error': '选项名称不能为空'}), 400
        
        option = InkOptionService.create_ink_option(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': option,
            'message': '油墨选项创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/ink-options/<option_id>', methods=['PUT'])
@jwt_required()
def update_ink_option(option_id):
    """更新油墨选项"""
    try:
        from app.services.package_method_service import InkOptionService
        
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        option = InkOptionService.update_ink_option(option_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': option,
            'message': '油墨选项更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/ink-options/<option_id>', methods=['DELETE'])
@jwt_required()
def delete_ink_option(option_id):
    """删除油墨选项"""
    try:
        from app.services.package_method_service import InkOptionService
        
        InkOptionService.delete_ink_option(option_id)
        
        return jsonify({
            'success': True,
            'message': '油墨选项删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/ink-options/batch', methods=['PUT'])
@jwt_required()
def batch_update_ink_options():
    """批量更新油墨选项"""
    try:
        from app.services.package_method_service import InkOptionService
        
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not isinstance(data, list):
            return jsonify({'error': '请求数据必须是数组'}), 400
        
        results = InkOptionService.batch_update_ink_options(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': results,
            'message': f'成功更新 {len(results)} 个油墨选项'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500 

# 报价运费管理API
@bp.route('/quote-freights', methods=['GET'])
@jwt_required()
def get_quote_freights():
    """获取报价运费列表"""
    try:
        from app.services.package_method_service import QuoteFreightService
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        enabled_only = request.args.get('enabled_only', False, type=bool)
        
        # 获取报价运费列表
        result = QuoteFreightService.get_quote_freights(
            page=page,
            per_page=per_page,
            search=search,
            enabled_only=enabled_only
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/quote-freights/enabled', methods=['GET'])
@jwt_required()
def get_enabled_quote_freights():
    """获取启用的报价运费列表（用于下拉选择）"""
    try:
        from app.services.package_method_service import QuoteFreightService
        
        freights = QuoteFreightService.get_enabled_quote_freights()
        
        return jsonify({
            'success': True,
            'data': freights
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/quote-freights/<freight_id>', methods=['GET'])
@jwt_required()
def get_quote_freight(freight_id):
    """获取报价运费详情"""
    try:
        from app.services.package_method_service import QuoteFreightService
        
        freight = QuoteFreightService.get_quote_freight(freight_id)
        
        return jsonify({
            'success': True,
            'data': freight
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/quote-freights', methods=['POST'])
@jwt_required()
def create_quote_freight():
    """创建报价运费"""
    try:
        from app.services.package_method_service import QuoteFreightService
        
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        freight = QuoteFreightService.create_quote_freight(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': freight,
            'message': '报价运费创建成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/quote-freights/<freight_id>', methods=['PUT'])
@jwt_required()
def update_quote_freight(freight_id):
    """更新报价运费"""
    try:
        from app.services.package_method_service import QuoteFreightService
        
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        freight = QuoteFreightService.update_quote_freight(freight_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': freight,
            'message': '报价运费更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/quote-freights/<freight_id>', methods=['DELETE'])
@jwt_required()
def delete_quote_freight(freight_id):
    """删除报价运费"""
    try:
        from app.services.package_method_service import QuoteFreightService
        
        QuoteFreightService.delete_quote_freight(freight_id)
        
        return jsonify({
            'success': True,
            'message': '报价运费删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/quote-freights/batch', methods=['PUT'])
@jwt_required()
def batch_update_quote_freights():
    """批量更新报价运费"""
    try:
        from app.services.package_method_service import QuoteFreightService
        
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not isinstance(data, list):
            return jsonify({'error': '请求数据必须是数组'}), 400
        
        results = QuoteFreightService.batch_update_quote_freights(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': results,
            'message': f'成功更新 {len(results)} 个报价运费'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 材料分类管理API
@bp.route('/material-categories', methods=['GET'])
@jwt_required()
def get_material_categories():
    """获取材料分类列表"""
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search', '')
        material_type = request.args.get('material_type', '')
        is_enabled = request.args.get('is_enabled', '')
        
        # 转换is_enabled参数
        if is_enabled.lower() == 'true':
            is_enabled = True
        elif is_enabled.lower() == 'false':
            is_enabled = False
        else:
            is_enabled = None
        
        # 获取材料分类列表
        result = MaterialCategoryService.get_material_categories(
            page=page,
            per_page=per_page,
            search=search,
            material_type=material_type,
            is_enabled=is_enabled
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/material-categories/<category_id>', methods=['GET'])
@jwt_required()
def get_material_category(category_id):
    """获取材料分类详情"""
    try:
        category = MaterialCategoryService.get_material_category_by_id(category_id)
        
        if not category:
            return jsonify({'error': '材料分类不存在'}), 404
        
        return jsonify({
            'success': True,
            'data': category
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/material-categories', methods=['POST'])
@jwt_required()
def create_material_category():
    """创建材料分类"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        if not data.get('material_name'):
            return jsonify({'error': '材料分类名称不能为空'}), 400
        
        if not data.get('material_type'):
            return jsonify({'error': '材料属性不能为空'}), 400
        
        category = MaterialCategoryService.create_material_category(data)
        
        return jsonify({
            'success': True,
            'data': category,
            'message': '材料分类创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/material-categories/<category_id>', methods=['PUT'])
@jwt_required()
def update_material_category(category_id):
    """更新材料分类"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        category = MaterialCategoryService.update_material_category(category_id, data)
        
        return jsonify({
            'success': True,
            'data': category,
            'message': '材料分类更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/material-categories/<category_id>', methods=['DELETE'])
@jwt_required()
def delete_material_category(category_id):
    """删除材料分类"""
    try:
        MaterialCategoryService.delete_material_category(category_id)
        
        return jsonify({
            'success': True,
            'message': '材料分类删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/material-categories/batch', methods=['PUT'])
@jwt_required()
def batch_update_material_categories():
    """批量更新材料分类"""
    try:
        data = request.get_json()
        
        if not data or not isinstance(data, list):
            return jsonify({'error': '请求数据格式错误'}), 400
        
        results = MaterialCategoryService.batch_update_material_categories(data)
        
        return jsonify({
            'success': True,
            'data': results,
            'message': '批量更新完成'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/material-categories/options', methods=['GET'])
@jwt_required()
def get_material_category_options():
    """获取材料分类选项数据"""
    try:
        # 获取材料属性选项
        material_types = MaterialCategoryService.get_material_types()
        
        # 获取单位选项
        units = MaterialCategoryService.get_units()
        
        return jsonify({
            'success': True,
            'data': {
                'material_types': material_types,
                'units': units
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===== 产品分类管理 API =====

@bp.route('/product-categories', methods=['GET'])
@jwt_required()
def get_product_categories():
    """获取产品分类列表"""
    try:
        from app.services.package_method_service import ProductCategoryService
        
        # 获取查询参数
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 100)), 100)
        search = request.args.get('search')
        enabled_only = request.args.get('enabled_only', 'false').lower() == 'true'
        
        # 获取当前用户和租户信息
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        if not tenant_id:
            return jsonify({'error': '租户信息缺失'}), 400
        
        # 获取产品分类列表
        result = ProductCategoryService.get_product_categories(
            page=page,
            per_page=per_page,
            search=search,
            enabled_only=enabled_only
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/product-categories/<product_category_id>', methods=['GET'])
@jwt_required()
def get_product_category(product_category_id):
    """获取产品分类详情"""
    try:
        from app.services.package_method_service import ProductCategoryService
        
        product_category = ProductCategoryService.get_product_category(product_category_id)
        
        return jsonify({
            'success': True,
            'data': product_category
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/product-categories', methods=['POST'])
@jwt_required()
def create_product_category():
    """创建产品分类"""
    try:
        from app.services.package_method_service import ProductCategoryService
        
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # 添加调试日志
        current_app.logger.info(f"Creating product category with data: {data}")
        current_app.logger.info(f"Current user ID: {current_user_id}")
        
        if not data:
            current_app.logger.error("Request data is empty")
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        if not data.get('category_name'):
            current_app.logger.error("Category name is missing")
            return jsonify({'error': '产品分类名称不能为空'}), 400
        
        product_category = ProductCategoryService.create_product_category(data, current_user_id)
        
        current_app.logger.info(f"Product category created successfully: {product_category}")
        
        return jsonify({
            'success': True,
            'data': product_category,
            'message': '产品分类创建成功'
        }), 201
        
    except ValueError as e:
        current_app.logger.error(f"ValueError in create_product_category: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Exception in create_product_category: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/product-categories/<product_category_id>', methods=['PUT'])
@jwt_required()
def update_product_category(product_category_id):
    """更新产品分类"""
    try:
        from app.services.package_method_service import ProductCategoryService
        
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        product_category = ProductCategoryService.update_product_category(product_category_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': product_category,
            'message': '产品分类更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/product-categories/<product_category_id>', methods=['DELETE'])
@jwt_required()
def delete_product_category(product_category_id):
    """删除产品分类"""
    try:
        from app.services.package_method_service import ProductCategoryService
        
        ProductCategoryService.delete_product_category(product_category_id)
        
        return jsonify({
            'success': True,
            'message': '产品分类删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/product-categories/batch', methods=['PUT'])
@jwt_required()
def batch_update_product_categories():
    """批量更新产品分类（用于可编辑表格）"""
    try:
        from app.services.package_method_service import ProductCategoryService
        
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not isinstance(data, list):
            return jsonify({'error': '请求数据必须是数组'}), 400
        
        results = ProductCategoryService.batch_update_product_categories(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': results,
            'message': f'成功更新 {len(results)} 个产品分类'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500