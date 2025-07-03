# -*- coding: utf-8 -*-
"""
TeamGroup 服务
"""

from app.services.base_service import TenantAwareService
from app.models.basic_data import TeamGroup, TeamGroupMember, TeamGroupMachine, TeamGroupProcess, Employee, Machine, ProcessCategory
from sqlalchemy import func, and_, or_
from sqlalchemy.exc import IntegrityError
import uuid
from datetime import datetime
from typing import Optional
import re

class TeamGroupService(TenantAwareService):
    """班组管理服务"""
    
    def __init__(self, tenant_id: Optional[str] = None, schema_name: Optional[str] = None):
        """初始化TeamGroup服务"""
        super().__init__(tenant_id, schema_name)
    
    def get_team_groups(self, page=1, per_page=20, search=None, is_enabled=None):
        """获取班组列表"""
        try:
            query = self.session.query(TeamGroup)
            
            # 搜索条件
            if search:
                search_pattern = f"%{search}%"
                query = query.filter(or_(
                    TeamGroup.team_code.ilike(search_pattern),
                    TeamGroup.team_name.ilike(search_pattern),
                    TeamGroup.circulation_card_id.ilike(search_pattern)
                ))
            
            # 启用状态筛选
            if is_enabled is not None:
                query = query.filter(TeamGroup.is_enabled == is_enabled)
            
            # 排序
            query = query.order_by(TeamGroup.sort_order.asc(), TeamGroup.team_name.asc())
            
            # 分页
            total = query.count()
            team_groups = query.offset((page - 1) * per_page).limit(per_page).all()
            
            return {
                'team_groups': [team_group.to_dict() for team_group in team_groups],
                'total': total,
                'page': page,
                'per_page': per_page,
                'pages': (total + per_page - 1) // per_page
            }
            
        except Exception as e:
            self.rollback()
            raise e
    
    def get_team_group(self, team_group_id):
        """获取班组详情"""
        try:
            team_group = self.session.query(TeamGroup).get(uuid.UUID(team_group_id))
            if not team_group:
                raise ValueError("班组不存在")
            
            return team_group.to_dict(include_details=True)
            
        except Exception as e:
            raise e
    
    def create_team_group(self, data, created_by):
        """创建班组"""
        try:
            # 生成班组编号
            if not data.get('team_code'):
                data['team_code'] = TeamGroup.generate_team_code()
            
            # 准备班组数据
            team_group_data = {
                'team_code': data['team_code'],
                'team_name': data['team_name'],
                'circulation_card_id': data.get('circulation_card_id'),
                'day_shift_hours': data.get('day_shift_hours'),
                'night_shift_hours': data.get('night_shift_hours'),
                'rotating_shift_hours': data.get('rotating_shift_hours'),
                'description': data.get('description'),
                'sort_order': data.get('sort_order', 0),
                'is_enabled': data.get('is_enabled', True),
            }
            
            # 创建班组对象
            team_group = self.create_with_tenant(TeamGroup, **team_group_data)
            self.session.flush()  # 获取ID
            
            # 处理子表数据
            team_group_id = team_group.id
            
            # 添加班组人员
            if data.get('team_members'):
                for member_data in data['team_members']:
                    member_detail = {
                        'team_group_id': team_group_id,
                        'employee_id': uuid.UUID(member_data['employee_id']),
                        'piece_rate_percentage': member_data.get('piece_rate_percentage', 0),
                        'saving_bonus_percentage': member_data.get('saving_bonus_percentage', 0),
                        'remarks': member_data.get('remarks'),
                        'sort_order': member_data.get('sort_order', 0),
                    }
                    member = self.create_with_tenant(TeamGroupMember, **member_detail)
            
            # 添加班组机台
            if data.get('team_machines'):
                for machine_data in data['team_machines']:
                    machine_detail = {
                        'team_group_id': team_group_id,
                        'machine_id': uuid.UUID(machine_data['machine_id']),
                        'remarks': machine_data.get('remarks'),
                        'sort_order': machine_data.get('sort_order', 0),
                    }
                    machine = self.create_with_tenant(TeamGroupMachine, **machine_detail)
            
            # 添加班组工序分类
            if data.get('team_processes'):
                for process_data in data['team_processes']:
                    process_detail = {
                        'team_group_id': team_group_id,
                        'process_category_id': uuid.UUID(process_data['process_category_id']),
                        'sort_order': process_data.get('sort_order', 0),
                    }
                    process = self.create_with_tenant(TeamGroupProcess, **process_detail)
            
            self.commit()
            
            return team_group.to_dict(include_details=True)
            
        except IntegrityError as e:
            self.rollback()
            if 'team_code' in str(e):
                raise ValueError("班组编号已存在")
            elif 'uq_team_group_employee' in str(e):
                raise ValueError("该员工已经分配到此班组")
            elif 'uq_team_group_machine' in str(e):
                raise ValueError("该机台已经分配到此班组")
            elif 'uq_team_group_process' in str(e):
                raise ValueError("该工序分类已经分配到此班组")
            else:
                raise ValueError("数据完整性错误")
        except Exception as e:
            self.rollback()
            raise e
    
    def update_team_group(self, team_group_id, data, updated_by):
        """更新班组"""
        try:
            team_group = self.session.query(TeamGroup).get(uuid.UUID(team_group_id))
            if not team_group:
                raise ValueError("班组不存在")
            
            # 更新字段
            for key, value in data.items():
                if hasattr(team_group, key):
                    setattr(team_group, key, value)
            
            team_group.updated_by = uuid.UUID(updated_by)
            
            self.commit()
            return team_group.to_dict()
            
        except Exception as e:
            self.rollback()
            raise ValueError(f'更新班组失败: {str(e)}')
    
    def delete_team_group(self, team_group_id):
        """删除班组"""
        try:
            team_group = self.session.query(TeamGroup).get(uuid.UUID(team_group_id))
            if not team_group:
                raise ValueError("班组不存在")
            
            # 删除子表数据（CASCADE会自动处理）
            self.session.delete(team_group)
            self.commit()
            
            return {"message": "班组删除成功"}
            
        except Exception as e:
            self.rollback()
            raise e
    
    def get_team_group_options(self):
        """获取班组选项列表"""
        try:
            team_groups = self.session.query(TeamGroup).filter_by(is_enabled=True).all()
            return [
                {
                    'id': str(team_group.id),
                    'team_code': team_group.team_code,
                    'team_name': team_group.team_name,
                    'value': str(team_group.id),
                    'label': f"{team_group.team_code} - {team_group.team_name}"
                }
                for team_group in team_groups
            ]
            
        except Exception as e:
            raise e
    
    def get_employee_options(self):
        """获取员工选项列表"""
        try:
            employees = self.session.query(Employee).filter_by(is_enabled=True).all()
            return [
                {
                    'id': str(employee.id),
                    'employee_id': employee.employee_id,
                    'employee_name': employee.employee_name,
                    'position_name': employee.position.position_name if employee.position else None,
                    'value': str(employee.id),
                    'label': f"{employee.employee_id} - {employee.employee_name}"
                }
                for employee in employees
            ]
            
        except Exception as e:
            raise e
    
    def get_machine_options(self):
        """获取机台选项列表"""
        try:
            machines = self.session.query(Machine).filter_by(is_enabled=True).all()
            return [
                {
                    'id': str(machine.id),
                    'machine_code': machine.machine_code,
                    'machine_name': machine.machine_name,
                    'value': str(machine.id),
                    'label': f"{machine.machine_code} - {machine.machine_name}"
                }
                for machine in machines
            ]
            
        except Exception as e:
            raise e
    
    def get_process_category_options(self):
        """获取工序分类选项列表"""
        try:
            process_categories = self.session.query(ProcessCategory).filter_by(is_enabled=True).all()
            return [
                {
                    'id': str(process_category.id),
                    'process_name': process_category.process_name,
                    'value': str(process_category.id),
                    'label': process_category.process_name
                }
                for process_category in process_categories
            ]
            
        except Exception as e:
            raise e
    
    # 子表管理方法
    def add_team_member(self, team_group_id, member_data, created_by):
        """添加班组成员"""
        try:
            member_detail = {
                'team_group_id': uuid.UUID(team_group_id),
                'employee_id': uuid.UUID(member_data['employee_id']),
                'piece_rate_percentage': member_data.get('piece_rate_percentage', 0),
                'saving_bonus_percentage': member_data.get('saving_bonus_percentage', 0),
                'remarks': member_data.get('remarks'),
                'sort_order': member_data.get('sort_order', 0),
            }
            
            member = self.create_with_tenant(TeamGroupMember, **member_detail)
            self.commit()
            
            return member.to_dict()
            
        except IntegrityError as e:
            self.rollback()
            if 'uq_team_group_employee' in str(e):
                raise ValueError("该员工已经分配到此班组")
            else:
                raise ValueError("数据完整性错误")
        except Exception as e:
            self.rollback()
            raise e
    
    def update_team_member(self, member_id, member_data, updated_by):
        """更新班组成员"""
        try:
            member = self.session.query(TeamGroupMember).get(uuid.UUID(member_id))
            if not member:
                raise ValueError("班组成员不存在")
            
            member.piece_rate_percentage = member_data.get('piece_rate_percentage', member.piece_rate_percentage)
            member.saving_bonus_percentage = member_data.get('saving_bonus_percentage', member.saving_bonus_percentage)
            member.remarks = member_data.get('remarks', member.remarks)
            member.sort_order = member_data.get('sort_order', member.sort_order)
            member.updated_by = uuid.UUID(updated_by)
            
            self.commit()
            
            return member.to_dict()
            
        except Exception as e:
            self.rollback()
            raise e
    
    def delete_team_member(self, member_id):
        """删除班组成员"""
        try:
            member = self.session.query(TeamGroupMember).get(uuid.UUID(member_id))
            if not member:
                raise ValueError("班组成员不存在")
            
            self.session.delete(member)
            self.commit()
            
            return {"message": "班组成员删除成功"}
            
        except Exception as e:
            self.rollback()
            raise e
    
    def add_team_machine(self, team_group_id, machine_data, created_by):
        """添加班组机台"""
        try:
            machine_detail = {
                'team_group_id': uuid.UUID(team_group_id),
                'machine_id': uuid.UUID(machine_data['machine_id']),
                'remarks': machine_data.get('remarks'),
                'sort_order': machine_data.get('sort_order', 0),
            }
            
            machine = self.create_with_tenant(TeamGroupMachine, **machine_detail)
            self.commit()
            
            return machine.to_dict()
            
        except IntegrityError as e:
            self.rollback()
            if 'uq_team_group_machine' in str(e):
                raise ValueError("该机台已经分配到此班组")
            else:
                raise ValueError("数据完整性错误")
        except Exception as e:
            self.rollback()
            raise e
    
    def delete_team_machine(self, machine_id):
        """删除班组机台"""
        try:
            machine = self.session.query(TeamGroupMachine).get(uuid.UUID(machine_id))
            if not machine:
                raise ValueError("班组机台不存在")
            
            self.session.delete(machine)
            self.commit()
            
            return {"message": "班组机台删除成功"}
            
        except Exception as e:
            self.rollback()
            raise e
    
    def add_team_process(self, team_group_id, process_data, created_by):
        """添加班组工序分类"""
        try:
            process_detail = {
                'team_group_id': uuid.UUID(team_group_id),
                'process_category_id': uuid.UUID(process_data['process_category_id']),
                'sort_order': process_data.get('sort_order', 0),
            }
            
            process = self.create_with_tenant(TeamGroupProcess, **process_detail)
            self.commit()
            
            return process.to_dict()
            
        except IntegrityError as e:
            self.rollback()
            if 'uq_team_group_process' in str(e):
                raise ValueError("该工序分类已经分配到此班组")
            else:
                raise ValueError("数据完整性错误")
        except Exception as e:
            self.rollback()
            raise e
    
    def delete_team_process(self, process_id):
        """删除班组工序分类"""
        try:
            process = self.session.query(TeamGroupProcess).get(uuid.UUID(process_id))
            if not process:
                raise ValueError("班组工序分类不存在")
            
            self.session.delete(process)
            self.commit()
            
            return {"message": "班组工序分类删除成功"}
            
        except Exception as e:
            self.rollback()
            raise e


def get_team_group_service(tenant_id: Optional[str] = None, schema_name: Optional[str] = None) -> TeamGroupService:
    """获取班组服务实例"""
    return TeamGroupService(tenant_id=tenant_id, schema_name=schema_name)