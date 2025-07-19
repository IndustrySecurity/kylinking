# -*- coding: utf-8 -*-
"""
包装方式管理API路由
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services.base_archive.production_archive.package_method_service import PackageMethodService

bp = Blueprint('package_method', __name__)


@bp.route('/', methods=['GET'])
@jwt_required()
def get_package_methods():
    """获取包装方式列表"""
    try:
        package_method_service = PackageMethodService()
        # 获取查询参数
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search')
        enabled_only = request.args.get('enabled_only', 'false').lower() == 'true'
        
        # 获取包装方式列表
        result = package_method_service.get_package_methods(
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


@bp.route('/<package_method_id>', methods=['GET'])
@jwt_required()
def get_package_method(package_method_id):
    """获取包装方式详情"""
    try:
        package_method_service = PackageMethodService()
        package_method = package_method_service.get_package_method(package_method_id)
        
        return jsonify({
            'success': True,
            'data': package_method
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/', methods=['POST'])
@jwt_required()
def create_package_method():
    """创建包装方式"""
    try:
        package_method_service = PackageMethodService()
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        if not data.get('package_name'):
            return jsonify({'error': '包装方式名称不能为空'}), 400
        
        package_method = package_method_service.create_package_method(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': package_method,
            'message': '包装方式创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<package_method_id>', methods=['PUT'])
@jwt_required()
def update_package_method(package_method_id):
    """更新包装方式"""
    try:
        package_method_service = PackageMethodService()
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        package_method = package_method_service.update_package_method(package_method_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': package_method,
            'message': '包装方式更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<package_method_id>', methods=['DELETE'])
@jwt_required()
def delete_package_method(package_method_id):
    """删除包装方式"""
    try:
        package_method_service = PackageMethodService()
        package_method_service.delete_package_method(package_method_id)
        
        return jsonify({
            'success': True,
            'message': '包装方式删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/batch', methods=['PUT'])
@jwt_required()
def batch_update_package_methods():
    """批量更新包装方式"""
    try:
        package_method_service = PackageMethodService()
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'data' not in data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        results = package_method_service.batch_update_package_methods(data['data'], current_user_id)
        
        return jsonify({
            'success': True,
            'data': results,
            'message': '批量更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/enabled', methods=['GET'])
@jwt_required()
def get_enabled_package_methods():
    """获取启用的包装方式列表"""
    try:
        package_method_service = PackageMethodService()
        package_methods = package_method_service.get_enabled_package_methods()
        
        return jsonify({
            'success': True,
            'data': package_methods
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 