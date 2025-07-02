# -*- coding: utf-8 -*-
"""
CustomerCategory 服务
"""

from app.services.base_service import TenantAwareService
from app.models.basic_data import CustomerCategoryManagement
from sqlalchemy import func, and_, or_
from sqlalchemy.exc import IntegrityError
import uuid
from datetime import datetime
import re

class CustomerCategoryService(TenantAwareService):
    """客户分类服务"""
    
    def get_categories(self, include_inactive=False):
        """获取客户分类树"""
        query = self.session.query(CustomerCategoryManagement)
        
        if not include_inactive:
            query = query.filter(CustomerCategoryManagement.is_enabled == True)
        
        categories = query.order_by(CustomerCategoryManagement.sort_order, CustomerCategoryManagement.category_name).all()
        
        # 构建树形结构
        category_dict = {str(cat.id): cat.to_dict() for cat in categories}
        tree = []
        
        for cat_dict in category_dict.values():
            if cat_dict['parent_id']:
                parent = category_dict.get(cat_dict['parent_id'])
                if parent:
                    if 'children' not in parent:
                        parent['children'] = []
                    parent['children'].append(cat_dict)
            else:
                tree.append(cat_dict)
        
        return tree
    
    def create_category(self, data):
        """创建客户分类"""
        try:
            # 准备分类数据
            category_data = {
                'category_code': data.get('category_code'),
                'category_name': data['category_name'],
                'sort_order': data.get('sort_order', 0),
                'description': data.get('description')
            }
            
            # 使用继承的create_with_tenant方法
            category = self.create_with_tenant(CustomerCategoryManagement, **category_data)
            self.commit()
            
            return category.to_dict()
            
        except IntegrityError:
            self.rollback()
            raise ValueError("分类编码已存在")
        except Exception as e:
            self.rollback()
            raise ValueError(f"创建分类失败: {str(e)}")

    def update_category(self, category_id, data):
        """更新客户分类"""
        try:
            category = self.session.query(CustomerCategoryManagement).get(uuid.UUID(category_id))
            if not category:
                raise ValueError("分类不存在")
            
            # 更新字段
            for key, value in data.items():
                if hasattr(category, key):
                    setattr(category, key, value)
            
            self.commit()
            return category.to_dict()
            
        except Exception as e:
            self.rollback()
            raise ValueError(f"更新分类失败: {str(e)}")

    def delete_category(self, category_id):
        """删除客户分类"""
        try:
            category = self.session.query(CustomerCategoryManagement).get(uuid.UUID(category_id))
            if not category:
                raise ValueError("分类不存在")
            
            self.session.delete(category)
            self.commit()
            
            return True
            
        except Exception as e:
            self.rollback()
            raise ValueError(f"删除分类失败: {str(e)}")

    def get_customer_categories(self, page=1, per_page=20, search=None, enabled_only=False):
        """获取客户分类列表"""
        try:
            # 构建基础查询
            query = self.session.query(CustomerCategoryManagement)
            
            # 添加搜索条件
            if search:
                search_pattern = f'%{search}%'
                query = query.filter(or_(
                    CustomerCategoryManagement.category_name.ilike(search_pattern),
                    CustomerCategoryManagement.category_code.ilike(search_pattern),
                    CustomerCategoryManagement.description.ilike(search_pattern)
                ))
            
            if enabled_only:
                query = query.filter(CustomerCategoryManagement.is_enabled == True)
            
            # 排序
            query = query.order_by(CustomerCategoryManagement.sort_order, CustomerCategoryManagement.category_name)
            
            # 分页
            total = query.count()
            offset = (page - 1) * per_page
            categories = query.offset(offset).limit(per_page).all()
            
            customer_categories = []
            for category in categories:
                category_data = category.to_dict(include_user_info=True)
                # 添加用户信息
                if category.created_by:
                    try:
                        from app.models.user import User
                        creator = self.session.query(User).get(category.created_by)
                        category_data['created_by_name'] = creator.get_full_name() if creator else '未知用户'
                    except Exception:
                        category_data['created_by_name'] = '未知用户'
                        
                if category.updated_by:
                    try:
                        from app.models.user import User
                        updater = self.session.query(User).get(category.updated_by)
                        category_data['updated_by_name'] = updater.get_full_name() if updater else '未知用户'
                    except Exception:
                        category_data['updated_by_name'] = '未知用户'
                        
                customer_categories.append(category_data)
            
            # 计算分页信息
            pages = (total + per_page - 1) // per_page
            has_next = page < pages
            has_prev = page > 1
            
            return {
                'customer_categories': customer_categories,
                'total': total,
                'pages': pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': has_next,
                'has_prev': has_prev
            }
            
        except Exception as e:
            raise ValueError(f"获取客户分类列表失败: {str(e)}")

    def get_customer_category(self, category_id):
        """获取客户分类详情"""
        try:
            category = self.session.query(CustomerCategoryManagement).get(uuid.UUID(category_id))
            if not category:
                raise ValueError("客户分类不存在")
            
            return category.to_dict()
            
        except Exception as e:
            raise ValueError(f"获取客户分类详情失败: {str(e)}")

    def create_customer_category(self, data, created_by):
        """创建客户分类"""
        try:
            # 验证数据
            if not data.get('category_name'):
                raise ValueError('客户分类名称不能为空')
            
            try:
                created_by_uuid = uuid.UUID(created_by)
            except ValueError:
                raise ValueError('无效的创建用户ID')
            
            # 检查名称是否重复
            existing = self.session.query(CustomerCategoryManagement).filter_by(
                category_name=data['category_name']
            ).first()
            if existing:
                raise ValueError('客户分类名称已存在')
            
            # 创建客户分类
            category = CustomerCategoryManagement(
                category_name=data['category_name'],
                category_code=data.get('category_code'),
                description=data.get('description'),
                sort_order=data.get('sort_order', 0),
                is_enabled=data.get('is_enabled', True),
                created_by=created_by_uuid
            )
            
            self.session.add(category)
            self.session.commit()
            
            return category.to_dict()
            
        except Exception as e:
            self.session.rollback()
            raise ValueError(f"创建客户分类失败: {str(e)}")

    def update_customer_category(self, category_id, data, updated_by):
        """更新客户分类"""
        try:
            try:
                cat_uuid = uuid.UUID(category_id)
                updated_by_uuid = uuid.UUID(updated_by)
            except ValueError:
                raise ValueError('无效的ID')
            
            category = self.session.query(CustomerCategoryManagement).get(cat_uuid)
            if not category:
                raise ValueError('客户分类不存在')
            
            # 检查名称是否重复（排除自己）
            if data.get('category_name') and data['category_name'] != category.category_name:
                existing = self.session.query(CustomerCategoryManagement).filter_by(
                    category_name=data['category_name']
                ).first()
                if existing:
                    raise ValueError('客户分类名称已存在')
            
            # 更新字段
            for field in ['category_name', 'category_code', 'description', 'sort_order', 'is_enabled']:
                if field in data:
                    setattr(category, field, data[field])
            
            category.updated_by = updated_by_uuid
            self.session.commit()
            
            return category.to_dict()
            
        except Exception as e:
            self.session.rollback()
            raise ValueError(f"更新客户分类失败: {str(e)}")

    def delete_customer_category(self, category_id):
        """删除客户分类"""
        try:
            try:
                cat_uuid = uuid.UUID(category_id)
            except ValueError:
                raise ValueError('无效的客户分类ID')
            
            category = self.session.query(CustomerCategoryManagement).get(cat_uuid)
            if not category:
                raise ValueError('客户分类不存在')
            
            self.session.delete(category)
            self.session.commit()
            
        except Exception as e:
            self.session.rollback()
            raise ValueError(f"删除客户分类失败: {str(e)}")

    def get_category_options(self):
        """获取分类选项列表"""
        try:
            categories = self.session.query(CustomerCategoryManagement).filter(
                CustomerCategoryManagement.is_enabled == True
            ).order_by(CustomerCategoryManagement.sort_order, CustomerCategoryManagement.category_name).all()
            
            return [
                {'value': str(cat.id), 'label': cat.category_name}
                for cat in categories
            ]
            
        except Exception as e:
            raise ValueError(f"获取分类选项失败: {str(e)}")


def get_customer_category_service(tenant_id: str = None, schema_name: str = None) -> CustomerCategoryService:
    """获取客户分类服务实例"""
    return CustomerCategoryService(tenant_id=tenant_id, schema_name=schema_name)


