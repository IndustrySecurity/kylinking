"""
产品管理API
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.api.tenant.routes import tenant_required
from app.services.base_archive.base_data.product_management_service import get_product_management_service

# 创建蓝图
product_management_bp = Blueprint('product_management', __name__)

# 设置别名以便注册路由时使用
bp = product_management_bp

@bp.route('/', methods=['GET'])
@jwt_required()
@tenant_required
def get_products():
    """获取产品列表"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search')
        customer_id = request.args.get('customer_id')
        bag_type_id = request.args.get('bag_type_id')
        status = request.args.get('status')
        
        # 调用服务层
        service = get_product_management_service()
        result = service.get_products(
            page=page,
            per_page=per_page,
            search=search,
            customer_id=customer_id,
            bag_type_id=bag_type_id,
            status=status
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

@bp.route('/<product_id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_product(product_id):
    """获取产品详情"""
    try:
        service = get_product_management_service()
        product = service.get_product_detail(product_id)
        
        return jsonify({
            'success': True,
            'data': product
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/', methods=['POST'])
@jwt_required()
@tenant_required
def create_product():
    """创建产品"""
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
            
        service = get_product_management_service()
        result = service.create_product(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '产品创建成功'
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/<product_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_product(product_id):
    """更新产品"""
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
            
        service = get_product_management_service()
        result = service.update_product(product_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '产品更新成功'
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/<product_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_product(product_id):
    """删除产品"""
    try:
        service = get_product_management_service()
        result = service.delete_product(product_id)
        
        if not result:
            return jsonify({
                'success': False,
                'message': '产品不存在'
            }), 404
            
        return jsonify({
            'success': True,
            'message': '产品删除成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/form-options', methods=['GET'])
@jwt_required()
@tenant_required
def get_product_form_options():
    """获取产品表单选项"""
    try:
        service = get_product_management_service()
        options = service.get_form_options()
        
        return jsonify({
            'success': True,
            'data': options
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500 

@bp.route('/options', methods=['GET'])
@jwt_required()
@tenant_required
def get_product_options():
    """获取产品选项"""
    try:
        service = get_product_management_service()
        
        # 获取产品列表
        products = service.get_products(page=1, per_page=1000)  # 获取所有产品
        
        # 转换为选项格式
        options = []
        if products and 'products' in products:
            for product in products['products']:
                options.append({
                    'value': str(product['id']),
                    'label': product['product_name'],
                    'code': product.get('product_code', ''),
                    'specification': product.get('specification', ''),
                    'unit': product.get('unit', ''),
                    'price': product.get('price', 0),
                    'bag_type': product.get('bag_type', ''),
                    'material': product.get('material', ''),
                    'color': product.get('color', ''),
                    'width': product.get('width', 0),
                    'length': product.get('length', 0),
                    'thickness': product.get('thickness', 0)
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

@bp.route('/<product_id>/details', methods=['GET'])
@jwt_required()
@tenant_required
def get_product_details(product_id):
    """获取产品详细信息"""
    try:
        service = get_product_management_service()
        
        # 获取产品详情
        product = service.get_product_detail(product_id)
        
        if not product:
            return jsonify({'error': '产品不存在'}), 404
        
        # 转换为前端需要的格式
        product_details = {
            'id': str(product['id']),
            'product_code': product.get('product_code', ''),
            'product_name': product['product_name'],
            'specification': product.get('specification', ''),
            'unit': product.get('unit', ''),
            'price': product.get('price', 0),
            'bag_type': product.get('bag_type', ''),
            'material': product.get('material', ''),
            'color': product.get('color', ''),
            'width': product.get('width', 0),
            'length': product.get('length', 0),
            'thickness': product.get('thickness', 0),
            'customer_id': product.get('customer_id'),
            'customer_name': product.get('customer_name', ''),
            'category_id': product.get('category_id'),
            'category_name': product.get('category_name', '')
        }
        
        return jsonify({
            'success': True,
            'data': product_details
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

