from marshmallow import Schema, fields, validate, ValidationError, validates_schema
import re


class LoginSchema(Schema):
    """
    登录请求数据验证
    """
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=6))


class RegisterSchema(Schema):
    """
    注册请求数据验证
    """
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=8))
    password_confirm = fields.String(required=True)
    first_name = fields.String(validate=validate.Length(min=1, max=100))
    last_name = fields.String(validate=validate.Length(min=1, max=100))
    tenant_id = fields.UUID(allow_none=True)
    
    @validates_schema
    def validate_password(self, data, **kwargs):
        """
        验证密码复杂度和确认密码
        """
        password = data.get('password')
        password_confirm = data.get('password_confirm')
        
        # 检查密码确认
        if password != password_confirm:
            raise ValidationError('Passwords do not match', 'password_confirm')
        
        # 检查密码复杂度
        if password:
            # 至少包含一个数字和一个字母
            if not (re.search(r'\d', password) and re.search(r'[a-zA-Z]', password)):
                raise ValidationError('Password must contain at least one letter and one number', 'password')
    
    class Meta:
        # 指定哪些字段在序列化时输出
        fields = ('email', 'password', 'first_name', 'last_name', 'tenant_id')


class PasswordResetRequestSchema(Schema):
    """
    密码重置请求数据验证
    """
    email = fields.Email(required=True)


class PasswordResetSchema(Schema):
    """
    密码重置数据验证
    """
    token = fields.String(required=True)
    password = fields.String(required=True, validate=validate.Length(min=8))
    password_confirm = fields.String(required=True)
    
    @validates_schema
    def validate_password(self, data, **kwargs):
        """
        验证密码复杂度和确认密码
        """
        password = data.get('password')
        password_confirm = data.get('password_confirm')
        
        # 检查密码确认
        if password != password_confirm:
            raise ValidationError('Passwords do not match', 'password_confirm')
        
        # 检查密码复杂度
        if password:
            # 至少包含一个数字和一个字母
            if not (re.search(r'\d', password) and re.search(r'[a-zA-Z]', password)):
                raise ValidationError('Password must contain at least one letter and one number', 'password') 