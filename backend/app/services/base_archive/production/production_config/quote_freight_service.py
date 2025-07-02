# -*- coding: utf-8 -*-
"""
QuoteFreight管理服务
"""
from typing import Dict, List, Optional, Any
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import uuid

from app.services.base_service import TenantAwareService
from app.models.basic_data import QuoteFreight
from app.models.user import User


class QuoteFreightService(TenantAwareService):
    """报价运费管理服务"""

    def __init__(self, tenant_id: Optional[str] = None, schema_name: Optional[str] = None):
        """初始化QuoteFreight服务"""
        super().__init__(tenant_id, schema_name)

        if schema_name != 'public':
            pass

    def get_quote_freights(self, page=1, per_page=20, search=None, enabled_only=False):
        """获取报价运费列表"""
        from flask import g, current_app
        
        try:
            
            # 获取当前schema名称
            schema_name = getattr(g, 'schema_name', current_app.config.get('DEFAULT_SCHEMA', 'public'))
            
            # 构建基础查询
            base_query = f"""
            SELECT 
                id, region, percentage, sort_order, is_enabled, description,
                created_by, updated_by, created_at, updated_at
            FROM {schema_name}.quote_freights
            """
            
            # 添加搜索条件
            where_conditions = []
            params = {}
            
            if search:
                where_conditions.append("""
                    (region ILIKE :search OR 
                     description ILIKE :search)
                """)
                params['search'] = f'%{search}%'
            
            if enabled_only:
                where_conditions.append("is_enabled = true")
            
            # 构建完整查询
            if where_conditions:
                base_query += " WHERE " + " AND ".join(where_conditions)
            
            base_query += " ORDER BY sort_order, region"
            
            # 计算总数
            count_query = f"""
            SELECT COUNT(*) as total
            FROM {schema_name}.quote_freights
            """
            if where_conditions:
                count_query += " WHERE " + " AND ".join(where_conditions)
            
            # 执行查询
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
            
            quote_freights = []
            for row in rows:
                freight_data = {
                    'id': str(row.id),
                    'region': row.region,
                    'percentage': float(row.percentage) if row.percentage else 0,
                    'sort_order': row.sort_order,
                    'is_enabled': row.is_enabled,
                    'description': row.description,
                    'created_by': str(row.created_by) if row.created_by else None,
                    'updated_by': str(row.updated_by) if row.updated_by else None,
                    'created_at': row.created_at.isoformat() if row.created_at else None,
                    'updated_at': row.updated_at.isoformat() if row.updated_at else None,
                }
                
                # 获取创建人和修改人用户名
                if row.created_by:
                    created_user = User.query.get(row.created_by)
                    if created_user:
                        freight_data['created_by_name'] = created_user.get_full_name()
                    else:
                        freight_data['created_by_name'] = '未知用户'
                else:
                    freight_data['created_by_name'] = '系统'
                    
                if row.updated_by:
                    updated_user = User.query.get(row.updated_by)
                    if updated_user:
                        freight_data['updated_by_name'] = updated_user.get_full_name()
                    else:
                        freight_data['updated_by_name'] = '未知用户'
                else:
                    freight_data['updated_by_name'] = ''
                
                quote_freights.append(freight_data)
            
            # 计算分页信息
            pages = (total + per_page - 1) // per_page
            has_next = page < pages
            has_prev = page > 1
            
            return {
                'quote_freights': quote_freights,
                'total': total,
                'pages': pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': has_next,
                'has_prev': has_prev
            }
            
        except Exception as e:
            current_app.logger.error(f"Error querying quote freights: {str(e)}")
            raise ValueError(f'查询报价运费失败: {str(e)}')
    def get_quote_freight(self, freight_id):
        """获取报价运费详情"""
        
        try:
            freight_uuid = uuid.UUID(freight_id)
        except ValueError:
            raise ValueError('无效的报价运费ID')
        
        from app.models.basic_data import QuoteFreight
        freight = QuoteFreight.query.get(freight_uuid)
        if not freight:
            raise ValueError('报价运费不存在')
        
        freight_data = freight.to_dict()
        
        # 获取创建人和修改人用户名
        if freight.created_by:
            created_user = User.query.get(freight.created_by)
            if created_user:
                freight_data['created_by_name'] = created_user.get_full_name()
            else:
                freight_data['created_by_name'] = '未知用户'
        
        if freight.updated_by:
            updated_user = User.query.get(freight.updated_by)
            if updated_user:
                freight_data['updated_by_name'] = updated_user.get_full_name()
            else:
                freight_data['updated_by_name'] = '未知用户'
        
        return freight_data
    def create_quote_freight(self, data, created_by):
        """创建报价运费"""
        from flask import g, current_app
        
        try:
            
            # 验证必填字段
            if not data.get('region'):
                raise ValueError("区域不能为空")
            
            # 获取当前schema名称
            schema_name = getattr(g, 'schema_name', current_app.config.get('DEFAULT_SCHEMA', 'public'))
            
            # 生成UUID
            freight_id = uuid.uuid4()
            
            # 构建插入SQL
            insert_sql = f"""
            INSERT INTO {schema_name}.quote_freights 
            (id, region, percentage, sort_order, is_enabled, description, created_by, updated_by, created_at, updated_at)
            VALUES 
            (:id, :region, :percentage, :sort_order, :is_enabled, :description, :created_by, :updated_by, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """
            
            # 准备参数
            params = {
                'id': freight_id,
                'region': data.get('region'),
                'percentage': data.get('percentage', 0),
                'sort_order': data.get('sort_order', 0),
                'is_enabled': data.get('is_enabled', True),
                'description': data.get('description', ''),
                'created_by': created_by,
                'updated_by': created_by
            }
            
            # 执行插入
            self.get_session().execute(text(insert_sql), params)
            self.get_session().commit()
            
            # 查询并返回创建的记录
            select_sql = f"""
            SELECT id, region, percentage, sort_order, is_enabled, description,
                   created_by, updated_by, created_at, updated_at
            FROM {schema_name}.quote_freights 
            WHERE id = :id
            """
            
            result = self.get_session().execute(text(select_sql), {'id': freight_id})
            row = result.fetchone()
            
            if row:
                return {
                    'id': str(row.id),
                    'region': row.region,
                    'percentage': float(row.percentage) if row.percentage else 0,
                    'sort_order': row.sort_order,
                    'is_enabled': row.is_enabled,
                    'description': row.description,
                    'created_by': str(row.created_by) if row.created_by else None,
                    'updated_by': str(row.updated_by) if row.updated_by else None,
                    'created_at': row.created_at.isoformat() if row.created_at else None,
                    'updated_at': row.updated_at.isoformat() if row.updated_at else None,
                }
            else:
                raise ValueError("创建记录后无法查询到数据")
            
        except Exception as e:
            self.get_session().rollback()
            current_app.logger.error(f"Error creating quote freight: {str(e)}")
            raise ValueError(f"创建报价运费失败: {str(e)}")
    def update_quote_freight(self, freight_id, data, updated_by):
        """更新报价运费"""
        from flask import g, current_app
        
        try:
            # 获取当前schema名称
            schema_name = getattr(g, 'schema_name', current_app.config.get('DEFAULT_SCHEMA', 'public'))
            
            # 验证记录是否存在
            check_sql = f"""
            SELECT id FROM {schema_name}.quote_freights WHERE id = :id
            """
            result = self.get_session().execute(text(check_sql), {'id': freight_id})
            if not result.fetchone():
                raise ValueError("报价运费不存在")
            
            # 构建更新SQL
            update_fields = []
            params = {'id': freight_id, 'updated_by': updated_by}
            
            if 'region' in data:
                update_fields.append("region = :region")
                params['region'] = data['region']
            if 'percentage' in data:
                update_fields.append("percentage = :percentage")
                params['percentage'] = data['percentage']
            if 'sort_order' in data:
                update_fields.append("sort_order = :sort_order")
                params['sort_order'] = data['sort_order']
            if 'is_enabled' in data:
                update_fields.append("is_enabled = :is_enabled")
                params['is_enabled'] = data['is_enabled']
            if 'description' in data:
                update_fields.append("description = :description")
                params['description'] = data['description']
            
            if not update_fields:
                raise ValueError("没有要更新的字段")
            
            update_fields.append("updated_by = :updated_by")
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            
            update_sql = f"""
            UPDATE {schema_name}.quote_freights 
            SET {', '.join(update_fields)}
            WHERE id = :id
            """
            
            # 执行更新
            self.get_session().execute(text(update_sql), params)
            self.get_session().commit()
            
            # 查询并返回更新后的记录
            select_sql = f"""
            SELECT id, region, percentage, sort_order, is_enabled, description,
                   created_by, updated_by, created_at, updated_at
            FROM {schema_name}.quote_freights 
            WHERE id = :id
            """
            
            result = self.get_session().execute(text(select_sql), {'id': freight_id})
            row = result.fetchone()
            
            if row:
                return {
                    'id': str(row.id),
                    'region': row.region,
                    'percentage': float(row.percentage) if row.percentage else 0,
                    'sort_order': row.sort_order,
                    'is_enabled': row.is_enabled,
                    'description': row.description,
                    'created_by': str(row.created_by) if row.created_by else None,
                    'updated_by': str(row.updated_by) if row.updated_by else None,
                    'created_at': row.created_at.isoformat() if row.created_at else None,
                    'updated_at': row.updated_at.isoformat() if row.updated_at else None,
                }
            else:
                raise ValueError("更新记录后无法查询到数据")
            
        except Exception as e:
            self.get_session().rollback()
            current_app.logger.error(f"Error updating quote freight: {str(e)}")
            raise ValueError(f"更新报价运费失败: {str(e)}")
    def delete_quote_freight(self, freight_id):
        """删除报价运费"""
        
        try:
            freight_uuid = uuid.UUID(freight_id)
        except ValueError:
            raise ValueError('无效的报价运费ID')
        
        from app.models.basic_data import QuoteFreight
        freight = QuoteFreight.query.get(freight_uuid)
        if not freight:
            raise ValueError('报价运费不存在')
        
        try:
            self.get_session().delete(freight)
            self.get_session().commit()
        except Exception as e:
            self.get_session().rollback()
            raise ValueError(f'删除报价运费失败: {str(e)}')
    def batch_update_quote_freights(self, data_list, updated_by):
        """批量更新报价运费（用于可编辑表格）"""
        
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
                    freight = QuoteFreightService().update_quote_freight(
                        data['id'], data, updated_by
                    )
                    results.append(freight)
                else:
                    # 创建新记录
                    freight = QuoteFreightService().create_quote_freight(
                        data, updated_by
                    )
                    results.append(freight)
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
    def get_enabled_quote_freights(self):
        """获取启用的报价运费列表（用于下拉选择）"""
        
        from app.models.basic_data import QuoteFreight
        freights = QuoteFreight.query.filter_by(
            is_enabled=True
        ).order_by(QuoteFreight.sort_order, QuoteFreight.region).all()
        
        return [freight.to_dict() for freight in freights]


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

