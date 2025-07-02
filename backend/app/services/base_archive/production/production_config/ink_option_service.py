# -*- coding: utf-8 -*-
"""
InkOption管理服务
"""
from typing import Dict, List, Optional, Any
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import uuid

from app.services.base_service import TenantAwareService
from app.models.basic_data import InkOption
from app.models.user import User


class InkOptionService(TenantAwareService):
    """油墨选项管理服务"""

    def __init__(self, tenant_id: Optional[str] = None, schema_name: Optional[str] = None):
        """初始化InkOption服务"""
        super().__init__(tenant_id, schema_name)

        if schema_name != 'public':
            pass

    def get_ink_options(self, page=1, per_page=20, search=None, enabled_only=False):
        """获取油墨选项列表"""
        
        # 获取当前schema名称
        
        from flask import g, current_app
        schema_name = getattr(g, 'schema_name', current_app.config.get('DEFAULT_SCHEMA', 'public'))
        
        # 构建基础查询
        base_query = f"""
        SELECT 
            id, option_name, sort_order, 
            is_enabled, description, created_by, updated_by, created_at, updated_at
        FROM {schema_name}.ink_options
        """
        
        # 添加搜索条件
        where_conditions = []
        params = {}
        
        if search:
            where_conditions.append("""
                (option_name ILIKE :search OR 
                 description ILIKE :search)
            """)
            params['search'] = f'%{search}%'
        
        if enabled_only:
            where_conditions.append("is_enabled = true")
        
        # 构建完整查询
        if where_conditions:
            base_query += " WHERE " + " AND ".join(where_conditions)
        
        base_query += " ORDER BY sort_order, created_at"
        
        # 计算总数
        count_query = f"""
        SELECT COUNT(*) as total
        FROM {schema_name}.ink_options
        """
        if where_conditions:
            count_query += " WHERE " + " AND ".join(where_conditions)
        
        # 执行查询
        try:
            # 获取总数
            count_result = self.get_session().execute(text(count_query), params)
            total = count_result.scalar()
            
            # 计算分页
            offset = (page - 1) * per_page
            params['limit'] = per_page
            params['offset'] = offset
            
            # 添加分页
            paginated_query = base_query + " LIMIT :limit OFFSET :offset"
            
            # 执行分页查询
            result = self.get_session().execute(text(paginated_query), params)
            rows = result.fetchall()
            
            ink_options = []
            for row in rows:
                option_data = {
                    'id': str(row.id),
                    'option_name': row.option_name,
                    'sort_order': row.sort_order,
                    'is_enabled': row.is_enabled,
                    'description': row.description,
                    'created_by': str(row.created_by) if row.created_by else None,
                    'updated_by': str(row.updated_by) if row.updated_by else None,
                    'created_at': row.created_at.isoformat() if row.created_at else None,
                    'updated_at': row.updated_at.isoformat() if row.updated_at else None,
                }
                
                # 获取创建人和修改人用户名
                if row.created_by:
                    created_user = User.query.get(row.created_by)
                    if created_user:
                        option_data['created_by_name'] = created_user.get_full_name()
                    else:
                        option_data['created_by_name'] = '未知用户'
                else:
                    option_data['created_by_name'] = '系统'
                    
                if row.updated_by:
                    updated_user = User.query.get(row.updated_by)
                    if updated_user:
                        option_data['updated_by_name'] = updated_user.get_full_name()
                    else:
                        option_data['updated_by_name'] = '未知用户'
                else:
                    option_data['updated_by_name'] = ''
                
                ink_options.append(option_data)
            
            # 计算分页信息
            pages = (total + per_page - 1) // per_page
            has_next = page < pages
            has_prev = page > 1
            
            return {
                'ink_options': ink_options,
                'total': total,
                'pages': pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': has_next,
                'has_prev': has_prev
            }
            
        except Exception as e:
            current_app.logger.error(f"Error querying ink options: {str(e)}")
            raise ValueError(f'查询油墨选项失败: {str(e)}')
    def get_ink_option(self, option_id):
        """获取油墨选项详情"""
        
        try:
            option_uuid = uuid.UUID(option_id)
        except ValueError:
            raise ValueError('无效的油墨选项ID')
        
        from app.models.basic_data import InkOption
        option = InkOption.query.get(option_uuid)
        if not option:
            raise ValueError('油墨选项不存在')
        
        option_data = option.to_dict()
        
        # 获取创建人和修改人用户名
        if option.created_by:
            created_user = User.query.get(option.created_by)
            if created_user:
                option_data['created_by_name'] = created_user.get_full_name()
            else:
                option_data['created_by_name'] = '未知用户'
        
        if option.updated_by:
            updated_user = User.query.get(option.updated_by)
            if updated_user:
                option_data['updated_by_name'] = updated_user.get_full_name()
            else:
                option_data['updated_by_name'] = '未知用户'
        
        return option_data
    def create_ink_option(self, data, created_by):
        """创建油墨选项"""
        
        # 验证数据
        if not data.get('option_name'):
            raise ValueError('选项名称不能为空')
        
        from app.models.basic_data import InkOption
        
        # 检查选项名称是否重复
        existing = InkOption.query.filter_by(
            option_name=data['option_name']
        ).first()
        if existing:
            raise ValueError('选项名称已存在')
        
        try:
            created_by_uuid = uuid.UUID(created_by)
        except ValueError:
            raise ValueError('无效的创建用户ID')
        
        # 创建油墨选项
        option = InkOption(
            option_name=data['option_name'],
            sort_order=data.get('sort_order', 0),
            is_enabled=data.get('is_enabled', True),
            description=data.get('description'),
            created_by=created_by_uuid
        )
        
        try:
            self.get_session().add(option)
            self.get_session().commit()
            return option.to_dict()
        except Exception as e:
            self.get_session().rollback()
            raise ValueError(f'创建油墨选项失败: {str(e)}')
    def update_ink_option(self, option_id, data, updated_by):
        """更新油墨选项"""
        
        try:
            option_uuid = uuid.UUID(option_id)
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的ID')
        
        from app.models.basic_data import InkOption
        option = InkOption.query.get(option_uuid)
        if not option:
            raise ValueError('油墨选项不存在')
        
        # 检查选项名称是否重复（排除自己）
        if 'option_name' in data and data['option_name'] != option.option_name:
            existing = InkOption.query.filter(
                and_(
                    InkOption.option_name == data['option_name'],
                    InkOption.id != option_uuid
                )
            ).first()
            if existing:
                raise ValueError('选项名称已存在')
        
        # 更新字段
        for key, value in data.items():
            if hasattr(option, key):
                setattr(option, key, value)
        
        option.updated_by = updated_by_uuid
        
        try:
            self.get_session().commit()
            return option.to_dict()
        except Exception as e:
            self.get_session().rollback()
            raise ValueError(f'更新油墨选项失败: {str(e)}')
    def delete_ink_option(self, option_id):
        """删除油墨选项"""
        
        try:
            option_uuid = uuid.UUID(option_id)
        except ValueError:
            raise ValueError('无效的油墨选项ID')
        
        from app.models.basic_data import InkOption
        option = InkOption.query.get(option_uuid)
        if not option:
            raise ValueError('油墨选项不存在')
        
        try:
            self.get_session().delete(option)
            self.get_session().commit()
        except Exception as e:
            self.get_session().rollback()
            raise ValueError(f'删除油墨选项失败: {str(e)}')
    def batch_update_ink_options(self, data_list, updated_by):
        """批量更新油墨选项（用于可编辑表格）"""
        
        try:
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的用户ID')
        
        results = []
        errors = []
        
        for index, data in enumerate(data_list):
            try:
                if 'id' in data and data['id']:
                    # 更新现有记录
                    option = InkOptionService().update_ink_option(
                        data['id'], data, updated_by
                    )
                    results.append(option)
                else:
                    # 创建新记录
                    option = InkOptionService().create_ink_option(
                        data, updated_by
                    )
                    results.append(option)
            except ValueError as e:
                errors.append({
                    'index': index,
                    'error': str(e),
                    'data': data
                })
        
        if errors:
            # 如果有错误，回滚事务
            self.get_session().rollback()
            raise ValueError(f'批量更新失败，错误详情: {errors}')
        
        return results
    def get_enabled_ink_options(self):
        """获取启用的油墨选项列表（用于下拉选择）"""
        
        from app.models.basic_data import InkOption
        options = InkOption.query.filter_by(
            is_enabled=True
        ).order_by(InkOption.sort_order, InkOption.option_name).all()
        
        return [option.to_dict() for option in options]

# ==================== 工厂函数 ====================

def get_ink_option_service(tenant_id: str = None, schema_name: str = None) -> InkOptionService:
    """
    获取油墨选项服务实例
    
    Args:
        tenant_id: 租户ID（可选）
        schema_name: Schema名称（可选）
    
    Returns:
        InkOptionService: 油墨选项服务实例
    """
    return InkOptionService(tenant_id=tenant_id, schema_name=schema_name)

