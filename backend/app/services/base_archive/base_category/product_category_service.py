# -*- coding: utf-8 -*-
"""
ProductCategory管理服务
"""
from typing import Dict, List, Optional, Any
from sqlalchemy import text, or_, and_
from sqlalchemy.exc import SQLAlchemyError
import uuid

from app.services.base_service import TenantAwareService
from app.models.basic_data import ProductCategory
from app.models.user import User


class ProductCategoryService(TenantAwareService):
    """产品分类管理服务"""

    def __init__(self, tenant_id: Optional[str] = None, schema_name: Optional[str] = None):
        """初始化ProductCategory服务"""
        super().__init__(tenant_id, schema_name)

        if schema_name != 'public':
            pass

    def get_product_categories(self, page=1, per_page=20, search=None, enabled_only=False):
        """获取产品分类列表"""
        try:
            # 构建查询
            query = self.session.query(ProductCategory)
            
            # 添加搜索条件
            if search:
                search_pattern = f"%{search}%"
                query = query.filter(or_(
                    ProductCategory.category_name.ilike(search_pattern),
                    ProductCategory.subject_name.ilike(search_pattern),
                    ProductCategory.description.ilike(search_pattern)
                ))
            
            if enabled_only:
                query = query.filter(ProductCategory.is_enabled == True)
        
            # 排序
            query = query.order_by(ProductCategory.sort_order, ProductCategory.created_at)
            
            # 分页
            total = query.count()
            product_categories = query.offset((page - 1) * per_page).limit(per_page).all()
            
            # 添加用户信息
            for category in product_categories:
                if category.created_by:
                    creator = self.session.query(User).get(category.created_by)
                    category.created_by_name = creator.get_full_name() if creator else '未知用户'
                else:
                    category.created_by_name = '系统'
                    
                if category.updated_by:
                    updater = self.session.query(User).get(category.updated_by)
                    category.updated_by_name = updater.get_full_name() if updater else '未知用户'
                else:
                    category.updated_by_name = ''
            
            # 计算分页信息
            pages = (total + per_page - 1) // per_page
            has_next = page < pages
            has_prev = page > 1
            
            return {
                'product_categories': [category.to_dict(include_user_info=True) for category in product_categories],
                'total': total,
                'pages': pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': has_next,
                'has_prev': has_prev
            }
            
        except Exception as e:
            raise ValueError(f'查询产品分类失败: {str(e)}')
    def get_product_category(self, product_category_id):
        """获取产品分类详情"""
        try:
            product_category_uuid = uuid.UUID(product_category_id)
        except ValueError:
            raise ValueError('无效的产品分类ID')
        
        product_category = self.session.query(ProductCategory).get(product_category_uuid)
        if not product_category:
            raise ValueError('产品分类不存在')
        
        # 添加用户信息
        if product_category.created_by:
            created_user = self.session.query(User).get(product_category.created_by)
            product_category.created_by_name = created_user.get_full_name() if created_user else '未知用户'
        
        if product_category.updated_by:
            updated_user = self.session.query(User).get(product_category.updated_by)
            product_category.updated_by_name = updated_user.get_full_name() if updated_user else '未知用户'
        
        return product_category.to_dict(include_user_info=True)
    def create_product_category(self, data, created_by):
        """创建产品分类"""
        # 验证数据
        if not data.get('category_name'):
            raise ValueError('产品分类名称不能为空')
        
        # 检查产品分类名称是否重复
        existing = self.session.query(ProductCategory).filter_by(
            category_name=data['category_name']
        ).first()
        if existing:
            raise ValueError('产品分类名称已存在')
        
        try:
            created_by_uuid = uuid.UUID(created_by)
        except ValueError:
            raise ValueError('无效的创建用户ID')
        
        try:
        # 创建产品分类
            product_category = self.create_with_tenant(ProductCategory,
            category_name=data['category_name'],
            subject_name=data.get('subject_name'),
            is_blown_film=data.get('is_blown_film', False),
            delivery_days=data.get('delivery_days'),
            description=data.get('description'),
            sort_order=data.get('sort_order', 0),
            is_enabled=data.get('is_enabled', True),
            created_by=created_by_uuid
        )
        
            self.commit()
            return product_category.to_dict()
        except Exception as e:
            self.rollback()
            raise ValueError(f'创建产品分类失败: {str(e)}')
    def update_product_category(self, product_category_id, data, updated_by):
        """更新产品分类"""
        try:
            product_category_uuid = uuid.UUID(product_category_id)
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的ID')
        
        product_category = self.session.query(ProductCategory).get(product_category_uuid)
        if not product_category:
            raise ValueError('产品分类不存在')
        
        # 检查产品分类名称是否重复（排除自己）
        if 'category_name' in data and data['category_name'] != product_category.category_name:
            existing = self.session.query(ProductCategory).filter(
                and_(
                    ProductCategory.category_name == data['category_name'],
                    ProductCategory.id != product_category_uuid
                )
            ).first()
            if existing:
                raise ValueError('产品分类名称已存在')
        
        # 更新字段
        for key, value in data.items():
            if hasattr(product_category, key):
                setattr(product_category, key, value)
        
        product_category.updated_by = updated_by_uuid
        
        try:
            self.commit()
            return product_category.to_dict()
        except Exception as e:
            self.rollback()
            raise ValueError(f'更新产品分类失败: {str(e)}')
    def delete_product_category(self, product_category_id):
        """删除产品分类"""
        try:
            product_category_uuid = uuid.UUID(product_category_id)
        except ValueError:
            raise ValueError('无效的产品分类ID')
        
        product_category = self.session.query(ProductCategory).get(product_category_uuid)
        if not product_category:
            raise ValueError('产品分类不存在')
        
        try:
            self.session.delete(product_category)
            self.commit()
        except Exception as e:
            self.rollback()
            raise ValueError(f'删除产品分类失败: {str(e)}')
    def batch_update_product_categories(self, data_list, updated_by):
        """批量更新产品分类（用于可编辑表格）"""
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
                    product_category = self.update_product_category(
                        data['id'], data, updated_by
                    )
                    results.append(product_category)
                else:
                    # 创建新记录
                    product_category = self.create_product_category(
                        data, updated_by
                    )
                    results.append(product_category)
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
    
    def get_enabled_product_categories(self):
        """获取启用的产品分类列表（用于下拉选择）"""
        product_categories = self.session.query(ProductCategory).filter_by(
            is_enabled=True
        ).order_by(ProductCategory.sort_order, ProductCategory.category_name).all()
        
        return [pc.to_dict() for pc in product_categories]

