# -*- coding: utf-8 -*-
"""
错误信息常量定义
统一管理所有API返回的错误信息，确保使用中文
"""

# 通用错误信息
COMMON_ERRORS = {
    'required_field': '此字段为必填项',
    'invalid_format': '格式无效',
    'not_found': '未找到相关记录',
    'permission_denied': '权限不足',
    'server_error': '服务器内部错误',
    'database_error': '数据库错误',
    'validation_error': '数据验证失败',
    'duplicate_record': '记录已存在',
    'operation_failed': '操作失败',
    'operation_success': '操作成功',
}

# 认证相关错误信息
AUTH_ERRORS = {
    'invalid_credentials': '邮箱或密码错误',
    'account_inactive': '账户已被禁用',
    'admin_required': '需要管理员权限',
    'superadmin_required': '需要超级管理员权限',
    'email_exists': '邮箱已被注册',
    'user_not_found': '用户不存在',
    'password_required': '密码为必填项',
    'password_too_short': '密码长度至少为6个字符',
    'password_mismatch': '两次输入的密码不匹配',
    'current_password_incorrect': '当前密码错误',
    'logout_success': '成功退出登录',
    'password_changed': '密码修改成功',
    'password_reset_success': '密码重置成功',
    'profile_updated': '个人信息更新成功',
}

# 租户相关错误信息
TENANT_ERRORS = {
    'tenant_not_found': '租户不存在',
    'slug_exists': '租户标识已存在',
    'schema_exists': 'Schema名称已存在',
    'tenant_created': '租户创建成功',
    'tenant_updated': '租户更新成功',
    'tenant_deactivated': '租户已停用',
    'user_not_in_tenant': '用户不属于此租户',
}

# 用户管理相关错误信息
USER_ERRORS = {
    'email_required': '邮箱为必填项',
    'email_exists': '邮箱已被注册',
    'user_created': '用户创建成功',
    'user_updated': '用户更新成功',
    'user_deleted': '用户删除成功',
    'user_not_found': '用户不存在',
    'user_not_in_tenant': '在此租户中未找到用户',
    'cannot_delete_last_admin': '无法删除最后一个管理员用户',
    'user_status_changed': '用户状态已更改',
    'user_enabled': '用户已启用',
    'user_disabled': '用户已禁用',
}

# 角色管理相关错误信息
ROLE_ERRORS = {
    'role_name_required': '角色名称为必填项',
    'role_exists': '角色名称已存在',
    'role_created': '角色创建成功',
    'role_updated': '角色更新成功',
    'role_deleted': '角色删除成功',
    'role_not_found': '角色不存在',
    'role_not_in_tenant': '在此租户中未找到角色',
    'permission_ids_required': '权限ID为必填项',
    'user_ids_required': '用户ID为必填项',
    'role_permissions_updated': '角色权限更新成功',
    'role_users_updated': '角色用户更新成功',
}

# 权限管理相关错误信息
PERMISSION_ERRORS = {
    'permission_name_required': '权限名称为必填项',
    'permission_created': '权限创建成功',
    'permission_updated': '权限更新成功',
    'permission_deleted': '权限删除成功',
    'permission_not_found': '权限不存在',
    'no_data_provided': '未提供数据',
}

# 生产计划相关错误信息
PRODUCTION_ERRORS = {
    'name_required': '名称为必填项',
    'start_date_required': '开始日期为必填项',
    'end_date_required': '结束日期为必填项',
    'status_required': '状态为必填项',
    'invalid_date_format': '日期格式无效，请使用YYYY-MM-DD格式',
    'end_date_before_start': '结束日期不能早于开始日期',
    'plan_created': '生产计划创建成功',
    'plan_updated': '生产计划更新成功',
    'plan_deleted': '生产计划删除成功',
    'plan_not_found': '生产计划不存在',
    'equipment_id_required': '设备ID为必填项',
    'start_time_required': '开始时间为必填项',
    'quantity_required': '数量为必填项',
    'invalid_datetime_format': '日期时间格式无效，请使用ISO格式(YYYY-MM-DDTHH:MM:SS.sssZ)',
    'record_created': '生产记录创建成功',
}

# 库存相关错误信息
INVENTORY_ERRORS = {
    'missing_required_field': '缺少必需字段',
    'create_failed': '创建失败',
    'get_failed': '获取失败',
    'update_failed': '更新失败',
    'delete_failed': '删除失败',
    'submit_failed': '提交失败',
    'approve_failed': '审核失败',
    'execute_failed': '执行失败',
    'cancel_failed': '取消失败',
}

# 动态字段相关错误信息
DYNAMIC_FIELD_ERRORS = {
    'operation_failed': '操作失败',
    'field_not_found': '字段不存在',
    'field_exists': '字段已存在',
    'invalid_field_type': '字段类型无效',
    'field_created': '字段创建成功',
    'field_updated': '字段更新成功',
    'field_deleted': '字段删除成功',
}

def get_error_message(category, key, **kwargs):
    """
    获取错误信息
    
    Args:
        category: 错误类别 (如 'AUTH_ERRORS', 'USER_ERRORS' 等)
        key: 错误键名
        **kwargs: 格式化参数
    
    Returns:
        str: 格式化的错误信息
    """
    error_dict = globals().get(category, {})
    message = error_dict.get(key, '未知错误')
    
    if kwargs:
        try:
            message = message.format(**kwargs)
        except (KeyError, ValueError):
            pass
    
    return message 