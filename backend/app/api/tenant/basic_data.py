# -*- coding: utf-8 -*-
"""
基础档案管理API路由
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services.basic_data_service import (
    CustomerService, CustomerCategoryService, 
    SupplierService, ProductService,
    TenantFieldConfigIntegrationService
)
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