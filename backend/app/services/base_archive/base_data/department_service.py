# -*- coding: utf-8 -*-
"""
Department 服务
"""

from app.services.base_service import TenantAwareService
from app.models.basic_data import Department
from app.extensions import db
from sqlalchemy import func, text, and_, or_
from sqlalchemy.exc import IntegrityError
import uuid
from datetime import datetime
import re

class DepartmentService(TenantAwareService):
    """部门管理服务"""
    
    def _set_schema(self):
        """设置当前租户的schema搜索路径"""
        from flask import g, current_app
        from sqlalchemy import text
        schema_name = getattr(g, 'schema_name', current_app.config.get('DEFAULT_SCHEMA', 'public'))
        if schema_name != 'public':
            current_app.logger.info(f"Setting search_path to {schema_name} in DepartmentService")
            self.get_session().execute(text(f'SET search_path TO {schema_name}, public'))
    
    def get_departments(self, page=1, per_page=20, search=None):
        """获取部门列表"""
        # 设置schema
        self._set_schema()
        
        query = self.get_session().query(Department)
        
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
        
        return {
            'departments': [dept.to_dict(include_user_info=True) for dept in departments],
            'total': total,
            'current_page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }
    
    def get_department(self, dept_id):
        """获取部门详情"""
        # 设置schema
        self._set_schema()
        
        department = self.get_session().query(Department).get(uuid.UUID(dept_id))
        if not department:
            raise ValueError("部门不存在")
        return department.to_dict(include_user_info=True)
    
    def create_department(self, data, created_by):
        """创建部门"""
        # 设置schema
        self._set_schema()
        
        try:
            # 生成部门编号
            if not data.get('dept_code'):
                data['dept_code'] = Department.generate_dept_code()
            
            # 验证上级部门
            parent_id = None
            if data.get('parent_id'):
                parent_id = uuid.UUID(data['parent_id'])
                parent_dept = self.get_session().query(Department).get(parent_id)
                if not parent_dept:
                    raise ValueError("上级部门不存在")
                if not parent_dept.is_enabled:
                    raise ValueError("上级部门未启用")
            
            # 创建部门对象
            department = Department(
                dept_code=data['dept_code'],
                dept_name=data['dept_name'],
                parent_id=parent_id,
                is_blown_film=data.get('is_blown_film', False),
                description=data.get('description', ''),
                sort_order=data.get('sort_order', 0),
                is_enabled=data.get('is_enabled', True),
                created_by=uuid.UUID(created_by)
            )
            
            self.get_session().add(department)
            self.get_session().commit()
            
            return department.to_dict(include_user_info=True)
            
        except IntegrityError as e:
            self.get_session().rollback()
            if 'dept_code' in str(e):
                raise ValueError("部门编号已存在")
            raise ValueError("数据完整性错误")
        except Exception as e:
            self.get_session().rollback()
            raise ValueError(f"创建部门失败: {str(e)}")
    
    def update_department(self, dept_id, data, updated_by):
        """更新部门"""
        # 设置schema
        self._set_schema()
        
        try:
            department = self.get_session().query(Department).get(uuid.UUID(dept_id))
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
                    
                    parent_dept = self.get_session().query(Department).get(parent_id)
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
            
            self.get_session().commit()
            
            return department.to_dict(include_user_info=True)
            
        except IntegrityError as e:
            self.get_session().rollback()
            if 'dept_code' in str(e):
                raise ValueError("部门编号已存在")
            raise ValueError("数据完整性错误")
        except Exception as e:
            self.get_session().rollback()
            raise ValueError(f"更新部门失败: {str(e)}")
    
    def delete_department(self, dept_id):
        """删除部门"""
        # 设置schema
        self._set_schema()
        
        try:
            department = self.get_session().query(Department).get(uuid.UUID(dept_id))
            if not department:
                raise ValueError("部门不存在")
            
            # 检查是否有子部门
            children_count = self.get_session().query(Department).filter(Department.parent_id == department.id).count()
            if children_count > 0:
                raise ValueError("存在子部门，无法删除")
            
            self.get_session().delete(department)
            self.get_session().commit()
            
            return True
            
        except Exception as e:
            self.get_session().rollback()
            raise ValueError(f"删除部门失败: {str(e)}")
    
    def batch_update_departments(self, updates, updated_by):
        """批量更新部门"""
        # 设置schema
        self._set_schema()
        
        try:
            updated_departments = []
            
            for update_data in updates:
                dept_id = update_data.get('id')
                if not dept_id:
                    continue
                
                department = self.get_session().query(Department).get(uuid.UUID(dept_id))
                if not department:
                    continue
                
                # 更新字段
                update_fields = ['dept_name', 'is_blown_film', 'description', 'sort_order', 'is_enabled']
                for field in update_fields:
                    if field in update_data:
                        setattr(department, field, update_data[field])
                
                department.updated_by = uuid.UUID(updated_by)
                updated_departments.append(department)
            
            self.get_session().commit()
            
            return [dept.to_dict(include_user_info=True) for dept in updated_departments]
            
        except Exception as e:
            self.get_session().rollback()
            raise ValueError(f"批量更新部门失败: {str(e)}")
    
    def get_department_options(self):
        """获取部门选项数据"""
        # 设置schema
        self._set_schema()
        
        try:
            departments = Department.get_enabled_list()
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
    
    def get_department_tree(self, ):
        """获取部门树形结构"""
        # 设置schema
        self._set_schema()
        
        try:
            return Department.get_department_tree()
        except Exception as e:
            raise ValueError(f"获取部门树形结构失败: {str(e)}")


