"""
供应商管理API
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.api.tenant.routes import tenant_required
from app.services.base_archive.base_data.supplier_service import get_supplier_service

# 创建蓝图
supplier_bp = Blueprint('supplier', __name__)

# 设置别名以便注册路由时使用
bp = supplier_bp

# 根路径路由（兼容前端期望的路径）
@bp.route('/', methods=['GET'])
@jwt_required()
@tenant_required
def get_suppliers_root():
    """获取供应商列表（根路径）"""
    return get_suppliers()

@bp.route('/<supplier_id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_supplier_root(supplier_id):
    """获取供应商详情（根路径）"""
    return get_supplier(supplier_id)

@bp.route('/', methods=['POST'])
@jwt_required()
@tenant_required
def create_supplier_root():
    """创建供应商（根路径）"""
    return create_supplier()

@bp.route('/<supplier_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_supplier_root(supplier_id):
    """更新供应商（根路径）"""
    return update_supplier(supplier_id)

@bp.route('/<supplier_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_supplier_root(supplier_id):
    """删除供应商（根路径）"""
    return delete_supplier(supplier_id)

@bp.route('/form-options', methods=['GET'])
@jwt_required()
@tenant_required
def get_supplier_form_options_root():
    """获取供应商表单选项（根路径）"""
    return get_supplier_form_options()

# 原有的/suppliers路径路由（保持兼容性）
@bp.route('/suppliers', methods=['GET'])
@jwt_required()
@tenant_required
def get_suppliers():
    """获取供应商列表"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search')
        category_id = request.args.get('category_id')
        status = request.args.get('status')
        
        # 调用服务层
        service = get_supplier_service()
        result = service.get_suppliers(
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
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/suppliers/<supplier_id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_supplier(supplier_id):
    """获取供应商详情"""
    try:
        service = get_supplier_service()
        supplier = service.get_supplier_by_id(supplier_id)
        
        if not supplier:
            return jsonify({
                'success': False,
                'message': '供应商不存在'
            }), 404
            
        return jsonify({
            'success': True,
            'data': supplier
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/suppliers', methods=['POST'])
@jwt_required()
@tenant_required
def create_supplier():
    """创建供应商"""
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
            
        service = get_supplier_service()
        result = service.create_supplier(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '供应商创建成功'
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

@bp.route('/suppliers/<supplier_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_supplier(supplier_id):
    """更新供应商"""
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
            
        service = get_supplier_service()
        result = service.update_supplier(supplier_id, data, current_user_id)
        
        if not result:
            return jsonify({
                'success': False,
                'message': '供应商不存在'
            }), 404
            
        return jsonify({
            'success': True,
            'data': result,
            'message': '供应商更新成功'
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

@bp.route('/suppliers/<supplier_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_supplier(supplier_id):
    """删除供应商"""
    try:
        service = get_supplier_service()
        result = service.delete_supplier(supplier_id)
        
        if not result:
            return jsonify({
                'success': False,
                'message': '供应商不存在'
            }), 404
            
        return jsonify({
            'success': True,
            'message': '供应商删除成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/suppliers/form-options', methods=['GET'])
@jwt_required()
@tenant_required
def get_supplier_form_options():
    """获取供应商表单选项"""
    try:
        service = get_supplier_service()
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

@bp.route('/suppliers/enabled', methods=['GET'])
@jwt_required()
@tenant_required
def get_enabled_suppliers():
    """获取启用的供应商选项"""
    try:
        service = get_supplier_service()
        suppliers = service.get_enabled_suppliers()
        
        return jsonify({
            'success': True,
            'data': suppliers
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/suppliers/batch-update', methods=['POST'])
@jwt_required()
@tenant_required
def batch_update_suppliers():
    """批量更新供应商"""
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
            
        service = get_supplier_service()
        result = service.batch_update_suppliers(data, current_user_id)
        
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

@bp.route('/suppliers/import', methods=['POST'])
@jwt_required()
@tenant_required
def import_suppliers():
    """导入供应商数据"""
    try:
        # TODO: 实现导入逻辑
        return jsonify({
            'success': True,
            'message': '导入功能正在开发中'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/suppliers/export', methods=['GET'])
@jwt_required()
@tenant_required
def export_suppliers():
    """导出供应商数据"""
    try:
        # TODO: 实现导出逻辑
        return jsonify({
            'success': True,
            'message': '导出功能正在开发中'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/suppliers/search', methods=['GET'])
@jwt_required()
@tenant_required
def search_suppliers():
    """搜索供应商"""
    try:
        keyword = request.args.get('keyword', '')
        
        service = get_supplier_service()
        result = service.search_suppliers(keyword)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500 