from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from datetime import timedelta
import logging

# 初始化SQLAlchemy
db = SQLAlchemy()

# 初始化JWTManager
jwt = JWTManager()

# 初始化Migrate
migrate = Migrate()

# 添加JWT自定义错误处理
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    print(f"DEBUG - Expired token: {jwt_payload}")
    return {"message": "Token has expired"}, 401

@jwt.invalid_token_loader
def invalid_token_callback(error_string):
    print(f"DEBUG - Invalid token: {error_string}")
    return {"message": f"Invalid token: {error_string}"}, 401

@jwt.unauthorized_loader
def missing_token_callback(error_string):
    print(f"DEBUG - Missing token: {error_string}")
    return {"message": f"Missing JWT token: {error_string}"}, 401

@jwt.needs_fresh_token_loader
def token_not_fresh_callback(jwt_header, jwt_payload):
    print(f"DEBUG - Token not fresh: {jwt_payload}")
    return {"message": "Fresh token required"}, 401

@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    print(f"DEBUG - Revoked token: {jwt_payload}")
    return {"message": "Token has been revoked"}, 401 