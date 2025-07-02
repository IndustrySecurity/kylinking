# -*- coding: utf-8 -*-
"""
QuoteAccessory管理服务
"""
from typing import Dict, List, Optional, Any
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import uuid

from app.services.base_service import TenantAwareService
from app.models.basic_data import QuoteAccessory
from app.models.user import User


class QuoteAccessoryService(TenantAwareService):
    """报价辅材管理服务"""

    def __init__(self, tenant_id: Optional[str] = None, schema_name: Optional[str] = None):
        """初始化QuoteAccessory服务"""
        super().__init__(tenant_id, schema_name)

        if schema_name != 'public':
            pass

    def get_quote_accessories(self, page=1, per_page=20, search=None, enabled_only=False):
        """获取报价辅材列表"""
        from app.models.basic_data import QuoteAccessory
        from app.models.user import User
        from flask import current_app, g
        from sqlalchemy import text
        
        schema_name = getattr(g, 'schema_name', current_app.config.get('DEFAULT_SCHEMA', 'public'))
        
        # 基础查询
        base_query = f"""
        SELECT 
            q.id, q.material_name, q.unit_price, q.calculation_scheme_id, 
            q.sort_order, q.description, q.is_enabled, q.created_by, 
            q.updated_by, q.created_at, q.updated_at
        FROM {schema_name}.quote_accessories q
        """
        
        # 构建查询条件
        where_conditions = []
        params = {}
        
        if search:
            where_conditions.append("""
                (q.material_name ILIKE :search OR 
                 q.description ILIKE :search)
            """)
            params['search'] = f'%{search}%'
        
        if enabled_only:
            where_conditions.append("q.is_enabled = true")
        
        # 构建完整查询
        if where_conditions:
            base_query += " WHERE " + " AND ".join(where_conditions)
        
        base_query += " ORDER BY q.sort_order, q.created_at"
        
        # 计算总数
        count_query = f"""
        SELECT COUNT(*) as total
        FROM {schema_name}.quote_accessories q
        """
        if where_conditions:
            count_query += " WHERE " + " AND ".join(where_conditions)
        
        # 执行查询
        try:
            # 获取总数
            count_result = self.get_session().execute(text(count_query), params)
            total = count_result.scalar()
            
            # 计算分页
            offset = (page - 1) * per_page
            params['limit'] = per_page
            params['offset'] = offset
            
            # 添加分页
            paginated_query = base_query + " LIMIT :limit OFFSET :offset"
            
            # 执行分页查询
            result = self.get_session().execute(text(paginated_query), params)
            rows = result.fetchall()
            
            quote_accessories = []
            for row in rows:
                quote_accessory_data = {
                    'id': str(row.id),
                    'material_name': row.material_name,
                    'unit_price': float(row.unit_price) if row.unit_price else 0,
                    'calculation_scheme_id': str(row.calculation_scheme_id) if row.calculation_scheme_id else None,
                    'sort_order': row.sort_order,
                    'description': row.description,
                    'is_enabled': row.is_enabled,
                    'created_by': str(row.created_by) if row.created_by else None,
                    'updated_by': str(row.updated_by) if row.updated_by else None,
                    'created_at': row.created_at.isoformat() if row.created_at else None,
                    'updated_at': row.updated_at.isoformat() if row.updated_at else None,
                }
                
                # 获取创建人和修改人用户名
                if row.created_by:
                    created_user = User.query.get(row.created_by)
                    if created_user:
                        quote_accessory_data['created_by_name'] = created_user.get_full_name()
                    else:
                        quote_accessory_data['created_by_name'] = '未知用户'
                else:
                    quote_accessory_data['created_by_name'] = '系统'
                    
                if row.updated_by:
                    updated_user = User.query.get(row.updated_by)
                    if updated_user:
                        quote_accessory_data['updated_by_name'] = updated_user.get_full_name()
                    else:
                        quote_accessory_data['updated_by_name'] = '未知用户'
                else:
                    quote_accessory_data['updated_by_name'] = ''
                
                quote_accessories.append(quote_accessory_data)
            
            # 计算分页信息
            pages = (total + per_page - 1) // per_page
            has_next = page < pages
            has_prev = page > 1
            
            return {
                'quote_accessories': quote_accessories,
                'total': total,
                'pages': pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': has_next,
                'has_prev': has_prev
            }
            
        except Exception as e:
            current_app.logger.error(f"Error querying quote accessories: {str(e)}")
            raise ValueError(f'查询报价配件失败: {str(e)}')
    def get_quote_accessory(self, quote_accessory_id):
        """获取单个报价辅材"""
        from app.models.basic_data import QuoteAccessory
        
        try:
            quote_accessory_uuid = uuid.UUID(quote_accessory_id)
        except ValueError:
            raise ValueError('无效的报价配件ID')
        
        try:
            quote_accessory = self.session.query(QuoteAccessory).get(quote_accessory_uuid)
            if not quote_accessory:
                return None
            
            return quote_accessory.to_dict(include_user_info=True)
            
        except Exception as e:
            raise ValueError(f'获取报价配件失败: {str(e)}')
    def create_quote_accessory(self, data, created_by):
        """创建报价辅材"""
        from app.models.basic_data import QuoteAccessory
        
        # 验证数据
        if not data.get('material_name'):
            raise ValueError('材料名称不能为空')
        
        # 检查材料名称是否重复
        existing = self.session.query(QuoteAccessory).filter_by(
            material_name=data['material_name']
        ).first()
        if existing:
            raise ValueError('材料名称已存在')
        
        try:
            # 确保created_by是UUID类型
            if created_by:
                created_by_uuid = uuid.UUID(created_by) if isinstance(created_by, str) else created_by
            else:
                created_by_uuid = None
            
            # 准备数据
            quote_accessory_data = {
                'material_name': data['material_name'],
                'unit_price': data.get('unit_price'),
                'calculation_scheme_id': uuid.UUID(data['calculation_scheme_id']) if data.get('calculation_scheme_id') else None,
                'sort_order': data.get('sort_order', 0),
                'description': data.get('description'),
                'is_enabled': data.get('is_enabled', True),
                'created_by': created_by_uuid
            }
            
            # 创建实例
            quote_accessory = QuoteAccessory(**quote_accessory_data)
            self.session.add(quote_accessory)
            
            self.commit()
            return quote_accessory.to_dict()
            
        except Exception as e:
            self.rollback()
            raise ValueError(f'创建报价配件失败: {str(e)}')
    def update_quote_accessory(self, quote_accessory_id, data, updated_by):
        """更新报价辅材"""
        from app.models.basic_data import QuoteAccessory
        
        try:
            quote_accessory_uuid = uuid.UUID(quote_accessory_id)
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的ID')
        
        quote_accessory = self.session.query(QuoteAccessory).get(quote_accessory_uuid)
        if not quote_accessory:
            return None
        
        # 检查材料名称是否重复（排除自己）
        if 'material_name' in data and data['material_name'] != quote_accessory.material_name:
            existing = self.session.query(QuoteAccessory).filter(
                QuoteAccessory.material_name == data['material_name'],
                QuoteAccessory.id != quote_accessory_uuid
            ).first()
            if existing:
                raise ValueError('材料名称已存在')
        
        try:
            # 更新字段
            for key, value in data.items():
                if key == 'calculation_scheme_id' and value:
                    value = uuid.UUID(value)
                if hasattr(quote_accessory, key):
                    setattr(quote_accessory, key, value)
            
            quote_accessory.updated_by = updated_by_uuid
            
            self.commit()
            return quote_accessory.to_dict()
            
        except Exception as e:
            self.rollback()
            raise ValueError(f'更新报价配件失败: {str(e)}')
    def delete_quote_accessory(self, quote_accessory_id):
        """删除报价辅材"""
        from app.models.basic_data import QuoteAccessory
        
        try:
            quote_accessory_uuid = uuid.UUID(quote_accessory_id)
        except ValueError:
            raise ValueError('无效的报价配件ID')
        
        quote_accessory = self.session.query(QuoteAccessory).get(quote_accessory_uuid)
        if not quote_accessory:
            return False
        
        try:
            self.session.delete(quote_accessory)
            self.commit()
            return True
            
        except Exception as e:
            self.rollback()
            raise ValueError(f'删除报价配件失败: {str(e)}')
    def batch_update_quote_accessories(self, data_list, updated_by):
        """批量更新报价辅材"""
        from app.models.basic_data import QuoteAccessory
        
        
        try:
            updated_count = 0
            for item_data in data_list:
                quote_accessory_id = item_data.get('id')
                if quote_accessory_id:
                    quote_accessory = QuoteAccessory.query.get(quote_accessory_id)
                    if quote_accessory:
                        # 更新字段
                        for field in ['material_name', 'unit_price', 'calculation_scheme_id', 'sort_order', 'description', 'is_enabled']:
                            if field in item_data:
                                setattr(quote_accessory, field, item_data[field])
                        
                        quote_accessory.updated_by = updated_by
                        updated_count += 1
            
            self.get_session().commit()
            current_app.logger.info(f"Batch updated {updated_count} quote accessories")
            return updated_count
            
        except Exception as e:
            self.get_session().rollback()
            current_app.logger.error(f"Error batch updating quote accessories: {str(e)}")
            raise e
    def get_enabled_quote_accessories(self):
        """获取启用的报价辅材列表"""
        from app.models.basic_data import QuoteAccessory
        
        try:
            quote_accessories = self.session.query(QuoteAccessory).filter_by(
                is_enabled=True
            ).order_by(QuoteAccessory.sort_order, QuoteAccessory.material_name).all()
            
            return [item.to_dict() for item in quote_accessories]
            
        except Exception as e:
            raise ValueError(f'获取启用的报价配件失败: {str(e)}')


# ==================== 工厂函数 ====================

def get_quote_accessory_service(tenant_id: str = None, schema_name: str = None) -> QuoteAccessoryService:
    """
    获取报价配件服务实例
    
    Args:
        tenant_id: 租户ID（可选）
        schema_name: Schema名称（可选）
    
    Returns:
        QuoteAccessoryService: 报价配件服务实例
    """
    return QuoteAccessoryService(tenant_id=tenant_id, schema_name=schema_name)

