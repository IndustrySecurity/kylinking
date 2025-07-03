# -*- coding: utf-8 -*-
"""
Specification管理服务
"""
from typing import Dict, List, Optional, Any
from sqlalchemy import and_
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

    def get_specifications(self, page=1, per_page=20, search=None, enabled_only=False):
        """获取规格列表"""
        try:
            # 构建基础查询
            query = self.session.query(Specification)
            
            # 添加搜索条件
            if search:
                search_pattern = f'%{search}%'
                query = query.filter(
                    (Specification.spec_name.ilike(search_pattern)) |
                    (Specification.description.ilike(search_pattern))
                )
            
            if enabled_only:
                query = query.filter(Specification.is_enabled == True)
            
            # 排序
            query = query.order_by(Specification.sort_order, Specification.created_at)
            
            # 分页
            total = query.count()
            offset = (page - 1) * per_page
            specifications_list = query.offset(offset).limit(per_page).all()
            
            specifications = []
            for specification in specifications_list:
                spec_data = specification.to_dict()
                
                # 获取创建人和修改人用户名
                if specification.created_by:
                    created_user = self.session.query(User).get(specification.created_by)
                    if created_user:
                        spec_data['created_by_name'] = created_user.get_full_name()
                    else:
                        spec_data['created_by_name'] = '未知用户'
                else:
                    spec_data['created_by_name'] = '系统'
                    
                if specification.updated_by:
                    updated_user = self.session.query(User).get(specification.updated_by)
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
            raise ValueError(f'查询规格失败: {str(e)}')

    def get_specification(self, spec_id):
        """获取规格详情"""
        try:
            spec_uuid = uuid.UUID(spec_id)
        except ValueError:
            raise ValueError('无效的规格ID')
        
        specification = self.session.query(Specification).get(spec_uuid)
        if not specification:
            raise ValueError('规格不存在')
        
        spec_data = specification.to_dict()
        
        # 获取创建人和修改人用户名
        if specification.created_by:
            created_user = self.session.query(User).get(specification.created_by)
            if created_user:
                spec_data['created_by_name'] = created_user.get_full_name()
            else:
                spec_data['created_by_name'] = '未知用户'
        
        if specification.updated_by:
            updated_user = self.session.query(User).get(specification.updated_by)
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
        
        # 检查规格名称是否重复
        existing = self.session.query(Specification).filter_by(
            spec_name=data['spec_name']
        ).first()
        if existing:
            raise ValueError('规格名称已存在')
        
        try:
            created_by_uuid = uuid.UUID(created_by)
        except ValueError:
            raise ValueError('无效的创建用户ID')
        
        # 准备数据
        spec_data = {
            'spec_name': data['spec_name'],
            'length': data['length'],
            'width': data['width'],
            'roll': data['roll'],
            'description': data.get('description'),
            'sort_order': data.get('sort_order', 0),
            'is_enabled': data.get('is_enabled', True),
        }
        
        try:
            specification = self.create_with_tenant(Specification, **spec_data)
            
            # 计算面积和格式
            if hasattr(specification, 'calculate_area_and_format'):
                specification.calculate_area_and_format()
            
            self.commit()
            return specification.to_dict()
        except Exception as e:
            self.rollback()
            raise ValueError(f'创建规格失败: {str(e)}')

    def update_specification(self, spec_id, data, updated_by):
        """更新规格"""
        try:
            spec_uuid = uuid.UUID(spec_id)
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的ID')
        
        specification = self.session.query(Specification).get(spec_uuid)
        if not specification:
            raise ValueError('规格不存在')
        
        # 检查规格名称是否重复（排除自己）
        if 'spec_name' in data and data['spec_name'] != specification.spec_name:
            existing = self.session.query(Specification).filter(
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
        if hasattr(specification, 'calculate_area_and_format'):
            specification.calculate_area_and_format()
        
        try:
            self.commit()
            return specification.to_dict()
        except Exception as e:
            self.rollback()
            raise ValueError(f'更新规格失败: {str(e)}')

    def delete_specification(self, spec_id):
        """删除规格"""
        try:
            spec_uuid = uuid.UUID(spec_id)
        except ValueError:
            raise ValueError('无效的规格ID')
        
        specification = self.session.query(Specification).get(spec_uuid)
        if not specification:
            raise ValueError('规格不存在')
        
        try:
            self.session.delete(specification)
            self.commit()
        except Exception as e:
            self.rollback()
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
                    specification = self.update_specification(
                        data['id'], data, updated_by
                    )
                    results.append(specification)
                else:
                    # 创建新记录
                    specification = self.create_specification(
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
            self.rollback()
            raise ValueError(f'批量更新失败，错误详情: {errors}')
        
        return results

    def get_enabled_specifications(self):
        """获取启用的规格列表（用于下拉选择）"""
        try:
            specifications = self.session.query(Specification).filter_by(
                is_enabled=True
            ).order_by(Specification.sort_order, Specification.spec_name).all()
            
            return [spec.to_dict() for spec in specifications]
        except Exception as e:
            raise ValueError(f'获取启用规格失败: {str(e)}')


def get_specification_service(tenant_id: Optional[str] = None, schema_name: Optional[str] = None) -> SpecificationService:
    """获取规格服务实例"""
    return SpecificationService(tenant_id=tenant_id, schema_name=schema_name) 
