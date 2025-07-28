# -*- coding: utf-8 -*-
"""
权限管理服务类
"""
from typing import Dict, List, Optional, Any
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import uuid

from app.services.base_service import BaseService
from app.models.user import Permission
from app.models.user import User


class PermissionService(BaseService):
    """权限管理服务"""

    def __init__(self):
        """初始化权限服务"""
        # 权限是系统级别的，存储在system schema中
        super().__init__(tenant_id=None, schema_name='system')

    def get_permissions(self, page=1, per_page=20, search=None):
        """获取权限列表"""
        try:
            # 构建基础查询
            query = self.session.query(Permission)
            
            # 添加搜索条件
            if search:
                search_pattern = f'%{search}%'
                query = query.filter(
                    Permission.name.ilike(search_pattern) |
                    Permission.description.ilike(search_pattern)
                )
            
            # 排序
            query = query.order_by(Permission.name)
            
            # 分页
            total = query.count()
            offset = (page - 1) * per_page
            permissions_list = query.offset(offset).limit(per_page).all()
            
            permissions = []
            for permission in permissions_list:
                permission_data = {
                    "id": str(permission.id),
                    "name": permission.name,
                    "description": permission.description,
                    "created_at": permission.created_at.isoformat() if permission.created_at else None,
                    "updated_at": permission.updated_at.isoformat() if permission.updated_at else None
                }
                permissions.append(permission_data)
            
            return {
                "permissions": permissions,
                "total": total,
                "page": page,
                "per_page": per_page,
                "pages": (total + per_page - 1) // per_page
            }
            
        except Exception as e:
            self.logger.error(f"获取权限列表失败: {str(e)}")
            raise ValueError(f"获取权限列表失败: {str(e)}")

    def get_permission_by_id(self, permission_id: str):
        """根据ID获取权限"""
        try:
            permission = self.session.query(Permission).filter(
                Permission.id == uuid.UUID(permission_id)
            ).first()
            
            if not permission:
                return None
            
            return {
                "id": str(permission.id),
                "name": permission.name,
                "description": permission.description,
                "created_at": permission.created_at.isoformat() if permission.created_at else None,
                "updated_at": permission.updated_at.isoformat() if permission.updated_at else None
            }
            
        except Exception as e:
            self.logger.error(f"获取权限详情失败: {str(e)}")
            raise ValueError(f"获取权限详情失败: {str(e)}")

    def create_permission(self, name: str, description: str = None, created_by: str = None):
        """创建新权限"""
        try:
            # 检查权限名称是否已存在
            existing_permission = self.session.query(Permission).filter(
                Permission.name == name
            ).first()
            
            if existing_permission:
                raise ValueError("权限名称已存在")
            
            # 创建新权限
            new_permission = Permission(
                name=name,
                description=description
            )
            
            self.session.add(new_permission)
            self.session.commit()
            
            return {
                "id": str(new_permission.id),
                "name": new_permission.name,
                "description": new_permission.description,
                "created_at": new_permission.created_at.isoformat() if new_permission.created_at else None,
                "updated_at": new_permission.updated_at.isoformat() if new_permission.updated_at else None
            }
            
        except IntegrityError:
            self.session.rollback()
            raise ValueError("权限名称已存在")
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"创建权限失败: {str(e)}")
            raise ValueError(f"创建权限失败: {str(e)}")

    def update_permission(self, permission_id: str, name: str = None, description: str = None, updated_by: str = None):
        """更新权限"""
        try:
            permission = self.session.query(Permission).filter(
                Permission.id == uuid.UUID(permission_id)
            ).first()
            
            if not permission:
                raise ValueError("权限不存在")
            
            # 检查新名称是否与其他权限冲突
            if name and name != permission.name:
                existing_permission = self.session.query(Permission).filter(
                    Permission.name == name,
                    Permission.id != uuid.UUID(permission_id)
                ).first()
                
                if existing_permission:
                    raise ValueError("权限名称已存在")
                
                permission.name = name
            
            if description is not None:
                permission.description = description
            
            self.session.commit()
            
            return {
                "id": str(permission.id),
                "name": permission.name,
                "description": permission.description,
                "created_at": permission.created_at.isoformat() if permission.created_at else None,
                "updated_at": permission.updated_at.isoformat() if permission.updated_at else None
            }
            
        except IntegrityError:
            self.session.rollback()
            raise ValueError("权限名称已存在")
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"更新权限失败: {str(e)}")
            raise ValueError(f"更新权限失败: {str(e)}")

    def delete_permission(self, permission_id: str):
        """删除权限"""
        try:
            permission = self.session.query(Permission).filter(
                Permission.id == uuid.UUID(permission_id)
            ).first()
            
            if not permission:
                raise ValueError("权限不存在")
            
            # 检查权限是否被角色使用
            # 这里可以添加检查逻辑，如果权限被使用则不允许删除
            
            self.session.delete(permission)
            self.session.commit()
            
            return True
            
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"删除权限失败: {str(e)}")
            raise ValueError(f"删除权限失败: {str(e)}")

    def get_all_permissions(self):
        """获取所有权限（不分页）"""
        try:
            permissions = self.session.query(Permission).order_by(Permission.name).all()
            
            return [
                {
                    "id": str(permission.id),
                    "name": permission.name,
                    "description": permission.description
                }
                for permission in permissions
            ]
            
        except Exception as e:
            self.logger.error(f"获取所有权限失败: {str(e)}")
            raise ValueError(f"获取所有权限失败: {str(e)}")


def get_permission_service() -> PermissionService:
    """获取权限服务实例"""
    return PermissionService() 