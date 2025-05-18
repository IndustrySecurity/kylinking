from marshmallow import Schema, fields, validate, ValidationError, validates_schema, validates
import re


class TenantSchema(Schema):
    """
    租户数据序列化
    """
    id = fields.UUID(dump_only=True)
    name = fields.String(dump_only=True)
    slug = fields.String(dump_only=True)
    schema_name = fields.String(dump_only=True)
    domain = fields.String(dump_only=True)
    contact_email = fields.Email(dump_only=True)
    contact_phone = fields.String(dump_only=True)
    is_active = fields.Boolean(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class TenantCreateSchema(Schema):
    """
    创建租户的请求数据验证
    """
    name = fields.String(required=True, validate=validate.Length(min=2, max=255))
    slug = fields.String(required=True, validate=validate.Length(min=2, max=100))
    schema_name = fields.String(required=True, validate=validate.Length(min=2, max=63))
    domain = fields.String(validate=validate.Length(max=255))
    contact_email = fields.Email(required=True)
    contact_phone = fields.String(validate=validate.Length(max=50))
    is_active = fields.Boolean(default=True)
    
    # 管理员信息，用于创建初始管理员账户
    admin = fields.Dict(keys=fields.String(), values=fields.Field())
    
    @validates('slug')
    def validate_slug(self, value):
        """
        验证slug格式
        """
        if value and not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', value):
            raise ValidationError('Slug must contain only lowercase letters, numbers, and hyphens, and cannot begin or end with a hyphen')
    
    @validates('schema_name')
    def validate_schema_name(self, value):
        """
        验证schema_name格式
        """
        if value:
            # PostgreSQL schema名称只能包含字母、数字和下划线，且不能以数字开头
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', value):
                raise ValidationError('Schema name must start with a letter or underscore, and contain only letters, numbers, and underscores')
            
            # 检查保留的schema名称
            reserved_schemas = ['public', 'information_schema', 'pg_catalog', 'pg_toast', 'system']
            if value.lower() in reserved_schemas:
                raise ValidationError(f'Schema name cannot be one of the reserved names: {", ".join(reserved_schemas)}')


class TenantUpdateSchema(Schema):
    """
    更新租户的请求数据验证
    """
    name = fields.String(validate=validate.Length(min=2, max=255))
    slug = fields.String(validate=validate.Length(min=2, max=100))
    domain = fields.String(validate=validate.Length(max=255), allow_none=True)
    contact_email = fields.Email()
    contact_phone = fields.String(validate=validate.Length(max=50), allow_none=True)
    is_active = fields.Boolean()
    
    @validates('slug')
    def validate_slug(self, value):
        """
        验证slug格式
        """
        if value and not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', value):
            raise ValidationError('Slug must contain only lowercase letters, numbers, and hyphens, and cannot begin or end with a hyphen') 