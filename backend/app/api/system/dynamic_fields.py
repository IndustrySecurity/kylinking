from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.utils.decorators import tenant_required
from app.services.system.dynamic_field_service import get_dynamic_field_service

dynamic_fields_bp = Blueprint('dynamic_fields', __name__)

# 打印路由注册信息
print("✅ dynamic_fields 蓝图创建成功")
print("📋 注册的路由:")
print("   - GET  /field-types")
print("   - GET  /<model_name>/fields")
print("   - GET  /<model_name>/<page_name>/fields")
print("   - POST /<model_name>/fields")
print("   - PUT  /fields/<field_id>")
print("   - DELETE /fields/<field_id>")
print("   - GET  /<model_name>/<record_id>/values")
print("   - GET  /<model_name>/page/<page_name>/<record_id>/values")
print("   - POST /<model_name>/<record_id>/values")
print("   - POST /<model_name>/page/<page_name>/<record_id>/values")
print("   - DELETE /<model_name>/page/<page_name>/<record_id>/values")
print("   - POST /<model_name>/<record_id>/cleanup-duplicates")
print("   - GET  /<model_name>/stats")
print("   - GET  /stats")

# 1. 字段类型
@dynamic_fields_bp.route('/field-types', methods=['GET'])
@jwt_required()
@tenant_required
def get_field_types():
    """获取支持的字段类型"""
    field_types = [
        {'value': 'text', 'label': '文本'},
        {'value': 'number', 'label': '数字'},
        {'value': 'date', 'label': '日期'},
        {'value': 'select', 'label': '选择框'},
        {'value': 'checkbox', 'label': '复选框'},
        {'value': 'calculated', 'label': '计算字段'},
    ]
    return jsonify({'success': True, 'data': field_types})

# 2. 获取模型字段定义
@dynamic_fields_bp.route('/<string:model_name>/fields', methods=['GET'])
@jwt_required()
@tenant_required
def get_model_fields(model_name):
    try:
        service = get_dynamic_field_service()
        page_name = request.args.get('page_name')
        
        # 如果没有指定page_name，返回所有字段
        if page_name is None:
            fields = service.get_all_model_fields(model_name)
        else:
            fields = service.get_model_fields(model_name, page_name)
            
        return jsonify({'success': True, 'data': fields})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# 3. 获取指定页面字段定义
@dynamic_fields_bp.route('/<string:model_name>/<string:page_name>/fields', methods=['GET'])
@jwt_required()
@tenant_required
def get_page_fields(model_name, page_name):
    try:
        service = get_dynamic_field_service()
        fields = service.get_page_fields(model_name, page_name)
        return jsonify({'success': True, 'data': fields})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# 4. 创建字段定义
@dynamic_fields_bp.route('/<string:model_name>/fields', methods=['POST'])
@jwt_required()
@tenant_required
def create_field(model_name):
    try:
        service = get_dynamic_field_service()
        field_data = request.json
        page_name = field_data.get('page_name', 'default')
        
        # 确保页面名称不是空字符串
        if not page_name or not page_name.strip():
            page_name = 'default'
        else:
            page_name = page_name.strip()
        
        field_data_copy = field_data.copy()
        if 'page_name' in field_data_copy:
            del field_data_copy['page_name']
        field = service.create_field(model_name, page_name, field_data_copy)
        return jsonify({'success': True, 'data': field})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# 5. 更新字段定义
@dynamic_fields_bp.route('/fields/<string:field_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_field(field_id):
    try:
        service = get_dynamic_field_service()
        field_data = request.json
        
        # 确保页面名称不是空字符串
        if 'page_name' in field_data:
            page_name = field_data['page_name']
            if not page_name or not page_name.strip():
                field_data['page_name'] = 'default'
            else:
                field_data['page_name'] = page_name.strip()
        
        field = service.update_field(field_id, field_data)
        if field:
            return jsonify({'success': True, 'data': field})
        else:
            return jsonify({'success': False, 'message': '字段不存在'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# 6. 删除字段定义
@dynamic_fields_bp.route('/fields/<string:field_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_field(field_id):
    try:
        service = get_dynamic_field_service()
        success = service.delete_field(field_id)
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': '字段不存在'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# 7. 获取记录动态字段值
@dynamic_fields_bp.route('/<string:model_name>/<path:record_id>/values', methods=['GET'])
@jwt_required()
@tenant_required
def get_record_values(model_name, record_id):
    try:
        service = get_dynamic_field_service()
        page_name = request.args.get('page_name', 'default')
        values = service.get_record_dynamic_values(model_name, record_id, page_name)
        return jsonify({'success': True, 'data': values})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# 8. 获取记录指定页面动态字段值
@dynamic_fields_bp.route('/<string:model_name>/page/<string:page_name>/<path:record_id>/values', methods=['GET'])
@jwt_required()
@tenant_required
def get_record_page_values(model_name, page_name, record_id):
    try:
        service = get_dynamic_field_service()
        values = service.get_record_page_values(model_name, page_name, record_id)
        return jsonify({'success': True, 'data': values})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# 9. 保存记录动态字段值
@dynamic_fields_bp.route('/<string:model_name>/<path:record_id>/values', methods=['POST'])
@jwt_required()
@tenant_required
def save_record_values(model_name, record_id):
    try:
        service = get_dynamic_field_service()
        values = request.json
        page_name = request.args.get('page_name', 'default')
        service.save_record_dynamic_values(model_name, record_id, values, page_name)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# 10. 保存记录指定页面动态字段值
@dynamic_fields_bp.route('/<string:model_name>/page/<string:page_name>/<path:record_id>/values', methods=['POST'])
@jwt_required()
@tenant_required
def save_record_page_values(model_name, page_name, record_id):
    try:
        service = get_dynamic_field_service()
        values = request.json
        service.save_record_page_values(model_name, page_name, record_id, values)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# 11. 删除记录指定页面的所有动态字段值
@dynamic_fields_bp.route('/<string:model_name>/page/<string:page_name>/<path:record_id>/values', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_record_page_values(model_name, page_name, record_id):
    try:
        service = get_dynamic_field_service()
        service.delete_record_page_values(model_name, page_name, record_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# 12. 清理记录中重复的动态字段值
@dynamic_fields_bp.route('/<string:model_name>/<path:record_id>/cleanup-duplicates', methods=['POST'])
@jwt_required()
@tenant_required
def cleanup_duplicate_values(model_name, record_id):
    try:
        service = get_dynamic_field_service()
        deleted_count = service.cleanup_duplicate_values(model_name, record_id)
        return jsonify({'success': True, 'deleted_count': deleted_count})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# 13. 获取模型数据统计信息
@dynamic_fields_bp.route('/<string:model_name>/stats', methods=['GET'])
@jwt_required()
@tenant_required
def get_model_stats(model_name):
    try:
        service = get_dynamic_field_service()
        stats = service.get_model_data_stats(model_name)
        return jsonify({'success': True, 'data': stats})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# 14. 获取所有模型数据统计信息
@dynamic_fields_bp.route('/stats', methods=['GET'])
@jwt_required()
@tenant_required
def get_all_models_stats():
    try:
        service = get_dynamic_field_service()
        stats = service.get_all_models_stats()
        return jsonify({'success': True, 'data': stats})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500 