# -*- coding: utf-8 -*-
"""
客户管理API
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import uuid

from app.utils.decorators import tenant_required
from app.utils.tenant_context import tenant_context_required
from app.services.base_archive.base_data.customer_service import CustomerService

customer_bp = Blueprint('customer', __name__)

# 为统一导入方式提供别名
bp = customer_bp

@customer_bp.route('/', methods=['GET'])
@jwt_required()
@tenant_required
def get_customers():
    """获取客户列表"""
    try:
        customer_service = CustomerService()
        # 获取查询参数
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search')
        category_id = request.args.get('category_id')
        status = request.args.get('status')
        
        # 获取客户列表
        result = customer_service.get_customers(
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

@customer_bp.route('/<customer_id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_customer(customer_id):
    """获取客户详情"""
    try:
        customer_service = CustomerService()
        customer = customer_service.get_customer(customer_id)
        
        return jsonify({
            'success': True,
            'data': customer
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取客户详情失败: {str(e)}'
        }), 500

@customer_bp.route('/', methods=['POST'])
@jwt_required()
@tenant_required
def create_customer():
    """创建客户"""
    try:
        customer_service = CustomerService()
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        if not data:
            return jsonify({'success': False, 'message': '请求数据不能为空'}), 400
        
        # 验证必填字段
        if not data.get('customer_name'):
            return jsonify({'success': False, 'message': '客户名称不能为空'}), 400
        
        # 检查是否有子表数据，如果有使用create_customer_with_subtables
        has_subtables = any(key in data for key in ['contacts', 'delivery_addresses', 'invoice_units', 'payment_units', 'affiliated_companies'])
        
        if has_subtables:
            customer = customer_service.create_customer_with_subtables(data, current_user_id)
        else:
            customer = customer_service.create_customer(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': customer,
            'message': '客户创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'创建客户失败: {str(e)}'
        }), 500

@customer_bp.route('/<customer_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_customer(customer_id):
    """更新客户"""
    try:
        customer_service = CustomerService()
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        if not data:
            return jsonify({'success': False, 'message': '请求数据不能为空'}), 400
        
        # 检查是否有子表数据，如果有使用update_customer_with_subtables
        has_subtables = any(key in data for key in ['contacts', 'delivery_addresses', 'invoice_units', 'payment_units', 'affiliated_companies'])
        
        if has_subtables:
            customer = customer_service.update_customer_with_subtables(customer_id, data, current_user_id)
        else:
            customer = customer_service.update_customer(customer_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': customer,
            'message': '客户更新成功'
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'更新客户失败: {str(e)}'
        }), 500

@customer_bp.route('/<customer_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_customer(customer_id):
    """删除客户"""
    try:
        customer_service = CustomerService()
        customer_service.delete_customer(customer_id)
        
        return jsonify({
            'success': True,
            'message': '客户删除成功'
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'删除客户失败: {str(e)}'
        }), 500

@customer_bp.route('/form-options', methods=['GET'])
@jwt_required()
@tenant_required
def get_customer_form_options():
    """获取客户表单选项"""
    try:
        customer_service = CustomerService()
        options = customer_service.get_form_options()
        
        return jsonify({
            'success': True,
            'data': options
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取表单选项失败: {str(e)}'
        }), 500

# 添加options别名路由
@customer_bp.route('/options', methods=['GET'])  
@jwt_required()
@tenant_required
def get_customer_options():
    """获取客户选项"""
    try:
        customer_service = CustomerService()
        
        # 获取客户列表
        customers = customer_service.get_customers(page=1, per_page=1000)  # 获取所有客户
        
        # 转换为选项格式
        options = []
        if customers and 'customers' in customers:
            for customer in customers['customers']:
                options.append({
                    'value': str(customer['id']),
                    'label': customer['customer_name'],
                    'code': customer.get('customer_code', ''),
                    'contact_person': customer.get('contact_person', ''),
                    'phone': customer.get('phone', ''),
                    'mobile': customer.get('mobile', ''),
                    'address': customer.get('address', ''),
                    'payment_method_id': customer.get('payment_method_id'),
                    'salesperson_id': customer.get('salesperson_id'),
                    'company_id': customer.get('company_id'),
                    'tax_rate_id': customer.get('tax_rate_id'),
                    'tax_rate': customer.get('tax_rate', 0)
                })
        
        return jsonify({
            'success': True,
            'data': options
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@customer_bp.route('/<customer_id>/contacts', methods=['GET'])
@jwt_required()
@tenant_required  
def get_customer_contacts(customer_id):
    """获取客户联系人选项"""
    try:
        customer_service = CustomerService()
        
        # 获取客户联系人
        contacts = customer_service.get_customer_contacts(customer_id)
        
        # 转换为前端需要的格式
        contact_options = []
        for contact in contacts:
            contact_options.append({
                'id': str(contact['id']),
                'value': str(contact['id']),
                'label': contact['contact_name'],
                'contact_name': contact['contact_name'],
                'phone': contact.get('mobile', ''),
                'mobile': contact.get('mobile', ''),
                'email': contact.get('email', ''),
                'position': contact.get('position', ''),
                'department': contact.get('department', '')
            })
        
        return jsonify({
            'success': True,
            'data': contact_options
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@customer_bp.route('/<customer_id>/details', methods=['GET'])
@jwt_required()
@tenant_required
def get_customer_details(customer_id):
    """获取客户详细信息"""
    try:
        customer_service = CustomerService()
        
        # 获取客户详情
        customer = customer_service.get_customer(customer_id)
        
        if not customer:
            return jsonify({'error': '客户不存在'}), 404
        
        # 转换为前端需要的格式
        customer_details = {
            'id': str(customer['id']),
            'customer_name': customer['customer_name'],
            'customer_code': customer.get('customer_code', ''),
            'contact_person': customer.get('contact_person', ''),
            'phone': customer.get('phone', ''),
            'mobile': customer.get('mobile', ''),
            'address': customer.get('address', ''),
            'payment_method_id': customer.get('payment_method_id'),
            'salesperson_id': customer.get('salesperson_id'),
            'company_id': customer.get('company_id'),
            'tax_rate_id': customer.get('tax_rate_id'),
            'tax_rate': customer.get('tax_rate', 0)
        }
        
        return jsonify({
            'success': True,
            'data': customer_details
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@customer_bp.route('/enabled', methods=['GET'])
@jwt_required()
def get_enabled_customers():
    """获取启用的客户选项"""
    try:
        customer_service = CustomerService()
        result = customer_service.get_list(enabled_only=True)
        
        customer_options = []
        for customer in result['customers']:
            customer_options.append({
                'value': customer['id'],
                'label': f"{customer['customer_code']} - {customer['customer_name']}"
            })
        
        return jsonify({
            'success': True,
            'data': customer_options
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取启用客户失败: {str(e)}'
        }), 500