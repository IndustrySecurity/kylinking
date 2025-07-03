# -*- coding: utf-8 -*-
"""
QuoteAccessory 服务
"""

from app.services.base_service import TenantAwareService
from app.extensions import db
from sqlalchemy import func, text, and_, or_
from sqlalchemy.exc import IntegrityError
import uuid
from datetime import datetime
import re

class QuoteAccessoryService(TenantAwareService):
    """报价配件服务"""

    def get_quote_accessories(self, page=1, per_page=20, search=None):
        """获取报价配件列表"""
        from app.models.basic_data import QuoteAccessory
        
        try:
            query = self.session.query(QuoteAccessory)
            
            # 搜索条件
            if search:
                search_pattern = f"%{search}%"
                query = query.filter(or_(
                    QuoteAccessory.accessory_name.ilike(search_pattern),
                    QuoteAccessory.description.ilike(search_pattern)
                ))
            
            # 计算总数
            total = query.count()
            
            # 排序和分页
            query = query.order_by(QuoteAccessory.sort_order, QuoteAccessory.accessory_name)
            accessories = query.offset((page - 1) * per_page).limit(per_page).all()
            
            return {
                'accessories': [accessory.to_dict() for accessory in accessories],
                'total': total,
                'current_page': page,
                'per_page': per_page,
                'pages': (total + per_page - 1) // per_page
            }
            
        except Exception as e:
            raise ValueError(f"获取报价配件列表失败: {str(e)}")
    
    def get_quote_accessory(self, accessory_id):
        """获取报价配件详情"""
        from app.models.basic_data import QuoteAccessory
        
        try:
            accessory = self.session.query(QuoteAccessory).get(uuid.UUID(accessory_id))
            if not accessory:
                raise ValueError("报价配件不存在")
            return accessory.to_dict()
        except Exception as e:
            raise ValueError(f"获取报价配件详情失败: {str(e)}")
    
    def create_quote_accessory(self, data, created_by):
        """创建报价配件"""
        from app.models.basic_data import QuoteAccessory
        
        try:
            # 验证必填字段
            if not data.get('accessory_name'):
                raise ValueError("配件名称不能为空")
        
            # 检查名称是否重复
            existing = self.session.query(QuoteAccessory).filter_by(
                accessory_name=data['accessory_name']
            ).first()
            if existing:
                raise ValueError("配件名称已存在")
            
            # 创建报价配件对象
            accessory = self.create_with_tenant(QuoteAccessory,
                accessory_name=data['accessory_name'],
                unit_price=data.get('unit_price', 0.0),
                unit=data.get('unit', ''),
                description=data.get('description', ''),
                sort_order=data.get('sort_order', 0),
                is_enabled=data.get('is_enabled', True),
                created_by=uuid.UUID(created_by)
            )
            
            self.commit()
            return accessory.to_dict()
            
        except IntegrityError as e:
            self.rollback()
            raise ValueError("数据完整性错误")
        except Exception as e:
            self.rollback()
            raise ValueError(f"创建报价配件失败: {str(e)}")
    
    def update_quote_accessory(self, accessory_id, data, updated_by):
        """更新报价配件"""
        from app.models.basic_data import QuoteAccessory
        
        try:
            accessory = self.session.query(QuoteAccessory).get(uuid.UUID(accessory_id))
            if not accessory:
                raise ValueError("报价配件不存在")
        
            # 验证必填字段
            if 'accessory_name' in data and not data['accessory_name']:
                raise ValueError("配件名称不能为空")
            
            # 检查名称是否重复（排除自己）
            if 'accessory_name' in data:
                existing = self.session.query(QuoteAccessory).filter(
                    QuoteAccessory.accessory_name == data['accessory_name'],
                    QuoteAccessory.id != accessory.id
                ).first()
                if existing:
                    raise ValueError("配件名称已存在")
        
            # 更新字段
            for key, value in data.items():
                if hasattr(accessory, key):
                    setattr(accessory, key, value)
            
            accessory.updated_by = uuid.UUID(updated_by)
            
            self.commit()
            return accessory.to_dict()
            
        except IntegrityError as e:
            self.rollback()
            raise ValueError("数据完整性错误")
        except Exception as e:
            self.rollback()
            raise ValueError(f"更新报价配件失败: {str(e)}")
    
    def delete_quote_accessory(self, accessory_id):
        """删除报价配件"""
        from app.models.basic_data import QuoteAccessory
        
        try:
            accessory = self.session.query(QuoteAccessory).get(uuid.UUID(accessory_id))
            if not accessory:
                raise ValueError("报价配件不存在")
            
            self.session.delete(accessory)
            self.commit()
            
            return True
            
        except Exception as e:
            self.rollback()
            raise ValueError(f"删除报价配件失败: {str(e)}")
    
    def batch_update_quote_accessories(self, updates, updated_by):
        """批量更新报价配件"""
        from app.models.basic_data import QuoteAccessory
        
        try:
            results = []
            
            for update_data in updates:
                accessory_id = update_data.get('id')
                if not accessory_id:
                    continue
                    
                accessory = self.session.query(QuoteAccessory).get(uuid.UUID(accessory_id))
                if not accessory:
                    continue
                
                        # 更新字段
                update_fields = ['accessory_name', 'unit_price', 'unit', 'description', 'sort_order', 'is_enabled']
                
                for field in update_fields:
                    if field in update_data:
                        setattr(accessory, field, update_data[field])
                        
                # 更新审计字段
                accessory.updated_by = uuid.UUID(updated_by)
                
                results.append(accessory.to_dict())
            
            self.commit()
            
            return results
            
        except Exception as e:
            self.rollback()
            raise ValueError(f"批量更新报价配件失败: {str(e)}")
    
    def get_quote_accessory_options(self):
        """获取报价配件选项数据"""
        from app.models.basic_data import QuoteAccessory
        
        try:
            # 获取启用的报价配件
            enabled_accessories = self.session.query(QuoteAccessory).filter(
                QuoteAccessory.is_enabled == True
            ).order_by(QuoteAccessory.sort_order, QuoteAccessory.accessory_name).all()
            
            return {
                'accessories': [
                    {
                        'id': str(accessory.id),
                        'accessory_name': accessory.accessory_name,
                        'unit_price': float(accessory.unit_price),
                        'unit': accessory.unit,
                        'sort_order': accessory.sort_order
                    }
                    for accessory in enabled_accessories
                ]
            }
            
        except Exception as e:
            raise ValueError(f"获取报价配件选项失败: {str(e)}")


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

