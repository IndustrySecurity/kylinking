# -*- coding: utf-8 -*-
"""
Employee 服务
"""

from app.services.base_service import TenantAwareService
from app.models.basic_data import Employee
from sqlalchemy import func, and_, or_
from sqlalchemy.exc import IntegrityError
import uuid
from datetime import datetime
import re
import logging

class EmployeeService(TenantAwareService):
    """员工管理服务"""
    
    def __init__(self, tenant_id=None, schema_name=None):
        super().__init__(tenant_id=tenant_id, schema_name=schema_name)
        self.logger = logging.getLogger(__name__)  # 添加logger初始化
    
    def get_employees(self, page=1, per_page=20, search=None, department_id=None, position_id=None, employment_status=None):
        """获取员工列表"""
        try:
            # 构建查询
            query = self.session.query(Employee)
            
            # 搜索条件
            if search:
                search_pattern = f"%{search}%"
                query = query.filter(or_(
                    Employee.employee_id.ilike(search_pattern),
                    Employee.employee_name.ilike(search_pattern),
                    Employee.mobile_phone.ilike(search_pattern),
                    Employee.id_number.ilike(search_pattern)
                ))
            
            # 部门筛选
            if department_id:
                query = query.filter(Employee.department_id == uuid.UUID(department_id))
            
            # 职位筛选
            if position_id:
                query = query.filter(Employee.position_id == uuid.UUID(position_id))
            
            # 在职状态筛选
            if employment_status:
                query = query.filter(Employee.employment_status == employment_status)
            
            # 排序
            query = query.order_by(Employee.sort_order, Employee.employee_name)
            
            # 分页
            total = query.count()
            employees = query.offset((page - 1) * per_page).limit(per_page).all()
            
            # 添加用户信息
            for employee in employees:
                if employee.created_by:
                    from app.models.user import User
                    creator = self.session.query(User).get(employee.created_by)
                    employee.created_by_name = creator.get_full_name() if creator else '未知用户'
                if employee.updated_by:
                    from app.models.user import User
                    updater = self.session.query(User).get(employee.updated_by)
                    employee.updated_by_name = updater.get_full_name() if updater else '未知用户'
            
            return {
                'employees': [emp.to_dict(include_user_info=True) for emp in employees],
                'total': total,
                'current_page': page,
                'per_page': per_page,
                'pages': (total + per_page - 1) // per_page
            }
            
        except Exception as e:
            raise ValueError(f"获取员工列表失败: {str(e)}")
    
    def get_employee(self, employee_id):
        """获取员工详情"""
        try:
            employee = self.session.query(Employee).get(uuid.UUID(employee_id))
            if not employee:
                raise ValueError("员工不存在")
            
            # 添加用户信息
            if employee.created_by:
                from app.models.user import User
                creator = self.session.query(User).get(employee.created_by)
                employee.created_by_name = creator.get_full_name() if creator else '未知用户'
            if employee.updated_by:
                from app.models.user import User
                updater = self.session.query(User).get(employee.updated_by)
                employee.updated_by_name = updater.get_full_name() if updater else '未知用户'
            
            return employee.to_dict(include_user_info=True)
            
        except Exception as e:
            raise ValueError(f"获取员工详情失败: {str(e)}")
    
    def get_employee_options(self):
        """获取员工选项列表"""
        try:
            employees = self.session.query(Employee).filter(Employee.is_enabled == True).order_by(Employee.sort_order, Employee.employee_name).all()
            return {
                'success': True,
                'data': [
                    {
                        'id': str(emp.id),
                        'employee_id': emp.employee_id,
                        'employee_name': emp.employee_name,
                        'department_name': emp.department.dept_name if emp.department else None,
                        'position_name': emp.position.position_name if emp.position else None
                    }
                    for emp in employees
                ]
            }
        except Exception as e:
            self.rollback()
            return {
                'success': False,
                'message': f'获取员工选项失败: {str(e)}'
            }

    def get_employment_status_options(self):
        """获取在职状态选项"""
        return [
            {'value': 'trial', 'label': '试用'},
            {'value': 'active', 'label': '在职'},
            {'value': 'leave', 'label': '离职'}
        ]

    def get_business_type_options(self):
        """获取业务类型选项"""
        return [
            {'value': 'salesperson', 'label': '业务员'},
            {'value': 'purchaser', 'label': '采购员'},
            {'value': 'comprehensive', 'label': '综合'},
            {'value': 'delivery_person', 'label': '送货员'}
        ]

    def get_gender_options(self):
        """获取性别选项"""
        return [
            {'value': 'male', 'label': '男'},
            {'value': 'female', 'label': '女'},
            {'value': 'confidential', 'label': '保密'}
        ]

    def get_evaluation_level_options(self):
        """获取评量流程级别选项"""
        return [
            {'value': 'finance', 'label': '财务'},
            {'value': 'technology', 'label': '工艺'},
            {'value': 'supply', 'label': '供应'},
            {'value': 'marketing', 'label': '营销'}
        ]

    def auto_fill_department_from_position(self, position_id):
        """根据职位自动填入部门"""
        try:
            if not position_id:
                return None
                
            from app.models.basic_data import Position
            position = self.session.query(Position).get(uuid.UUID(position_id))
            if position and position.department_id:
                return str(position.department_id)
            
            return None
        except Exception:
            return None

    def create_employee(self, data, created_by):
        """创建员工"""
        try:
            # 如果提供了职位，自动填入部门
            if data.get('position_id'):
                department_id = self.auto_fill_department_from_position(data['position_id'])
                if department_id:
                    data['department_id'] = department_id

            # 生成员工工号
            if not data.get('employee_id'):
                data['employee_id'] = Employee.generate_employee_id()

            # 验证数据
            if self.session.query(Employee).filter_by(employee_id=data['employee_id']).first():
                return {
                    'success': False,
                    'message': '员工工号已存在'
                }

            # 准备员工数据
            employee_data = {
                'employee_id': data['employee_id'],
                'employee_name': data['employee_name'],
                'position_id': uuid.UUID(data['position_id']) if data.get('position_id') else None,
                'department_id': uuid.UUID(data['department_id']) if data.get('department_id') else None,
                'employment_status': data.get('employment_status', 'trial'),
                'business_type': data.get('business_type'),
                'gender': data.get('gender'),
                'mobile_phone': data.get('mobile_phone'),
                'landline_phone': data.get('landline_phone'),
                'emergency_phone': data.get('emergency_phone'),
                'hire_date': datetime.strptime(data['hire_date'], '%Y-%m-%d').date() if data.get('hire_date') else None,
                'birth_date': datetime.strptime(data['birth_date'], '%Y-%m-%d').date() if data.get('birth_date') else None,
                'circulation_card_id': data.get('circulation_card_id'),
                'workshop_id': data.get('workshop_id'),
                'id_number': data.get('id_number'),
                'salary_1': data.get('salary_1', 0),
                'salary_2': data.get('salary_2', 0),
                'salary_3': data.get('salary_3', 0),
                'salary_4': data.get('salary_4', 0),
                'native_place': data.get('native_place'),
                'ethnicity': data.get('ethnicity'),
                'province': data.get('province'),
                'city': data.get('city'),
                'district': data.get('district'),
                'street': data.get('street'),
                'birth_address': data.get('birth_address'),
                'archive_location': data.get('archive_location'),
                'household_registration': data.get('household_registration'),
                'evaluation_level': data.get('evaluation_level'),
                'leave_date': datetime.strptime(data['leave_date'], '%Y-%m-%d').date() if data.get('leave_date') else None,
                'seniority_wage': data.get('seniority_wage'),
                'assessment_wage': data.get('assessment_wage'),
                'contract_start_date': datetime.strptime(data['contract_start_date'], '%Y-%m-%d').date() if data.get('contract_start_date') else None,
                'contract_end_date': datetime.strptime(data['contract_end_date'], '%Y-%m-%d').date() if data.get('contract_end_date') else None,
                'expiry_warning_date': datetime.strptime(data['expiry_warning_date'], '%Y-%m-%d').date() if data.get('expiry_warning_date') else None,
                'ufida_code': data.get('ufida_code'),
                'kingdee_push': data.get('kingdee_push', False),
                'remarks': data.get('remarks'),
                'sort_order': data.get('sort_order', 0),
                'is_enabled': data.get('is_enabled', True),
            }

            # 使用继承的create_with_tenant方法
            employee = self.create_with_tenant(Employee, **employee_data)
            self.commit()

            return {
                'success': True,
                'message': '员工创建成功',
                'data': employee.to_dict(include_user_info=True)
            }

        except Exception as e:
            self.rollback()
            return {
                'success': False,
                'message': f'创建员工失败: {str(e)}'
            }

    def update_employee(self, employee_id, data, updated_by):
        """更新员工"""
        try:
            employee = self.session.query(Employee).get(uuid.UUID(employee_id))
            if not employee:
                return {
                    'success': False,
                    'message': '员工不存在'
                }

            # 如果修改了职位，自动更新部门
            if 'position_id' in data and data['position_id'] != str(employee.position_id):
                department_id = self.auto_fill_department_from_position(data['position_id'])
                if department_id:
                    data['department_id'] = department_id

            # 更新字段
            for key, value in data.items():
                if hasattr(employee, key):
                    setattr(employee, key, value)
            
            employee.updated_by = uuid.UUID(updated_by)
            
            try:
                self.commit()
                return employee.to_dict(include_user_info=True)
            except Exception as e:
                self.rollback()
                raise ValueError(f'更新员工失败: {str(e)}')

        except Exception as e:
            self.rollback()
            raise ValueError(f"更新员工失败: {str(e)}")

    def delete_employee(self, employee_id):
        """删除员工"""
        try:
            employee = self.session.query(Employee).get(uuid.UUID(employee_id))
            if not employee:
                raise ValueError("员工不存在")
            
            self.session.delete(employee)
            self.commit()
            
            return True
            
        except Exception as e:
            self.rollback()
            raise ValueError(f"删除员工失败: {str(e)}")
    
    def batch_update_employees(self, updates, updated_by):
        """批量更新员工"""
        try:
            updated_employees = []
            
            for update_data in updates:
                emp_id = update_data.get('id')
                if not emp_id:
                    continue
                
                employee = self.session.query(Employee).get(uuid.UUID(emp_id))
                if not employee:
                    continue
                
                # 更新指定字段
                update_fields = ['employment_status', 'sort_order', 'is_enabled']
                for field in update_fields:
                    if field in update_data:
                        setattr(employee, field, update_data[field])
                
                employee.updated_by = uuid.UUID(updated_by)
                updated_employees.append(employee)
            
            self.commit()
            
            return [emp.to_dict(include_user_info=True) for emp in updated_employees]
            
        except Exception as e:
            self.rollback()
            raise ValueError(f"批量更新员工失败: {str(e)}")

    def get_form_options(self):
        """获取员工表单选项数据"""
        try:
            from app.models.basic_data import Department, Position
            
            # 获取部门
            departments = self.session.query(Department).filter(
                Department.is_enabled == True
            ).order_by(Department.dept_name).all()
            
            # 获取职位
            positions = self.session.query(Position).filter(
                Position.is_enabled == True
            ).order_by(Position.position_name).all()
            
            return {
                'departments': [
                    {'value': str(dept.id), 'label': dept.dept_name}
                    for dept in departments
                ],
                'positions': [
                    {'value': str(pos.id), 'label': pos.position_name}
                    for pos in positions
                ],
                'employment_status_options': self.get_employment_status_options(),
                'business_type_options': self.get_business_type_options(),
                'gender_options': self.get_gender_options(),
                'evaluation_level_options': self.get_evaluation_level_options()
            }
            
        except Exception as e:
            raise ValueError(f"获取表单选项失败: {str(e)}")


def get_employee_service(tenant_id: str = None, schema_name: str = None) -> EmployeeService:
    """获取员工服务实例"""
    return EmployeeService(tenant_id=tenant_id, schema_name=schema_name)


