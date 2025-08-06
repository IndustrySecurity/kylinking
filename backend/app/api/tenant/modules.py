from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.module_service import ModuleService, TenantExtensionService, TenantConfigService
from app.models.user import User
from app.extensions import db
import uuid

bp = Blueprint('tenant_modules', __name__)


@bp.route('/', methods=['GET'])
@jwt_required()
def get_tenant_modules():
    """获取租户可用的模块列表"""
    try:
        current_user_id = get_jwt_identity()
        user = db.session.query(User).get(uuid.UUID(current_user_id))
        
        if not user or not user.tenant_id:
            return jsonify({'error': '用户未关联租户'}), 400
        
        tenant_id = str(user.tenant_id)
        modules = ModuleService.get_available_modules(tenant_id=tenant_id)
        
        return jsonify({
            'success': True,
            'data': modules
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/config', methods=['GET'])
@jwt_required()
def get_tenant_config_summary():
    """获取租户配置概要"""
    try:
        current_user_id = get_jwt_identity()
        user = db.session.query(User).get(uuid.UUID(current_user_id))
        
        if not user or not user.tenant_id:
            return jsonify({'error': '用户未关联租户'}), 400
        
        if not user.is_admin:
            return jsonify({'error': '权限不足，需要管理员权限'}), 403
        
        tenant_id = str(user.tenant_id)
        summary = TenantConfigService.get_tenant_config_summary(tenant_id)
        
        return jsonify({
            'success': True,
            'data': summary
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<module_id>/configure', methods=['POST'])
@jwt_required()
def configure_module(module_id):
    """配置租户模块"""
    try:
        current_user_id = get_jwt_identity()
        user = db.session.query(User).get(uuid.UUID(current_user_id))
        
        if not user or not user.tenant_id:
            return jsonify({'error': '用户未关联租户'}), 400
        
        if not user.is_admin:
            return jsonify({'error': '权限不足，需要管理员权限'}), 403
        
        data = request.get_json()
        tenant_id = str(user.tenant_id)
        
        tenant_module = ModuleService.configure_tenant_module(
            tenant_id=tenant_id,
            module_id=module_id,
            is_enabled=data.get('is_enabled', True),
            is_visible=data.get('is_visible', True),
            custom_config=data.get('custom_config', {}),
            custom_permissions=data.get('custom_permissions', {}),
            configured_by=current_user_id
        )
        
        return jsonify({
            'success': True,
            'data': {
                'tenant_id': tenant_id,
                'module_id': module_id,
                'is_enabled': tenant_module.is_enabled,
                'is_visible': tenant_module.is_visible,
                'message': '模块配置成功'
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<module_id>/fields', methods=['GET'])
@jwt_required()
def get_module_fields(module_id):
    """获取模块字段列表（包含租户配置）"""
    try:
        current_user_id = get_jwt_identity()
        user = db.session.query(User).get(uuid.UUID(current_user_id))
        
        if not user or not user.tenant_id:
            return jsonify({'error': '用户未关联租户'}), 400
        
        tenant_id = str(user.tenant_id)
        fields = ModuleService.get_module_fields(module_id, tenant_id=tenant_id)
        
        return jsonify({
            'success': True,
            'data': fields
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<module_id>/fields/<field_id>/configure', methods=['POST'])
@jwt_required()
def configure_field(module_id, field_id):
    """配置租户字段"""
    try:
        current_user_id = get_jwt_identity()
        user = db.session.query(User).get(uuid.UUID(current_user_id))
        
        if not user or not user.tenant_id:
            return jsonify({'error': '用户未关联租户'}), 400
        
        if not user.is_admin:
            return jsonify({'error': '权限不足，需要管理员权限'}), 403
        
        data = request.get_json()
        tenant_id = str(user.tenant_id)
        
        field_config = ModuleService.configure_tenant_field(
            tenant_id=tenant_id,
            field_id=field_id,
            is_enabled=data.get('is_enabled', True),
            is_visible=data.get('is_visible', True),
            is_required=data.get('is_required'),
            is_readonly=data.get('is_readonly', False),
            custom_label=data.get('custom_label'),
            custom_placeholder=data.get('custom_placeholder'),
            custom_help_text=data.get('custom_help_text'),
            custom_validation_rules=data.get('custom_validation_rules', {}),
            custom_options=data.get('custom_options', {}),
            custom_default_value=data.get('custom_default_value'),
            display_order=data.get('display_order', 0),
            column_width=data.get('column_width'),
            field_group=data.get('field_group'),
            configured_by=current_user_id
        )
        
        return jsonify({
            'success': True,
            'data': {
                'tenant_id': tenant_id,
                'field_id': field_id,
                'is_enabled': field_config.is_enabled,
                'is_visible': field_config.is_visible,
                'custom_label': field_config.custom_label,
                'message': '字段配置成功'
            }
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/extensions', methods=['GET'])
@jwt_required()
def get_tenant_extensions():
    """获取租户扩展列表"""
    try:
        current_user_id = get_jwt_identity()
        user = db.session.query(User).get(uuid.UUID(current_user_id))
        
        if not user or not user.tenant_id:
            return jsonify({'error': '用户未关联租户'}), 400
        
        tenant_id = str(user.tenant_id)
        extension_type = request.args.get('type')
        module_id = request.args.get('module_id')
        
        extensions = TenantExtensionService.get_tenant_extensions(
            tenant_id=tenant_id,
            extension_type=extension_type,
            module_id=module_id
        )
        
        return jsonify({
            'success': True,
            'data': extensions
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/extensions', methods=['POST'])
@jwt_required()
def create_tenant_extension():
    """创建租户扩展"""
    try:
        current_user_id = get_jwt_identity()
        user = db.session.query(User).get(uuid.UUID(current_user_id))
        
        if not user or not user.tenant_id:
            return jsonify({'error': '用户未关联租户'}), 400
        
        if not user.is_admin:
            return jsonify({'error': '权限不足，需要管理员权限'}), 403
        
        data = request.get_json()
        tenant_id = str(user.tenant_id)
        
        extension = TenantExtensionService.create_extension(
            tenant_id=tenant_id,
            extension_type=data['extension_type'],
            extension_name=data['extension_name'],
            extension_key=data['extension_key'],
            extension_config=data.get('extension_config', {}),
            extension_schema=data.get('extension_schema', {}),
            extension_metadata=data.get('extension_metadata', {}),
            module_id=data.get('module_id'),
            created_by=current_user_id
        )
        
        return jsonify({
            'success': True,
            'data': {
                'id': str(extension.id),
                'extension_name': extension.extension_name,
                'extension_key': extension.extension_key,
                'message': '扩展创建成功'
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/extensions/<extension_id>', methods=['PUT'])
@jwt_required()
def update_tenant_extension(extension_id):
    """更新租户扩展"""
    try:
        current_user_id = get_jwt_identity()
        user = db.session.query(User).get(uuid.UUID(current_user_id))
        
        if not user or not user.tenant_id:
            return jsonify({'error': '用户未关联租户'}), 400
        
        if not user.is_admin:
            return jsonify({'error': '权限不足，需要管理员权限'}), 403
        
        data = request.get_json()
        
        extension = TenantExtensionService.update_extension(
            extension_id=extension_id,
            extension_config=data.get('extension_config'),
            extension_schema=data.get('extension_schema'),
            extension_metadata=data.get('extension_metadata'),
            is_active=data.get('is_active')
        )
        
        return jsonify({
            'success': True,
            'data': {
                'id': str(extension.id),
                'extension_name': extension.extension_name,
                'is_active': extension.is_active,
                'message': '扩展更新成功'
            }
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/config/export', methods=['GET'])
@jwt_required()
def export_tenant_config():
    """导出租户配置"""
    try:
        current_user_id = get_jwt_identity()
        user = db.session.query(User).get(uuid.UUID(current_user_id))
        
        if not user or not user.tenant_id:
            return jsonify({'error': '用户未关联租户'}), 400
        
        if not user.is_admin:
            return jsonify({'error': '权限不足，需要管理员权限'}), 403
        
        tenant_id = str(user.tenant_id)
        config = TenantConfigService.export_tenant_config(tenant_id)
        
        return jsonify({
            'success': True,
            'data': config
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/config/initialize', methods=['POST'])
@jwt_required()
def initialize_tenant_config():
    """初始化租户配置"""
    try:
        current_user_id = get_jwt_identity()
        user = db.session.query(User).get(uuid.UUID(current_user_id))
        
        if not user or not user.tenant_id:
            return jsonify({'error': '用户未关联租户'}), 400
        
        if not user.is_admin:
            return jsonify({'error': '权限不足，需要管理员权限'}), 403
        
        tenant_id = str(user.tenant_id)
        result = TenantConfigService.initialize_tenant_modules(tenant_id, current_user_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '租户配置初始化成功'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500 