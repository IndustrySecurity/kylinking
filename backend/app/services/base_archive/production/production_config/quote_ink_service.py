# -*- coding: utf-8 -*-
"""
QuoteInk管理服务
"""
from typing import Dict, List, Optional, Any
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import uuid

from app.services.base_service import TenantAwareService
from app.models.basic_data import QuoteInk
from app.models.user import User
from flask import current_app
from app.extensions import db


class QuoteInkService(TenantAwareService):
    """报价油墨服务类"""

    def __init__(self, tenant_id: Optional[str] = None, schema_name: Optional[str] = None):
        """初始化QuoteInk服务"""
        super().__init__(tenant_id, schema_name)

        if schema_name != 'public':
            pass

    def get_quote_inks(self, page=1, per_page=20, search=None, enabled_only=False):
        """获取报价油墨列表"""
        try:
            from app.models.basic_data import QuoteInk
            
            query = QuoteInk.query
            
            # 搜索过滤
            if search:
                search_pattern = f"%{search}%"
                query = query.filter(
                    db.or_(
                        QuoteInk.category_name.ilike(search_pattern),
                        QuoteInk.unit_price_formula.ilike(search_pattern),
                        QuoteInk.description.ilike(search_pattern)
                    )
                )
            
            # 启用状态过滤
            if enabled_only:
                query = query.filter(QuoteInk.is_enabled == True)
            
            # 排序
            query = query.order_by(QuoteInk.sort_order, QuoteInk.category_name)
            
            # 分页
            pagination = query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            quote_inks = [quote_ink.to_dict() for quote_ink in pagination.items]
            
            return {
                'quote_inks': quote_inks,
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': pagination.page,
                'per_page': pagination.per_page,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
            
        except Exception as e:
            current_app.logger.error(f"获取报价油墨列表失败: {str(e)}")
            raise e
    def get_quote_ink(self, quote_ink_id):
        """获取单个报价油墨"""
        try:
            from app.models.basic_data import QuoteInk
            
            quote_ink = QuoteInk.query.get(quote_ink_id)
            if not quote_ink:
                raise ValueError("报价油墨不存在")
            
            return quote_ink.to_dict()
            
        except Exception as e:
            current_app.logger.error(f"获取报价油墨失败: {str(e)}")
            raise e
    def create_quote_ink(self, data, created_by):
        """创建报价油墨"""
        try:
            from app.models.basic_data import QuoteInk
            
            # 验证必填字段
            if not data.get('category_name'):
                raise ValueError("分类名称不能为空")
            
            quote_ink = QuoteInk(
                category_name=data.get('category_name'),
                square_price=data.get('square_price'),
                unit_price_formula=data.get('unit_price_formula'),
                gram_weight=data.get('gram_weight'),
                is_ink=data.get('is_ink', False),
                is_solvent=data.get('is_solvent', False),
                sort_order=data.get('sort_order', 0),
                description=data.get('description'),
                is_enabled=data.get('is_enabled', True),
                created_by=created_by
            )
            
            self.get_session().add(quote_ink)
            self.get_session().commit()
            
            return quote_ink.to_dict()
            
        except Exception as e:
            self.get_session().rollback()
            current_app.logger.error(f"创建报价油墨失败: {str(e)}")
            raise e
    def update_quote_ink(self, quote_ink_id, data, updated_by):
        """更新报价油墨"""
        try:
            from app.models.basic_data import QuoteInk
            
            quote_ink = QuoteInk.query.get(quote_ink_id)
            if not quote_ink:
                raise ValueError("报价油墨不存在")
            
            # 更新字段
            if 'category_name' in data:
                quote_ink.category_name = data['category_name']
            if 'square_price' in data:
                quote_ink.square_price = data['square_price']
            if 'unit_price_formula' in data:
                quote_ink.unit_price_formula = data['unit_price_formula']
            if 'gram_weight' in data:
                quote_ink.gram_weight = data['gram_weight']
            if 'is_ink' in data:
                quote_ink.is_ink = data['is_ink']
            if 'is_solvent' in data:
                quote_ink.is_solvent = data['is_solvent']
            if 'sort_order' in data:
                quote_ink.sort_order = data['sort_order']
            if 'description' in data:
                quote_ink.description = data['description']
            if 'is_enabled' in data:
                quote_ink.is_enabled = data['is_enabled']
            
            quote_ink.updated_by = updated_by
            
            self.get_session().commit()
            
            return quote_ink.to_dict()
            
        except Exception as e:
            self.get_session().rollback()
            current_app.logger.error(f"更新报价油墨失败: {str(e)}")
            raise e
    def delete_quote_ink(self, quote_ink_id):
        """删除报价油墨"""
        try:
            from app.models.basic_data import QuoteInk
            
            quote_ink = QuoteInk.query.get(quote_ink_id)
            if not quote_ink:
                raise ValueError("报价油墨不存在")
            
            self.get_session().delete(quote_ink)
            self.get_session().commit()
            
        except Exception as e:
            self.get_session().rollback()
            current_app.logger.error(f"删除报价油墨失败: {str(e)}")
            raise e
    def batch_update_quote_inks(self, data_list, updated_by):
        """批量更新报价油墨"""
        try:
            from app.models.basic_data import QuoteInk
            
            results = []
            for data in data_list:
                if data.get('id'):
                    # 更新现有记录
                    quote_ink = QuoteInk.query.get(data['id'])
                    if quote_ink:
                        result = QuoteInkService().update_quote_ink(data['id'], data, updated_by)
                        results.append(result)
                else:
                    # 创建新记录
                    result = QuoteInkService().create_quote_ink(data, updated_by)
                    results.append(result)
            
            return results
            
        except Exception as e:
            current_app.logger.error(f"批量更新报价油墨失败: {str(e)}")
            raise e
    def get_enabled_quote_inks(self):
        """获取启用的报价油墨列表"""
        try:
            from app.models.basic_data import QuoteInk
            
            quote_inks = QuoteInk.get_enabled_list()
            return [quote_ink.to_dict() for quote_ink in quote_inks]
            
        except Exception as e:
            current_app.logger.error(f"获取启用报价油墨列表失败: {str(e)}")
            raise e

# 创建服务实例的工厂函数
def get_quote_ink_service():
    """获取报价油墨服务实例"""
    return QuoteInkService()

