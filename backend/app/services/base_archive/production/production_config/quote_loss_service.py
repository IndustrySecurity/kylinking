# -*- coding: utf-8 -*-
"""
QuoteLoss管理服务
"""
from typing import Dict, List, Optional, Any
from sqlalchemy import text, and_
from sqlalchemy.exc import SQLAlchemyError
import uuid

from app.services.base_service import TenantAwareService
from app.models.basic_data import QuoteLoss
from sqlalchemy import cast, String
from app.models.user import User


class QuoteLossService(TenantAwareService):
    """报价损耗管理服务"""

    def __init__(self, tenant_id: Optional[str] = None, schema_name: Optional[str] = None):
        """初始化QuoteLoss服务"""
        super().__init__(tenant_id, schema_name)

        if schema_name != 'public':
            pass

    def get_quote_losses(self, page=1, per_page=20, search=None, enabled_only=False):
        """获取报价损耗列表"""
        
        # 获取当前schema名称
        
        from flask import g, current_app
        schema_name = getattr(g, 'schema_name', current_app.config.get('DEFAULT_SCHEMA', 'public'))
        
        # 构建基础查询
        base_query = f"""
        SELECT 
            id, bag_type, layer_count, meter_range, loss_rate, cost,
            description, sort_order, is_enabled, created_by, updated_by, created_at, updated_at
        FROM {schema_name}.quote_losses
        """
        
        # 添加搜索条件
        where_conditions = []
        params = {}
        
        if search:
            where_conditions.append("""
                (bag_type ILIKE :search OR 
                 description ILIKE :search OR 
                 cast(layer_count, String) ILIKE :search)
            """)
            params['search'] = f'%{search}%'
        
        if enabled_only:
            where_conditions.append("is_enabled = true")
        
        # 构建完整查询
        if where_conditions:
            base_query += " WHERE " + " AND ".join(where_conditions)
        
        base_query += " ORDER BY sort_order, created_at"
        
        # 计算总数
        count_query = f"""
        SELECT COUNT(*) as total
        FROM {schema_name}.quote_losses
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
            
            quote_losses = []
            for row in rows:
                quote_loss_data = {
                    'id': str(row.id),
                    'bag_type': row.bag_type,
                    'layer_count': row.layer_count,
                    'meter_range': float(row.meter_range) if row.meter_range else None,
                    'loss_rate': float(row.loss_rate) if row.loss_rate else None,
                    'cost': float(row.cost) if row.cost else None,
                    'description': row.description,
                    'sort_order': row.sort_order,
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
                        quote_loss_data['created_by_name'] = created_user.get_full_name()
                    else:
                        quote_loss_data['created_by_name'] = '未知用户'
                else:
                    quote_loss_data['created_by_name'] = '系统'
                
                if row.updated_by:
                    updated_user = User.query.get(row.updated_by)
                    if updated_user:
                        quote_loss_data['updated_by_name'] = updated_user.get_full_name()
                    else:
                        quote_loss_data['updated_by_name'] = '未知用户'
                else:
                    quote_loss_data['updated_by_name'] = None
                
                quote_losses.append(quote_loss_data)
            
            return {
                'quote_losses': quote_losses,
                'total': total,
                'current_page': page,
                'per_page': per_page,
                'total_pages': (total + per_page - 1) // per_page
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting quote losses: {str(e)}")
            raise ValueError(f'获取报价损耗列表失败: {str(e)}')
    def get_quote_loss(self, quote_loss_id):
        """获取报价损耗详情"""
        
        try:
            quote_loss_uuid = uuid.UUID(quote_loss_id)
        except ValueError:
            raise ValueError('无效的报价损耗ID')
        
        from app.models.basic_data import QuoteLoss
        quote_loss = QuoteLoss.query.get(quote_loss_uuid)
        if not quote_loss:
            raise ValueError('报价损耗不存在')
        
        quote_loss_data = quote_loss.to_dict()
        
        # 获取创建人和修改人用户名
        if quote_loss.created_by:
            created_user = User.query.get(quote_loss.created_by)
            if created_user:
                quote_loss_data['created_by_name'] = created_user.get_full_name()
            else:
                quote_loss_data['created_by_name'] = '未知用户'
        
        if quote_loss.updated_by:
            updated_user = User.query.get(quote_loss.updated_by)
            if updated_user:
                quote_loss_data['updated_by_name'] = updated_user.get_full_name()
            else:
                quote_loss_data['updated_by_name'] = '未知用户'
        
        return quote_loss_data
    def create_quote_loss(self, data, created_by):
        """创建报价损耗"""
        
        # 验证数据
        if not data.get('bag_type'):
            raise ValueError('袋型不能为空')
        if not data.get('layer_count'):
            raise ValueError('层数不能为空')
        if not data.get('meter_range'):
            raise ValueError('米数区间不能为空')
        if not data.get('loss_rate'):
            raise ValueError('损耗不能为空')
        if not data.get('cost'):
            raise ValueError('费用不能为空')
        
        # 检查是否重复（袋型+层数+米数区间的组合应该唯一）
        from app.models.basic_data import QuoteLoss
        existing = QuoteLoss.query.filter_by(
            bag_type=data['bag_type'],
            layer_count=data['layer_count'],
            meter_range=data['meter_range']
        ).first()
        if existing:
            raise ValueError('相同袋型、层数和米数区间的记录已存在')
        
        try:
            created_by_uuid = uuid.UUID(created_by)
        except ValueError:
            raise ValueError('无效的创建用户ID')
        
        # 创建报价损耗
        quote_loss = QuoteLoss(
            bag_type=data['bag_type'],
            layer_count=data['layer_count'],
            meter_range=data['meter_range'],
            loss_rate=data['loss_rate'],
            cost=data['cost'],
            description=data.get('description'),
            sort_order=data.get('sort_order', 0),
            is_enabled=data.get('is_enabled', True),
            created_by=created_by_uuid
        )
        
        try:
            self.get_session().add(quote_loss)
            self.get_session().commit()
            return quote_loss.to_dict()
        except Exception as e:
            self.get_session().rollback()
            raise ValueError(f'创建报价损耗失败: {str(e)}')
    def update_quote_loss(self, quote_loss_id, data, updated_by):
        """更新报价损耗"""
        
        try:
            quote_loss_uuid = uuid.UUID(quote_loss_id)
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的ID')
        
        from app.models.basic_data import QuoteLoss
        quote_loss = QuoteLoss.query.get(quote_loss_uuid)
        if not quote_loss:
            raise ValueError('报价损耗不存在')
        
        # 检查是否重复（排除自己）
        if ('bag_type' in data or 'layer_count' in data or 'meter_range' in data):
            bag_type = data.get('bag_type', quote_loss.bag_type)
            layer_count = data.get('layer_count', quote_loss.layer_count)
            meter_range = data.get('meter_range', quote_loss.meter_range)
            
            existing = QuoteLoss.query.filter(
                and_(
                    QuoteLoss.bag_type == bag_type,
                    QuoteLoss.layer_count == layer_count,
                    QuoteLoss.meter_range == meter_range,
                    QuoteLoss.id != quote_loss_uuid
                )
            ).first()
            if existing:
                raise ValueError('相同袋型、层数和米数区间的记录已存在')
        
        # 更新字段
        for key, value in data.items():
            if hasattr(quote_loss, key):
                setattr(quote_loss, key, value)
        
        quote_loss.updated_by = updated_by_uuid
        
        try:
            self.get_session().commit()
            return quote_loss.to_dict()
        except Exception as e:
            self.get_session().rollback()
            raise ValueError(f'更新报价损耗失败: {str(e)}')
    def delete_quote_loss(self, quote_loss_id):
        """删除报价损耗"""
        
        try:
            quote_loss_uuid = uuid.UUID(quote_loss_id)
        except ValueError:
            raise ValueError('无效的报价损耗ID')
        
        from app.models.basic_data import QuoteLoss
        quote_loss = QuoteLoss.query.get(quote_loss_uuid)
        if not quote_loss:
            raise ValueError('报价损耗不存在')
        
        try:
            self.get_session().delete(quote_loss)
            self.get_session().commit()
        except Exception as e:
            self.get_session().rollback()
            raise ValueError(f'删除报价损耗失败: {str(e)}')
    def batch_update_quote_losses(self, data_list, updated_by):
        """批量更新报价损耗（用于可编辑表格）"""
        
        try:
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的用户ID')
        
        results = []
        errors = []
        
        for index, data in enumerate(data_list):
            try:
                if 'id' in data and data['id']:
                    # 更新现有记录
                    quote_loss = QuoteLossService().update_quote_loss(
                        data['id'], data, updated_by
                    )
                    results.append(quote_loss)
                else:
                    # 创建新记录
                    quote_loss = QuoteLossService().create_quote_loss(
                        data, updated_by
                    )
                    results.append(quote_loss)
            except ValueError as e:
                errors.append({
                    'index': index,
                    'error': str(e),
                    'data': data
                })
        
        if errors:
            # 如果有错误，回滚事务
            self.get_session().rollback()
            raise ValueError(f'批量更新失败，错误详情: {errors}')
        
        return results
    def get_enabled_quote_losses(self):
        """获取启用的报价损耗列表（用于下拉选择）"""
        
        from app.models.basic_data import QuoteLoss
        quote_losses = QuoteLoss.query.filter_by(
            is_enabled=True
        ).order_by(QuoteLoss.sort_order, QuoteLoss.bag_type).all()
        
        return [ql.to_dict() for ql in quote_losses]

# 创建服务实例的工厂函数
def get_quote_loss_service():
    """获取报价损耗服务实例"""
    return QuoteLossService()

