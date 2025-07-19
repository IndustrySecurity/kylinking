# -*- coding: utf-8 -*-
"""
单位管理服务
"""
from typing import Dict, List, Optional, Any
from sqlalchemy.exc import SQLAlchemyError
import uuid

from app.services.base_service import TenantAwareService
from app.models.basic_data import Unit
from app.models.user import User


class UnitService(TenantAwareService):
    """单位管理服务"""

    def __init__(self, tenant_id: Optional[str] = None, schema_name: Optional[str] = None):
        """初始化单位服务"""
        super().__init__(tenant_id, schema_name)

    def get_units(self, page: int = 1, per_page: int = 20, 
                  search: Optional[str] = None, enabled_only: bool = False) -> Dict[str, Any]:
        """获取单位列表"""
        try:
            # 构建基础查询
            query = self.session.query(Unit)
            
            # 添加搜索条件
            if search:
                search_pattern = f'%{search}%'
                query = query.filter(
                    Unit.unit_name.ilike(search_pattern) |
                    Unit.description.ilike(search_pattern)
                )
        
            if enabled_only:
                query = query.filter(Unit.is_enabled == True)
            
            # 排序
            query = query.order_by(Unit.sort_order, Unit.created_at)
            
            # 分页
            total = query.count()
            offset = (page - 1) * per_page
            units_list = query.offset(offset).limit(per_page).all()
            
            units = []
            for unit in units_list:
                unit_data = unit.to_dict()
                
                # 获取用户名
                if unit.created_by:
                    created_user = self.session.query(User).get(unit.created_by)
                    unit_data['created_by_name'] = created_user.get_full_name() if created_user else '未知用户'
                else:
                    unit_data['created_by_name'] = '系统'
                    
                if unit.updated_by:
                    updated_user = self.session.query(User).get(unit.updated_by)
                    unit_data['updated_by_name'] = updated_user.get_full_name() if updated_user else '未知用户'
                else:
                    unit_data['updated_by_name'] = ''
                
                units.append(unit_data)
            
            pages = (total + per_page - 1) // per_page
            
            return {
                'units': units,
                'total': total,
                'pages': pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': page < pages,
                'has_prev': page > 1
            }
            
        except Exception as e:
            raise ValueError(f'查询单位失败: {str(e)}')

    def get_unit(self, unit_id: str) -> Dict[str, Any]:
        """获取单位详情"""
        try:
            unit_uuid = uuid.UUID(unit_id)
        except ValueError:
            raise ValueError('无效的单位ID')
        
        unit = self.session.query(Unit).get(unit_uuid)
        if not unit:
            raise ValueError('单位不存在')
        
        unit_data = unit.to_dict()
        
        # 获取用户名
        if unit.created_by:
            created_user = self.session.query(User).get(unit.created_by)
            unit_data['created_by_name'] = created_user.get_full_name() if created_user else '未知用户'
        
        if unit.updated_by:
            updated_user = self.session.query(User).get(unit.updated_by)
            unit_data['updated_by_name'] = updated_user.get_full_name() if updated_user else '未知用户'
        
        return unit_data

    def create_unit(self, data: Dict[str, Any], created_by: str) -> Dict[str, Any]:
        """创建单位"""
        if not data.get('unit_name'):
            raise ValueError('单位名称不能为空')
        
        # 检查名称重复
        existing = self.session.query(Unit).filter_by(unit_name=data['unit_name']).first()
        if existing:
            raise ValueError('单位名称已存在')
        
        try:
            created_by_uuid = uuid.UUID(created_by)
        except ValueError:
            raise ValueError('无效的创建用户ID')
        
        # 准备数据
        unit_data = {
            'unit_name': data['unit_name'],
            'description': data.get('description'),
            'sort_order': data.get('sort_order', 0),
            'is_enabled': data.get('is_enabled', True),
        }
        
        try:
            # 创建单位
            unit = self.create_with_tenant(Unit, **unit_data)
            self.commit()
            
            return self.get_unit(str(unit.id))
        except Exception as e:
            self.rollback()
            raise ValueError(f'创建单位失败: {str(e)}')

    def update_unit(self, unit_id: str, data: Dict[str, Any], updated_by: str) -> Dict[str, Any]:
        """更新单位"""
        try:
            unit_uuid = uuid.UUID(unit_id)
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的ID')
        
        unit = self.session.query(Unit).get(unit_uuid)
        if not unit:
            raise ValueError('单位不存在')
        
        # 检查名称重复
        if 'unit_name' in data and data['unit_name'] != unit.unit_name:
            existing = self.session.query(Unit).filter_by(unit_name=data['unit_name']).first()
            if existing:
                raise ValueError('单位名称已存在')
        
        # 更新字段
        for key, value in data.items():
            if hasattr(unit, key) and key not in ['id', 'created_by', 'created_at']:
                setattr(unit, key, value)
        
        unit.updated_by = updated_by_uuid
        
        try:
            self.commit()
            return self.get_unit(unit_id)
        except Exception as e:
            self.rollback()
            raise ValueError(f'更新单位失败: {str(e)}')

    def delete_unit(self, unit_id: str) -> bool:
        """删除单位"""
        try:
            unit_uuid = uuid.UUID(unit_id)
        except ValueError:
            raise ValueError('无效的单位ID')
        
        unit = self.session.query(Unit).get(unit_uuid)
        if not unit:
            raise ValueError('单位不存在')
        
        try:
            self.session.delete(unit)
            self.commit()
            return True
        except Exception as e:
            self.rollback()
            raise ValueError(f'删除单位失败: {str(e)}')

    def get_enabled_units(self) -> List[Dict[str, Any]]:
        """获取启用的单位列表"""
        try:
            units = self.session.query(Unit).filter_by(is_enabled=True).order_by(
                Unit.sort_order, Unit.created_at
            ).all()
            
            return [unit.to_dict() for unit in units]
        except Exception as e:
            raise ValueError(f'获取启用单位失败: {str(e)}')


def get_unit_service(tenant_id: Optional[str] = None, schema_name: Optional[str] = None) -> UnitService:
    """获取单位服务实例"""
    return UnitService(tenant_id=tenant_id, schema_name=schema_name)

