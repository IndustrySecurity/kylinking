# -*- coding: utf-8 -*-
"""
基础档案管理API路由
"""

from flask import Blueprint, request, jsonify, current_app, g
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from .routes import tenant_required
from app.services.basic_data_service import (
    CustomerService, CustomerCategoryService, 
    SupplierService, ProductService,
    TenantFieldConfigIntegrationService,
    CalculationParameterService, CalculationSchemeService, DepartmentService, PositionService, EmployeeService,
    WarehouseService, BagTypeService, TeamGroupService
)
from app.services.material_category_service import MaterialCategoryService
from app.models.user import User
from app.models.basic_data import ProcessCategory
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

# 报价材料管理
@bp.route('/quote-materials', methods=['GET'])
@jwt_required()
def get_quote_materials():
    """获取报价材料列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        enabled_only = request.args.get('enabled_only', False, type=bool)
        
        from app.services.package_method_service import QuoteMaterialService
        result = QuoteMaterialService.get_quote_materials(
            page=page,
            per_page=per_page,
            search=search,
            enabled_only=enabled_only
        )
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': result
        })
        
    except Exception as e:
        current_app.logger.error(f"获取报价材料列表失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'获取失败: {str(e)}',
            'data': None
        }), 500

@bp.route('/quote-materials/<quote_material_id>', methods=['GET'])
@jwt_required()
def get_quote_material(quote_material_id):
    """获取单个报价材料"""
    try:
        from app.services.package_method_service import QuoteMaterialService
        result = QuoteMaterialService.get_quote_material(quote_material_id)
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': result
        })
        
    except ValueError as e:
        return jsonify({
            'code': 404,
            'message': str(e),
            'data': None
        }), 404
    except Exception as e:
        current_app.logger.error(f"获取报价材料失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'获取失败: {str(e)}',
            'data': None
        }), 500

@bp.route('/quote-materials', methods=['POST'])
@jwt_required()
def create_quote_material():
    """创建报价材料"""
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        from app.services.package_method_service import QuoteMaterialService
        result = QuoteMaterialService.create_quote_material(data, current_user_id)
        
        return jsonify({
            'code': 200,
            'message': '创建成功',
            'data': result
        })
        
    except ValueError as e:
        return jsonify({
            'code': 400,
            'message': str(e),
            'data': None
        }), 400
    except Exception as e:
        current_app.logger.error(f"创建报价材料失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'创建失败: {str(e)}',
            'data': None
        }), 500

@bp.route('/quote-materials/<quote_material_id>', methods=['PUT'])
@jwt_required()
def update_quote_material(quote_material_id):
    """更新报价材料"""
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        from app.services.package_method_service import QuoteMaterialService
        result = QuoteMaterialService.update_quote_material(quote_material_id, data, current_user_id)
        
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': result
        })
        
    except ValueError as e:
        return jsonify({
            'code': 404,
            'message': str(e),
            'data': None
        }), 404
    except Exception as e:
        current_app.logger.error(f"更新报价材料失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'更新失败: {str(e)}',
            'data': None
        }), 500

@bp.route('/quote-materials/<quote_material_id>', methods=['DELETE'])
@jwt_required()
def delete_quote_material(quote_material_id):
    """删除报价材料"""
    try:
        from app.services.package_method_service import QuoteMaterialService
        QuoteMaterialService.delete_quote_material(quote_material_id)
        
        return jsonify({
            'code': 200,
            'message': '删除成功',
            'data': None
        })
        
    except ValueError as e:
        return jsonify({
            'code': 404,
            'message': str(e),
            'data': None
        }), 404
    except Exception as e:
        current_app.logger.error(f"删除报价材料失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'删除失败: {str(e)}',
            'data': None
        }), 500

@bp.route('/quote-materials/batch', methods=['PUT'])
@jwt_required()
def batch_update_quote_materials():
    """批量更新报价材料"""
    try:
        data_list = request.get_json()
        current_user_id = get_jwt_identity()
        
        from app.services.package_method_service import QuoteMaterialService
        QuoteMaterialService.batch_update_quote_materials(data_list, current_user_id)
        
        return jsonify({
            'code': 200,
            'message': '批量更新成功',
            'data': None
        })
        
    except Exception as e:
        current_app.logger.error(f"批量更新报价材料失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'批量更新失败: {str(e)}',
            'data': None
        }), 500

@bp.route('/quote-materials/enabled', methods=['GET'])
@jwt_required()
def get_enabled_quote_materials():
    """获取启用的报价材料列表"""
    try:
        from app.services.package_method_service import QuoteMaterialService
        result = QuoteMaterialService.get_enabled_quote_materials()
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': result
        })
        
    except Exception as e:
        current_app.logger.error(f"获取启用报价材料列表失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'获取失败: {str(e)}',
            'data': None
        }), 500


# 报价辅材管理
@bp.route('/quote-accessories', methods=['GET'])
@jwt_required()
def get_quote_accessories():
    """获取报价辅材列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        enabled_only = request.args.get('enabled_only', False, type=bool)
        
        from app.services.package_method_service import QuoteAccessoryService
        result = QuoteAccessoryService.get_quote_accessories(
            page=page,
            per_page=per_page,
            search=search,
            enabled_only=enabled_only
        )
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': result
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting quote accessories: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'获取失败: {str(e)}',
            'data': None
        }), 500


@bp.route('/quote-accessories/<quote_accessory_id>', methods=['GET'])
@jwt_required()
def get_quote_accessory(quote_accessory_id):
    """获取单个报价辅材"""
    try:
        from app.services.package_method_service import QuoteAccessoryService
        result = QuoteAccessoryService.get_quote_accessory(quote_accessory_id)
        
        if result is None:
            return jsonify({
                'code': 404,
                'message': '报价辅材不存在',
                'data': None
            }), 404
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': result
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting quote accessory {quote_accessory_id}: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'获取失败: {str(e)}',
            'data': None
        }), 500


@bp.route('/quote-accessories', methods=['POST'])
@jwt_required()
def create_quote_accessory():
    """创建报价辅材"""
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        from app.services.package_method_service import QuoteAccessoryService
        result = QuoteAccessoryService.create_quote_accessory(data, current_user_id)
        
        return jsonify({
            'code': 200,
            'message': '创建成功',
            'data': result
        })
        
    except Exception as e:
        current_app.logger.error(f"Error creating quote accessory: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'创建失败: {str(e)}',
            'data': None
        }), 500


@bp.route('/quote-accessories/<quote_accessory_id>', methods=['PUT'])
@jwt_required()
def update_quote_accessory(quote_accessory_id):
    """更新报价辅材"""
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        from app.services.package_method_service import QuoteAccessoryService
        result = QuoteAccessoryService.update_quote_accessory(quote_accessory_id, data, current_user_id)
        
        if result is None:
            return jsonify({
                'code': 404,
                'message': '报价辅材不存在',
                'data': None
            }), 404
        
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': result
        })
        
    except Exception as e:
        current_app.logger.error(f"Error updating quote accessory {quote_accessory_id}: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'更新失败: {str(e)}',
            'data': None
        }), 500


@bp.route('/quote-accessories/<quote_accessory_id>', methods=['DELETE'])
@jwt_required()
def delete_quote_accessory(quote_accessory_id):
    """删除报价辅材"""
    try:
        from app.services.package_method_service import QuoteAccessoryService
        success = QuoteAccessoryService.delete_quote_accessory(quote_accessory_id)
        
        if not success:
            return jsonify({
                'code': 404,
                'message': '报价辅材不存在',
                'data': None
            }), 404
        
        return jsonify({
            'code': 200,
            'message': '删除成功',
            'data': None
        })
        
    except Exception as e:
        current_app.logger.error(f"Error deleting quote accessory {quote_accessory_id}: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'删除失败: {str(e)}',
            'data': None
        }), 500


@bp.route('/quote-accessories/batch', methods=['PUT'])
@jwt_required()
def batch_update_quote_accessories():
    """批量更新报价辅材"""
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        from app.services.package_method_service import QuoteAccessoryService
        updated_count = QuoteAccessoryService.batch_update_quote_accessories(data, current_user_id)
        
        return jsonify({
            'code': 200,
            'message': f'批量更新成功，共更新 {updated_count} 条记录',
            'data': {'updated_count': updated_count}
        })
        
    except Exception as e:
        current_app.logger.error(f"Error batch updating quote accessories: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'批量更新失败: {str(e)}',
            'data': None
        }), 500


@bp.route('/quote-accessories/enabled', methods=['GET'])
@jwt_required()
def get_enabled_quote_accessories():
    """获取启用的报价辅材列表"""
    try:
        from app.services.package_method_service import QuoteAccessoryService
        result = QuoteAccessoryService.get_enabled_quote_accessories()
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': result
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting enabled quote accessories: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'获取失败: {str(e)}',
            'data': None
        }), 500

@bp.route('/quote-accessories/calculation-schemes', methods=['GET'])
@jwt_required()
def get_material_quote_calculation_schemes():
    """获取材料报价分类的计算方案选项"""
    try:
        from app.services.basic_data_service import CalculationSchemeService
        
        # 获取材料报价分类的计算方案
        result = CalculationSchemeService.get_calculation_schemes_by_category('material_quote')
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': result
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting material quote calculation schemes: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'获取失败: {str(e)}',
            'data': None
        }), 500

# ===== 报价损耗管理 API =====

@bp.route('/quote-losses', methods=['GET'])
@jwt_required()
def get_quote_losses():
    """获取报价损耗列表"""
    try:
        from app.services.package_method_service import QuoteLossService
        
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
        
        # 获取报价损耗列表
        result = QuoteLossService.get_quote_losses(
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


@bp.route('/quote-losses/<quote_loss_id>', methods=['GET'])
@jwt_required()
def get_quote_loss(quote_loss_id):
    """获取报价损耗详情"""
    try:
        from app.services.package_method_service import QuoteLossService
        
        quote_loss = QuoteLossService.get_quote_loss(quote_loss_id)
        
        return jsonify({
            'success': True,
            'data': quote_loss
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/quote-losses', methods=['POST'])
@jwt_required()
def create_quote_loss():
    """创建报价损耗"""
    try:
        from app.services.package_method_service import QuoteLossService
        
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        required_fields = ['bag_type', 'layer_count', 'meter_range', 'loss_rate', 'cost']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field}不能为空'}), 400
        
        quote_loss = QuoteLossService.create_quote_loss(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': quote_loss,
            'message': '报价损耗创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/quote-losses/<quote_loss_id>', methods=['PUT'])
@jwt_required()
def update_quote_loss(quote_loss_id):
    """更新报价损耗"""
    try:
        from app.services.package_method_service import QuoteLossService
        
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        quote_loss = QuoteLossService.update_quote_loss(quote_loss_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': quote_loss,
            'message': '报价损耗更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/quote-losses/<quote_loss_id>', methods=['DELETE'])
@jwt_required()
def delete_quote_loss(quote_loss_id):
    """删除报价损耗"""
    try:
        from app.services.package_method_service import QuoteLossService
        
        QuoteLossService.delete_quote_loss(quote_loss_id)
        
        return jsonify({
            'success': True,
            'message': '报价损耗删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/quote-losses/batch', methods=['PUT'])
@jwt_required()
def batch_update_quote_losses():
    """批量更新报价损耗"""
    try:
        from app.services.package_method_service import QuoteLossService
        
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not isinstance(data, list):
            return jsonify({'error': '请求数据格式错误'}), 400
        
        results = QuoteLossService.batch_update_quote_losses(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': results,
            'message': '批量更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/quote-losses/enabled', methods=['GET'])
@jwt_required()
def get_enabled_quote_losses():
    """获取启用的报价损耗列表"""
    try:
        from app.services.package_method_service import QuoteLossService
        
        quote_losses = QuoteLossService.get_enabled_quote_losses()
        
        return jsonify({
            'success': True,
            'data': quote_losses
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 计算参数管理API
@bp.route('/calculation-parameters', methods=['GET'])
@jwt_required()
def get_calculation_parameters():
    """获取计算参数列表"""
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search', '')
        
        # 获取计算参数列表
        result = CalculationParameterService.get_calculation_parameters(
            page=page,
            per_page=per_page,
            search=search
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/calculation-parameters/<param_id>', methods=['GET'])
@jwt_required()
def get_calculation_parameter(param_id):
    """获取计算参数详情"""
    try:
        param = CalculationParameterService.get_calculation_parameter(param_id)
        
        return jsonify({
            'success': True,
            'data': param
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/calculation-parameters', methods=['POST'])
@jwt_required()
def create_calculation_parameter():
    """创建计算参数"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        if not data.get('parameter_name'):
            return jsonify({'error': '计算参数名称不能为空'}), 400
        
        param = CalculationParameterService.create_calculation_parameter(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': param,
            'message': '计算参数创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/calculation-parameters/<param_id>', methods=['PUT'])
@jwt_required()
def update_calculation_parameter(param_id):
    """更新计算参数"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        param = CalculationParameterService.update_calculation_parameter(param_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': param,
            'message': '计算参数更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/calculation-parameters/<param_id>', methods=['DELETE'])
@jwt_required()
def delete_calculation_parameter(param_id):
    """删除计算参数"""
    try:
        CalculationParameterService.delete_calculation_parameter(param_id)
        
        return jsonify({
            'success': True,
            'message': '计算参数删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/calculation-parameters/batch', methods=['PUT'])
@jwt_required()
def batch_update_calculation_parameters():
    """批量更新计算参数"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not isinstance(data, list):
            return jsonify({'error': '请求数据必须是数组'}), 400
        
        results = CalculationParameterService.batch_update_calculation_parameters(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': results,
            'message': f'成功更新 {len(results)} 个计算参数'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/calculation-parameters/options', methods=['GET'])
@jwt_required()
def get_calculation_parameter_options():
    """获取计算参数选项数据"""
    try:
        options = CalculationParameterService.get_calculation_parameter_options()
        
        return jsonify({
            'success': True,
            'data': options
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 计算方案管理API
@bp.route('/calculation-schemes', methods=['GET'])
@jwt_required()
def get_calculation_schemes():
    """获取计算方案列表"""
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search', '')
        category = request.args.get('category', '')
        
        # 获取计算方案列表
        result = CalculationSchemeService.get_calculation_schemes(
            page=page,
            per_page=per_page,
            search=search,
            category=category if category else None
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/calculation-schemes/<scheme_id>', methods=['GET'])
@jwt_required()
def get_calculation_scheme(scheme_id):
    """获取计算方案详情"""
    try:
        scheme = CalculationSchemeService.get_calculation_scheme(scheme_id)
        
        return jsonify({
            'success': True,
            'data': scheme
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/calculation-schemes', methods=['POST'])
@jwt_required()
def create_calculation_scheme():
    """创建计算方案"""
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        # 创建计算方案
        scheme = CalculationSchemeService.create_calculation_scheme(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': scheme,
            'message': '创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/calculation-schemes/<scheme_id>', methods=['PUT'])
@jwt_required()
def update_calculation_scheme(scheme_id):
    """更新计算方案"""
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        # 更新计算方案
        scheme = CalculationSchemeService.update_calculation_scheme(scheme_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': scheme,
            'message': '更新成功'
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/calculation-schemes/<scheme_id>', methods=['DELETE'])
@jwt_required()
def delete_calculation_scheme(scheme_id):
    """删除计算方案"""
    try:
        CalculationSchemeService.delete_calculation_scheme(scheme_id)
        
        return jsonify({
            'success': True,
            'message': '删除成功'
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/calculation-schemes/categories', methods=['GET'])
@jwt_required()
def get_scheme_categories():
    """获取方案分类选项"""
    try:
        result = CalculationSchemeService.get_scheme_categories()
        
        return jsonify({
            'success': True,
            'data': {
                'scheme_categories': result
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/calculation-schemes/validate-formula', methods=['POST'])
@jwt_required()
def validate_formula():
    """验证计算公式"""
    try:
        data = request.get_json()
        formula = data.get('formula', '')
        
        result = CalculationSchemeService.validate_formula(formula)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/calculation-schemes/options', methods=['GET'])
@jwt_required()
def get_calculation_scheme_options():
    """获取计算方案选项数据"""
    try:
        result = CalculationSchemeService.get_calculation_scheme_options()
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/calculation-schemes/options-by-category', methods=['GET'])
@jwt_required()
def get_calculation_scheme_options_by_category():
    """获取按类别分组的计算方案选项数据"""
    try:
        result = CalculationSchemeService.get_calculation_scheme_options_by_category()
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


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
        is_enabled_str = request.args.get('is_enabled', '')
        
        # 处理is_enabled参数
        is_enabled = None
        if is_enabled_str.lower() == 'true':
            is_enabled = True
        elif is_enabled_str.lower() == 'false':
            is_enabled = False
        
        # 获取材料分类列表
        result = MaterialCategoryService.get_material_categories(
            page=page,
            per_page=per_page,
            search=search if search else None,
            material_type=material_type if material_type else None,
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
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/material-categories', methods=['POST'])
@jwt_required()
def create_material_category():
    """创建材料分类"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        if not data.get('material_name'):
            return jsonify({'error': '材料分类名称不能为空'}), 400
        
        if not data.get('material_type'):
            return jsonify({'error': '材料属性不能为空'}), 400
        
        category = MaterialCategoryService.create_material_category(data, current_user_id)
        
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
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        category = MaterialCategoryService.update_material_category(category_id, data, current_user_id)
        
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
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not isinstance(data, list):
            return jsonify({'error': '请求数据必须是数组'}), 400
        
        # 为每个更新记录添加updated_by信息
        for item in data:
            item['updated_by'] = current_user_id
        
        results = MaterialCategoryService.batch_update_material_categories(data)
        
        return jsonify({
            'success': True,
            'data': results,
            'message': f'成功更新 {len(results)} 个材料分类'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
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


# 产品分类管理API
@bp.route('/product-categories', methods=['GET'])
@jwt_required()
def get_product_categories():
    """获取产品分类列表"""
    try:
        from app.services.package_method_service import ProductCategoryService
        
        # 获取查询参数
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search', '')
        enabled_only_str = request.args.get('enabled_only', '')
        
        # 处理enabled_only参数
        enabled_only = enabled_only_str.lower() == 'true' if enabled_only_str else False
        
        # 获取产品分类列表
        result = ProductCategoryService.get_product_categories(
            page=page,
            per_page=per_page,
            search=search if search else None,
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
        
        category = ProductCategoryService.get_product_category(product_category_id)
        
        return jsonify({
            'success': True,
            'data': category
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
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        if not data.get('category_name'):
            return jsonify({'error': '产品分类名称不能为空'}), 400
        
        category = ProductCategoryService.create_product_category(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': category,
            'message': '产品分类创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
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
        
        category = ProductCategoryService.update_product_category(product_category_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': category,
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
    """批量更新产品分类"""
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


@bp.route('/product-categories/enabled', methods=['GET'])
@jwt_required()
def get_enabled_product_categories():
    """获取启用的产品分类列表"""
    try:
        from app.models.basic_data import ProductCategory
        
        product_categories = ProductCategory.get_enabled_list()
        
        return jsonify({
            'success': True,
            'data': [category.to_dict() for category in product_categories]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 部门管理路由
@bp.route('/departments', methods=['GET'])
@jwt_required()
def get_departments():
    """获取部门列表"""
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search')
        
        result = DepartmentService.get_departments(
            page=page,
            per_page=per_page,
            search=search
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/departments/<dept_id>', methods=['GET'])
@jwt_required()
def get_department(dept_id):
    """获取部门详情"""
    try:
        department = DepartmentService.get_department(dept_id)
        
        return jsonify({
            'success': True,
            'data': department
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/departments', methods=['POST'])
@jwt_required()
def create_department():
    """创建部门"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        if not data.get('dept_name'):
            return jsonify({'error': '部门名称不能为空'}), 400
        
        department = DepartmentService.create_department(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': department,
            'message': '部门创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/departments/<dept_id>', methods=['PUT'])
@jwt_required()
def update_department(dept_id):
    """更新部门"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        department = DepartmentService.update_department(dept_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': department,
            'message': '部门更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/departments/<dept_id>', methods=['DELETE'])
@jwt_required()
def delete_department(dept_id):
    """删除部门"""
    try:
        DepartmentService.delete_department(dept_id)
        
        return jsonify({
            'success': True,
            'message': '部门删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/departments/batch', methods=['PUT'])
@jwt_required()
def batch_update_departments():
    """批量更新部门"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not isinstance(data, list):
            return jsonify({'error': '请求数据格式错误'}), 400
        
        departments = DepartmentService.batch_update_departments(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': departments,
            'message': '部门批量更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/departments/options', methods=['GET'])
@jwt_required()
def get_department_options():
    """获取部门选项数据"""
    try:
        options = DepartmentService.get_department_options()
        
        return jsonify({
            'success': True,
            'data': options
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/departments/tree', methods=['GET'])
@jwt_required()
def get_department_tree():
    """获取部门树形结构"""
    try:
        tree = DepartmentService.get_department_tree()
        
        return jsonify({
            'success': True,
            'data': tree
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 职位管理接口
@bp.route('/positions', methods=['GET'])
@jwt_required()
def get_positions():
    """获取职位列表"""
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search', '')
        department_id = request.args.get('department_id', '')
        
        result = PositionService.get_positions(
            page=page,
            per_page=per_page,
            search=search,
            department_id=department_id if department_id else None
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/positions/<position_id>', methods=['GET'])
@jwt_required()
def get_position(position_id):
    """获取职位详情"""
    try:
        result = PositionService.get_position(position_id)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/positions', methods=['POST'])
@jwt_required()
def create_position():
    """创建职位"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
            
        if not data.get('position_name'):
            return jsonify({'error': '职位名称不能为空'}), 400
            
        if not data.get('department_id'):
            return jsonify({'error': '部门不能为空'}), 400
        
        result = PositionService.create_position(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '职位创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/positions/<position_id>', methods=['PUT'])
@jwt_required()
def update_position(position_id):
    """更新职位"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        result = PositionService.update_position(position_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '职位更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/positions/<position_id>', methods=['DELETE'])
@jwt_required()
def delete_position(position_id):
    """删除职位"""
    try:
        PositionService.delete_position(position_id)
        
        return jsonify({
            'success': True,
            'message': '职位删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/positions/options', methods=['GET'])
@jwt_required()
def get_position_options():
    """获取职位选项数据"""
    try:
        department_id = request.args.get('department_id')
        
        result = PositionService.get_position_options(department_id)
        
        return jsonify({
            'success': True,
            'data': {
                'positions': result
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== 员工管理 ====================

@bp.route('/employees', methods=['GET'])
@jwt_required()
def get_employees():
    """获取员工列表"""
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search')
        department_id = request.args.get('department_id')
        position_id = request.args.get('position_id')
        employment_status = request.args.get('employment_status')
        
        result = EmployeeService.get_employees(
            page=page,
            per_page=per_page,
            search=search,
            department_id=department_id,
            position_id=position_id,
            employment_status=employment_status
        )
        
        return jsonify({
            'success': True,
            'data': result['employees'],
            'pagination': {
                'page': result['current_page'],
                'per_page': result['per_page'],
                'total': result['total'],
                'pages': result['pages']
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/employees/<employee_id>', methods=['GET'])
@jwt_required()
def get_employee(employee_id):
    """获取员工详情"""
    try:
        result = EmployeeService.get_employee(employee_id)
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/employees', methods=['POST'])
@jwt_required()
def create_employee():
    """创建员工"""
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        
        result = EmployeeService.create_employee(data, user_id)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/employees/<employee_id>', methods=['PUT'])
@jwt_required()
def update_employee(employee_id):
    """更新员工"""
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        
        result = EmployeeService.update_employee(employee_id, data, user_id)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/employees/<employee_id>', methods=['DELETE'])
@jwt_required()
def delete_employee(employee_id):
    """删除员工"""
    try:
        result = EmployeeService.delete_employee(employee_id)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/employees/batch', methods=['PUT'])
@jwt_required()
def batch_update_employees():
    """批量更新员工"""
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        updates = data.get('updates', [])
        
        result = EmployeeService.batch_update_employees(updates, user_id)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/employees/options', methods=['GET'])
@jwt_required()
def get_employee_options():
    """获取员工选项"""
    try:
        result = EmployeeService.get_employee_options()
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/employees/employment-status-options', methods=['GET'])
@jwt_required()
def get_employment_status_options():
    """获取在职状态选项"""
    try:
        options = EmployeeService.get_employment_status_options()
        return jsonify({
            'success': True,
            'data': options
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/employees/business-type-options', methods=['GET'])
@jwt_required()
def get_business_type_options():
    """获取业务类型选项"""
    try:
        options = EmployeeService.get_business_type_options()
        return jsonify({
            'success': True,
            'data': options
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/employees/gender-options', methods=['GET'])
@jwt_required()
def get_gender_options():
    """获取性别选项"""
    try:
        options = EmployeeService.get_gender_options()
        return jsonify({
            'success': True,
            'data': options
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/employees/evaluation-level-options', methods=['GET'])
@jwt_required()
def get_evaluation_level_options():
    """获取评量流程级别选项"""
    try:
        options = EmployeeService.get_evaluation_level_options()
        return jsonify({
            'success': True,
            'data': options
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/employees/next-employee-id', methods=['GET'])
@jwt_required()
def get_next_employee_id():
    """获取下一个员工工号"""
    try:
        from app.models.basic_data import Employee
        
        # 生成下一个员工工号
        next_id = Employee.generate_employee_id()
        
        return jsonify({
            'success': True,
            'data': {
                'employee_id': next_id
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# ====================== 仓库管理 ======================

@bp.route('/warehouses', methods=['GET'])
@jwt_required()
def get_warehouses():
    """获取仓库列表"""
    try:
        from app.services.basic_data_service import WarehouseService
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '').strip()
        warehouse_type = request.args.get('warehouse_type', '').strip()
        parent_warehouse_id = request.args.get('parent_warehouse_id', '').strip()
        
        result = WarehouseService.get_warehouses(
            page=page,
            per_page=per_page,
            search=search if search else None,
            warehouse_type=warehouse_type if warehouse_type else None,
            parent_warehouse_id=parent_warehouse_id if parent_warehouse_id else None
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/warehouses/<warehouse_id>', methods=['GET'])
@jwt_required()
def get_warehouse(warehouse_id):
    """获取仓库详情"""
    try:
        from app.services.basic_data_service import WarehouseService
        
        result = WarehouseService.get_warehouse(warehouse_id)
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/warehouses', methods=['POST'])
@jwt_required()
def create_warehouse():
    """创建仓库"""
    try:
        from app.services.basic_data_service import WarehouseService
        
        data = request.get_json()
        user_id = get_jwt_identity()
        
        result = WarehouseService.create_warehouse(data, user_id)
        return jsonify({
            'success': True,
            'data': result,
            'message': '仓库创建成功'
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/warehouses/<warehouse_id>', methods=['PUT'])
@jwt_required()
def update_warehouse(warehouse_id):
    """更新仓库"""
    try:
        from app.services.basic_data_service import WarehouseService
        
        data = request.get_json()
        user_id = get_jwt_identity()
        
        result = WarehouseService.update_warehouse(warehouse_id, data, user_id)
        return jsonify({
            'success': True,
            'data': result,
            'message': '仓库更新成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/warehouses/<warehouse_id>', methods=['DELETE'])
@jwt_required()
def delete_warehouse(warehouse_id):
    """删除仓库"""
    try:
        from app.services.basic_data_service import WarehouseService
        
        result = WarehouseService.delete_warehouse(warehouse_id)
        return jsonify({
            'success': True,
            'message': '仓库删除成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/warehouses/batch', methods=['PUT'])
@jwt_required()
def batch_update_warehouses():
    """批量更新仓库"""
    try:
        from app.services.basic_data_service import WarehouseService
        
        data = request.get_json()
        user_id = get_jwt_identity()
        updates = data.get('updates', [])
        
        result = WarehouseService.batch_update_warehouses(updates, user_id)
        return jsonify({
            'success': True,
            'data': result,
            'message': '批量更新成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/warehouses/options', methods=['GET'])
@jwt_required()
def get_warehouse_options():
    """获取仓库选项"""
    try:
        from app.services.basic_data_service import WarehouseService
        
        result = WarehouseService.get_warehouse_options()
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/warehouses/tree', methods=['GET'])
@jwt_required()
def get_warehouse_tree():
    """获取仓库树形结构"""
    try:
        from app.services.basic_data_service import WarehouseService
        
        result = WarehouseService.get_warehouse_tree()
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/warehouses/types', methods=['GET'])
@jwt_required()
def get_warehouse_types():
    """获取仓库类型选项"""
    try:
        from app.services.basic_data_service import WarehouseService
        
        result = WarehouseService.get_warehouse_types()
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/warehouses/accounting-methods', methods=['GET'])
@jwt_required()
def get_accounting_methods():
    """获取核算方式选项"""
    try:
        from app.services.basic_data_service import WarehouseService
        
        result = WarehouseService.get_accounting_methods()
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/warehouses/circulation-types', methods=['GET'])
@jwt_required()
def get_circulation_types():
    """获取流转类型选项"""
    try:
        from app.services.basic_data_service import WarehouseService
        
        result = WarehouseService.get_circulation_types()
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/warehouses/next-warehouse-code', methods=['GET'])
@jwt_required()
def get_next_warehouse_code():
    """获取下一个仓库编号"""
    try:
        from app.models.basic_data import Warehouse
        
        # 生成下一个仓库编号
        next_code = Warehouse.generate_warehouse_code()
        
        return jsonify({
            'success': True,
            'data': {
                'warehouse_code': next_code
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# ====================== 机台管理 ======================

@bp.route('/machines', methods=['GET'])
@jwt_required()
def get_machines():
    """获取机台列表"""
    try:
        from app.services.package_method_service import MachineService
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '').strip()
        enabled_only = request.args.get('enabled_only', False, type=bool)
        
        result = MachineService.get_machines(
            page=page,
            per_page=per_page,
            search=search if search else None,
            enabled_only=enabled_only
        )
        
        # 转换响应格式以匹配前端期望
        transformed_result = {
            'machines': result['items'],
            'total': result['total'],
            'pages': result['pages'],
            'current_page': result['current_page'],
            'per_page': result['per_page'],
            'has_next': result['has_next'],
            'has_prev': result['has_prev']
        }
        
        return jsonify({
            'success': True,
            'data': transformed_result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/machines/<machine_id>', methods=['GET'])
@jwt_required()
def get_machine(machine_id):
    """获取机台详情"""
    try:
        from app.services.package_method_service import MachineService
        
        result = MachineService.get_machine(machine_id)
        if not result:
            return jsonify({
                'success': False,
                'message': '机台不存在'
            }), 404
            
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/machines', methods=['POST'])
@jwt_required()
def create_machine():
    """创建机台"""
    try:
        from app.services.package_method_service import MachineService
        
        data = request.get_json()
        user_id = get_jwt_identity()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
        
        if not data.get('machine_name'):
            return jsonify({
                'success': False,
                'message': '机台名称不能为空'
            }), 400
        
        result = MachineService.create_machine(data, user_id)
        return jsonify({
            'success': True,
            'data': result,
            'message': '机台创建成功'
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/machines/<machine_id>', methods=['PUT'])
@jwt_required()
def update_machine(machine_id):
    """更新机台"""
    try:
        from app.services.package_method_service import MachineService
        
        data = request.get_json()
        user_id = get_jwt_identity()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
        
        result = MachineService.update_machine(machine_id, data, user_id)
        return jsonify({
            'success': True,
            'data': result,
            'message': '机台更新成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/machines/<machine_id>', methods=['DELETE'])
@jwt_required()
def delete_machine(machine_id):
    """删除机台"""
    try:
        from app.services.package_method_service import MachineService
        
        MachineService.delete_machine(machine_id)
        return jsonify({
            'success': True,
            'message': '机台删除成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/machines/batch', methods=['PUT'])
@jwt_required()
def batch_update_machines():
    """批量更新机台"""
    try:
        from app.services.package_method_service import MachineService
        
        data = request.get_json()
        user_id = get_jwt_identity()
        
        if not data or not isinstance(data, list):
            return jsonify({
                'success': False,
                'message': '请求数据格式错误'
            }), 400
        
        result = MachineService.batch_update_machines(data, user_id)
        return jsonify({
            'success': True,
            'data': result,
            'message': '批量更新成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/machines/enabled', methods=['GET'])
@jwt_required()
def get_enabled_machines():
    """获取启用的机台列表"""
    try:
        from app.services.package_method_service import MachineService
        
        result = MachineService.get_enabled_machines()
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f'获取启用的机台列表失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'获取启用的机台列表失败: {str(e)}'
        }), 500

# ====================== 报损类型管理 ======================

@bp.route('/loss-types', methods=['GET'])
@jwt_required()
def get_loss_types():
    """获取报损类型列表"""
    try:
        from app.services.package_method_service import LossTypeService
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '').strip()
        enabled_only = request.args.get('enabled_only', False, type=bool)
        
        result = LossTypeService.get_loss_types(
            page=page,
            per_page=per_page,
            search=search if search else None,
            enabled_only=enabled_only
        )
        
        # 转换响应格式以匹配前端期望
        transformed_result = {
            'loss_types': result['items'],
            'total': result['total'],
            'pages': result['pages'],
            'current_page': result['current_page'],
            'per_page': result['per_page'],
            'has_next': result['has_next'],
            'has_prev': result['has_prev']
        }
        
        return jsonify({
            'success': True,
            'data': transformed_result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/loss-types/<loss_type_id>', methods=['GET'])
@jwt_required()
def get_loss_type(loss_type_id):
    """获取报损类型详情"""
    try:
        from app.services.package_method_service import LossTypeService
        
        # 由于LossTypeService没有单独的get_loss_type方法，我们需要添加一个简单的实现
        from app.models.basic_data import LossType
        import uuid
        
        try:
            loss_type_uuid = uuid.UUID(loss_type_id)
        except ValueError:
            return jsonify({
                'success': False,
                'message': '无效的报损类型ID'
            }), 400
        
        loss_type = LossType.query.get(loss_type_uuid)
        if not loss_type:
            return jsonify({
                'success': False,
                'message': '报损类型不存在'
            }), 404
            
        return jsonify({
            'success': True,
            'data': loss_type.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/loss-types', methods=['POST'])
@jwt_required()
def create_loss_type():
    """创建报损类型"""
    try:
        from app.services.package_method_service import LossTypeService
        
        data = request.get_json()
        user_id = get_jwt_identity()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
        
        if not data.get('loss_type_name'):
            return jsonify({
                'success': False,
                'message': '报损类型名称不能为空'
            }), 400
        
        result = LossTypeService.create_loss_type(data, user_id)
        return jsonify({
            'success': True,
            'data': result,
            'message': '报损类型创建成功'
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/loss-types/<loss_type_id>', methods=['PUT'])
@jwt_required()
def update_loss_type(loss_type_id):
    """更新报损类型"""
    try:
        from app.services.package_method_service import LossTypeService
        
        data = request.get_json()
        user_id = get_jwt_identity()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
        
        result = LossTypeService.update_loss_type(loss_type_id, data, user_id)
        return jsonify({
            'success': True,
            'data': result,
            'message': '报损类型更新成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/loss-types/<loss_type_id>', methods=['DELETE'])
@jwt_required()
def delete_loss_type(loss_type_id):
    """删除报损类型"""
    try:
        from app.services.package_method_service import LossTypeService
        
        LossTypeService.delete_loss_type(loss_type_id)
        return jsonify({
            'success': True,
            'message': '报损类型删除成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/loss-types/batch', methods=['PUT'])
@jwt_required()
def batch_update_loss_types():
    """批量更新报损类型"""
    try:
        from app.services.package_method_service import LossTypeService
        
        data = request.get_json()
        user_id = get_jwt_identity()
        
        if not data or not isinstance(data, list):
            return jsonify({
                'success': False,
                'message': '请求数据格式错误'
            }), 400
        
        result = LossTypeService.batch_update_loss_types(data, user_id)
        return jsonify({
            'success': True,
            'data': result,
            'message': '批量更新成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/loss-types/enabled', methods=['GET'])
@jwt_required()
def get_enabled_loss_types():
    """获取启用的报损类型列表"""
    try:
        from app.services.package_method_service import LossTypeService
        
        result = LossTypeService.get_enabled_loss_types()
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# ====================== 报价油墨管理 ======================

@bp.route('/quote-inks', methods=['GET'])
@jwt_required()
def get_quote_inks():
    """获取报价油墨列表"""
    try:
        from app.services.package_method_service import QuoteInkService
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '').strip()
        enabled_only = request.args.get('enabled_only', False, type=bool)
        
        result = QuoteInkService.get_quote_inks(
            page=page,
            per_page=per_page,
            search=search if search else None,
            enabled_only=enabled_only
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/quote-inks/<quote_ink_id>', methods=['GET'])
@jwt_required()
def get_quote_ink(quote_ink_id):
    """获取报价油墨详情"""
    try:
        from app.services.package_method_service import QuoteInkService
        
        result = QuoteInkService.get_quote_ink(quote_ink_id)
        if not result:
            return jsonify({
                'success': False,
                'message': '报价油墨不存在'
            }), 404
            
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/quote-inks', methods=['POST'])
@jwt_required()
def create_quote_ink():
    """创建报价油墨"""
    try:
        from app.services.package_method_service import QuoteInkService
        
        data = request.get_json()
        user_id = get_jwt_identity()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
        
        result = QuoteInkService.create_quote_ink(data, user_id)
        return jsonify({
            'success': True,
            'data': result,
            'message': '报价油墨创建成功'
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/quote-inks/<quote_ink_id>', methods=['PUT'])
@jwt_required()
def update_quote_ink(quote_ink_id):
    """更新报价油墨"""
    try:
        from app.services.package_method_service import QuoteInkService
        
        data = request.get_json()
        user_id = get_jwt_identity()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
        
        result = QuoteInkService.update_quote_ink(quote_ink_id, data, user_id)
        return jsonify({
            'success': True,
            'data': result,
            'message': '报价油墨更新成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/quote-inks/<quote_ink_id>', methods=['DELETE'])
@jwt_required()
def delete_quote_ink(quote_ink_id):
    """删除报价油墨"""
    try:
        from app.services.package_method_service import QuoteInkService
        
        QuoteInkService.delete_quote_ink(quote_ink_id)
        return jsonify({
            'success': True,
            'message': '报价油墨删除成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/quote-inks/batch', methods=['PUT'])
@jwt_required()
def batch_update_quote_inks():
    """批量更新报价油墨"""
    try:
        from app.services.package_method_service import QuoteInkService
        
        data = request.get_json()
        user_id = get_jwt_identity()
        
        if not data or not isinstance(data, list):
            return jsonify({
                'success': False,
                'message': '请求数据格式错误'
            }), 400
        
        result = QuoteInkService.batch_update_quote_inks(data, user_id)
        return jsonify({
            'success': True,
            'data': result,
            'message': '批量更新成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/quote-inks/enabled', methods=['GET'])
@jwt_required()
def get_enabled_quote_inks():
    """获取启用的报价油墨列表"""
    try:
        from app.services.package_method_service import QuoteInkService
        
        result = QuoteInkService.get_enabled_quote_inks()
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# ====================== 工序分类管理 ======================

@bp.route('/process-categories', methods=['GET'])
@jwt_required()
def get_process_categories():
    """获取工序分类列表"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        
        # 构建查询
        query = ProcessCategory.query
        
        # 搜索功能
        if search:
            query = query.filter(
                db.or_(
                    ProcessCategory.process_name.ilike(f'%{search}%'),
                    ProcessCategory.category_type.ilike(f'%{search}%')
                )
            )
        
        # 分页查询
        pagination = query.order_by(ProcessCategory.sort_order, ProcessCategory.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {
                'items': [item.to_dict(include_user_info=True) for item in pagination.items],
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page,
                'per_page': per_page
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"获取工序分类列表失败: {str(e)}")
        return jsonify({'code': 500, 'message': f'获取失败: {str(e)}'})


@bp.route('/process-categories/<process_category_id>', methods=['GET'])
@jwt_required()
def get_process_category(process_category_id):
    """获取单个工序分类详情"""
    try:
        process_category = ProcessCategory.query.get_or_404(process_category_id)
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': process_category.to_dict(include_user_info=True)
        })
        
    except Exception as e:
        current_app.logger.error(f"获取工序分类详情失败: {str(e)}")
        return jsonify({'code': 500, 'message': f'获取失败: {str(e)}'})


@bp.route('/process-categories', methods=['POST'])
@jwt_required()
def create_process_category():
    """创建工序分类"""
    try:
        data = request.get_json()
        
        # 数据验证
        if not data.get('process_name'):
            return jsonify({'code': 400, 'message': '工序分类名称不能为空'})
        
        # 检查名称是否重复
        existing = ProcessCategory.query.filter_by(process_name=data['process_name']).first()
        if existing:
            return jsonify({'code': 400, 'message': '工序分类名称已存在'})
        
        # 创建工序分类
        process_category = ProcessCategory(
            process_name=data['process_name'],
            created_by=get_jwt_identity()
        )
        
        # 设置其他字段
        for field in ['category_type', 'sort_order', 'data_collection_mode', 'show_data_collection_interface', 
                     'description', 'is_enabled'] + \
                    [f'self_check_type_{i}' for i in range(1, 11)] + \
                    [f'process_material_{i}' for i in range(1, 11)] + \
                    ['reserved_popup_1', 'reserved_popup_2', 'reserved_popup_3'] + \
                    ['reserved_dropdown_1', 'reserved_dropdown_2', 'reserved_dropdown_3'] + \
                    [f'number_{i}' for i in range(1, 5)]:
            if field in data:
                setattr(process_category, field, data[field])
        
        # 设置布尔字段
        boolean_fields = [
            'report_quantity', 'report_personnel', 'report_data', 'report_kg', 'report_number',
            'report_time', 'down_report_time', 'machine_speed', 'cutting_specs', 'aging_room',
            'reserved_char_1', 'reserved_char_2', 'net_weight', 'production_task_display_order',
            'packing_bags_count', 'pallet_barcode', 'pallet_bag_loading', 'box_loading_count',
            'seed_bag_count', 'defect_bag_count', 'report_staff', 'shortage_count', 'material_specs',
            'color_mixing_count', 'batch_bags', 'production_date', 'compound', 'process_machine_allocation',
            'continuity_rate', 'strip_head_change_count', 'plate_support_change_count', 'plate_change_count',
            'lamination_change_count', 'plate_making_multiple', 'algorithm_time', 'timing', 'pallet_time',
            'glue_water_change_count', 'glue_drip_bag_change', 'pallet_sub_bag_change', 'transfer_report_change',
            'auto_print', 'process_rate', 'color_set_change_count', 'mesh_format_change_count', 'overtime',
            'team_date', 'sampling_time', 'start_reading', 'count_times', 'blade_count', 'power_consumption',
            'maintenance_time', 'end_time', 'malfunction_material_collection', 'is_query_machine',
            'mes_report_kg_manual', 'mes_kg_auto_calculation', 'auto_weighing_once', 'mes_process_feedback_clear',
            'mes_consumption_solvent_by_ton', 'single_report_open', 'multi_condition_open', 'mes_line_start_work_order',
            'mes_material_kg_consumption', 'mes_report_not_less_than_kg', 'mes_water_consumption_by_ton'
        ]
        
        for field in boolean_fields:
            if field in data:
                setattr(process_category, field, data[field])
        
        db.session.add(process_category)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '创建成功',
            'data': process_category.to_dict(include_user_info=True)
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"创建工序分类失败: {str(e)}")
        return jsonify({'code': 500, 'message': f'创建失败: {str(e)}'})


@bp.route('/process-categories/<process_category_id>', methods=['PUT'])
@jwt_required()
def update_process_category(process_category_id):
    """更新工序分类"""
    try:
        process_category = ProcessCategory.query.get_or_404(process_category_id)
        data = request.get_json()
        
        # 数据验证
        if not data.get('process_name'):
            return jsonify({'code': 400, 'message': '工序分类名称不能为空'})
        
        # 检查名称是否重复（排除自己）
        existing = ProcessCategory.query.filter(
            ProcessCategory.process_name == data['process_name'],
            ProcessCategory.id != process_category_id
        ).first()
        if existing:
            return jsonify({'code': 400, 'message': '工序分类名称已存在'})
        
        # 更新字段
        process_category.process_name = data['process_name']
        process_category.updated_by = get_jwt_identity()
        
        # 设置其他字段
        for field in ['category_type', 'sort_order', 'data_collection_mode', 'show_data_collection_interface',
                     'description', 'is_enabled'] + \
                    [f'self_check_type_{i}' for i in range(1, 11)] + \
                    [f'process_material_{i}' for i in range(1, 11)] + \
                    ['reserved_popup_1', 'reserved_popup_2', 'reserved_popup_3'] + \
                    ['reserved_dropdown_1', 'reserved_dropdown_2', 'reserved_dropdown_3'] + \
                    [f'number_{i}' for i in range(1, 5)]:
            if field in data:
                setattr(process_category, field, data[field])
        
        # 设置布尔字段
        boolean_fields = [
            'report_quantity', 'report_personnel', 'report_data', 'report_kg', 'report_number',
            'report_time', 'down_report_time', 'machine_speed', 'cutting_specs', 'aging_room',
            'reserved_char_1', 'reserved_char_2', 'net_weight', 'production_task_display_order',
            'packing_bags_count', 'pallet_barcode', 'pallet_bag_loading', 'box_loading_count',
            'seed_bag_count', 'defect_bag_count', 'report_staff', 'shortage_count', 'material_specs',
            'color_mixing_count', 'batch_bags', 'production_date', 'compound', 'process_machine_allocation',
            'continuity_rate', 'strip_head_change_count', 'plate_support_change_count', 'plate_change_count',
            'lamination_change_count', 'plate_making_multiple', 'algorithm_time', 'timing', 'pallet_time',
            'glue_water_change_count', 'glue_drip_bag_change', 'pallet_sub_bag_change', 'transfer_report_change',
            'auto_print', 'process_rate', 'color_set_change_count', 'mesh_format_change_count', 'overtime',
            'team_date', 'sampling_time', 'start_reading', 'count_times', 'blade_count', 'power_consumption',
            'maintenance_time', 'end_time', 'malfunction_material_collection', 'is_query_machine',
            'mes_report_kg_manual', 'mes_kg_auto_calculation', 'auto_weighing_once', 'mes_process_feedback_clear',
            'mes_consumption_solvent_by_ton', 'single_report_open', 'multi_condition_open', 'mes_line_start_work_order',
            'mes_material_kg_consumption', 'mes_report_not_less_than_kg', 'mes_water_consumption_by_ton'
        ]
        
        for field in boolean_fields:
            if field in data:
                setattr(process_category, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': process_category.to_dict(include_user_info=True)
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"更新工序分类失败: {str(e)}")
        return jsonify({'code': 500, 'message': f'更新失败: {str(e)}'})


@bp.route('/process-categories/<process_category_id>', methods=['DELETE'])
@jwt_required()
def delete_process_category(process_category_id):
    """删除工序分类"""
    try:
        process_category = ProcessCategory.query.get_or_404(process_category_id)
        
        # 可以添加删除前的业务逻辑检查
        
        db.session.delete(process_category)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '删除成功'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"删除工序分类失败: {str(e)}")
        return jsonify({'code': 500, 'message': f'删除失败: {str(e)}'})


@bp.route('/process-categories/batch', methods=['POST'])
@jwt_required()
def batch_update_process_categories():
    """批量更新工序分类"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'code': 400,
                'message': '请求数据不能为空'
            }), 400
        
        from app.services.package_method_service import ProcessCategoryService
        from flask_jwt_extended import get_jwt_identity
        
        updated_by = get_jwt_identity()
        results = ProcessCategoryService.batch_update_process_categories(data, updated_by)
        
        return jsonify({
            'code': 200,
            'message': '批量更新工序分类成功',
            'data': results
        })
        
    except ValueError as e:
        return jsonify({
            'code': 400,
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'批量更新工序分类失败: {str(e)}'
        }), 500

@bp.route('/process-categories/enabled', methods=['GET'])
@jwt_required()
def get_enabled_process_categories():
    """获取启用的工序分类列表"""
    try:
        from app.services.package_method_service import ProcessCategoryService
        
        result = ProcessCategoryService.get_enabled_process_categories()
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f'获取启用的工序分类列表失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'获取启用的工序分类列表失败: {str(e)}'
        }), 500


@bp.route('/process-categories/category-type-options', methods=['GET'])
@jwt_required()
def get_process_category_type_options():
    """获取工序分类类型选项"""
    try:
        options = ProcessCategory.get_category_type_options()
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': options
        })
        
    except Exception as e:
        current_app.logger.error(f"获取工序分类类型选项失败: {str(e)}")
        return jsonify({'code': 500, 'message': f'获取失败: {str(e)}'})


@bp.route('/process-categories/data-collection-mode-options', methods=['GET'])
@jwt_required()
def get_process_category_data_collection_mode_options():
    """获取数据自动采集模式选项"""
    try:
        options = ProcessCategory.get_data_collection_mode_options()
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': options
        })
        
    except Exception as e:
        current_app.logger.error(f"获取数据自动采集模式选项失败: {str(e)}")
        return jsonify({'code': 500, 'message': f'获取失败: {str(e)}'})

# ====================== 袋型管理 ======================

@bp.route('/bag-types', methods=['GET'])
@jwt_required()
def get_bag_types():
    """获取袋型列表"""
    try:
        from app.services.basic_data_service import BagTypeService
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '').strip()
        is_enabled = request.args.get('is_enabled')
        
        # 处理is_enabled参数
        enabled_filter = None
        if is_enabled and is_enabled.lower() in ['true', 'false']:
            enabled_filter = is_enabled.lower() == 'true'
        
        result = BagTypeService.get_bag_types(
            page=page,
            per_page=per_page,
            search=search if search else None,
            is_enabled=enabled_filter
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/bag-types/<bag_type_id>', methods=['GET'])
@jwt_required()
def get_bag_type(bag_type_id):
    """获取袋型详情"""
    try:
        from app.services.basic_data_service import BagTypeService
        
        result = BagTypeService.get_bag_type(bag_type_id)
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/bag-types', methods=['POST'])
@jwt_required()
def create_bag_type():
    """创建袋型"""
    try:
        from app.services.basic_data_service import BagTypeService
        
        data = request.get_json()
        user_id = get_jwt_identity()
        
        result = BagTypeService.create_bag_type(data, user_id)
        return jsonify({
            'success': True,
            'data': result,
            'message': '袋型创建成功'
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/bag-types/<bag_type_id>', methods=['PUT'])
@jwt_required()
def update_bag_type(bag_type_id):
    """更新袋型"""
    try:
        from app.services.basic_data_service import BagTypeService
        
        data = request.get_json()
        user_id = get_jwt_identity()
        
        result = BagTypeService.update_bag_type(bag_type_id, data, user_id)
        return jsonify({
            'success': True,
            'data': result,
            'message': '袋型更新成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/bag-types/<bag_type_id>', methods=['DELETE'])
@jwt_required()
def delete_bag_type(bag_type_id):
    """删除袋型"""
    try:
        from app.services.basic_data_service import BagTypeService
        
        result = BagTypeService.delete_bag_type(bag_type_id)
        return jsonify({
            'success': True,
            'message': '袋型删除成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/bag-types/batch', methods=['PUT'])
@jwt_required()
def batch_update_bag_types():
    """批量更新袋型"""
    try:
        from app.services.basic_data_service import BagTypeService
        
        data = request.get_json()
        user_id = get_jwt_identity()
        
        updates = data.get('updates', [])
        result = BagTypeService.batch_update_bag_types(updates, user_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '批量更新成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/bag-types/options', methods=['GET'])
@jwt_required()
def get_bag_type_options():
    """获取袋型选项"""
    try:
        from app.services.basic_data_service import BagTypeService
        
        result = BagTypeService.get_bag_type_options()
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/bag-types/form-options', methods=['GET'])
@jwt_required()
def get_bag_type_form_options():
    """获取袋型表单选项数据"""
    try:
        from app.services.basic_data_service import BagTypeService
        
        # 获取单位选项
        units = BagTypeService.get_unit_options()
        
        # 获取规格表达式选项
        spec_expressions = BagTypeService.get_calculation_scheme_options()
        
        # 获取袋型结构所需的所有公式选项（按分类划分）
        formula_options = BagTypeService.get_all_formula_options()
        
        return jsonify({
            'success': True,
            'data': {
                'units': units,
                'spec_expressions': spec_expressions,
                'structure_expressions': formula_options['structure_expressions'],
                'formulas': formula_options['formulas']
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# ====================== 袋型结构管理 ======================

@bp.route('/bag-types/<bag_type_id>/structures', methods=['GET'])
@jwt_required()
def get_bag_type_structures(bag_type_id):
    """获取袋型结构列表"""
    try:
        from app.services.basic_data_service import BagTypeService
        
        result = BagTypeService.get_bag_type_structures(bag_type_id)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/bag-types/<bag_type_id>/structures', methods=['POST'])
@jwt_required()
def batch_save_bag_type_structures(bag_type_id):
    """批量保存袋型结构"""
    try:
        from app.services.basic_data_service import BagTypeService
        from flask_jwt_extended import get_jwt_identity
        
        data = request.get_json()
        structures_data = data.get('structures', [])
        current_user_id = get_jwt_identity()
        
        result = BagTypeService.batch_update_bag_type_structures(
            bag_type_id, 
            structures_data, 
            current_user_id
        )
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/bag-type-structures/<structure_id>', methods=['PUT'])
@jwt_required()
def update_bag_type_structure(structure_id):
    """更新袋型结构"""
    try:
        from app.services.basic_data_service import BagTypeService
        from flask_jwt_extended import get_jwt_identity
        
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        result = BagTypeService.update_bag_type_structure(structure_id, data, current_user_id)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/bag-type-structures/<structure_id>', methods=['DELETE'])
@jwt_required()
def delete_bag_type_structure(structure_id):
    """删除袋型结构"""
    try:
        from app.services.basic_data_service import BagTypeService
        
        result = BagTypeService.delete_bag_type_structure(structure_id)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# ====================== 工序管理 ======================

@bp.route('/processes', methods=['GET'])
@jwt_required()
def get_processes():
    """获取工序列表"""
    try:
        from app.services.package_method_service import ProcessService
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '').strip()
        
        result = ProcessService.get_processes(
            page=page,
            per_page=per_page,
            search=search if search else None
        )
        
        # 将items字段重命名为processes以保持与前端的一致性
        if 'items' in result:
            result['processes'] = result.pop('items')
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        current_app.logger.error(f'获取工序列表失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'获取工序列表失败: {str(e)}'
        }), 500

@bp.route('/processes/<process_id>', methods=['GET'])
@jwt_required()
def get_process(process_id):
    """获取单个工序"""
    try:
        from app.services.package_method_service import ProcessService
        
        result = ProcessService.get_process(process_id)
        
        if not result:
            return jsonify({
                'code': 404,
                'message': '工序不存在'
            }), 404
            
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f'获取工序详情失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'获取工序详情失败: {str(e)}'
        }), 500

@bp.route('/processes', methods=['POST'])
@jwt_required()
def create_process():
    """创建工序"""
    try:
        from app.services.package_method_service import ProcessService
        
        data = request.get_json()
        if not data:
            return jsonify({'code': 400, 'message': '无效的请求数据'})
        
        if not data.get('process_name'):
            return jsonify({'code': 400, 'message': '工序名称不能为空'})
        
        # 获取当前用户ID
        current_user_id = get_jwt_identity()
        
        process = ProcessService.create_process(data, current_user_id)
        
        return jsonify({
            'success': True,
            'message': '创建成功',
            'data': process
        })
        
    except ValueError as e:
        return jsonify({'code': 400, 'message': str(e)})
    except Exception as e:
        current_app.logger.error(f"创建工序失败: {str(e)}")
        return jsonify({'code': 500, 'message': f'创建失败: {str(e)}'})

@bp.route('/processes/<process_id>', methods=['PUT'])
@jwt_required()
def update_process(process_id):
    """更新工序"""
    try:
        from app.services.package_method_service import ProcessService
        
        data = request.get_json()
        if not data:
            return jsonify({'code': 400, 'message': '无效的请求数据'})
        
        # 获取当前用户ID
        current_user_id = get_jwt_identity()
        
        process = ProcessService.update_process(process_id, data, current_user_id)
        
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': process
        })
        
    except ValueError as e:
        return jsonify({'code': 400, 'message': str(e)})
    except Exception as e:
        current_app.logger.error(f"更新工序失败: {str(e)}")
        return jsonify({'code': 500, 'message': f'更新失败: {str(e)}'})

@bp.route('/processes/<process_id>', methods=['DELETE'])
@jwt_required()
def delete_process(process_id):
    """删除工序"""
    try:
        from app.services.package_method_service import ProcessService
        
        ProcessService.delete_process(process_id)
        
        return jsonify({
            'code': 200,
            'message': '删除成功'
        })
        
    except ValueError as e:
        return jsonify({'code': 400, 'message': str(e)})
    except Exception as e:
        current_app.logger.error(f"删除工序失败: {str(e)}")
        return jsonify({'code': 500, 'message': f'删除失败: {str(e)}'})

@bp.route('/processes/batch', methods=['POST'])
@jwt_required()
def batch_update_processes():
    """批量更新工序"""
    try:
        from app.services.package_method_service import ProcessService
        
        data = request.get_json()
        if not data or not isinstance(data, list):
            return jsonify({'code': 400, 'message': '无效的请求数据'})
        
        # 获取当前用户ID
        current_user_id = get_jwt_identity()
        
        processes = ProcessService.batch_update_processes(data, current_user_id)
        
        return jsonify({
            'code': 200,
            'message': '批量更新成功',
            'data': processes
        })
        
    except ValueError as e:
        return jsonify({'code': 400, 'message': str(e)})
    except Exception as e:
        current_app.logger.error(f"批量更新工序失败: {str(e)}")
        return jsonify({'code': 500, 'message': f'批量更新失败: {str(e)}'})

@bp.route('/processes/enabled', methods=['GET'])
@jwt_required()
def get_enabled_processes():
    """获取启用的工序列表"""
    try:
        from app.services.package_method_service import ProcessService
        
        processes = ProcessService.get_enabled_processes()
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': processes
        })
        
    except Exception as e:
        current_app.logger.error(f"获取启用工序列表失败: {str(e)}")
        return jsonify({'code': 500, 'message': f'获取失败: {str(e)}'})

@bp.route('/processes/scheduling-method-options', methods=['GET'])
@jwt_required()
def get_scheduling_method_options():
    try:
        from app.services.package_method_service import ProcessService  # 必须有这行
        options = ProcessService.get_scheduling_method_options()
        return jsonify({
            'success': True,
            'data': options
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/processes/calculation-scheme-options', methods=['GET'])
@jwt_required()
def get_process_calculation_scheme_options():
    try:
        from app.services.package_method_service import ProcessService  # 修复未定义问题
        result = ProcessService.get_calculation_scheme_options_by_category()
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ====================== 袋型相关公式管理 ======================

@bp.route('/bag-related-formulas', methods=['GET'])
@jwt_required()
def get_bag_related_formulas():
    """获取袋型相关公式列表"""
    try:
        from app.services.basic_data_service import BagRelatedFormulaService
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '').strip()
        bag_type_id = request.args.get('bag_type_id', '').strip()
        is_enabled = request.args.get('is_enabled')
        
        # 处理布尔值
        if is_enabled is not None:
            is_enabled = is_enabled.lower() in ['true', '1', 'yes']
        
        result = BagRelatedFormulaService.get_bag_related_formulas(
            page=page,
            per_page=per_page,
            search=search if search else None,
            bag_type_id=bag_type_id if bag_type_id else None,
            is_enabled=is_enabled
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/bag-related-formulas/<formula_id>', methods=['GET'])
@jwt_required()
def get_bag_related_formula(formula_id):
    """获取单个袋型相关公式"""
    try:
        from app.services.basic_data_service import BagRelatedFormulaService
        
        result = BagRelatedFormulaService.get_bag_related_formula(formula_id)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/bag-related-formulas', methods=['POST'])
@jwt_required()
def create_bag_related_formula():
    """创建袋型相关公式"""
    try:
        from app.services.basic_data_service import BagRelatedFormulaService
        
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        result = BagRelatedFormulaService.create_bag_related_formula(data, current_user_id)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/bag-related-formulas/<formula_id>', methods=['PUT'])
@jwt_required()
def update_bag_related_formula(formula_id):
    """更新袋型相关公式"""
    try:
        from app.services.basic_data_service import BagRelatedFormulaService
        
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        result = BagRelatedFormulaService.update_bag_related_formula(formula_id, data, current_user_id)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/bag-related-formulas/<formula_id>', methods=['DELETE'])
@jwt_required()
def delete_bag_related_formula(formula_id):
    """删除袋型相关公式"""
    try:
        from app.services.basic_data_service import BagRelatedFormulaService
        
        result = BagRelatedFormulaService.delete_bag_related_formula(formula_id)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/bag-related-formulas/batch', methods=['PUT'])
@jwt_required()
def batch_update_bag_related_formulas():
    """批量更新袋型相关公式"""
    try:
        from app.services.basic_data_service import BagRelatedFormulaService
        
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        if not data or 'updates' not in data:
            return jsonify({
                'success': False,
                'message': '无效的请求数据'
            }), 400
        
        result = BagRelatedFormulaService.batch_update_bag_related_formulas(data['updates'], current_user_id)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/bag-related-formulas/options', methods=['GET'])
@jwt_required()
def get_bag_related_formula_options():
    """获取袋型相关公式选项数据"""
    try:
        from app.services.basic_data_service import BagRelatedFormulaService
        
        result = BagRelatedFormulaService.get_bag_related_formula_options()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# 班组管理API接口
@bp.route('/team-groups', methods=['GET'])
@jwt_required()
def get_team_groups():
    """获取班组列表"""
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search')
        is_enabled = request.args.get('is_enabled')
        
        if is_enabled is not None:
            is_enabled = is_enabled.lower() == 'true'
        
        result = TeamGroupService.get_team_groups(
            page=page,
            per_page=per_page,
            search=search,
            is_enabled=is_enabled
        )
        
        return jsonify({
            'success': True,
            'data': result['team_groups'],
            'pagination': {
                'page': result['page'],
                'per_page': result['per_page'],
                'total': result['total'],
                'pages': result['pages']
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/team-groups/<team_group_id>', methods=['GET'])
@jwt_required()
def get_team_group(team_group_id):
    """获取班组详情"""
    try:
        team_group = TeamGroupService.get_team_group(team_group_id)
        
        return jsonify({
            'success': True,
            'data': team_group
        })
        
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/team-groups', methods=['POST'])
@jwt_required()
def create_team_group():
    """创建班组"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': '请求数据不能为空'}), 400
        
        if not data.get('team_name'):
            return jsonify({'success': False, 'message': '班组名称不能为空'}), 400
        
        team_group = TeamGroupService.create_team_group(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': team_group,
            'message': '班组创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/team-groups/<team_group_id>', methods=['PUT'])
@jwt_required()
def update_team_group(team_group_id):
    """更新班组"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': '请求数据不能为空'}), 400
        
        team_group = TeamGroupService.update_team_group(team_group_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': team_group,
            'message': '班组更新成功'
        })
        
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/team-groups/<team_group_id>', methods=['DELETE'])
@jwt_required()
def delete_team_group(team_group_id):
    """删除班组"""
    try:
        result = TeamGroupService.delete_team_group(team_group_id)
        
        return jsonify({
            'success': True,
            'message': result['message']
        })
        
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/team-groups/options', methods=['GET'])
@jwt_required()
def get_team_group_options():
    """获取班组选项列表"""
    try:
        options = TeamGroupService.get_team_group_options()
        
        return jsonify({
            'success': True,
            'data': options
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/team-groups/form-options', methods=['GET'])
@jwt_required()
def get_team_group_form_options():
    """获取班组表单选项数据"""
    try:
        employee_options = TeamGroupService.get_employee_options()
        machine_options = TeamGroupService.get_machine_options()
        process_options = TeamGroupService.get_process_category_options()
        
        return jsonify({
            'success': True,
            'data': {
                'employees': employee_options,
                'machines': machine_options,
                'process_categories': process_options
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# 班组成员管理API
@bp.route('/team-groups/<team_group_id>/members', methods=['POST'])
@jwt_required()
def add_team_member(team_group_id):
    """添加班组成员"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': '请求数据不能为空'}), 400
        
        if not data.get('employee_id'):
            return jsonify({'success': False, 'message': '员工ID不能为空'}), 400
        
        member = TeamGroupService.add_team_member(team_group_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': member,
            'message': '班组成员添加成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/team-members/<member_id>', methods=['PUT'])
@jwt_required()
def update_team_member(member_id):
    """更新班组成员"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': '请求数据不能为空'}), 400
        
        member = TeamGroupService.update_team_member(member_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': member,
            'message': '班组成员更新成功'
        })
        
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/team-members/<member_id>', methods=['DELETE'])
@jwt_required()
def delete_team_member(member_id):
    """删除班组成员"""
    try:
        result = TeamGroupService.delete_team_member(member_id)
        
        return jsonify({
            'success': True,
            'message': result['message']
        })
        
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# 班组机台管理API
@bp.route('/team-groups/<team_group_id>/machines', methods=['POST'])
@jwt_required()
def add_team_machine(team_group_id):
    """添加班组机台"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': '请求数据不能为空'}), 400
        
        if not data.get('machine_id'):
            return jsonify({'success': False, 'message': '机台ID不能为空'}), 400
        
        machine = TeamGroupService.add_team_machine(team_group_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': machine,
            'message': '班组机台添加成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/team-machines/<machine_id>', methods=['DELETE'])
@jwt_required()
def delete_team_machine(machine_id):
    """删除班组机台"""
    try:
        result = TeamGroupService.delete_team_machine(machine_id)
        
        return jsonify({
            'success': True,
            'message': result['message']
        })
        
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# 班组工序分类管理API
@bp.route('/team-groups/<team_group_id>/processes', methods=['POST'])
@jwt_required()
def add_team_process(team_group_id):
    """添加班组工序分类"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': '请求数据不能为空'}), 400
        
        if not data.get('process_category_id'):
            return jsonify({'success': False, 'message': '工序分类ID不能为空'}), 400
        
        process = TeamGroupService.add_team_process(team_group_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': process,
            'message': '班组工序分类添加成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/team-processes/<process_id>', methods=['DELETE'])
@jwt_required()
def delete_team_process(process_id):
    """删除班组工序分类"""
    try:
        result = TeamGroupService.delete_team_process(process_id)
        
        return jsonify({
            'success': True,
            'message': result['message']
        })
        
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
