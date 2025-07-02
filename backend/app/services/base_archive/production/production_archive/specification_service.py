# -*- coding: utf-8 -*-
"""
Specification管理服务
"""
from typing import Dict, List, Optional, Any
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import uuid

from app.services.base_service import TenantAwareService
from app.models.basic_data import Specification
from app.models.user import User


class SpecificationService(TenantAwareService):
    """规格管理服务"""

    def __init__(self, tenant_id: Optional[str] = None, schema_name: Optional[str] = None):
        """初始化Specification服务"""
        super().__init__(tenant_id, schema_name)

        if schema_name != 'public':
            pass

    def get_specifications(self, page=1, per_page=20, search=None, enabled_only=False):
        """获取规格列表"""
        
        # 获取当前schema名称
        
        from flask import g, current_app
        schema_name = getattr(g, 'schema_name', current_app.config.get('DEFAULT_SCHEMA', 'public'))
        
        # 构建基础查询
        base_query = f"""
        SELECT 
            id, spec_name, length, width, roll, area_sqm, spec_format,
            description, sort_order, is_enabled, created_by, updated_by, 
            created_at, updated_at
        FROM {schema_name}.specifications
        """
        
        # 添加搜索条件
        where_conditions = []
        params = {}
        
        if search:
            where_conditions.append("""
                (spec_name ILIKE :search OR 
                 spec_format ILIKE :search OR
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
        FROM {schema_name}.specifications
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
            
            specifications = []
            for row in rows:
                spec_data = {
                    'id': str(row.id),
                    'spec_name': row.spec_name,
                    'length': float(row.length) if row.length else None,
                    'width': float(row.width) if row.width else None,
                    'roll': float(row.roll) if row.roll else None,
                    'area_sqm': float(row.area_sqm) if row.area_sqm else None,
                    'spec_format': row.spec_format,
                    'description': row.description,
                    'sort_order': row.sort_order,
                    'is_enabled': row.is_enabled,
                    'created_by': str(row.created_by) if row.created_by else None,
                    'updated_by': str(row.updated_by) if row.updated_by else None,
                    'created_at': row.created_at.isoformat() if row.created_at else None,
                    'updated_at': row.updated_at.isoformat() if row.updated_at else None,
                }
                
                # 获取创建人和修改人用户名
                if row.created_by:
                    created_user = User.query.get(row.created_by)
                    if created_user:
                        spec_data['created_by_name'] = created_user.get_full_name()
                    else:
                        spec_data['created_by_name'] = '未知用户'
                else:
                    spec_data['created_by_name'] = '系统'
                    
                if row.updated_by:
                    updated_user = User.query.get(row.updated_by)
                    if updated_user:
                        spec_data['updated_by_name'] = updated_user.get_full_name()
                    else:
                        spec_data['updated_by_name'] = '未知用户'
                else:
                    spec_data['updated_by_name'] = ''
                
                specifications.append(spec_data)
            
            # 计算分页信息
            pages = (total + per_page - 1) // per_page
            has_next = page < pages
            has_prev = page > 1
            
            return {
                'specifications': specifications,
                'total': total,
                'pages': pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': has_next,
                'has_prev': has_prev
            }
            
        except Exception as e:
            current_app.logger.error(f"Error querying specifications: {str(e)}")
            raise ValueError(f'查询规格失败: {str(e)}')
    def get_specification(self, spec_id):
        """获取规格详情"""
        
        try:
            spec_uuid = uuid.UUID(spec_id)
        except ValueError:
            raise ValueError('无效的规格ID')
        
        from app.models.basic_data import Specification
        specification = Specification.query.get(spec_uuid)
        if not specification:
            raise ValueError('规格不存在')
        
        spec_data = specification.to_dict()
        
        # 获取创建人和修改人用户名
        if specification.created_by:
            created_user = User.query.get(specification.created_by)
            if created_user:
                spec_data['created_by_name'] = created_user.get_full_name()
            else:
                spec_data['created_by_name'] = '未知用户'
        
        if specification.updated_by:
            updated_user = User.query.get(specification.updated_by)
            if updated_user:
                spec_data['updated_by_name'] = updated_user.get_full_name()
            else:
                spec_data['updated_by_name'] = '未知用户'
        
        return spec_data
    def create_specification(self, data, created_by):
        """创建规格"""
        
        # 验证数据
        if not data.get('spec_name'):
            raise ValueError('规格名称不能为空')
        
        if not data.get('length') or not data.get('width') or not data.get('roll'):
            raise ValueError('长、宽、卷不能为空')
        
        from app.models.basic_data import Specification
        
        # 检查规格名称是否重复
        existing = Specification.query.filter_by(
            spec_name=data['spec_name']
        ).first()
        if existing:
            raise ValueError('规格名称已存在')
        
        try:
            created_by_uuid = uuid.UUID(created_by)
        except ValueError:
            raise ValueError('无效的创建用户ID')
        
        # 创建规格
        specification = Specification(
            spec_name=data['spec_name'],
            length=data['length'],
            width=data['width'],
            roll=data['roll'],
            description=data.get('description'),
            sort_order=data.get('sort_order', 0),
            is_enabled=data.get('is_enabled', True),
            created_by=created_by_uuid
        )
        
        # 计算面积和格式
        specification.calculate_area_and_format()
        
        try:
            self.get_session().add(specification)
            self.get_session().commit()
            return specification.to_dict()
        except Exception as e:
            self.get_session().rollback()
            raise ValueError(f'创建规格失败: {str(e)}')
    def update_specification(self, spec_id, data, updated_by):
        """更新规格"""
        
        try:
            spec_uuid = uuid.UUID(spec_id)
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的ID')
        
        from app.models.basic_data import Specification
        specification = Specification.query.get(spec_uuid)
        if not specification:
            raise ValueError('规格不存在')
        
        # 检查规格名称是否重复（排除自己）
        if 'spec_name' in data and data['spec_name'] != specification.spec_name:
            existing = Specification.query.filter(
                and_(
                    Specification.spec_name == data['spec_name'],
                    Specification.id != spec_uuid
                )
            ).first()
            if existing:
                raise ValueError('规格名称已存在')
        
        # 更新字段
        for key, value in data.items():
            if hasattr(specification, key):
                setattr(specification, key, value)
        
        specification.updated_by = updated_by_uuid
        
        # 重新计算面积和格式
        specification.calculate_area_and_format()
        
        try:
            self.get_session().commit()
            return specification.to_dict()
        except Exception as e:
            self.get_session().rollback()
            raise ValueError(f'更新规格失败: {str(e)}')
    def delete_specification(self, spec_id):
        """删除规格"""
        
        try:
            spec_uuid = uuid.UUID(spec_id)
        except ValueError:
            raise ValueError('无效的规格ID')
        
        from app.models.basic_data import Specification
        specification = Specification.query.get(spec_uuid)
        if not specification:
            raise ValueError('规格不存在')
        
        try:
            self.get_session().delete(specification)
            self.get_session().commit()
        except Exception as e:
            self.get_session().rollback()
            raise ValueError(f'删除规格失败: {str(e)}')
    def batch_update_specifications(self, data_list, updated_by):
        """批量更新规格（用于可编辑表格）"""
        
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
                    specification = SpecificationService().update_specification(
                        data['id'], data, updated_by
                    )
                    results.append(specification)
                else:
                    # 创建新记录
                    specification = SpecificationService().create_specification(
                        data, updated_by
                    )
                    results.append(specification)
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
    def get_enabled_specifications(self):
        """获取启用的规格列表（用于下拉选择）"""
        
        from app.models.basic_data import Specification
        specifications = Specification.query.filter_by(
            is_enabled=True
        ).order_by(Specification.sort_order, Specification.spec_name).all()
        
        return [spec.to_dict() for spec in specifications] 
