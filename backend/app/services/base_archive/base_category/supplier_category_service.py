# -*- coding: utf-8 -*-
"""
SupplierCategory 服务
"""

from app.services.base_service import TenantAwareService
from app.models.basic_data import SupplierCategoryManagement
from app.models.user import User
from sqlalchemy import func, and_, or_
from sqlalchemy.exc import IntegrityError
import uuid
from datetime import datetime
import re
from typing import Optional
from flask import current_app

class SupplierCategoryService(TenantAwareService):
    """供应商分类服务"""
    
    def get_supplier_categories(self, page=1, per_page=20, search=None, enabled_only=False):
        """获取供应商分类列表"""
        try:
            # 构建基础查询
            query = self.session.query(SupplierCategoryManagement)
            
            # 添加搜索条件
            if search:
                search_pattern = f'%{search}%'
                query = query.filter(or_(
                    SupplierCategoryManagement.category_name.ilike(search_pattern),
                    SupplierCategoryManagement.category_code.ilike(search_pattern),
                    SupplierCategoryManagement.description.ilike(search_pattern)
                ))
            
            if enabled_only:
                query = query.filter(SupplierCategoryManagement.is_enabled == True)
            
            # 排序
            query = query.order_by(SupplierCategoryManagement.sort_order, SupplierCategoryManagement.created_at)
            
            # 分页
            total = query.count()
            offset = (page - 1) * per_page
            categories = query.offset(offset).limit(per_page).all()
            
            supplier_categories = []
            for category in categories:
                category_data = category.to_dict()
                
                # 获取创建人和修改人用户名
                if category.created_by:
                    created_user = self.session.query(User).get(category.created_by)
                    category_data['created_by_name'] = created_user.get_full_name() if created_user else '未知用户'
                else:
                    category_data['created_by_name'] = '系统'
                    
                if category.updated_by:
                    updated_user = self.session.query(User).get(category.updated_by)
                    category_data['updated_by_name'] = updated_user.get_full_name() if updated_user else '未知用户'
                else:
                    category_data['updated_by_name'] = ''
                
                supplier_categories.append(category_data)
            
            # 计算分页信息
            pages = (total + per_page - 1) // per_page
            has_next = page < pages
            has_prev = page > 1
            
            return {
                'supplier_categories': supplier_categories,
                'total': total,
                'pages': pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': has_next,
                'has_prev': has_prev
            }
            
        except Exception as e:
            current_app.logger.error(f"Error querying supplier categories: {str(e)}")
            raise ValueError(f'查询供应商分类失败: {str(e)}')
    
    def get_supplier_category(self, category_id):
        """获取供应商分类详情"""
        try:
            category_uuid = uuid.UUID(category_id)
        except ValueError:
            raise ValueError('无效的供应商分类ID')
        
        category = self.session.query(SupplierCategoryManagement).get(category_uuid)
        if not category:
            raise ValueError('供应商分类不存在')
        
        category_data = category.to_dict()
        
        # 获取创建人和修改人用户名
        if category.created_by:
            created_user = self.session.query(User).get(category.created_by)
            category_data['created_by_name'] = created_user.get_full_name() if created_user else '未知用户'
        
        if category.updated_by:
            updated_user = self.session.query(User).get(category.updated_by)
            category_data['updated_by_name'] = updated_user.get_full_name() if updated_user else '未知用户'
        
        return category_data
    
    def create_supplier_category(self, data, created_by):
        """创建供应商分类"""
        # 验证数据
        if not data.get('category_name'):
            raise ValueError('供应商分类名称不能为空')
        
        # 检查供应商分类名称是否重复
        existing = self.session.query(SupplierCategoryManagement).filter_by(
            category_name=data['category_name']
        ).first()
        if existing:
            raise ValueError('供应商分类名称已存在')
        
        # 检查编码是否重复
        if data.get('category_code'):
            existing_code = self.session.query(SupplierCategoryManagement).filter_by(
                category_code=data['category_code']
            ).first()
            if existing_code:
                raise ValueError('供应商分类编码已存在')
        
        try:
            created_by_uuid = uuid.UUID(created_by)
        except ValueError:
            raise ValueError('无效的创建用户ID')
        
        # 准备分类数据
        category_data = {
            'category_name': data['category_name'],
            'category_code': data.get('category_code'),
            'description': data.get('description'),
            'is_plate_making': data.get('is_plate_making', False),
            'is_outsourcing': data.get('is_outsourcing', False),
            'is_knife_plate': data.get('is_knife_plate', False),
            'sort_order': data.get('sort_order', 0),
            'is_enabled': data.get('is_enabled', True),
        }
        
        try:
            # 使用继承的create_with_tenant方法
            category = self.create_with_tenant(SupplierCategoryManagement, **category_data)
            self.commit()
            return category.to_dict()
        except Exception as e:
            self.rollback()
            raise ValueError(f'创建供应商分类失败: {str(e)}')
    
    def update_supplier_category(self, category_id, data, updated_by):
        """更新供应商分类"""
        try:
            category_uuid = uuid.UUID(category_id)
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的ID')
        
        category = self.session.query(SupplierCategoryManagement).get(category_uuid)
        if not category:
            raise ValueError('供应商分类不存在')
        
        # 检查名称是否重复（排除当前记录）
        if 'category_name' in data:
            existing = self.session.query(SupplierCategoryManagement).filter(
                SupplierCategoryManagement.category_name == data['category_name'],
                SupplierCategoryManagement.id != category_uuid
            ).first()
            if existing:
                raise ValueError('供应商分类名称已存在')
        
        # 检查编码是否重复（排除当前记录）
        if data.get('category_code'):
            existing_code = self.session.query(SupplierCategoryManagement).filter(
                SupplierCategoryManagement.category_code == data['category_code'],
                SupplierCategoryManagement.id != category_uuid
            ).first()
            if existing_code:
                raise ValueError('供应商分类编码已存在')
        
        # 更新字段
        update_fields = [
            'category_name', 'category_code', 'description', 
            'is_plate_making', 'is_outsourcing', 'is_knife_plate', 
            'sort_order', 'is_enabled'
        ]
        
        for field in update_fields:
            if field in data:
                setattr(category, field, data[field])
        
        category.updated_by = updated_by_uuid
        
        try:
            self.commit()
            return category.to_dict()
        except Exception as e:
            self.rollback()
            raise ValueError(f'更新供应商分类失败: {str(e)}')
    
    def delete_supplier_category(self, category_id):
        """删除供应商分类"""
        try:
            category_uuid = uuid.UUID(category_id)
        except ValueError:
            raise ValueError('无效的供应商分类ID')
        
        category = self.session.query(SupplierCategoryManagement).get(category_uuid)
        if not category:
            raise ValueError('供应商分类不存在')
        
        try:
            self.session.delete(category)
            self.commit()
            return True
        except Exception as e:
            self.rollback()
            raise ValueError(f'删除供应商分类失败: {str(e)}')
    
    def batch_update_supplier_categories(self, data_list, updated_by):
        """批量更新供应商分类"""
        try:
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的更新用户ID')
        
        results = []
        errors = []
        
        for item in data_list:
            try:
                if 'id' not in item:
                    errors.append({'error': '缺少ID字段', 'data': item})
                    continue
                
                result = self.update_supplier_category(item['id'], item, updated_by)
                results.append(result)
            except Exception as e:
                errors.append({'error': str(e), 'data': item})
        
        return {
            'success_count': len(results),
            'error_count': len(errors),
            'results': results,
            'errors': errors
        }
    
    def get_enabled_supplier_categories(self):
        """获取启用的供应商分类列表"""
        categories = self.session.query(SupplierCategoryManagement).filter_by(
            is_enabled=True
        ).order_by(SupplierCategoryManagement.sort_order).all()
        
        return [category.to_dict() for category in categories]

    def get_category_options(self):
        """获取分类选项列表"""
        try:
            categories = self.session.query(SupplierCategoryManagement).filter(
                SupplierCategoryManagement.is_enabled == True
            ).order_by(SupplierCategoryManagement.sort_order, SupplierCategoryManagement.category_name).all()
            
            return [
                {'value': str(cat.id), 'label': cat.category_name}
                for cat in categories
            ]
            
        except Exception as e:
            raise ValueError(f"获取分类选项失败: {str(e)}")


def get_supplier_category_service(tenant_id: str = None, schema_name: str = None) -> SupplierCategoryService:
    """获取供应商分类服务实例"""
    return SupplierCategoryService(tenant_id=tenant_id, schema_name=schema_name)

