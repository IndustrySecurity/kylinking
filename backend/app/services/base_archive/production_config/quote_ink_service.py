# -*- coding: utf-8 -*-
"""
QuoteInk 服务
"""

from app.services.base_service import TenantAwareService
from app.extensions import db
from sqlalchemy import func, text, and_, or_
from sqlalchemy.exc import IntegrityError
import uuid
from datetime import datetime
import re

class QuoteInkService(TenantAwareService):
    """报价油墨服务"""

    def get_quote_inks(self, page=1, per_page=20, search=None):
        """获取报价油墨列表"""
        from app.models.basic_data import QuoteInk
        
        try:
            query = self.session.query(QuoteInk)
            
            # 搜索条件
            if search:
                search_pattern = f"%{search}%"
                query = query.filter(or_(
                    QuoteInk.category_name.ilike(search_pattern),
                    QuoteInk.description.ilike(search_pattern)
                ))
            
            # 计算总数
            total = query.count()
            
            # 排序和分页
            query = query.order_by(QuoteInk.sort_order, QuoteInk.category_name)
            inks = query.offset((page - 1) * per_page).limit(per_page).all()
            
            return {
                'inks': [ink.to_dict() for ink in inks],
                'total': total,
                'current_page': page,
                'per_page': per_page,
                'pages': (total + per_page - 1) // per_page
            }
            
        except Exception as e:
            raise ValueError(f"获取报价油墨列表失败: {str(e)}")
    
    def get_quote_ink(self, ink_id):
        """获取报价油墨详情"""
        from app.models.basic_data import QuoteInk
        
        try:
            ink = self.session.query(QuoteInk).get(uuid.UUID(ink_id))
            if not ink:
                raise ValueError("报价油墨不存在")
            return ink.to_dict()
        except Exception as e:
            raise ValueError(f"获取报价油墨详情失败: {str(e)}")
    
    def create_quote_ink(self, data, created_by):
        """创建报价油墨"""
        from app.models.basic_data import QuoteInk
        
        try:
            # 验证必填字段
            if not data.get('category_name'):
                raise ValueError("油墨名称不能为空")
            
            # 检查名称是否重复
            existing = self.session.query(QuoteInk).filter_by(
                category_name=data['category_name']
            ).first()
            if existing:
                raise ValueError("油墨名称已存在")
            
            # 创建报价油墨对象
            ink = self.create_with_tenant(QuoteInk,
                category_name=data['category_name'],
                unit_price=data.get('unit_price', 0.0),
                ink_type=data.get('ink_type', ''),
                description=data.get('description', ''),
                sort_order=data.get('sort_order', 0),
                is_enabled=data.get('is_enabled', True),
                created_by=uuid.UUID(created_by)
            )
            
            self.commit()
            return ink.to_dict()
            
        except IntegrityError as e:
            self.rollback()
            raise ValueError("数据完整性错误")
        except Exception as e:
            self.rollback()
            raise ValueError(f"创建报价油墨失败: {str(e)}")
    
    def update_quote_ink(self, ink_id, data, updated_by):
        """更新报价油墨"""
        from app.models.basic_data import QuoteInk
        
        try:
            ink = self.session.query(QuoteInk).get(uuid.UUID(ink_id))
            if not ink:
                raise ValueError("报价油墨不存在")
            
            # 验证必填字段
            if 'category_name' in data and not data['category_name']:
                raise ValueError("油墨名称不能为空")
            
            # 检查名称是否重复（排除自己）
            if 'category_name' in data:
                existing = self.session.query(QuoteInk).filter(
                    QuoteInk.category_name == data['category_name'],
                    QuoteInk.id != ink.id
                ).first()
                if existing:
                    raise ValueError("油墨名称已存在")
            
            # 更新字段
            for key, value in data.items():
                if hasattr(ink, key):
                    setattr(ink, key, value)
            
            ink.updated_by = uuid.UUID(updated_by)
            
            self.commit()
            return ink.to_dict()
            
        except IntegrityError as e:
            self.rollback()
            raise ValueError("数据完整性错误")
        except Exception as e:
            self.rollback()
            raise ValueError(f"更新报价油墨失败: {str(e)}")
    
    def delete_quote_ink(self, ink_id):
        """删除报价油墨"""
        from app.models.basic_data import QuoteInk
        
        try:
            ink = self.session.query(QuoteInk).get(uuid.UUID(ink_id))
            if not ink:
                raise ValueError("报价油墨不存在")
            
            self.session.delete(ink)
            self.commit()
            
            return True
            
        except Exception as e:
            self.rollback()
            raise ValueError(f"删除报价油墨失败: {str(e)}")
    
    def batch_update_quote_inks(self, updates, updated_by):
        """批量更新报价油墨"""
        from app.models.basic_data import QuoteInk
        
        try:
            results = []
            
            for update_data in updates:
                ink_id = update_data.get('id')
                if not ink_id:
                    continue
                    
                ink = self.session.query(QuoteInk).get(uuid.UUID(ink_id))
                if not ink:
                    continue
                
                # 更新字段
                update_fields = ['category_name', 'unit_price', 'ink_type', 'description', 'sort_order', 'is_enabled']
                
                for field in update_fields:
                    if field in update_data:
                        setattr(ink, field, update_data[field])
                
                # 更新审计字段
                ink.updated_by = uuid.UUID(updated_by)
                
                results.append(ink.to_dict())
            
            self.commit()
            
            return results
            
        except Exception as e:
            self.rollback()
            raise ValueError(f"批量更新报价油墨失败: {str(e)}")
    
    def get_quote_ink_options(self):
        """获取报价油墨选项数据"""
        from app.models.basic_data import QuoteInk
        
        try:
            # 获取启用的报价油墨
            enabled_inks = self.session.query(QuoteInk).filter(
                QuoteInk.is_enabled == True
            ).order_by(QuoteInk.sort_order, QuoteInk.category_name).all()
            
            return {
                'inks': [
                    {
                        'id': str(ink.id),
                        'category_name': ink.category_name,
                        'unit_price': float(ink.unit_price),
                        'ink_type': ink.ink_type,
                        'sort_order': ink.sort_order
                    }
                    for ink in enabled_inks
                ]
            }
            
        except Exception as e:
            raise ValueError(f"获取报价油墨选项失败: {str(e)}")


# ==================== 工厂函数 ====================

def get_quote_ink_service(tenant_id: str = None, schema_name: str = None) -> QuoteInkService:
    """
    获取报价油墨服务实例
    
    Args:
        tenant_id: 租户ID（可选）
        schema_name: Schema名称（可选）
    
    Returns:
        QuoteInkService: 报价油墨服务实例
    """
    return QuoteInkService(tenant_id=tenant_id, schema_name=schema_name)

