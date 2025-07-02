# -*- coding: utf-8 -*-
"""
规格管理API路由
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services.base_archive.production.production_archive.specification_service import SpecificationService

bp = Blueprint('specification', __name__)


@bp.route('/', methods=['GET'])
@jwt_required()
def get_specifications():
    """获取规格列表"""
    try:
        specification_service = SpecificationService()
        # 获取查询参数
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search')
        enabled_only = request.args.get('enabled_only', 'false').lower() == 'true'
        
        # 获取规格列表
        result = specification_service.get_specifications(
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


@bp.route('/<spec_id>', methods=['GET'])
@jwt_required()
def get_specification(spec_id):
    """获取规格详情"""
    try:
        specification_service = SpecificationService()
        specification = specification_service.get_specification(spec_id)
        
        return jsonify({
            'success': True,
            'data': specification
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/', methods=['POST'])
@jwt_required()
def create_specification():
    """创建规格"""
    try:
        specification_service = SpecificationService()
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        if not data.get('spec_name'):
            return jsonify({'error': '规格名称不能为空'}), 400
        
        specification = specification_service.create_specification(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': specification,
            'message': '规格创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<spec_id>', methods=['PUT'])
@jwt_required()
def update_specification(spec_id):
    """更新规格"""
    try:
        specification_service = SpecificationService()
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        specification = specification_service.update_specification(spec_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': specification,
            'message': '规格更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<spec_id>', methods=['DELETE'])
@jwt_required()
def delete_specification(spec_id):
    """删除规格"""
    try:
        specification_service = SpecificationService()
        specification_service.delete_specification(spec_id)
        
        return jsonify({
            'success': True,
            'message': '规格删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/batch', methods=['PUT'])
@jwt_required()
def batch_update_specifications():
    """批量更新规格"""
    try:
        specification_service = SpecificationService()
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'data' not in data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        results = specification_service.batch_update_specifications(data['data'], current_user_id)
        
        return jsonify({
            'success': True,
            'data': results,
            'message': '批量更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500 