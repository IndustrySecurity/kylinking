from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.system.column_configuration_service import get_column_configuration_service

# 创建蓝图
column_config_bp = Blueprint('column_config', __name__)


@column_config_bp.route('/get', methods=['GET'])
@jwt_required()
def get_column_config():
    """获取列配置"""
    try:
        page_name = request.args.get('page_name')
        config_type = request.args.get('config_type')
        
        if not page_name or not config_type:
            return jsonify({
                'success': False,
                'message': '页面名称和配置类型不能为空'
            }), 400
        
        service = get_column_configuration_service()
        config = service.get_column_config(page_name, config_type)
        
        return jsonify({
            'success': True,
            'data': config
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@column_config_bp.route('/save', methods=['POST'])
@jwt_required()
def save_column_config():
    """保存列配置"""
    try:
        data = request.get_json()
        page_name = data.get('page_name')
        config_type = data.get('config_type')
        config_data = data.get('config_data')
        
        if not page_name or not config_type or config_data is None:
            return jsonify({
                'success': False,
                'message': '页面名称、配置类型和配置数据不能为空'
            }), 400
        
        current_user_id = get_jwt_identity()
        service = get_column_configuration_service()
        result = service.save_column_config(page_name, config_type, config_data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '配置保存成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@column_config_bp.route('/delete', methods=['DELETE'])
@jwt_required()
def delete_column_config():
    """删除列配置"""
    try:
        page_name = request.args.get('page_name')
        config_type = request.args.get('config_type')
        
        if not page_name or not config_type:
            return jsonify({
                'success': False,
                'message': '页面名称和配置类型不能为空'
            }), 400
        
        current_user_id = get_jwt_identity()
        service = get_column_configuration_service()
        result = service.delete_column_config(page_name, config_type, current_user_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '配置删除成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@column_config_bp.route('/list', methods=['GET'])
@jwt_required()
def get_all_configs():
    """获取所有配置"""
    try:
        page_name = request.args.get('page_name')
        
        service = get_column_configuration_service()
        configs = service.get_all_configs(page_name)
        
        return jsonify({
            'success': True,
            'data': configs
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500 