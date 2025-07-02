# -*- coding: utf-8 -*-
"""
CalculationParameter 服务
"""

from app.services.base_service import TenantAwareService
from app.extensions import db
from sqlalchemy import func, text, and_, or_
from sqlalchemy.exc import IntegrityError
import uuid
from datetime import datetime
import re

class CalculationParameterService(TenantAwareService):
    """计算参数服务"""
    
    def _set_schema(self):
        """设置当前租户的schema搜索路径"""
        from flask import g, current_app
        from sqlalchemy import text
        schema_name = getattr(g, 'schema_name', current_app.config.get('DEFAULT_SCHEMA', 'public'))
        if schema_name != 'public':
            current_app.logger.info(f"Setting search_path to {schema_name} in CalculationParameterService")
            self.get_session().execute(text(f'SET search_path TO {schema_name}, public'))
    
    def get_calculation_parameters(self, page=1, per_page=20, search=None):
        """获取计算参数列表"""
        from app.models.basic_data import CalculationParameter
        
        # 设置schema
        self._set_schema()
        
        query = CalculationParameter.query
        
        # 搜索条件
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                CalculationParameter.parameter_name.ilike(search_pattern)
            )
        
        # 排序
        query = query.order_by(CalculationParameter.sort_order, CalculationParameter.parameter_name)
        
        # 分页
        total = query.count()
        if per_page > 0:
            calculation_parameters = query.offset((page - 1) * per_page).limit(per_page).all()
        else:
            calculation_parameters = query.all()
        
        return {
            'calculation_parameters': [param.to_dict(include_user_info=True) for param in calculation_parameters],
            'total': total,
            'current_page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page if per_page > 0 else 1
        }
    
    def get_calculation_parameter(self, param_id):
        """获取计算参数详情"""
        from app.models.basic_data import CalculationParameter
        
        # 设置schema
        self._set_schema()
        
        param = CalculationParameter.query.get(uuid.UUID(param_id))
        if not param:
            raise ValueError("计算参数不存在")
        return param.to_dict(include_user_info=True)
    
    def create_calculation_parameter(self, data, created_by):
        """创建计算参数"""
        from app.models.basic_data import CalculationParameter
        
        # 设置schema
        self._set_schema()
        
        try:
            # 验证必填字段
            if not data.get('parameter_name'):
                raise ValueError("计算参数名称不能为空")
            
            # 检查名称是否重复
            existing = CalculationParameter.query.filter_by(
                parameter_name=data['parameter_name']
            ).first()
            if existing:
                raise ValueError("计算参数名称已存在")
            
            # 创建计算参数对象
            param = CalculationParameter(
                parameter_name=data['parameter_name'],
                description=data.get('description'),
                sort_order=data.get('sort_order', 0),
                is_enabled=data.get('is_enabled', True),
                created_by=uuid.UUID(created_by)
            )
            
            self.get_session().add(param)
            self.get_session().commit()
            
            return param.to_dict(include_user_info=True)
            
        except IntegrityError as e:
            self.get_session().rollback()
            raise ValueError("数据完整性错误")
        except Exception as e:
            self.get_session().rollback()
            raise ValueError(f"创建计算参数失败: {str(e)}")
    
    def update_calculation_parameter(self, param_id, data, updated_by):
        """更新计算参数"""
        from app.models.basic_data import CalculationParameter
        
        # 设置schema
        self._set_schema()
        
        try:
            param = CalculationParameter.query.get(uuid.UUID(param_id))
            if not param:
                raise ValueError("计算参数不存在")
            
            # 验证必填字段
            if 'parameter_name' in data and not data['parameter_name']:
                raise ValueError("计算参数名称不能为空")
            
            # 检查名称是否重复（排除自己）
            if 'parameter_name' in data:
                existing = CalculationParameter.query.filter(
                    CalculationParameter.parameter_name == data['parameter_name'],
                    CalculationParameter.id != param.id
                ).first()
                if existing:
                    raise ValueError("计算参数名称已存在")
            
            # 更新字段
            for key, value in data.items():
                if hasattr(param, key):
                    setattr(param, key, value)
            
            param.updated_by = uuid.UUID(updated_by)
            
            self.get_session().commit()
            
            return param.to_dict(include_user_info=True)
            
        except IntegrityError as e:
            self.get_session().rollback()
            raise ValueError("数据完整性错误")
        except Exception as e:
            self.get_session().rollback()
            raise ValueError(f"更新计算参数失败: {str(e)}")
    
    def delete_calculation_parameter(self, param_id):
        """删除计算参数"""
        from app.models.basic_data import CalculationParameter
        
        # 设置schema
        self._set_schema()
        
        try:
            param = CalculationParameter.query.get(uuid.UUID(param_id))
            if not param:
                raise ValueError("计算参数不存在")
            
            self.get_session().delete(param)
            self.get_session().commit()
            
            return True
            
        except Exception as e:
            self.get_session().rollback()
            raise ValueError(f"删除计算参数失败: {str(e)}")
    
    def batch_update_calculation_parameters(self, updates, updated_by):
        """批量更新计算参数"""
        from app.models.basic_data import CalculationParameter
        
        # 设置schema
        self._set_schema()
        
        try:
            results = []
            
            for update_data in updates:
                param_id = update_data.get('id')
                if not param_id:
                    continue
                    
                param = CalculationParameter.query.get(uuid.UUID(param_id))
                if not param:
                    continue
                
                # 更新字段
                update_fields = ['parameter_name', 'description', 'sort_order', 'is_enabled']
                
                for field in update_fields:
                    if field in update_data:
                        setattr(param, field, update_data[field])
                
                # 更新审计字段
                param.updated_by = uuid.UUID(updated_by)
                
                results.append(param.to_dict())
            
            self.get_session().commit()
            
            return results
            
        except Exception as e:
            self.get_session().rollback()
            raise ValueError(f"批量更新计算参数失败: {str(e)}")
    
    def get_calculation_parameter_options(self):
        """获取计算参数选项数据"""
        from app.models.basic_data import CalculationParameter
        
        # 设置schema
        self._set_schema()
        
        try:
            # 获取启用的计算参数
            enabled_params = CalculationParameter.get_enabled_list()
            
            return {
                'calculation_parameters': [
                    {
                        'id': str(param.id),
                        'parameter_name': param.parameter_name,
                        'sort_order': param.sort_order
                    }
                    for param in enabled_params
                ]
            }
            
        except Exception as e:
            raise ValueError(f"获取计算参数选项失败: {str(e)}")


# ==================== 工厂函数 ====================

def get_calculation_parameter_service(tenant_id: str = None, schema_name: str = None) -> CalculationParameterService:
    """
    获取计算参数服务实例
    
    Args:
        tenant_id: 租户ID（可选）
        schema_name: Schema名称（可选）
    
    Returns:
        CalculationParameterService: 计算参数服务实例
    """
    return CalculationParameterService(tenant_id=tenant_id, schema_name=schema_name)


