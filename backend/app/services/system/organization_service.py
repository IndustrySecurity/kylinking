# -*- coding: utf-8 -*-
"""
组织管理服务
"""

from app.services.base_service import BaseService
from app.models.organization import Organization
from app.models.user import User
from app.extensions import db
from sqlalchemy import func, and_, or_
from sqlalchemy.exc import IntegrityError
import uuid
from datetime import datetime
import logging
from typing import Optional, List, Dict, Any

class OrganizationService(BaseService):
    """组织管理服务"""
    
    def __init__(self, tenant_id=None, schema_name=None):
        super().__init__(tenant_id, schema_name)
        self.logger = logging.getLogger(__name__)
    
    def get_organizations(self, tenant_id: str, page=1, per_page=20, search=None):
        """获取组织列表"""
        try:
            query = self.session.query(Organization).filter(Organization.tenant_id == uuid.UUID(tenant_id))
            
            # 搜索条件
            if search:
                search_pattern = f"%{search}%"
                query = query.filter(or_(
                    Organization.name.ilike(search_pattern),
                    Organization.code.ilike(search_pattern),
                    Organization.description.ilike(search_pattern)
                ))
            
            # 排序
            query = query.order_by(Organization.level, Organization.name)
            
            # 分页
            total = query.count()
            organizations = query.offset((page - 1) * per_page).limit(per_page).all()
            
            # 构建返回数据
            org_list = []
            for org in organizations:
                org_data = {
                    'id': str(org.id),
                    'name': org.name,
                    'code': org.code,
                    'description': org.description,
                    'parent_id': str(org.parent_id) if org.parent_id else None,
                    'level': org.level,
                    'created_at': org.created_at.isoformat() if org.created_at else None,
                    'updated_at': org.updated_at.isoformat() if org.updated_at else None
                }
                org_list.append(org_data)
            
            return {
                'organizations': org_list,
                'total': total,
                'page': page,
                'per_page': per_page,
                'pages': (total + per_page - 1) // per_page
            }
            
        except Exception as e:
            self.logger.error(f"获取组织列表失败: {e}")
            raise
    
    def get_organization_tree(self, tenant_id: str):
        """获取组织树结构"""
        try:
            # 获取所有组织
            organizations = self.session.query(Organization).filter(
                Organization.tenant_id == uuid.UUID(tenant_id)
            ).order_by(Organization.level, Organization.name).all()
            
            # 构建树结构
            org_dict = {str(org.id): {
                'id': str(org.id),
                'name': org.name,
                'code': org.code,
                'description': org.description,
                'parent_id': str(org.parent_id) if org.parent_id else None,
                'level': org.level,
                'children': []
            } for org in organizations}
            
            # 构建父子关系
            root_nodes = []
            for org_id, org_data in org_dict.items():
                if org_data['parent_id'] is None:
                    root_nodes.append(org_data)
                else:
                    parent = org_dict.get(org_data['parent_id'])
                    if parent:
                        parent['children'].append(org_data)
            
            return root_nodes
            
        except Exception as e:
            self.logger.error(f"获取组织树失败: {e}")
            raise
    
    def create_organization(self, tenant_id: str, data: Dict[str, Any], created_by: str):
        """创建组织"""
        try:
            # 检查代码唯一性
            existing = self.session.query(Organization).filter(
                Organization.tenant_id == uuid.UUID(tenant_id),
                Organization.code == data['code']
            ).first()
            
            if existing:
                raise ValueError(f"组织代码 '{data['code']}' 已存在")
            
            # 计算层级
            level = 1
            if data.get('parent_id'):
                parent = self.session.query(Organization).filter(
                    Organization.id == uuid.UUID(data['parent_id']),
                    Organization.tenant_id == uuid.UUID(tenant_id)
                ).first()
                
                if not parent:
                    raise ValueError("父组织不存在")
                
                level = parent.level + 1
            
            # 创建组织
            organization = Organization(
                name=data['name'],
                code=data['code'],
                tenant_id=uuid.UUID(tenant_id),
                parent_id=uuid.UUID(data['parent_id']) if data.get('parent_id') else None,
                description=data.get('description'),
                level=level
            )
            
            self.session.add(organization)
            self.session.commit()
            
            return {
                'id': str(organization.id),
                'name': organization.name,
                'code': organization.code,
                'description': organization.description,
                'parent_id': str(organization.parent_id) if organization.parent_id else None,
                'level': organization.level,
                'created_at': organization.created_at.isoformat() if organization.created_at else None
            }
            
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"创建组织失败: {e}")
            raise
    
    def update_organization(self, tenant_id: str, org_id: str, data: Dict[str, Any], updated_by: str):
        """更新组织"""
        try:
            organization = self.session.query(Organization).filter(
                Organization.id == uuid.UUID(org_id),
                Organization.tenant_id == uuid.UUID(tenant_id)
            ).first()
            
            if not organization:
                raise ValueError("组织不存在")
            
            # 检查代码唯一性（排除自己）
            if data.get('code') and data['code'] != organization.code:
                existing = self.session.query(Organization).filter(
                    Organization.tenant_id == uuid.UUID(tenant_id),
                    Organization.code == data['code'],
                    Organization.id != uuid.UUID(org_id)
                ).first()
                
                if existing:
                    raise ValueError(f"组织代码 '{data['code']}' 已存在")
            
            # 更新字段
            if data.get('name'):
                organization.name = data['name']
            if data.get('code'):
                organization.code = data['code']
            if 'description' in data:
                organization.description = data['description']
            
            # 更新父组织
            if 'parent_id' in data:
                new_parent_id = uuid.UUID(data['parent_id']) if data['parent_id'] else None
                
                # 检查是否形成循环引用
                if new_parent_id and new_parent_id == organization.id:
                    raise ValueError("组织不能将自己设为父组织")
                
                # 检查新父组织是否存在
                if new_parent_id:
                    parent = self.session.query(Organization).filter(
                        Organization.id == new_parent_id,
                        Organization.tenant_id == uuid.UUID(tenant_id)
                    ).first()
                    
                    if not parent:
                        raise ValueError("父组织不存在")
                    
                    # 检查是否将组织设为自己的子组织的父组织
                    if self._is_descendant(organization.id, new_parent_id):
                        raise ValueError("不能将子组织设为父组织")
                
                organization.parent_id = new_parent_id
                
                # 重新计算层级
                organization.level = self._calculate_level(new_parent_id, tenant_id)
            
            organization.updated_at = datetime.now()
            self.session.commit()
            
            return {
                'id': str(organization.id),
                'name': organization.name,
                'code': organization.code,
                'description': organization.description,
                'parent_id': str(organization.parent_id) if organization.parent_id else None,
                'level': organization.level,
                'updated_at': organization.updated_at.isoformat() if organization.updated_at else None
            }
            
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"更新组织失败: {e}")
            raise
    
    def delete_organization(self, tenant_id: str, org_id: str):
        """删除组织"""
        try:
            organization = self.session.query(Organization).filter(
                Organization.id == uuid.UUID(org_id),
                Organization.tenant_id == uuid.UUID(tenant_id)
            ).first()
            
            if not organization:
                raise ValueError("组织不存在")
            
            # 检查是否有子组织
            children = self.session.query(Organization).filter(
                Organization.parent_id == uuid.UUID(org_id)
            ).count()
            
            if children > 0:
                raise ValueError("该组织下有子组织，无法删除")
            
            # 检查是否有关联的用户
            user_count = self.session.query(User).filter(
                User.tenant_id == uuid.UUID(tenant_id)
            ).join(organization.users).count()
            
            if user_count > 0:
                raise ValueError("该组织下有关联的用户，无法删除")
            
            self.session.delete(organization)
            self.session.commit()
            
            return True
            
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"删除组织失败: {e}")
            raise
    
    def assign_users_to_organization(self, tenant_id: str, org_id: str, user_ids: List[str]):
        """分配用户到组织"""
        try:
            organization = self.session.query(Organization).filter(
                Organization.id == uuid.UUID(org_id),
                Organization.tenant_id == uuid.UUID(tenant_id)
            ).first()
            
            if not organization:
                raise ValueError("组织不存在")
            
            # 获取用户
            users = self.session.query(User).filter(
                User.id.in_([uuid.UUID(uid) for uid in user_ids]),
                User.tenant_id == uuid.UUID(tenant_id)
            ).all()
            
            if len(users) != len(user_ids):
                raise ValueError("部分用户不存在或不属于该租户")
            
            # 分配用户到组织
            organization.users.extend(users)
            self.session.commit()
            
            return True
            
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"分配用户到组织失败: {e}")
            raise
    
    def _is_descendant(self, parent_id: uuid.UUID, child_id: uuid.UUID) -> bool:
        """检查是否为后代关系"""
        child = self.session.query(Organization).filter(Organization.id == child_id).first()
        if not child:
            return False
        
        if child.parent_id == parent_id:
            return True
        
        if child.parent_id:
            return self._is_descendant(parent_id, child.parent_id)
        
        return False
    
    def _calculate_level(self, parent_id: Optional[uuid.UUID], tenant_id: str) -> int:
        """计算组织层级"""
        if parent_id is None:
            return 1
        
        parent = self.session.query(Organization).filter(
            Organization.id == parent_id,
            Organization.tenant_id == uuid.UUID(tenant_id)
        ).first()
        
        if parent:
            return parent.level + 1
        
        return 1


def get_organization_service(tenant_id: str = None, schema_name: str = None) -> OrganizationService:
    """获取组织服务实例"""
    return OrganizationService(tenant_id=tenant_id, schema_name=schema_name) 