from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.module_service import ModuleService, TenantConfigService
from app.models.user import User
from app.extensions import db
import uuid

bp = Blueprint('admin_modules', __name__)


@bp.route('/', methods=['GET'])
@jwt_required()
def get_system_modules():
    """获取系统模块列表 - 超级管理员使用"""
    try:
        current_user_id = get_jwt_identity()
        print(f"DEBUG - Module List API: current_user_id = {current_user_id}")
        
        # 尝试从数据库获取用户
        user = None
        try:
            user = db.session.query(User).get(uuid.UUID(current_user_id))
            print(f"DEBUG - Module List API: user from DB = {user}")
            if user:
                print(f"DEBUG - Module List API: user.is_superadmin = {user.is_superadmin}")
        except Exception as e:
            print(f"DEBUG - Module List API: Error getting user from DB: {e}")
        
        # 同时检查JWT claims作为fallback
        from flask_jwt_extended import get_jwt
        claims = get_jwt()
        print(f"DEBUG - Module List API: JWT claims = {claims}")
        
        is_superadmin_from_jwt = claims.get('is_superadmin', False)
        is_admin_from_jwt = claims.get('is_admin', False)
        print(f"DEBUG - Module List API: JWT superadmin = {is_superadmin_from_jwt}, admin = {is_admin_from_jwt}")
        
        # 权限检查：数据库用户权限 OR JWT claims权限
        has_permission = False
        if user and user.is_superadmin:
            has_permission = True
            print("DEBUG - Module List API: Permission granted via DB user.is_superadmin")
        elif is_superadmin_from_jwt or is_admin_from_jwt:
            has_permission = True
            print("DEBUG - Module List API: Permission granted via JWT claims")
        
        if not has_permission:
            print("DEBUG - Module List API: Permission denied")
            return jsonify({'error': '权限不足'}), 403
        
        print("DEBUG - Module List API: Proceeding with module list...")
        
        modules = ModuleService.get_available_modules()
        return jsonify({
            'success': True,
            'data': modules
        })
    except Exception as e:
        print(f"DEBUG - Module List API: Exception = {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/', methods=['POST'])
@jwt_required()
def create_system_module():
    """创建系统模块 - 超级管理员使用"""
    try:
        current_user_id = get_jwt_identity()
        user = db.session.query(User).get(uuid.UUID(current_user_id))
        
        if not user or not user.is_superadmin:
            return jsonify({'error': '权限不足'}), 403
        
        data = request.get_json()
        
        module = ModuleService.create_system_module(
            name=data['name'],
            display_name=data['display_name'],
            description=data.get('description'),
            category=data.get('category'),
            version=data.get('version', '1.0.0'),
            icon=data.get('icon'),
            sort_order=data.get('sort_order', 0),
            is_core=data.get('is_core', False),
            dependencies=data.get('dependencies', []),
            default_config=data.get('default_config', {})
        )
        
        return jsonify({
            'success': True,
            'data': {
                'id': str(module.id),
                'name': module.name,
                'display_name': module.display_name,
                'message': '模块创建成功'
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<module_id>/fields', methods=['GET'])
@jwt_required()
def get_module_fields(module_id):
    """获取模块字段定义"""
    try:
        current_user_id = get_jwt_identity()
        user = db.session.query(User).get(uuid.UUID(current_user_id))
        
        if not user or not user.is_superadmin:
            return jsonify({'error': '权限不足'}), 403
        
        fields = ModuleService.get_module_fields(module_id)
        return jsonify({
            'success': True,
            'data': fields
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<module_id>/fields', methods=['POST'])
@jwt_required()
def add_module_field(module_id):
    """为模块添加字段定义"""
    try:
        current_user_id = get_jwt_identity()
        user = db.session.query(User).get(uuid.UUID(current_user_id))
        
        if not user or not user.is_superadmin:
            return jsonify({'error': '权限不足'}), 403
        
        data = request.get_json()
        
        field = ModuleService.add_module_field(
            module_id=module_id,
            field_name=data['field_name'],
            display_name=data['display_name'],
            field_type=data['field_type'],
            description=data.get('description'),
            is_required=data.get('is_required', False),
            is_system_field=data.get('is_system_field', False),
            is_configurable=data.get('is_configurable', True),
            sort_order=data.get('sort_order', 0),
            validation_rules=data.get('validation_rules', {}),
            field_options=data.get('field_options', {}),
            default_value=data.get('default_value')
        )
        
        return jsonify({
            'success': True,
            'data': {
                'id': str(field.id),
                'field_name': field.field_name,
                'display_name': field.display_name,
                'message': '字段添加成功'
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_module_statistics():
    """获取模块使用统计 - 超级管理员使用"""
    try:
        current_user_id = get_jwt_identity()
        print(f"DEBUG - Module API: current_user_id = {current_user_id}")
        
        # 尝试从数据库获取用户
        user = None
        try:
            user = db.session.query(User).get(uuid.UUID(current_user_id))
            print(f"DEBUG - Module API: user from DB = {user}")
            if user:
                print(f"DEBUG - Module API: user.is_superadmin = {user.is_superadmin}")
        except Exception as e:
            print(f"DEBUG - Module API: Error getting user from DB: {e}")
        
        # 同时检查JWT claims作为fallback
        from flask_jwt_extended import get_jwt
        claims = get_jwt()
        print(f"DEBUG - Module API: JWT claims = {claims}")
        
        is_superadmin_from_jwt = claims.get('is_superadmin', False)
        is_admin_from_jwt = claims.get('is_admin', False)
        print(f"DEBUG - Module API: JWT superadmin = {is_superadmin_from_jwt}, admin = {is_admin_from_jwt}")
        
        # 权限检查：数据库用户权限 OR JWT claims权限
        has_permission = False
        if user and user.is_superadmin:
            has_permission = True
            print("DEBUG - Module API: Permission granted via DB user.is_superadmin")
        elif is_superadmin_from_jwt or is_admin_from_jwt:
            has_permission = True
            print("DEBUG - Module API: Permission granted via JWT claims")
        
        if not has_permission:
            print("DEBUG - Module API: Permission denied")
            return jsonify({'error': '权限不足'}), 403
        
        print("DEBUG - Module API: Proceeding with statistics...")
        
        # 获取所有租户的配置统计
        from app.models.tenant import Tenant
        from app.models.module import TenantModule, SystemModule
        
        tenants = db.session.query(Tenant).filter(Tenant.is_active == True).all()
        total_modules = db.session.query(SystemModule).filter(SystemModule.is_active == True).count()
        
        tenant_stats = []
        for tenant in tenants:
            config_summary = TenantConfigService.get_tenant_config_summary(str(tenant.id))
            tenant_stats.append({
                'tenant_id': str(tenant.id),
                'tenant_name': tenant.name,
                'enabled_modules': config_summary['enabled_modules'],
                'module_coverage': config_summary['module_coverage'],
                'custom_field_configs': config_summary['custom_field_configs'],
                'extensions': config_summary['extensions']
            })
        
        return jsonify({
            'success': True,
            'data': {
                'total_tenants': len(tenants),
                'total_modules': total_modules,
                'tenant_statistics': tenant_stats
            }
        })
    except Exception as e:
        print(f"DEBUG - Module API: Exception = {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/tenants/<tenant_id>/modules', methods=['GET'])
@jwt_required()
def get_tenant_modules(tenant_id):
    """获取指定租户的模块配置 - 超级管理员使用"""
    try:
        current_user_id = get_jwt_identity()
        print(f"DEBUG - Tenant Modules API: current_user_id = {current_user_id}")
        print(f"DEBUG - Tenant Modules API: tenant_id = {tenant_id}")
        
        # 尝试从数据库获取用户
        user = None
        try:
            user = db.session.query(User).get(uuid.UUID(current_user_id))
            print(f"DEBUG - Tenant Modules API: user from DB = {user}")
            if user:
                print(f"DEBUG - Tenant Modules API: user.is_superadmin = {user.is_superadmin}")
        except Exception as e:
            print(f"DEBUG - Tenant Modules API: Error getting user from DB: {e}")
        
        # 同时检查JWT claims作为fallback
        from flask_jwt_extended import get_jwt
        claims = get_jwt()
        print(f"DEBUG - Tenant Modules API: JWT claims = {claims}")
        
        is_superadmin_from_jwt = claims.get('is_superadmin', False)
        is_admin_from_jwt = claims.get('is_admin', False)
        print(f"DEBUG - Tenant Modules API: JWT superadmin = {is_superadmin_from_jwt}, admin = {is_admin_from_jwt}")
        
        # 权限检查：数据库用户权限 OR JWT claims权限
        has_permission = False
        if user and user.is_superadmin:
            has_permission = True
            print("DEBUG - Tenant Modules API: Permission granted via DB user.is_superadmin")
        elif is_superadmin_from_jwt or is_admin_from_jwt:
            has_permission = True
            print("DEBUG - Tenant Modules API: Permission granted via JWT claims")
        
        if not has_permission:
            print("DEBUG - Tenant Modules API: Permission denied")
            return jsonify({'error': '权限不足'}), 403
        
        print("DEBUG - Tenant Modules API: Proceeding with tenant modules...")
        
        # 获取租户的模块配置
        config_summary = TenantConfigService.get_tenant_config_summary(tenant_id)
        modules = ModuleService.get_available_modules()
        
        # 获取租户的具体模块配置
        from app.models.module import TenantModule
        tenant_modules = db.session.query(TenantModule).filter(
            TenantModule.tenant_id == uuid.UUID(tenant_id)
        ).all()
        
        tenant_module_map = {str(tm.module_id): tm for tm in tenant_modules}
        
        # 组合数据
        result_modules = []
        for module in modules:
            tenant_config = tenant_module_map.get(module['id'])
            result_modules.append({
                **module,
                'is_enabled': tenant_config.is_enabled if tenant_config else True,
                'is_visible': tenant_config.is_visible if tenant_config else True,
                'custom_config': tenant_config.custom_config if tenant_config else {},
                'configured_at': tenant_config.configured_at.isoformat() if tenant_config and tenant_config.configured_at else None
            })
        
        return jsonify({
            'success': True,
            'data': {
                'summary': config_summary,
                'modules': result_modules
            }
        })
    except Exception as e:
        print(f"DEBUG - Tenant Modules API: Exception = {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/tenants/<tenant_id>/modules/<module_id>/configure', methods=['POST'])
@jwt_required()
def configure_tenant_module(tenant_id, module_id):
    """为租户配置模块 - 超级管理员使用"""
    try:
        current_user_id = get_jwt_identity()
        user = db.session.query(User).get(uuid.UUID(current_user_id))
        
        if not user or not user.is_superadmin:
            return jsonify({'error': '权限不足'}), 403
        
        data = request.get_json()
        
        # 配置租户模块
        tenant_module = ModuleService.configure_tenant_module(
            tenant_id=tenant_id,
            module_id=module_id,
            is_enabled=data.get('is_enabled', True),
            is_visible=data.get('is_visible', True),
            custom_config=data.get('custom_config', {}),
            custom_permissions=data.get('custom_permissions', {}),
            configured_by=str(user.id)
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


@bp.route('/tenants/<tenant_id>/initialize', methods=['POST'])
@jwt_required()
def initialize_tenant_modules(tenant_id):
    """为租户初始化模块配置 - 超级管理员使用"""
    try:
        current_user_id = get_jwt_identity()
        print(f"DEBUG - Initialize Modules API: current_user_id = {current_user_id}")
        print(f"DEBUG - Initialize Modules API: tenant_id = {tenant_id}")
        
        # 尝试从数据库获取用户
        user = None
        try:
            user = db.session.query(User).get(uuid.UUID(current_user_id))
            print(f"DEBUG - Initialize Modules API: user from DB = {user}")
            if user:
                print(f"DEBUG - Initialize Modules API: user.is_superadmin = {user.is_superadmin}")
        except Exception as e:
            print(f"DEBUG - Initialize Modules API: Error getting user from DB: {e}")
        
        # 同时检查JWT claims作为fallback
        from flask_jwt_extended import get_jwt
        claims = get_jwt()
        print(f"DEBUG - Initialize Modules API: JWT claims = {claims}")
        
        is_superadmin_from_jwt = claims.get('is_superadmin', False)
        is_admin_from_jwt = claims.get('is_admin', False)
        print(f"DEBUG - Initialize Modules API: JWT superadmin = {is_superadmin_from_jwt}, admin = {is_admin_from_jwt}")
        
        # 权限检查：数据库用户权限 OR JWT claims权限
        has_permission = False
        if user and user.is_superadmin:
            has_permission = True
            print("DEBUG - Initialize Modules API: Permission granted via DB user.is_superadmin")
        elif is_superadmin_from_jwt or is_admin_from_jwt:
            has_permission = True
            print("DEBUG - Initialize Modules API: Permission granted via JWT claims")
        
        if not has_permission:
            print("DEBUG - Initialize Modules API: Permission denied")
            return jsonify({'error': '权限不足'}), 403
        
        print("DEBUG - Initialize Modules API: Proceeding with initialization...")
        
        # 初始化租户模块配置 - 传递user_id参数
        result = TenantConfigService.initialize_tenant_modules(tenant_id, str(current_user_id))
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '租户模块初始化成功'
        })
    except Exception as e:
        print(f"DEBUG - Initialize Modules API: Exception = {e}")
        return jsonify({'error': str(e)}), 500 