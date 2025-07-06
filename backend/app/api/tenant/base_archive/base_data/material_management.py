# -*- coding: utf-8 -*-
"""
材料管理API路由
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services.base_archive.base_data.material_management_service import MaterialService

bp = Blueprint('material_management', __name__)


@bp.route('/', methods=['GET'])
@jwt_required()
def get_materials():
    """获取材料列表"""
    try:
        material_service = MaterialService()
        # 获取查询参数
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search')
        category_id = request.args.get('category_id')
        material_type = request.args.get('material_type')
        
        # 获取材料列表
        result = material_service.get_materials(
            page=page,
            page_size=per_page,
            search=search,
            material_category_id=category_id,
            inspection_type=material_type
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<material_id>', methods=['GET'])
@jwt_required()
def get_material(material_id):
    """获取材料详情"""
    try:
        material_service = MaterialService()
        material = material_service.get_material(material_id)
        
        return jsonify({
            'success': True,
            'data': material
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/', methods=['POST'])
@jwt_required()
def create_material():
    """创建材料"""
    try:
        material_service = MaterialService()
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        if not data.get('material_name'):
            return jsonify({'error': '材料名称不能为空'}), 400
        
        material = material_service.create_material(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': material,
            'message': '材料创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<material_id>', methods=['PUT'])
@jwt_required()
def update_material(material_id):
    """更新材料"""
    try:
        material_service = MaterialService()
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        material = material_service.update_material(material_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': material,
            'message': '材料更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<material_id>', methods=['DELETE'])
@jwt_required()
def delete_material(material_id):
    """删除材料"""
    try:
        material_service = MaterialService()
        material_service.delete_material(material_id)
        
        return jsonify({
            'success': True,
            'message': '材料删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/form-options', methods=['GET'])
@jwt_required()
def get_material_form_options():
    """获取材料表单选项数据"""
    try:
        material_service = MaterialService()
        options = material_service.get_form_options()
        
        return jsonify({
            'success': True,
            'data': options
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 


@bp.route('/options', methods=['GET'])
@jwt_required()
def get_material_options():
    """获取材料选项"""
    try:
        material_service = MaterialService()
        
        # 获取材料列表
        materials = material_service.get_materials(page=1, page_size=1000)  # 获取所有材料
        
        # 转换为选项格式
        options = []
        if materials and 'materials' in materials:
            for material in materials['materials']:
                options.append({
                    'value': str(material['id']),
                    'label': material['material_name'],
                    'code': material.get('material_code', ''),
                    'specification': material.get('specification', ''),
                    'unit': material.get('unit', ''),
                    'price': material.get('price', 0),
                    'material_type': material.get('material_type', ''),
                    'category_name': material.get('category_name', ''),
                    'supplier_name': material.get('supplier_name', ''),
                    'inspection_type': material.get('inspection_type', '')
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