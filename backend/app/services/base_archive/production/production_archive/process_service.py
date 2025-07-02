# -*- coding: utf-8 -*-
"""
Process管理服务
"""
from typing import Dict, List, Optional, Any
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import uuid

from app.services.base_service import TenantAwareService
from app.models.basic_data import Process, ProcessMachine, Unit
from app.models.user import User


class ProcessService(TenantAwareService):
    """工序服务类"""
    
    def __init__(self, tenant_id: Optional[str] = None, schema_name: Optional[str] = None):
        """初始化Process服务"""
        super().__init__(tenant_id, schema_name)
    
    def _get_unit_name(self, unit_value):
        """获取单位名称，如果是UUID则查找单位名称，否则直接返回"""
        if not unit_value:
            return None
        
        try:
            unit_uuid = uuid.UUID(unit_value)
            unit_obj = self.session.query(Unit).get(unit_uuid)
            return unit_obj.unit_name if unit_obj else unit_value
        except ValueError:
            # 不是UUID格式，直接返回原值
            return unit_value
    
    def get_processes(self, page=1, per_page=20, search=None):
        """获取工序列表"""
        try:
            # 构建查询
            query = self.session.query(Process)
            
            # 添加搜索条件
            if search:
                search_pattern = f'%{search}%'
                query = query.filter(
                    Process.process_name.ilike(search_pattern) |
                    Process.description.ilike(search_pattern)
                )
            
            # 排序
            query = query.order_by(Process.process_name)
            
            # 分页
            total = query.count()
            offset = (page - 1) * per_page
            processes_list = query.offset(offset).limit(per_page).all()
            
            processes = [process.to_dict() for process in processes_list]
            
            # 计算分页信息
            pages = (total + per_page - 1) // per_page
            has_next = page < pages
            has_prev = page > 1
            
            return {
                'processes': processes,
                'total': total,
                'pages': pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': has_next,
                'has_prev': has_prev
            }
            
        except Exception as e:
            raise ValueError(f'查询工序失败: {str(e)}')

    def get_process(self, process_id):
        """获取工序详情"""
        try:
            process_uuid = uuid.UUID(process_id)
        except ValueError:
            raise ValueError('无效的工序ID')
        
        process = self.session.query(Process).get(process_uuid)
        if not process:
            raise ValueError('工序不存在')
        
        return process.to_dict()

    def create_process(self, data, created_by):
        """创建工序"""
        # 验证数据
        if not data.get('process_name'):
            raise ValueError('工序名称不能为空')
        
        # 检查工序名称是否重复
        existing = self.session.query(Process).filter_by(
            process_name=data['process_name']
        ).first()
        if existing:
            raise ValueError('工序名称已存在')
        
        try:
            created_by_uuid = uuid.UUID(created_by)
        except ValueError:
            raise ValueError('无效的创建用户ID')
        
        # 准备工序数据
        process_data = {
            'process_name': data['process_name'],
            'description': data.get('description'),
            'is_enabled': data.get('is_enabled', True),
        }
        
        try:
            # 使用继承的create_with_tenant方法
            process = self.create_with_tenant(Process, **process_data)
            self.commit()
            return process.to_dict()
        except Exception as e:
            self.rollback()
            raise ValueError(f'创建工序失败: {str(e)}')

    def update_process(self, process_id, data, updated_by):
        """更新工序"""
        try:
            process_uuid = uuid.UUID(process_id)
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的ID')
        
        process = self.session.query(Process).get(process_uuid)
        if not process:
            raise ValueError('工序不存在')
        
        # 检查工序名称是否重复（排除自己）
        if 'process_name' in data and data['process_name'] != process.process_name:
            existing = self.session.query(Process).filter(
                Process.process_name == data['process_name'],
                Process.id != process_uuid
            ).first()
            if existing:
                raise ValueError('工序名称已存在')
        
        # 更新字段
        for key, value in data.items():
            if hasattr(process, key):
                setattr(process, key, value)
        
        process.updated_by = updated_by_uuid
        
        try:
            self.commit()
            return process.to_dict()
        except Exception as e:
            self.rollback()
            raise ValueError(f'更新工序失败: {str(e)}')

    def delete_process(self, process_id):
        """删除工序"""
        try:
            process_uuid = uuid.UUID(process_id)
        except ValueError:
            raise ValueError('无效的工序ID')
        
        process = self.session.query(Process).get(process_uuid)
        if not process:
            raise ValueError('工序不存在')
        
        try:
            self.session.delete(process)
            self.commit()
        except Exception as e:
            self.rollback()
            raise ValueError(f'删除工序失败: {str(e)}')

    def get_enabled_processes(self):
        """获取启用的工序列表（用于下拉选择）"""
        processes = self.session.query(Process).filter_by(
            is_enabled=True
        ).order_by(Process.process_name).all()
        
        return [process.to_dict() for process in processes]

    def get_calculation_scheme_options_by_category(self):
        """获取按分类的计算方案选项"""
        try:
            from app.models.basic_data import CalculationScheme
            
            schemes = self.session.query(CalculationScheme).filter(
                CalculationScheme.is_enabled == True
            ).order_by(CalculationScheme.scheme_name).all()
            
            return [
                {
                    'value': str(scheme.id),
                    'label': scheme.scheme_name,
                    'category': scheme.scheme_category or 'default'
                }
                for scheme in schemes
            ]
            
        except Exception as e:
            return []
    
    def get_scheduling_method_options(self):
        """获取排程方式选项"""
        return [
            {'value': '', 'label': '无'},
            {'value': 'investment_m', 'label': '投产m'},
            {'value': 'investment_kg', 'label': '投产kg'},
            {'value': 'production_piece', 'label': '投产(个)'},
            {'value': 'production_output', 'label': '产出m'},
            {'value': 'production_kg', 'label': '产出kg'},
            {'value': 'production_piece_out', 'label': '产出(个)'},
            {'value': 'production_set', 'label': '产出(套)'},
            {'value': 'production_sheet', 'label': '产出(张)'}
        ]


def get_process_service(tenant_id: str = None, schema_name: str = None) -> ProcessService:
    """获取工序服务实例"""
    return ProcessService(tenant_id=tenant_id, schema_name=schema_name)