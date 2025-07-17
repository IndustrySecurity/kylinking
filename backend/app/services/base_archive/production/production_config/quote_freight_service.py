# -*- coding: utf-8 -*-
"""
QuoteFreight 服务
"""

from app.services.base_service import TenantAwareService
from app.extensions import db
from sqlalchemy import func, text, and_, or_
from sqlalchemy.exc import IntegrityError
import uuid
from datetime import datetime
import re

class QuoteFreightService(TenantAwareService):
    """报价运费服务"""
    
    def get_quote_freights(self, page=1, per_page=20, search=None):
        """获取报价运费列表"""
        from app.models.basic_data import QuoteFreight
        
        try:
            query = self.session.query(QuoteFreight)
            
            # 搜索条件
            if search:
                search_pattern = f"%{search}%"
                query = query.filter(or_(
                    QuoteFreight.region.ilike(search_pattern),
                    QuoteFreight.description.ilike(search_pattern)
                ))
            
            # 计算总数
            total = query.count()
            
            # 排序和分页
            query = query.order_by(QuoteFreight.sort_order, QuoteFreight.region)
            freights = query.offset((page - 1) * per_page).limit(per_page).all()
            
            return {
                'freights': [freight.to_dict(include_user_info=True) for freight in freights],
                'total': total,
                'current_page': page,
                'per_page': per_page,
                'pages': (total + per_page - 1) // per_page
            }
            
        except Exception as e:
            raise ValueError(f"获取报价运费列表失败: {str(e)}")
    
    def get_quote_freight(self, freight_id):
        """获取报价运费详情"""
        from app.models.basic_data import QuoteFreight
        
        try:
            freight = self.session.query(QuoteFreight).get(uuid.UUID(freight_id))
            if not freight:
                raise ValueError("报价运费不存在")
            return freight.to_dict(include_user_info=True)
        except Exception as e:
            raise ValueError(f"获取报价运费详情失败: {str(e)}")
    
    def create_quote_freight(self, data, created_by):
        """创建报价运费"""
        from app.models.basic_data import QuoteFreight
        
        try:
            # 验证必填字段
            if not data.get('region'):
                raise ValueError("区域不能为空")
            
            # 检查区域是否重复
            existing = self.session.query(QuoteFreight).filter_by(
                region=data['region']
            ).first()
            if existing:
                raise ValueError("区域已存在")
            
            # 创建报价运费对象
            freight = self.create_with_tenant(QuoteFreight,
                region=data['region'],
                percentage=data.get('percentage', 0.0),
                description=data.get('description', ''),
                sort_order=data.get('sort_order', 0),
                is_enabled=data.get('is_enabled', True),
                created_by=uuid.UUID(created_by)
            )
            
            self.commit()
            return freight.to_dict(include_user_info=True)
            
        except IntegrityError as e:
            self.rollback()
            raise ValueError("数据完整性错误")
        except Exception as e:
            self.rollback()
            raise ValueError(f"创建报价运费失败: {str(e)}")
    
    def update_quote_freight(self, freight_id, data, updated_by):
        """更新报价运费"""
        from app.models.basic_data import QuoteFreight
        
        try:
            freight = self.session.query(QuoteFreight).get(uuid.UUID(freight_id))
            if not freight:
                raise ValueError("报价运费不存在")
            
            # 验证必填字段
            if 'region' in data and not data['region']:
                raise ValueError("区域不能为空")
            
            # 检查区域是否重复（排除自己）
            if 'region' in data:
                existing = self.session.query(QuoteFreight).filter(
                    QuoteFreight.region == data['region'],
                    QuoteFreight.id != freight.id
                ).first()
                if existing:
                    raise ValueError("区域已存在")
            
            # 更新字段
            for key, value in data.items():
                if hasattr(freight, key):
                    setattr(freight, key, value)
            
            freight.updated_by = uuid.UUID(updated_by)
            
            self.commit()
            return freight.to_dict(include_user_info=True)
            
        except IntegrityError as e:
            self.rollback()
            raise ValueError("数据完整性错误")
        except Exception as e:
            self.rollback()
            raise ValueError(f"更新报价运费失败: {str(e)}")
    
    def delete_quote_freight(self, freight_id):
        """删除报价运费"""
        from app.models.basic_data import QuoteFreight
        
        try:
            freight = self.session.query(QuoteFreight).get(uuid.UUID(freight_id))
            if not freight:
                raise ValueError("报价运费不存在")
            
            self.session.delete(freight)
            self.commit()
            
            return True
            
        except Exception as e:
            self.rollback()
            raise ValueError(f"删除报价运费失败: {str(e)}")
    
    def batch_update_quote_freights(self, updates, updated_by):
        """批量更新报价运费"""
        from app.models.basic_data import QuoteFreight
        
        try:
            results = []
            
            for update_data in updates:
                freight_id = update_data.get('id')
                if not freight_id:
                    continue
                    
                freight = self.session.query(QuoteFreight).get(uuid.UUID(freight_id))
                if not freight:
                    continue
                
                # 更新字段
                update_fields = ['region', 'percentage', 'description', 'sort_order', 'is_enabled']
                
                for field in update_fields:
                    if field in update_data:
                        setattr(freight, field, update_data[field])
                
                # 更新审计字段
                freight.updated_by = uuid.UUID(updated_by)
                
                results.append(freight.to_dict(include_user_info=True))
            
            self.commit()
            
            return results
            
        except Exception as e:
            self.rollback()
            raise ValueError(f"批量更新报价运费失败: {str(e)}")
    
    def get_quote_freight_options(self):
        """获取报价运费选项数据"""
        from app.models.basic_data import QuoteFreight
        
        try:
            # 获取启用的报价运费
            enabled_freights = self.session.query(QuoteFreight).filter(
                QuoteFreight.is_enabled == True
            ).order_by(QuoteFreight.sort_order, QuoteFreight.region).all()
            
            return {
                'freights': [
                    {
                        'id': str(freight.id),
                        'region': freight.region,
                        'percentage': float(freight.percentage),
                        'sort_order': freight.sort_order
                    }
                    for freight in enabled_freights
                ]
            }
            
        except Exception as e:
            raise ValueError(f"获取报价运费选项失败: {str(e)}")


# ==================== 工厂函数 ====================

def get_quote_freight_service(tenant_id: str = None, schema_name: str = None) -> QuoteFreightService:
    """
    获取报价运费服务实例
    
    Args:
        tenant_id: 租户ID（可选）
        schema_name: Schema名称（可选）
    
    Returns:
        QuoteFreightService: 报价运费服务实例
    """
    return QuoteFreightService(tenant_id=tenant_id, schema_name=schema_name)

