# -*- coding: utf-8 -*-
"""
Department 服务
"""

from app.services.base_service import TenantAwareService
from app.models.basic_data import Department
from app.models.user import User
from app.extensions import db
from sqlalchemy import func, text, and_, or_
from sqlalchemy.exc import IntegrityError
import uuid
from datetime import datetime
import re

class DepartmentService(TenantAwareService):
    """部门管理服务"""
    
    def get_departments(self, page=1, per_page=20, search=None):
        """获取部门列表"""
        query = self.session.query(Department)
        
        # 搜索条件
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(or_(
                Department.dept_code.ilike(search_pattern),
                Department.dept_name.ilike(search_pattern),
                Department.description.ilike(search_pattern)
            ))
        
        # 只查询启用的记录
        query = query.filter(Department.is_enabled == True)
        
        # 排序
        query = query.order_by(Department.sort_order, Department.dept_name)
        
        # 分页
        total = query.count()
        departments = query.offset((page - 1) * per_page).limit(per_page).all()
        
        # 批量获取用户信息，避免N+1查询
        user_ids = set()
        for dept in departments:
            if dept.created_by:
                user_ids.add(dept.created_by)
            if dept.updated_by:
                user_ids.add(dept.updated_by)
        
        # 一次性查询所有需要的用户信息
        users = {}
        if user_ids:
            user_list = self.session.query(User).filter(User.id.in_(user_ids)).all()
            users = {str(user.id): user for user in user_list}
        
        # 构建返回数据，手动添加用户信息
        department_list = []
        for dept in departments:
            dept_dict = dept.to_dict(include_user_info=False)
            
            # 添加用户信息
            if dept.created_by and str(dept.created_by) in users:
                dept_dict['created_by_name'] = users[str(dept.created_by)].get_full_name()
            else:
                dept_dict['created_by_name'] = '未知用户'
                
            if dept.updated_by and str(dept.updated_by) in users:
                dept_dict['updated_by_name'] = users[str(dept.updated_by)].get_full_name()
            else:
                dept_dict['updated_by_name'] = '未知用户'
            
            department_list.append(dept_dict)
        
        return {
            'departments': department_list,
            'total': total,
            'current_page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }
    
    def get_department(self, dept_id):
        """获取部门详情"""
        department = self.session.query(Department).get(uuid.UUID(dept_id))
        if not department:
            raise ValueError("部门不存在")
        
        # 构建返回数据
        dept_dict = department.to_dict(include_user_info=False)
        
        # 添加用户信息
        if department.created_by:
            creator = self.session.query(User).get(department.created_by)
            dept_dict['created_by_name'] = creator.get_full_name() if creator else '未知用户'
        if department.updated_by:
            updater = self.session.query(User).get(department.updated_by)
            dept_dict['updated_by_name'] = updater.get_full_name() if updater else '未知用户'
        
        return dept_dict
    
    def create_department(self, data, created_by):
        """创建部门"""
        try:
            # 生成部门编号
            if not data.get('dept_code'):
                data['dept_code'] = Department.generate_dept_code()
            
            # 验证上级部门
            parent_id = None
            if data.get('parent_id'):
                parent_id = uuid.UUID(data['parent_id'])
                parent_dept = self.session.query(Department).get(parent_id)
                if not parent_dept:
                    raise ValueError("上级部门不存在")
                if not parent_dept.is_enabled:
                    raise ValueError("上级部门未启用")
            
            # 创建部门对象
            department = self.create_with_tenant(Department,
                dept_code=data['dept_code'],
                dept_name=data['dept_name'],
                parent_id=parent_id,
                is_blown_film=data.get('is_blown_film', False),
                description=data.get('description', ''),
                sort_order=data.get('sort_order', 0),
                is_enabled=data.get('is_enabled', True),
                created_by=uuid.UUID(created_by)
            )
            
            self.commit()
            
            return department.to_dict(include_user_info=True)
            
        except IntegrityError as e:
            self.rollback()
            if 'dept_code' in str(e):
                raise ValueError("部门编号已存在")
            raise ValueError("数据完整性错误")
        except Exception as e:
            self.rollback()
            raise ValueError(f"创建部门失败: {str(e)}")
    
    def update_department(self, dept_id, data, updated_by):
        """更新部门"""
        try:
            department = self.session.query(Department).get(uuid.UUID(dept_id))
            if not department:
                raise ValueError("部门不存在")
            
            # 验证上级部门
            if 'parent_id' in data:
                parent_id = None
                if data['parent_id']:
                    parent_id = uuid.UUID(data['parent_id'])
                    # 防止循环引用
                    if parent_id == department.id:
                        raise ValueError("不能将自己设置为上级部门")
                    
                    parent_dept = self.session.query(Department).get(parent_id)
                    if not parent_dept:
                        raise ValueError("上级部门不存在")
                    if not parent_dept.is_enabled:
                        raise ValueError("上级部门未启用")
                    
                    # 检查是否会形成循环引用
                    current_parent = parent_dept
                    while current_parent:
                        if current_parent.parent_id == department.id:
                            raise ValueError("设置此上级部门会形成循环引用")
                        current_parent = current_parent.parent
                
                data['parent_id'] = parent_id
            
            # 更新字段
            for key, value in data.items():
                if hasattr(department, key):
                    setattr(department, key, value)
            
            department.updated_by = uuid.UUID(updated_by)
            
            self.commit()
            
            return department.to_dict(include_user_info=True)
            
        except IntegrityError as e:
            self.rollback()
            if 'dept_code' in str(e):
                raise ValueError("部门编号已存在")
            raise ValueError("数据完整性错误")
        except Exception as e:
            self.rollback()
            raise ValueError(f"更新部门失败: {str(e)}")
    
    def delete_department(self, dept_id):
        """删除部门"""
        try:
            department = self.session.query(Department).get(uuid.UUID(dept_id))
            if not department:
                raise ValueError("部门不存在")
            
            # 检查是否有子部门
            children_count = self.session.query(Department).filter(Department.parent_id == department.id).count()
            if children_count > 0:
                raise ValueError("存在子部门，无法删除")
            
            self.session.delete(department)
            self.commit()
            
            return True
            
        except Exception as e:
            self.rollback()
            raise ValueError(f"删除部门失败: {str(e)}")
    
    def batch_update_departments(self, updates, updated_by):
        """批量更新部门"""
        try:
            updated_departments = []
            
            for update_data in updates:
                dept_id = update_data.get('id')
                if not dept_id:
                    continue
                
                department = self.session.query(Department).get(uuid.UUID(dept_id))
                if not department:
                    continue
                
                # 更新字段
                update_fields = ['dept_name', 'is_blown_film', 'description', 'sort_order', 'is_enabled']
                for field in update_fields:
                    if field in update_data:
                        setattr(department, field, update_data[field])
                
                department.updated_by = uuid.UUID(updated_by)
                updated_departments.append(department)
            
            self.commit()
            
            return [dept.to_dict(include_user_info=True) for dept in updated_departments]
            
        except Exception as e:
            self.rollback()
            raise ValueError(f"批量更新部门失败: {str(e)}")
    
    def get_department_options(self):
        """获取部门选项数据"""
        try:
            departments = self.session.query(Department).filter(
                Department.is_enabled == True
            ).order_by(Department.sort_order, Department.dept_name).all()
            
            return [
                {
                    'value': str(dept.id),
                    'label': dept.dept_name,
                    'code': dept.dept_code
                }
                for dept in departments
            ]
        except Exception as e:
            raise ValueError(f"获取部门选项失败: {str(e)}")
    
    def get_department_tree(self):
        """获取部门树形结构"""
        try:
            # 获取所有启用的部门
            departments = self.session.query(Department).filter(
                Department.is_enabled == True
            ).order_by(Department.sort_order, Department.dept_name).all()
            
            # 构建树形结构
            department_dict = {str(dept.id): dept for dept in departments}
            tree = []
            
            for dept in departments:
                dept_data = dept.to_dict()
                dept_data['children'] = []
                
                if dept.parent_id is None:
                    # 根部门
                    tree.append(dept_data)
                else:
                    # 子部门
                    parent_id = str(dept.parent_id)
                    if parent_id in department_dict:
                        parent_data = next((d for d in tree if d['id'] == parent_id), None)
                        if parent_data:
                            parent_data['children'].append(dept_data)
                        else:
                            # 如果父级不在根级别，需要递归查找
                            def find_and_add_child(nodes, parent_id, child_data):
                                for node in nodes:
                                    if node['id'] == parent_id:
                                        node['children'].append(child_data)
                                        return True
                                    elif node['children'] and find_and_add_child(node['children'], parent_id, child_data):
                                        return True
                                return False
                            
                            find_and_add_child(tree, parent_id, dept_data)
            
            return tree
        except Exception as e:
            raise ValueError(f"获取部门树形结构失败: {str(e)}")


