from flask import jsonify, request, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_current_user
)
from app.api.auth import auth_bp
from app.models.user import User
from app.extensions import db
from app.schemas.auth import LoginSchema, RegisterSchema
from app.utils.tenant_context import TenantContext
from datetime import datetime


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    用户登录
    """
    # 验证请求数据
    schema = LoginSchema()
    data = schema.load(request.json)
    
    # 尝试从请求头获取租户信息，如果没有，尝试从邮箱提取
    tenant_id = request.headers.get('X-Tenant-ID')
    email = data['email']
    
    if not tenant_id and '@' in email:
        # 提取邮箱域名部分
        email_domain = email.split('@')[1]
        if email_domain and email_domain != 'kylinking.com':
            # 检查是否是 tenant.kylinking.com 格式
            if '.' in email_domain:
                domain_parts = email_domain.split('.')
                if len(domain_parts) > 2:
                    # 查询数据库，查找匹配的租户
                    from app.models.tenant import Tenant
                    tenant = Tenant.query.filter_by(slug=domain_parts[0]).first()
                    if tenant:
                        tenant_id = str(tenant.id)
                        current_app.logger.info(f"Extracted tenant '{tenant.name}' (ID: {tenant.id}) from email domain")
    
    # 查找用户
    user = User.query.filter_by(email=data['email']).first()
    
    # 验证用户和密码
    if not user or not user.check_password(data['password']):
        return jsonify({"message": "Invalid email or password"}), 401
    
    # 验证用户状态
    if not user.is_active:
        return jsonify({"message": "Account is inactive"}), 403
    
    # 更新最后登录时间 - 直接设置，不调用方法
    user.last_login_at = datetime.now()
    db.session.commit()
    
    # 创建访问令牌和刷新令牌
    additional_claims = {
        "is_admin": user.is_admin,
        "is_superadmin": user.is_superadmin,
        "tenant_id": str(user.tenant_id) if user.tenant_id else None
    }
    
    access_token = create_access_token(identity=str(user.id), additional_claims=additional_claims)
    refresh_token = create_refresh_token(identity=str(user.id))
    
    # 获取租户信息
    tenant_info = None
    if user.tenant_id:
        from app.models.tenant import Tenant
        tenant = Tenant.query.get(user.tenant_id)
        if tenant:
            tenant_info = {
                "id": str(tenant.id),
                "name": tenant.name,
                "slug": tenant.slug,
                "schema_name": tenant.schema_name,
                "is_active": tenant.is_active
            }
    
    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_admin": user.is_admin,
            "is_superadmin": user.is_superadmin,
            "tenant_id": str(user.tenant_id) if user.tenant_id else None
        },
        "tenant": tenant_info
    }), 200


@auth_bp.route('/admin-login', methods=['POST'])
def admin_login():
    """
    管理员登录
    """
    # 验证请求数据
    schema = LoginSchema()
    data = schema.load(request.json)
    
    # 查找用户
    user = User.query.filter_by(email=data['email']).first()
    
    # 验证用户和密码
    if not user or not user.check_password(data['password']):
        return jsonify({"message": "Invalid email or password"}), 401
    
    # 验证用户状态和管理员权限
    if not user.is_active:
        return jsonify({"message": "Account is inactive"}), 403
    
    if not user.is_superadmin:
        return jsonify({"message": "Superadmin privileges required"}), 403
    
    # 更新最后登录时间
    user.last_login_at = datetime.now()
    db.session.commit()
    
    # 创建访问令牌和刷新令牌 - 确保is_admin设置为True
    additional_claims = {
        "is_admin": True,  # 强制设置为True，确保管理员权限
        "is_superadmin": user.is_superadmin,
        "tenant_id": str(user.tenant_id) if user.tenant_id else None
    }
    
    print(f"DEBUG - Admin login for user {user.email}, claims: {additional_claims}")
    
    access_token = create_access_token(identity=str(user.id), additional_claims=additional_claims)
    refresh_token = create_refresh_token(identity=str(user.id))
    
    # 获取租户信息
    tenant_info = None
    if user.tenant_id:
        from app.models.tenant import Tenant
        tenant = Tenant.query.get(user.tenant_id)
        if tenant:
            tenant_info = {
                "id": str(tenant.id),
                "name": tenant.name,
                "slug": tenant.slug,
                "schema_name": tenant.schema_name,
                "is_active": tenant.is_active
            }
    
    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_admin": user.is_admin,
            "is_superadmin": user.is_superadmin,
            "tenant_id": str(user.tenant_id) if user.tenant_id else None
        },
        "tenant": tenant_info
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    刷新访问令牌
    """
    # 获取当前用户ID
    current_user_id = get_jwt_identity()
    
    # 查找用户
    user = User.query.filter_by(id=current_user_id).first()
    
    if not user or not user.is_active:
        return jsonify({"message": "User not found or inactive"}), 404
    
    # 创建新的访问令牌
    additional_claims = {
        "is_admin": user.is_admin or user.is_superadmin,  # 确保管理员权限被保留
        "is_superadmin": user.is_superadmin,
        "tenant_id": str(user.tenant_id) if user.tenant_id else None
    }
    
    print(f"DEBUG - Token refresh for user {user.email}, claims: {additional_claims}")
    
    access_token = create_access_token(identity=current_user_id, additional_claims=additional_claims)
    
    return jsonify({"access_token": access_token}), 200


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    用户注册（仅在系统允许自注册时使用）
    """
    # 验证请求数据
    schema = RegisterSchema()
    data = schema.load(request.json)
    
    # 检查邮箱是否已存在
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"message": "Email already registered"}), 400
    
    # 创建新用户
    tenant_id = data.get('tenant_id')
    new_user = User(
        email=data['email'],
        password=data['password'],
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        tenant_id=tenant_id,
        is_active=True,
        is_admin=False,
        is_superadmin=False
    )
    
    # 保存用户
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({
        "message": "User registered successfully",
        "user": {
            "id": str(new_user.id),
            "email": new_user.email
        }
    }), 201


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    用户登出
    注意：由于JWT是无状态的，服务器端不需要额外操作
    客户端应该删除本地存储的token
    """
    return jsonify({"message": "Successfully logged out"}), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_user_info():
    """
    获取当前用户信息
    """
    current_user_id = get_jwt_identity()
    user = User.query.filter_by(id=current_user_id).first()
    
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    return jsonify({
        "user": {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_admin": user.is_admin,
            "is_superadmin": user.is_superadmin,
            "tenant_id": str(user.tenant_id) if user.tenant_id else None,
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None
        }
    }), 200


@auth_bp.route('/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    """
    修改密码
    """
    current_user_id = get_jwt_identity()
    user = User.query.filter_by(id=current_user_id).first()
    
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    data = request.json
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not current_password or not new_password:
        return jsonify({"message": "Current password and new password are required"}), 400
    
    # 验证当前密码
    if not user.check_password(current_password):
        return jsonify({"message": "Current password is incorrect"}), 400
    
    # 验证新密码长度
    if len(new_password) < 6:
        return jsonify({"message": "New password must be at least 6 characters long"}), 400
    
    # 设置新密码
    user.set_password(new_password)
    db.session.commit()
    
    return jsonify({"message": "Password changed successfully"}), 200


@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """
    更新个人信息
    """
    current_user_id = get_jwt_identity()
    user = User.query.filter_by(id=current_user_id).first()
    
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    data = request.json
    
    # 只更新现有字段
    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']
    
    db.session.commit()
    
    return jsonify({
        "message": "Profile updated successfully",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_admin": user.is_admin,
            "is_superadmin": user.is_superadmin,
            "tenant_id": str(user.tenant_id) if user.tenant_id else None
        }
    }), 200


@auth_bp.route('/debug/token', methods=['POST'])
def debug_token():
    """
    调试令牌
    """
    data = request.json
    token = data.get('token')
    
    if not token:
        return jsonify({
            "error": "No token provided"
        }), 400
    
    try:
        # 尝试解析令牌
        from flask_jwt_extended import decode_token
        
        try:
            decoded = decode_token(token)
            return jsonify({
                "valid": True,
                "decoded": decoded
            })
        except Exception as e:
            return jsonify({
                "valid": False,
                "error": str(e)
            })
    except Exception as e:
        return jsonify({
            "error": f"Failed to process token: {str(e)}"
        }), 500 