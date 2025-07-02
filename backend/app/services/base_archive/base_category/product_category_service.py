# -*- coding: utf-8 -*-
"""
ProductCategory管理服务
"""
from typing import Dict, List, Optional, Any
from sqlalchemy import text
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
        
        # 获取当前schema名称
        
        from flask import g, current_app
        schema_name = getattr(g, 'schema_name', current_app.config.get('DEFAULT_SCHEMA', 'public'))
        
        # 构建基础查询
        base_query = f"""
        SELECT 
            id, category_name, subject_name, is_blown_film, delivery_days,
            description, sort_order, is_enabled, created_by, updated_by, created_at, updated_at
        FROM {schema_name}.product_categories
        """
        
        # 添加搜索条件
        where_conditions = []
        params = {}
        
        if search:
            where_conditions.append("""
                (category_name ILIKE :search OR 
                 subject_name ILIKE :search OR 
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
        FROM {schema_name}.product_categories
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
            
            product_categories = []
            for row in rows:
                product_category_data = {
                    'id': str(row.id),
                    'category_name': row.category_name,
                    'subject_name': row.subject_name,
                    'is_blown_film': row.is_blown_film,
                    'delivery_days': row.delivery_days,
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
                        product_category_data['created_by_name'] = created_user.get_full_name()
                    else:
                        product_category_data['created_by_name'] = '未知用户'
                else:
                    product_category_data['created_by_name'] = '系统'
                    
                if row.updated_by:
                    updated_user = User.query.get(row.updated_by)
                    if updated_user:
                        product_category_data['updated_by_name'] = updated_user.get_full_name()
                    else:
                        product_category_data['updated_by_name'] = '未知用户'
                else:
                    product_category_data['updated_by_name'] = ''
                
                product_categories.append(product_category_data)
            
            # 计算分页信息
            pages = (total + per_page - 1) // per_page
            has_next = page < pages
            has_prev = page > 1
            
            return {
                'product_categories': product_categories,
                'total': total,
                'pages': pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': has_next,
                'has_prev': has_prev
            }
            
        except Exception as e:
            current_app.logger.error(f"Error querying product categories: {str(e)}")
            raise ValueError(f'查询产品分类失败: {str(e)}')
    def get_product_category(self, product_category_id):
        """获取产品分类详情"""
        
        try:
            product_category_uuid = uuid.UUID(product_category_id)
        except ValueError:
            raise ValueError('无效的产品分类ID')
        
        from app.models.basic_data import ProductCategory
        product_category = ProductCategory.query.get(product_category_uuid)
        if not product_category:
            raise ValueError('产品分类不存在')
        
        product_category_data = product_category.to_dict()
        
        # 获取创建人和修改人用户名
        if product_category.created_by:
            created_user = User.query.get(product_category.created_by)
            if created_user:
                product_category_data['created_by_name'] = created_user.get_full_name()
            else:
                product_category_data['created_by_name'] = '未知用户'
        
        if product_category.updated_by:
            updated_user = User.query.get(product_category.updated_by)
            if updated_user:
                product_category_data['updated_by_name'] = updated_user.get_full_name()
            else:
                product_category_data['updated_by_name'] = '未知用户'
        
        return product_category_data
    def create_product_category(self, data, created_by):
        """创建产品分类"""
        
        # 验证数据
        if not data.get('category_name'):
            raise ValueError('产品分类名称不能为空')
        
        from app.models.basic_data import ProductCategory
        
        # 检查产品分类名称是否重复
        existing = ProductCategory.query.filter_by(
            category_name=data['category_name']
        ).first()
        if existing:
            raise ValueError('产品分类名称已存在')
        
        try:
            created_by_uuid = uuid.UUID(created_by)
        except ValueError:
            raise ValueError('无效的创建用户ID')
        
        # 创建产品分类
        product_category = ProductCategory(
            category_name=data['category_name'],
            subject_name=data.get('subject_name'),
            is_blown_film=data.get('is_blown_film', False),
            delivery_days=data.get('delivery_days'),
            description=data.get('description'),
            sort_order=data.get('sort_order', 0),
            is_enabled=data.get('is_enabled', True),
            created_by=created_by_uuid
        )
        
        try:
            self.get_session().add(product_category)
            self.get_session().commit()
            return product_category.to_dict()
        except Exception as e:
            self.get_session().rollback()
            raise ValueError(f'创建产品分类失败: {str(e)}')
    def update_product_category(self, product_category_id, data, updated_by):
        """更新产品分类"""
        
        try:
            product_category_uuid = uuid.UUID(product_category_id)
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的ID')
        
        from app.models.basic_data import ProductCategory
        product_category = ProductCategory.query.get(product_category_uuid)
        if not product_category:
            raise ValueError('产品分类不存在')
        
        # 检查产品分类名称是否重复（排除自己）
        if 'category_name' in data and data['category_name'] != product_category.category_name:
            existing = ProductCategory.query.filter(
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
            self.get_session().commit()
            return product_category.to_dict()
        except Exception as e:
            self.get_session().rollback()
            raise ValueError(f'更新产品分类失败: {str(e)}')
    def delete_product_category(self, product_category_id):
        """删除产品分类"""
        
        try:
            product_category_uuid = uuid.UUID(product_category_id)
        except ValueError:
            raise ValueError('无效的产品分类ID')
        
        from app.models.basic_data import ProductCategory
        product_category = ProductCategory.query.get(product_category_uuid)
        if not product_category:
            raise ValueError('产品分类不存在')
        
        try:
            self.get_session().delete(product_category)
            self.get_session().commit()
        except Exception as e:
            self.get_session().rollback()
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
                    product_category = ProductCategoryService().update_product_category(
                        data['id'], data, updated_by
                    )
                    results.append(product_category)
                else:
                    # 创建新记录
                    product_category = ProductCategoryService().create_product_category(
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
            self.get_session().rollback()
            raise ValueError(f'批量更新失败，错误详情: {errors}')
        
        return results
    def get_enabled_product_categories(self):
        """获取启用的产品分类列表（用于下拉选择）"""
        
        from app.models.basic_data import ProductCategory
        product_categories = ProductCategory.query.filter_by(
            is_enabled=True
        ).order_by(ProductCategory.sort_order, ProductCategory.category_name).all()
        
        return [pc.to_dict() for pc in product_categories]

