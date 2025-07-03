# -*- coding: utf-8 -*-
# type: ignore
# pyright: reportGeneralTypeIssues=false
# pyright: reportAttributeAccessIssue=false
# pyright: reportOptionalMemberAccess=false
"""
Position 服务
"""

from app.services.base_service import TenantAwareService
from app.models.basic_data import Position, Department
from app.models.user import User
from app.extensions import db
from sqlalchemy import func, text, and_, or_
from sqlalchemy.exc import IntegrityError
import uuid
from datetime import datetime
import re

class PositionService(TenantAwareService):
    """职位管理服务"""
    
    def get_positions(self, page=1, per_page=20, search=None, department_id=None):
        """获取职位列表"""
        try:
            # 构建查询
            query = self.session.query(Position)
            
            # 搜索条件
            if search:
                query = query.filter(Position.position_name.like(f'%{search}%'))
            
            # 部门筛选
            if department_id:
                query = query.filter(Position.department_id == uuid.UUID(department_id))
            
            # 排序
            query = query.order_by(Position.sort_order, Position.position_name)
            
            # 分页
            total = query.count()
            positions = query.offset((page - 1) * per_page).limit(per_page).all()
            
            # 添加用户信息
            for position in positions:
                if position.created_by:
                    creator = self.session.query(User).get(position.created_by)
                    position.created_by_name = creator.get_full_name() if creator else '未知用户'
                if position.updated_by:
                    updater = self.session.query(User).get(position.updated_by)
                    position.updated_by_name = updater.get_full_name() if updater else '未知用户'
            
            return {
                'positions': [pos.to_dict(include_user_info=True) for pos in positions],
                'total': total,
                'current_page': page,
                'per_page': per_page,
                'pages': (total + per_page - 1) // per_page
            }
            
        except Exception as e:
            raise ValueError(f"获取职位列表失败: {str(e)}")
    
    def get_position(self, position_id):
        """获取职位详情"""
        try:
            position = self.session.query(Position).get(uuid.UUID(position_id))
            if not position:
                raise ValueError("职位不存在")
            
            # 添加用户信息
            if position.created_by:
                creator = self.session.query(User).get(position.created_by)
                position.created_by_name = creator.get_full_name() if creator else '未知用户'
            if position.updated_by:
                updater = self.session.query(User).get(position.updated_by)
                position.updated_by_name = updater.get_full_name() if updater else '未知用户'
            
            return position.to_dict(include_user_info=True)
            
        except Exception as e:
            raise ValueError(f"获取职位详情失败: {str(e)}")
    
    def create_position(self, data, created_by):
        """创建职位"""
        try:
            # 验证部门
            department = self.session.query(Department).get(uuid.UUID(data['department_id']))
            if not department:
                raise ValueError("部门不存在")
            if not department.is_enabled:
                raise ValueError("部门未启用")
            
            # 验证上级职位
            parent_position_id = None
            if data.get('parent_position_id'):
                parent_position_id = uuid.UUID(data['parent_position_id'])
                parent_position = self.session.query(Position).get(parent_position_id)
                if not parent_position:
                    raise ValueError("上级职位不存在")
                if not parent_position.is_enabled:
                    raise ValueError("上级职位未启用")
            
            # 创建职位对象
            position = self.create_with_tenant(Position,
                position_name=data['position_name'],
                department_id=uuid.UUID(data['department_id']),
                parent_position_id=parent_position_id,
                hourly_wage=data.get('hourly_wage'),
                standard_pass_rate=data.get('standard_pass_rate'),
                is_supervisor=data.get('is_supervisor', False),
                is_machine_operator=data.get('is_machine_operator', False),
                description=data.get('description', ''),
                sort_order=data.get('sort_order', 0),
                is_enabled=data.get('is_enabled', True),
                created_by=uuid.UUID(created_by)
            )
            
            self.commit()
            
            # 添加用户信息
            creator = self.session.query(User).get(position.created_by)
            position.created_by_name = creator.get_full_name() if creator else '未知用户'
            
            return position.to_dict(include_user_info=True)
            
        except IntegrityError as e:
            self.rollback()
            raise ValueError("数据完整性错误")
        except Exception as e:
            self.rollback()
            raise ValueError(f"创建职位失败: {str(e)}")
    
    def update_position(self, position_id, data, updated_by):
        """更新职位"""
        try:
            position = self.session.query(Position).get(uuid.UUID(position_id))
            if not position:
                raise ValueError("职位不存在")
            
            # 验证部门
            if 'department_id' in data:
                department = self.session.query(Department).get(uuid.UUID(data['department_id']))
                if not department:
                    raise ValueError("部门不存在")
                if not department.is_enabled:
                    raise ValueError("部门未启用")
            
            # 验证上级职位
            if 'parent_position_id' in data:
                parent_position_id = None
                if data['parent_position_id']:
                    parent_position_id = uuid.UUID(data['parent_position_id'])
                    # 防止循环引用
                    if parent_position_id == position.id:
                        raise ValueError("不能将自己设置为上级职位")
                    
                    parent_position = self.session.query(Position).get(parent_position_id)
                    if not parent_position:
                        raise ValueError("上级职位不存在")
                    if not parent_position.is_enabled:
                        raise ValueError("上级职位未启用")
                    
                    # 检查是否会形成循环引用
                    current_parent = parent_position
                    while current_parent:
                        if current_parent.parent_position_id == position.id:
                            raise ValueError("设置此上级职位会形成循环引用")
                        current_parent = current_parent.parent_position
                
                data['parent_position_id'] = parent_position_id
            
            # 更新字段
            for key, value in data.items():
                if hasattr(position, key):
                    setattr(position, key, value)
            
            position.updated_by = uuid.UUID(updated_by)
            
            self.commit()
            
            # 添加用户信息
            if position.updated_by:
                updater = self.session.query(User).get(position.updated_by)
                position.updated_by_name = updater.get_full_name() if updater else '未知用户'
            
            return position.to_dict(include_user_info=True)
            
        except IntegrityError as e:
            self.rollback()
            raise ValueError("数据完整性错误")
        except Exception as e:
            self.rollback()
            raise ValueError(f"更新职位失败: {str(e)}")
    
    def delete_position(self, position_id):
        """删除职位"""
        try:
            position = self.session.query(Position).get(uuid.UUID(position_id))
            if not position:
                raise ValueError("职位不存在")
            
            # 检查是否有下级职位
            children_count = self.session.query(Position).filter(Position.parent_position_id == position.id).count()
            if children_count > 0:
                raise ValueError("存在下级职位，无法删除")
            
            self.session.delete(position)
            self.commit()
            
            return True
            
        except Exception as e:
            self.rollback()
            raise ValueError(f"删除职位失败: {str(e)}")
    
    def get_position_options(self, department_id=None):
        """获取职位选项数据"""
        try:
            query = self.session.query(Position).filter(Position.is_enabled == True)
            
            # 按部门筛选
            if department_id:
                query = query.filter(Position.department_id == uuid.UUID(department_id))
            
            positions = query.order_by(Position.sort_order, Position.position_name).all()
            
            return [
                {
                    'value': str(pos.id),
                    'label': pos.position_name,
                    'department_id': str(pos.department_id),
                    'department_name': pos.department.dept_name if pos.department else None
                }
                for pos in positions
            ]
        except Exception as e:
            raise ValueError(f"获取职位选项失败: {str(e)}")
    
    def get_department_options(self):
        """获取部门选项数据"""
        try:
            from app.models.basic_data import Department
            departments = self.session.query(Department).filter(
                Department.is_enabled == True
            ).order_by(Department.sort_order, Department.dept_name).all()
            
            return [
                {
                    'value': str(dept.id),
                    'label': dept.dept_name,
                    'description': dept.description
                }
                for dept in departments
            ]
        except Exception as e:
            raise ValueError(f"获取部门选项失败: {str(e)}")

    def get_form_options(self):
        """获取职位表单选项数据"""
        try:
            from app.models.basic_data import Department
            
            # 获取部门选项
            departments = self.session.query(Department).filter(
                Department.is_enabled == True
            ).order_by(Department.sort_order, Department.dept_name).all()
            
            # 获取所有职位作为上级职位选项
            positions = self.session.query(Position).filter(
                Position.is_enabled == True
            ).order_by(Position.sort_order, Position.position_name).all()
            
            return {
                'departments': [
                    {
                        'value': str(dept.id),
                        'label': dept.dept_name,
                        'description': dept.description
                    }
                    for dept in departments
                ],
                'parent_positions': [
                    {
                        'value': str(pos.id),
                        'label': pos.position_name,
                        'department_id': str(pos.department_id),
                        'department_name': pos.department.dept_name if pos.department else None
                    }
                    for pos in positions
                ]
            }
        except Exception as e:
            raise ValueError(f"获取表单选项失败: {str(e)}")

    def get_parent_position_options(self, department_id=None, current_position_id=None):
        """获取上级职位选项"""
        try:
            query = self.session.query(Position).filter(Position.is_enabled == True)
            
            # 按部门筛选
            if department_id:
                query = query.filter(Position.department_id == uuid.UUID(department_id))
            
            # 排除当前职位（编辑时使用）
            if current_position_id:
                query = query.filter(Position.id != uuid.UUID(current_position_id))
            
            positions = query.order_by(Position.sort_order, Position.position_name).all()
            
            return [
                {
                    'value': str(pos.id),
                    'label': pos.position_name,
                    'department_id': str(pos.department_id),
                    'department_name': pos.department.dept_name if pos.department else None
                }
                for pos in positions
            ]
        except Exception as e:
            raise ValueError(f"获取上级职位选项失败: {str(e)}")


