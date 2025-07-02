# -*- coding: utf-8 -*-
"""
单位管理服务
"""
from typing import Dict, List, Optional, Any
from sqlalchemy import text
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
        session = self.get_session()
        
        base_query = f"""
        SELECT 
            id, unit_name, description, sort_order, 
            is_enabled, created_by, updated_by, created_at, updated_at
        FROM {self.schema_name}.units
        """
        
        where_conditions = []
        params = {}
        
        if search:
            where_conditions.append("""
                (unit_name ILIKE :search OR 
                 description ILIKE :search)
            """)
            params['search'] = f'%{search}%'
        
        if enabled_only:
            where_conditions.append("is_enabled = true")
        
        if where_conditions:
            base_query += " WHERE " + " AND ".join(where_conditions)
        
        base_query += " ORDER BY sort_order, created_at"
        
        try:
            # 获取总数
            count_query = f"SELECT COUNT(*) as total FROM {self.schema_name}.units"
            if where_conditions:
                count_query += " WHERE " + " AND ".join(where_conditions)
            
            count_result = session.execute(text(count_query), params)
            total = count_result.scalar()
            
            # 分页查询
            offset = (page - 1) * per_page
            params.update({'limit': per_page, 'offset': offset})
            paginated_query = base_query + " LIMIT :limit OFFSET :offset"
            
            result = session.execute(text(paginated_query), params)
            rows = result.fetchall()
            
            units = []
            for row in rows:
                unit_data = {
                    'id': str(row.id),
                    'unit_name': row.unit_name,
                    'description': row.description,
                    'sort_order': row.sort_order,
                    'is_enabled': row.is_enabled,
                    'created_by': str(row.created_by) if row.created_by else None,
                    'updated_by': str(row.updated_by) if row.updated_by else None,
                    'created_at': row.created_at.isoformat() if row.created_at else None,
                    'updated_at': row.updated_at.isoformat() if row.updated_at else None,
                }
                
                # 获取用户名
                if row.created_by:
                    created_user = User.query.get(row.created_by)
                    unit_data['created_by_name'] = created_user.get_full_name() if created_user else '未知用户'
                else:
                    unit_data['created_by_name'] = '系统'
                    
                if row.updated_by:
                    updated_user = User.query.get(row.updated_by)
                    unit_data['updated_by_name'] = updated_user.get_full_name() if updated_user else '未知用户'
                else:
                    unit_data['updated_by_name'] = ''
                
                units.append(unit_data)
            
            pages = (total + per_page - 1) // per_page
            self.log_operation('get_units', {'total': total, 'page': page})
            
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
            self.log_operation('get_units_error', {'error': str(e)})
            raise ValueError(f'查询单位失败: {str(e)}')

    def get_unit(self, unit_id: str) -> Dict[str, Any]:
        """获取单位详情"""
        try:
            unit_uuid = uuid.UUID(unit_id)
        except ValueError:
            raise ValueError('无效的单位ID')
        
        unit = Unit.query.get(unit_uuid)
        if not unit:
            raise ValueError('单位不存在')
        
        unit_data = unit.to_dict()
        
        # 获取用户名
        if unit.created_by:
            created_user = User.query.get(unit.created_by)
            unit_data['created_by_name'] = created_user.get_full_name() if created_user else '未知用户'
        
        if unit.updated_by:
            updated_user = User.query.get(unit.updated_by)
            unit_data['updated_by_name'] = updated_user.get_full_name() if updated_user else '未知用户'
        
        self.log_operation('get_unit', {'unit_id': unit_id})
        return unit_data

    def create_unit(self, data: Dict[str, Any], created_by: str) -> Dict[str, Any]:
        """创建单位"""
        if not data.get('unit_name'):
            raise ValueError('单位名称不能为空')
        
        # 检查名称重复
        existing = Unit.query.filter_by(unit_name=data['unit_name']).first()
        if existing:
            raise ValueError('单位名称已存在')
        
        try:
            created_by_uuid = uuid.UUID(created_by)
        except ValueError:
            raise ValueError('无效的创建用户ID')
        
        # 创建单位
        unit = self.create_with_tenant(
            Unit,
            unit_name=data['unit_name'],
            description=data.get('description'),
            sort_order=data.get('sort_order', 0),
            is_enabled=data.get('is_enabled', True),
            created_by=created_by_uuid
        )
        
        self.commit()
        self.log_operation('create_unit', {'unit_id': str(unit.id)})
        
        return self.get_unit(str(unit.id))

    def update_unit(self, unit_id: str, data: Dict[str, Any], updated_by: str) -> Dict[str, Any]:
        """更新单位"""
        try:
            unit_uuid = uuid.UUID(unit_id)
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的ID')
        
        unit = Unit.query.get(unit_uuid)
        if not unit:
            raise ValueError('单位不存在')
        
        # 检查名称重复
        if 'unit_name' in data and data['unit_name'] != unit.unit_name:
            existing = Unit.query.filter_by(unit_name=data['unit_name']).first()
            if existing:
                raise ValueError('单位名称已存在')
        
        # 更新字段
        for key, value in data.items():
            if hasattr(unit, key) and key not in ['id', 'created_by', 'created_at']:
                setattr(unit, key, value)
        
        unit.updated_by = updated_by_uuid
        
        self.commit()
        self.log_operation('update_unit', {'unit_id': unit_id})
        
        return self.get_unit(unit_id)

    def delete_unit(self, unit_id: str) -> bool:
        """删除单位"""
        try:
            unit_uuid = uuid.UUID(unit_id)
        except ValueError:
            raise ValueError('无效的单位ID')
        
        session = self.get_session()
        unit = session.query(Unit).get(unit_uuid)
        if not unit:
            raise ValueError('单位不存在')
        
        session.delete(unit)
        self.commit()
        self.log_operation('delete_unit', {'unit_id': unit_id})
        
        return True

    def get_enabled_units(self) -> List[Dict[str, Any]]:
        """获取启用的单位列表"""
        units = Unit.query.filter_by(is_enabled=True).order_by(
            Unit.sort_order, Unit.created_at
        ).all()
        
        self.log_operation('get_enabled_units', {'count': len(units)})
        return [unit.to_dict() for unit in units]

