from flask import jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.api.admin import admin_bp
from app.models.tenant import Tenant
from app.models.user import User, Role, Permission
from app.extensions import db
from app.schemas.tenant import TenantSchema, TenantCreateSchema, TenantUpdateSchema
from app.utils.tenant_context import TenantContext
from slugify import slugify
import re
import uuid
from functools import wraps


def admin_required(fn):
    """
    装饰器，确保只有管理员可以访问
    """
    @jwt_required()
    @wraps(fn)  # 添加functools.wraps保留原始函数名称
    def admin_wrapper(*args, **kwargs):
        claims = get_jwt()
        
        # 详细调试信息
        print(f"DEBUG - JWT claims in admin_required: {claims}")
        print(f"DEBUG - Request path: {request.path}")
        print(f"DEBUG - Request method: {request.method}")
        
        # 获取管理员状态
        is_admin_claim = claims.get('is_admin')
        is_superadmin_claim = claims.get('is_superadmin')
        
        print(f"DEBUG - Raw admin status: is_admin={is_admin_claim}, is_superadmin={is_superadmin_claim}")
        print(f"DEBUG - Raw admin types: is_admin type={type(is_admin_claim).__name__}, is_superadmin type={type(is_superadmin_claim).__name__}")
        
        # 这里明确处理各种可能的值
        is_admin = False
        is_superadmin = False
        
        # 对字符串进行特殊处理
        if isinstance(is_admin_claim, str):
            is_admin = is_admin_claim.lower() in ['true', 'yes', 't', 'y', '1']
        # 对布尔值直接使用
        elif isinstance(is_admin_claim, bool):
            is_admin = is_admin_claim
        # 对数字类型处理
        elif isinstance(is_admin_claim, (int, float)):
            is_admin = bool(is_admin_claim)
            
        # 同样处理超级管理员状态
        if isinstance(is_superadmin_claim, str):
            is_superadmin = is_superadmin_claim.lower() in ['true', 'yes', 't', 'y', '1']
        elif isinstance(is_superadmin_claim, bool):
            is_superadmin = is_superadmin_claim
        elif isinstance(is_superadmin_claim, (int, float)):
            is_superadmin = bool(is_superadmin_claim)
            
        print(f"DEBUG - Processed admin status: is_admin={is_admin}, is_superadmin={is_superadmin}")
        
        if not is_admin and not is_superadmin:
            print(f"DEBUG - Access denied: User is not admin or superadmin")
            return jsonify({"message": "Admin privileges required"}), 403
            
        print(f"DEBUG - Access granted: User is {'superadmin' if is_superadmin else 'admin'}")
        return fn(*args, **kwargs)
    
    return admin_wrapper


def superadmin_required(fn):
    """
    装饰器，确保只有超级管理员可以访问
    """
    @jwt_required()
    @wraps(fn)  # 添加functools.wraps保留原始函数名称
    def superadmin_wrapper(*args, **kwargs):
        claims = get_jwt()
        if not claims.get('is_superadmin'):
            return jsonify({"message": "Superadmin privileges required"}), 403
        return fn(*args, **kwargs)
    
    return superadmin_wrapper


@admin_bp.route('/tenants', methods=['GET'])
@admin_required
def get_tenants():
    """
    获取所有租户列表
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 获取所有租户
    query = Tenant.query
    
    # 过滤条件
    if request.args.get('name'):
        query = query.filter(Tenant.name.ilike(f"%{request.args.get('name')}%"))
    
    if request.args.get('active') is not None:
        is_active = request.args.get('active').lower() == 'true'
        query = query.filter(Tenant.is_active == is_active)
    
    # 分页
    pagination = query.order_by(Tenant.created_at.desc()).paginate(page=page, per_page=per_page)
    
    # 序列化
    schema = TenantSchema(many=True)
    tenants_data = schema.dump(pagination.items)
    
    return jsonify({
        "tenants": tenants_data,
        "total": pagination.total,
        "pages": pagination.pages,
        "page": page,
        "per_page": per_page
    }), 200


@admin_bp.route('/tenants/<uuid:tenant_id>', methods=['GET'])
@admin_required
def get_tenant(tenant_id):
    """
    获取单个租户详情
    """
    tenant = Tenant.query.get_or_404(tenant_id)
    
    # 序列化
    schema = TenantSchema()
    tenant_data = schema.dump(tenant)
    
    # 获取租户的用户数量
    users_count = User.query.filter_by(tenant_id=tenant_id).count()
    tenant_data['users_count'] = users_count
    
    return jsonify({"tenant": tenant_data}), 200


@admin_bp.route('/tenants', methods=['POST'])
@superadmin_required
def create_tenant():
    """
    创建新租户
    """
    # 打印请求数据以进行调试
    print("Received request.json:", request.json)
    
    # 如果schema_name没有提供，则从slug自动生成
    if request.json and 'slug' in request.json and ('schema_name' not in request.json or not request.json['schema_name']):
        # 将连字符替换为下划线，去除其他特殊字符，确保符合PostgreSQL schema命名规则
        slug = request.json['slug']
        # 确保第一个字符是字母或下划线
        if slug and slug[0].isdigit():
            schema_name = 't_' + re.sub(r'[^a-zA-Z0-9_]', '_', slug)
        else:
            schema_name = re.sub(r'[^a-zA-Z0-9_]', '_', slug)
        
        # 添加到请求数据
        request_data = request.json.copy() if isinstance(request.json, dict) else {}
        request_data['schema_name'] = schema_name
    else:
        request_data = request.json
    
    # 验证请求数据
    schema = TenantCreateSchema()
    data = schema.load(request_data)
    
    # 打印验证后的数据
    print("Validated data:", data)
    
    # 检查slug是否已存在
    if Tenant.query.filter_by(slug=data['slug']).first():
        return jsonify({"message": "Slug already exists"}), 400
    
    # 检查schema_name是否已存在
    if Tenant.query.filter_by(schema_name=data['schema_name']).first():
        return jsonify({"message": "Schema name already exists"}), 400
    
    # 创建新租户
    new_tenant = Tenant(
        name=data['name'],
        slug=data['slug'],
        schema_name=data['schema_name'],
        contact_email=data['contact_email'],
        domain=data.get('domain'),
        contact_phone=data.get('contact_phone'),
        is_active=data.get('is_active', True)
    )
    
    # 保存租户
    db.session.add(new_tenant)
    db.session.commit()
    
    # 如果指定了初始管理员，创建管理员账户
    admin_data = data.get('admin')
    if admin_data and admin_data.get('email') and admin_data.get('password'):
        # 创建管理员角色
        admin_role = Role(name="Admin", description="Tenant Administrator", tenant_id=new_tenant.id)
        db.session.add(admin_role)
        db.session.commit()
        
        # 创建管理员用户 - 简化权限模型，直接设置is_admin=True
        admin_user = User(
            email=admin_data['email'],
            password=admin_data['password'],
            first_name=admin_data.get('first_name'),
            last_name=admin_data.get('last_name'),
            tenant_id=new_tenant.id,
            is_active=True,
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()
    
    # 序列化返回数据
    schema = TenantSchema()
    tenant_data = schema.dump(new_tenant)
    
    return jsonify({"tenant": tenant_data, "message": "Tenant created successfully"}), 201


@admin_bp.route('/tenants/<uuid:tenant_id>', methods=['PUT'])
@superadmin_required
def update_tenant(tenant_id):
    """
    更新租户信息
    """
    tenant = Tenant.query.get_or_404(tenant_id)
    
    # 验证请求数据
    schema = TenantUpdateSchema()
    data = schema.load(request.json)
    
    # 更新slug，确保唯一性
    if data.get('slug') and data['slug'] != tenant.slug:
        if Tenant.query.filter_by(slug=data['slug']).first():
            return jsonify({"message": "Slug already exists"}), 400
        tenant.slug = data['slug']
    
    # 更新基本信息
    if data.get('name'):
        tenant.name = data['name']
    
    if data.get('contact_email'):
        tenant.contact_email = data['contact_email']
    
    if 'contact_phone' in data:
        tenant.contact_phone = data['contact_phone']
    
    if 'domain' in data:
        tenant.domain = data['domain']
    
    if 'is_active' in data:
        tenant.is_active = data['is_active']
    
    # 保存更新
    db.session.commit()
    
    # 序列化返回数据
    schema = TenantSchema()
    tenant_data = schema.dump(tenant)
    
    return jsonify({"tenant": tenant_data, "message": "Tenant updated successfully"}), 200


@admin_bp.route('/tenants/<uuid:tenant_id>', methods=['DELETE'])
@superadmin_required
def delete_tenant(tenant_id):
    """
    删除租户（实际上是停用）
    """
    tenant = Tenant.query.get_or_404(tenant_id)
    
    # 不是真正删除，而是停用
    tenant.is_active = False
    db.session.commit()
    
    return jsonify({"message": "Tenant deactivated successfully"}), 200


@admin_bp.route('/stats', methods=['GET'])
@admin_required
def get_admin_stats():
    """
    获取系统统计信息
    """
    # 租户数量
    total_tenants = Tenant.query.count()
    active_tenants = Tenant.query.filter_by(is_active=True).count()
    
    # 用户数量
    total_users = User.query.count()
    admin_users = User.query.filter_by(is_admin=True).count()
    
    # 近期创建的租户
    recent_tenants = Tenant.query.order_by(Tenant.created_at.desc()).limit(5).all()
    schema = TenantSchema(many=True)
    recent_tenants_data = schema.dump(recent_tenants)
    
    return jsonify({
        "stats": {
            "tenants": {
                "total": total_tenants,
                "active": active_tenants
            },
            "users": {
                "total": total_users,
                "admin": admin_users
            }
        },
        "recent_tenants": recent_tenants_data
    }), 200


# --------------------------------
# 用户管理相关路由
# --------------------------------

@admin_bp.route('/tenants/<uuid:tenant_id>/users', methods=['GET'])
@admin_required
def get_tenant_users(tenant_id):
    """
    获取指定租户的所有用户
    """
    tenant = Tenant.query.get_or_404(tenant_id)
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 构建查询
    query = User.query.filter_by(tenant_id=tenant_id)
    
    # 过滤条件
    if request.args.get('email'):
        query = query.filter(User.email.ilike(f"%{request.args.get('email')}%"))
    
    if request.args.get('active') is not None:
        is_active = request.args.get('active').lower() == 'true'
        query = query.filter(User.is_active == is_active)
    
    # 分页
    pagination = query.order_by(User.created_at.desc()).paginate(page=page, per_page=per_page)
    
    # 准备返回数据
    users_data = []
    for user in pagination.items:
        user_data = {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_active": user.is_active,
            "is_admin": user.is_admin,
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat(),
            "roles": []  # 简化后的模型不再有roles关系
        }
        users_data.append(user_data)
    
    return jsonify({
        "users": users_data,
        "total": pagination.total,
        "pages": pagination.pages,
        "page": page,
        "per_page": per_page
    }), 200


@admin_bp.route('/tenants/<uuid:tenant_id>/users/<uuid:user_id>', methods=['GET'])
@admin_required
def get_tenant_user(tenant_id, user_id):
    """
    获取租户下特定用户的详情
    """
    # 验证租户
    tenant = Tenant.query.get_or_404(tenant_id)
    
    # 查询用户
    user = User.query.filter_by(id=user_id, tenant_id=tenant_id).first()
    if not user:
        return jsonify({"message": "User not found in this tenant"}), 404
    
    # 准备用户数据
    user_data = {
        "id": str(user.id),
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_active": user.is_active,
        "is_admin": user.is_admin,
        "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
        "created_at": user.created_at.isoformat(),
        "updated_at": user.updated_at.isoformat(),
        "roles": []  # 简化后的模型不再有roles关系
    }
    
    return jsonify({"user": user_data}), 200


@admin_bp.route('/tenants/<uuid:tenant_id>/users', methods=['POST'])
@admin_required
def create_tenant_user(tenant_id):
    """
    为租户创建新用户
    """
    # 验证租户
    tenant = Tenant.query.get_or_404(tenant_id)
    
    # 验证请求数据
    data = request.json
    
    # 必填字段检查
    if not data.get('email'):
        return jsonify({"message": "Email is required"}), 400
    
    if not data.get('password'):
        return jsonify({"message": "Password is required"}), 400
    
    # 检查邮箱是否已存在
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"message": "Email already registered"}), 400
    
    # 创建新用户
    new_user = User(
        email=data['email'],
        password=data['password'],
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        tenant_id=tenant_id,
        is_active=data.get('is_active', True),
        is_admin=data.get('is_admin', False)
    )
    
    # 保存用户
    db.session.add(new_user)
    db.session.commit()
    
    # 准备返回数据
    user_data = {
        "id": str(new_user.id),
        "email": new_user.email,
        "first_name": new_user.first_name,
        "last_name": new_user.last_name,
        "is_active": new_user.is_active,
        "is_admin": new_user.is_admin,
        "created_at": new_user.created_at.isoformat(),
        "roles": []  # 简化后的模型不再有roles关系
    }
    
    return jsonify({
        "message": "User created successfully",
        "user": user_data
    }), 201


@admin_bp.route('/tenants/<uuid:tenant_id>/users/<uuid:user_id>', methods=['PUT'])
@admin_required
def update_tenant_user(tenant_id, user_id):
    """
    更新租户用户
    """
    # 验证租户
    tenant = Tenant.query.get_or_404(tenant_id)
    
    # 查询用户
    user = User.query.filter_by(id=user_id, tenant_id=tenant_id).first()
    if not user:
        return jsonify({"message": "User not found in this tenant"}), 404
    
    # 验证请求数据
    data = request.json
    
    # 更新用户信息
    if data.get('first_name') is not None:
        user.first_name = data['first_name']
    
    if data.get('last_name') is not None:
        user.last_name = data['last_name']
    
    if data.get('is_active') is not None:
        user.is_active = data['is_active']
    
    if data.get('is_admin') is not None:
        user.is_admin = data['is_admin']
    
    # 保存更新
    db.session.commit()
    
    # 准备返回数据
    user_data = {
        "id": str(user.id),
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_active": user.is_active,
        "is_admin": user.is_admin,
        "updated_at": user.updated_at.isoformat(),
        "roles": []  # 简化后的模型不再有roles关系
    }
    
    return jsonify({
        "message": "User updated successfully",
        "user": user_data
    }), 200


@admin_bp.route('/tenants/<uuid:tenant_id>/users/<uuid:user_id>/toggle-status', methods=['PATCH'])
@admin_required
def toggle_user_status(tenant_id, user_id):
    """
    切换用户的活跃状态
    """
    # 验证租户
    tenant = Tenant.query.get_or_404(tenant_id)
    
    # 查询用户
    user = User.query.filter_by(id=user_id, tenant_id=tenant_id).first()
    if not user:
        return jsonify({"message": "User not found in this tenant"}), 404
    
    # 切换状态
    user.is_active = not user.is_active
    
    # 保存更新
    db.session.commit()
    
    return jsonify({
        "message": f"User status changed to {'active' if user.is_active else 'inactive'}",
        "is_active": user.is_active
    }), 200


@admin_bp.route('/tenants/<uuid:tenant_id>/users/<uuid:user_id>/reset-password', methods=['POST'])
@admin_required
def reset_user_password(tenant_id, user_id):
    """
    重置用户密码
    """
    # 验证租户
    tenant = Tenant.query.get_or_404(tenant_id)
    
    # 查询用户
    user = User.query.filter_by(id=user_id, tenant_id=tenant_id).first()
    if not user:
        return jsonify({"message": "User not found in this tenant"}), 404
    
    # 验证请求数据
    data = request.json
    if not data.get('password'):
        return jsonify({"message": "Password is required"}), 400
    
    # 更新密码
    user.set_password(data['password'])
    
    # 保存更新
    db.session.commit()
    
    return jsonify({"message": "Password reset successfully"}), 200


@admin_bp.route('/tenants/<uuid:tenant_id>/roles', methods=['GET'])
@admin_required
def get_tenant_roles(tenant_id):
    """
    获取租户的所有角色
    """
    print(f"DEBUG - Inside get_tenant_roles for tenant_id: {tenant_id}")
    try:
        # 验证租户
        tenant = Tenant.query.get_or_404(tenant_id)
        
        # 获取请求参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        name = request.args.get('name', '')
        
        print(f"DEBUG - Getting roles for tenant {tenant_id} with page={page}, per_page={per_page}, name={name}")
        
        # 构建查询
        query = Role.query.filter_by(tenant_id=tenant_id)
        
        # 过滤条件
        if name:
            query = query.filter(Role.name.ilike(f"%{name}%"))
        
        # 查询总记录数
        total_count = query.count()
        print(f"DEBUG - Total roles found before pagination: {total_count}")
        
        # 分页
        if page and per_page:
            pagination = query.order_by(Role.created_at.desc()).paginate(page=page, per_page=per_page)
            roles = pagination.items
            total = pagination.total
            pages = pagination.pages
        else:
            # 不分页时返回所有结果
            roles = query.order_by(Role.created_at.desc()).all()
            total = len(roles)
            pages = 1
        
        # 准备返回数据
        roles_data = []
        for role in roles:
            # 查询权限和用户数量
            permissions_count = len(role.permissions)
            users_count = len(role.users)
            
            role_data = {
                "id": str(role.id),
                "name": role.name,
                "description": role.description,
                "created_at": role.created_at.isoformat(),
                "updated_at": role.updated_at.isoformat(),
                "permissions_count": permissions_count,
                "users_count": users_count
            }
            roles_data.append(role_data)

        print(f"DEBUG - Returning {len(roles_data)} roles after pagination")
        return jsonify({
            "roles": roles_data,
            "total": total,
            "pages": pages,
            "page": page,
            "per_page": per_page
        }), 200
    except Exception as e:
        print(f"DEBUG - Error in get_tenant_roles: {str(e)}")
        return jsonify({"message": "Failed to retrieve roles", "error": str(e)}), 500


@admin_bp.route('/tenants/<uuid:tenant_id>/roles/<uuid:role_id>', methods=['GET'])
@admin_required
def get_tenant_role(tenant_id, role_id):
    """
    获取租户角色详情
    """
    # 验证租户
    tenant = Tenant.query.get_or_404(tenant_id)
    
    # 查询角色
    role = Role.query.filter_by(id=role_id, tenant_id=tenant_id).first()
    if not role:
        return jsonify({"message": "Role not found in this tenant"}), 404
    
    # 准备返回数据
    permissions_data = []
    for permission in role.permissions:
        permission_data = {
            "id": str(permission.id),
            "name": permission.name,
            "description": permission.description
        }
        permissions_data.append(permission_data)
    
    users_data = []
    for user in role.users:
        user_data = {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_admin": user.is_admin
        }
        users_data.append(user_data)
    
    role_data = {
        "id": str(role.id),
        "name": role.name,
        "description": role.description,
        "created_at": role.created_at.isoformat(),
        "updated_at": role.updated_at.isoformat(),
        "permissions": permissions_data,
        "users": users_data
    }
    
    return jsonify({"role": role_data}), 200


@admin_bp.route('/tenants/<uuid:tenant_id>/roles', methods=['POST'])
@admin_required
def create_tenant_role(tenant_id):
    """
    为租户创建新角色
    """
    # 验证租户
    tenant = Tenant.query.get_or_404(tenant_id)
    
    # 验证请求数据
    data = request.json
    
    if not data.get('name'):
        return jsonify({"message": "Role name is required"}), 400
    
    # 检查角色名是否已存在
    existing_role = Role.query.filter_by(tenant_id=tenant_id, name=data['name']).first()
    if existing_role:
        return jsonify({"message": "Role with this name already exists for this tenant"}), 400
    
    # 创建新角色
    new_role = Role(
        name=data['name'],
        description=data.get('description'),
        tenant_id=tenant_id
    )
    
    # 保存角色
    db.session.add(new_role)
    db.session.commit()
    
    # 准备返回数据
    role_data = {
        "id": str(new_role.id),
        "name": new_role.name,
        "description": new_role.description,
        "created_at": new_role.created_at.isoformat(),
        "updated_at": new_role.updated_at.isoformat()
    }
    
    return jsonify({
        "message": "Role created successfully",
        "role": role_data
    }), 201


@admin_bp.route('/tenants/<uuid:tenant_id>/roles/<uuid:role_id>', methods=['PUT'])
@admin_required
def update_tenant_role(tenant_id, role_id):
    """
    更新租户角色
    """
    # 验证租户
    tenant = Tenant.query.get_or_404(tenant_id)
    
    # 查询角色
    role = Role.query.filter_by(id=role_id, tenant_id=tenant_id).first()
    if not role:
        return jsonify({"message": "Role not found in this tenant"}), 404
    
    # 验证请求数据
    data = request.json
    
    if data.get('name') and data['name'] != role.name:
        # 检查新名称是否与其他角色冲突
        existing_role = Role.query.filter_by(tenant_id=tenant_id, name=data['name']).first()
        if existing_role and existing_role.id != role_id:
            return jsonify({"message": "Role with this name already exists for this tenant"}), 400
        
        role.name = data['name']
    
    if 'description' in data:
        role.description = data['description']
    
    # 保存更新
    db.session.commit()
    
    # 准备返回数据
    role_data = {
        "id": str(role.id),
        "name": role.name,
        "description": role.description,
        "updated_at": role.updated_at.isoformat()
    }
    
    return jsonify({
        "message": "Role updated successfully",
        "role": role_data
    }), 200


@admin_bp.route('/tenants/<uuid:tenant_id>/roles/<uuid:role_id>', methods=['DELETE'])
@admin_required
def delete_tenant_role(tenant_id, role_id):
    """
    删除租户角色
    """
    # 验证租户
    tenant = Tenant.query.get_or_404(tenant_id)
    
    # 查询角色
    role = Role.query.filter_by(id=role_id, tenant_id=tenant_id).first()
    if not role:
        return jsonify({"message": "Role not found in this tenant"}), 404
    
    # 删除角色
    db.session.delete(role)
    db.session.commit()
    
    return jsonify({"message": "Role deleted successfully"}), 200


@admin_bp.route('/tenants/<uuid:tenant_id>/roles/<uuid:role_id>/permissions', methods=['PUT'])
@admin_required
def update_role_permissions(tenant_id, role_id):
    """
    更新角色权限
    """
    # 验证租户
    tenant = Tenant.query.get_or_404(tenant_id)
    
    # 查询角色
    role = Role.query.filter_by(id=role_id, tenant_id=tenant_id).first()
    if not role:
        return jsonify({"message": "Role not found in this tenant"}), 404
    
    # 验证请求数据
    data = request.json
    if 'permission_ids' not in data:
        return jsonify({"message": "Permission IDs are required"}), 400
    
    # 清除现有权限
    role.permissions = []
    
    # 添加新权限
    for permission_id in data['permission_ids']:
        permission = Permission.query.get(permission_id)
        if permission:
            role.permissions.append(permission)
    
    # 保存更新
    db.session.commit()
    
    return jsonify({"message": "Role permissions updated successfully"}), 200


@admin_bp.route('/tenants/<uuid:tenant_id>/roles/<uuid:role_id>/users', methods=['PUT'])
@admin_required
def update_role_users(tenant_id, role_id):
    """
    更新角色用户
    """
    # 验证租户
    tenant = Tenant.query.get_or_404(tenant_id)
    
    # 查询角色
    role = Role.query.filter_by(id=role_id, tenant_id=tenant_id).first()
    if not role:
        return jsonify({"message": "Role not found in this tenant"}), 404
    
    # 验证请求数据
    data = request.json
    if 'user_ids' not in data:
        return jsonify({"message": "User IDs are required"}), 400
    
    # 获取该租户下所有用户
    tenant_users = User.query.filter_by(tenant_id=tenant_id).all()
    tenant_user_ids = {str(user.id) for user in tenant_users}
    
    # 验证所有用户ID都属于该租户
    for user_id in data['user_ids']:
        if user_id not in tenant_user_ids:
            return jsonify({"message": f"User {user_id} does not belong to this tenant"}), 400
    
    # 清除角色与用户的关联
    role.users = []
    
    # 添加新的用户关联
    for user_id in data['user_ids']:
        user = User.query.get(user_id)
        if user and user.tenant_id == tenant_id:
            role.users.append(user)
    
    # 保存更新
    db.session.commit()
    
    return jsonify({"message": "Role users updated successfully"}), 200


# --------------------------------
# 角色和权限管理相关路由
# --------------------------------

@admin_bp.route('/permissions', methods=['GET'])
@admin_required
def get_permissions():
    """
    获取所有权限列表
    """
    print("DEBUG - Inside get_permissions function")
    try:
        # 查询所有权限
        permissions = Permission.query.all()
        
        # 准备返回数据
        permissions_data = []
        for permission in permissions:
            permission_data = {
                "id": str(permission.id),
                "name": permission.name,
                "description": permission.description,
                "created_at": permission.created_at.isoformat(),
                "updated_at": permission.updated_at.isoformat()
            }
            permissions_data.append(permission_data)

        print(f"DEBUG - Found {len(permissions_data)} permissions")
        return jsonify({"permissions": permissions_data}), 200
    except Exception as e:
        print(f"DEBUG - Error in get_permissions: {str(e)}")
        return jsonify({"message": "Failed to retrieve permissions", "error": str(e)}), 500


@admin_bp.route('/debug/auth', methods=['GET'])
def debug_auth():
    """
    调试端点，用于检查认证信息
    """
    auth_header = request.headers.get('Authorization')
    
    # 获取令牌
    token = None
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
    
    response = {
        "has_auth_header": auth_header is not None,
        "auth_header": auth_header,
        "token": token,
        "token_parsed": None
    }
    
    # 尝试解析令牌（不验证签名）
    if token:
        try:
            from flask_jwt_extended import decode_token
            try:
                decoded = decode_token(token)
                response["token_parsed"] = decoded
            except Exception as e:
                response["token_error"] = str(e)
        except Exception as e:
            response["parse_error"] = str(e)
    
    return jsonify(response) 