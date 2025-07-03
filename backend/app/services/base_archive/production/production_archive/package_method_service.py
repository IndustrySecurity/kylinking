# -*- coding: utf-8 -*-
"""
PackageMethod管理服务
"""
from typing import Dict, List, Optional, Any
from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError
import uuid

from app.services.base_service import TenantAwareService
from app.models.basic_data import PackageMethod
from app.models.user import User


class PackageMethodService(TenantAwareService):
    """包装方式管理服务"""

    def __init__(self, tenant_id: Optional[str] = None, schema_name: Optional[str] = None):
        """初始化PackageMethod服务"""
        super().__init__(tenant_id, schema_name)

    def get_package_methods(self, page=1, per_page=20, search=None, enabled_only=False):
        """获取包装方式列表"""
        try:
            # 构建基础查询
            query = self.session.query(PackageMethod)
            
            # 添加搜索条件
            if search:
                search_pattern = f'%{search}%'
                query = query.filter(
                    PackageMethod.package_name.ilike(search_pattern) |
                    PackageMethod.package_code.ilike(search_pattern) |
                    PackageMethod.description.ilike(search_pattern)
                )
            
            if enabled_only:
                query = query.filter(PackageMethod.is_enabled == True)
            
            # 排序
            query = query.order_by(PackageMethod.sort_order, PackageMethod.created_at)
            
            # 分页
            total = query.count()
            offset = (page - 1) * per_page
            package_methods_list = query.offset(offset).limit(per_page).all()
            
            package_methods = []
            for package_method in package_methods_list:
                package_method_data = package_method.to_dict()
                
                # 获取创建人和修改人用户名
                if package_method.created_by:
                    created_user = self.session.query(User).get(package_method.created_by)
                    if created_user:
                        package_method_data['created_by_name'] = created_user.get_full_name()
                    else:
                        package_method_data['created_by_name'] = '未知用户'
                else:
                    package_method_data['created_by_name'] = '系统'
                    
                if package_method.updated_by:
                    updated_user = self.session.query(User).get(package_method.updated_by)
                    if updated_user:
                        package_method_data['updated_by_name'] = updated_user.get_full_name()
                    else:
                        package_method_data['updated_by_name'] = '未知用户'
                else:
                    package_method_data['updated_by_name'] = ''
                
                package_methods.append(package_method_data)
            
            # 计算分页信息
            pages = (total + per_page - 1) // per_page
            has_next = page < pages
            has_prev = page > 1
            
            return {
                'package_methods': package_methods,
                'total': total,
                'pages': pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': has_next,
                'has_prev': has_prev
            }
            
        except Exception as e:
            raise ValueError(f'查询包装方式失败: {str(e)}')

    def get_package_method(self, package_method_id):
        """获取包装方式详情"""
        try:
            package_method_uuid = uuid.UUID(package_method_id)
        except ValueError:
            raise ValueError('无效的包装方式ID')
        
        package_method = self.session.query(PackageMethod).get(package_method_uuid)
        if not package_method:
            raise ValueError('包装方式不存在')
        
        package_method_data = package_method.to_dict()
        
        # 获取创建人和修改人用户名
        if package_method.created_by:
            created_user = self.session.query(User).get(package_method.created_by)
            if created_user:
                package_method_data['created_by_name'] = created_user.get_full_name()
            else:
                package_method_data['created_by_name'] = '未知用户'
        
        if package_method.updated_by:
            updated_user = self.session.query(User).get(package_method.updated_by)
            if updated_user:
                package_method_data['updated_by_name'] = updated_user.get_full_name()
            else:
                package_method_data['updated_by_name'] = '未知用户'
        
        return package_method_data

    def create_package_method(self, data, created_by):
        """创建包装方式"""
        # 验证数据
        if not data.get('package_name'):
            raise ValueError('包装方式名称不能为空')
        
        # 检查包装方式名称是否重复
        existing = self.session.query(PackageMethod).filter_by(
            package_name=data['package_name']
        ).first()
        if existing:
            raise ValueError('包装方式名称已存在')
        
        # 检查编码是否重复
        if data.get('package_code'):
            existing_code = self.session.query(PackageMethod).filter_by(
                package_code=data['package_code']
            ).first()
            if existing_code:
                raise ValueError('包装方式编码已存在')
        
        try:
            created_by_uuid = uuid.UUID(created_by)
        except ValueError:
            raise ValueError('无效的创建用户ID')
        
        # 准备数据
        package_method_data = {
            'package_name': data['package_name'],
            'package_code': data.get('package_code'),
            'description': data.get('description'),
            'sort_order': data.get('sort_order', 0),
            'is_enabled': data.get('is_enabled', True),
        }
        
        try:
            package_method = self.create_with_tenant(PackageMethod, **package_method_data)
            self.commit()
            return package_method.to_dict()
        except Exception as e:
            self.rollback()
            raise ValueError(f'创建包装方式失败: {str(e)}')

    def update_package_method(self, package_method_id, data, updated_by):
        """更新包装方式"""
        try:
            package_method_uuid = uuid.UUID(package_method_id)
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的ID')
        
        package_method = self.session.query(PackageMethod).get(package_method_uuid)
        if not package_method:
            raise ValueError('包装方式不存在')
        
        # 检查包装方式名称是否重复（排除自己）
        if 'package_name' in data and data['package_name'] != package_method.package_name:
            existing = self.session.query(PackageMethod).filter(
                and_(
                    PackageMethod.package_name == data['package_name'],
                    PackageMethod.id != package_method_uuid
                )
            ).first()
            if existing:
                raise ValueError('包装方式名称已存在')
        
        # 检查编码是否重复（排除自己）
        if 'package_code' in data and data['package_code'] != package_method.package_code:
            existing_code = self.session.query(PackageMethod).filter(
                and_(
                    PackageMethod.package_code == data['package_code'],
                    PackageMethod.id != package_method_uuid
                )
            ).first()
            if existing_code:
                raise ValueError('包装方式编码已存在')
        
        # 更新字段
        for key, value in data.items():
            if hasattr(package_method, key):
                setattr(package_method, key, value)
        
        package_method.updated_by = updated_by_uuid
        
        try:
            self.commit()
            return package_method.to_dict()
        except Exception as e:
            self.rollback()
            raise ValueError(f'更新包装方式失败: {str(e)}')

    def delete_package_method(self, package_method_id):
        """删除包装方式"""
        try:
            package_method_uuid = uuid.UUID(package_method_id)
        except ValueError:
            raise ValueError('无效的包装方式ID')
        
        package_method = self.session.query(PackageMethod).get(package_method_uuid)
        if not package_method:
            raise ValueError('包装方式不存在')
        
        try:
            self.session.delete(package_method)
            self.commit()
        except Exception as e:
            self.rollback()
            raise ValueError(f'删除包装方式失败: {str(e)}')

    def get_enabled_package_methods(self):
        """获取启用的包装方式列表（用于下拉选择）"""
        try:
            package_methods = self.session.query(PackageMethod).filter_by(
                is_enabled=True
            ).order_by(PackageMethod.sort_order, PackageMethod.package_name).all()
            
            return [pm.to_dict() for pm in package_methods]
        except Exception as e:
            raise ValueError(f'获取启用包装方式失败: {str(e)}')


def get_package_method_service(tenant_id: Optional[str] = None, schema_name: Optional[str] = None) -> PackageMethodService:
    """获取包装方式服务实例"""
    return PackageMethodService(tenant_id=tenant_id, schema_name=schema_name)

