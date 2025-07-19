# -*- coding: utf-8 -*-
"""
报价配件管理API
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.tenant.routes import tenant_required
from app.services.base_archive.production_config.quote_accessory_service import QuoteAccessoryService

bp = Blueprint('quote_accessory', __name__)

def get_quote_accessory_service():
    """获取报价配件服务实例"""
    return QuoteAccessoryService()

@bp.route('/', methods=['GET'])
@jwt_required()
@tenant_required
def get_quote_accessories():
    """获取报价配件列表"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        search = request.args.get('search', '')
        
        service = get_quote_accessory_service()
        result = service.get_quote_accessories(page=page, per_page=per_page, search=search)
        
        return jsonify({
            'code': 200,
            'success': True,
            'data': result,
            'message': '获取成功'
        })
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/', methods=['POST'])
@jwt_required()
@tenant_required
def create_quote_accessory():
    """创建报价配件"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'code': 400,
                'success': False,
                'message': '请求数据不能为空'
            }), 400
        
        user_id = get_jwt_identity()
        service = get_quote_accessory_service()
        result = service.create_quote_accessory(data, user_id)
        
        return jsonify({
            'code': 200,
            'success': True,
            'data': result,
            'message': '报价配件创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({
            'code': 400,
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'code': 500,
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/<accessory_id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_quote_accessory(accessory_id):
    """获取报价配件详情"""
    try:
        service = get_quote_accessory_service()
        result = service.get_quote_accessory(accessory_id)
        
        if result is None:
            return jsonify({
                'code': 404,
                'success': False,
                'message': '报价配件不存在'
            }), 404
        
        return jsonify({
            'code': 200,
            'success': True,
            'data': result,
            'message': '获取成功'
        })
        
    except ValueError as e:
        return jsonify({
            'code': 404,
            'success': False,
            'message': str(e)
        }), 404
    except Exception as e:
        return jsonify({
            'code': 500,
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/<accessory_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_quote_accessory(accessory_id):
    """更新报价配件"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'code': 400,
                'success': False,
                'message': '请求数据不能为空'
            }), 400
        
        user_id = get_jwt_identity()
        service = get_quote_accessory_service()
        result = service.update_quote_accessory(accessory_id, data, user_id)
        
        if result is None:
            return jsonify({
                'code': 404,
                'success': False,
                'message': '报价配件不存在'
            }), 404
        
        return jsonify({
            'code': 200,
            'success': True,
            'data': result,
            'message': '报价配件更新成功'
        })
        
    except ValueError as e:
        return jsonify({
            'code': 400,
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'code': 500,
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/<accessory_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_quote_accessory(accessory_id):
    """删除报价配件"""
    try:
        service = get_quote_accessory_service()
        result = service.delete_quote_accessory(accessory_id)
        
        if not result:
            return jsonify({
                'code': 404,
                'success': False,
                'message': '报价配件不存在'
            }), 404
        
        return jsonify({
            'code': 200,
            'success': True,
            'message': '报价配件删除成功'
        })
        
    except ValueError as e:
        return jsonify({
            'code': 400,
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'code': 500,
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/enabled', methods=['GET'])
@jwt_required()
@tenant_required
def get_enabled_quote_accessories():
    """获取启用的报价配件列表"""
    try:
        service = get_quote_accessory_service()
        result = service.get_enabled_quote_accessories()
        
        return jsonify({
            'code': 200,
            'success': True,
            'data': result,
            'message': '获取成功'
        })
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/batch', methods=['PUT'])
@jwt_required()
@tenant_required
def batch_update_quote_accessories():
    """批量更新报价配件"""
    try:
        data = request.get_json()
        if not data or not isinstance(data, list):
            return jsonify({
                'code': 400,
                'success': False,
                'message': '请求数据必须是数组'
            }), 400
        
        user_id = get_jwt_identity()
        service = get_quote_accessory_service()
        result = service.batch_update_quote_accessories(data, user_id)
        
        return jsonify({
            'code': 200,
            'success': True,
            'data': {'updated_count': result},
            'message': f'成功更新{result}个报价配件'
        })
        
    except ValueError as e:
        return jsonify({
            'code': 400,
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'code': 500,
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/calculation-schemes', methods=['GET'])
@jwt_required()
@tenant_required
def get_calculation_schemes():
    """获取材料报价分类的计算方案选项"""
    try:
        from app.services.base_archive.production_config.calculation_scheme_service import get_calculation_scheme_service
        
        scheme_service = get_calculation_scheme_service()
        schemes = scheme_service.get_calculation_schemes_by_category('material_quote')
        
        return jsonify({
            'code': 200,
            'success': True,
            'data': schemes,
            'message': '获取成功'
        })
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'success': False,
            'message': str(e)
        }), 500 