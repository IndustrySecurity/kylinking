# -*- coding: utf-8 -*-
"""
SettlementMethod管理服务
"""
from typing import Dict, List, Optional, Any
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import uuid

from app.services.base_service import TenantAwareService
from app.models.basic_data import SettlementMethod
from app.models.user import User


class SettlementMethodService(TenantAwareService):
    """结算方式服务类"""

    def __init__(self, tenant_id: Optional[str] = None, schema_name: Optional[str] = None):
        """初始化SettlementMethod服务"""
        super().__init__(tenant_id, schema_name)

        if schema_name != 'public':
            pass

    def get_settlement_methods(self, page=1, per_page=20, search=None, enabled_only=False):
        """获取结算方式列表"""
        
        # 获取当前schema名称
        from flask import g, current_app
        schema_name = getattr(g, 'schema_name', current_app.config.get('DEFAULT_SCHEMA', 'public'))
        
        # 构建基础查询
        base_query = f"""
        SELECT 
            id, settlement_name, description, sort_order, is_enabled,
            created_by, updated_by, created_at, updated_at
        FROM {schema_name}.settlement_methods
        """
        
        # 构建查询条件
        where_conditions = []
        params = {}
        
        if search:
            where_conditions.append("""
                (settlement_name ILIKE :search OR 
                 description ILIKE :search)
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
        FROM {schema_name}.settlement_methods
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
            
            settlement_methods = []
            for row in rows:
                settlement_method_data = {
                    'id': str(row.id),
                    'settlement_name': row.settlement_name,
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
                        settlement_method_data['created_by_name'] = created_user.get_full_name()
                    else:
                        settlement_method_data['created_by_name'] = '未知用户'
                else:
                    settlement_method_data['created_by_name'] = '系统'
                    
                if row.updated_by:
                    updated_user = User.query.get(row.updated_by)
                    if updated_user:
                        settlement_method_data['updated_by_name'] = updated_user.get_full_name()
                    else:
                        settlement_method_data['updated_by_name'] = '未知用户'
                else:
                    settlement_method_data['updated_by_name'] = ''
                
                settlement_methods.append(settlement_method_data)
            
            # 计算分页信息
            pages = (total + per_page - 1) // per_page
            has_next = page < pages
            has_prev = page > 1
            
            return {
                'settlement_methods': settlement_methods,
                'total': total,
                'pages': pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': has_next,
                'has_prev': has_prev
            }
            
        except Exception as e:
            current_app.logger.error(f"Error querying settlement methods: {str(e)}")
            raise ValueError(f'查询结算方式失败: {str(e)}')
    def get_settlement_method(self, settlement_method_id):
        """获取结算方式详情"""
        
        try:
            settlement_method_uuid = uuid.UUID(settlement_method_id)
        except ValueError:
            raise ValueError('无效的结算方式ID')
        
        from app.models.basic_data import SettlementMethod
        settlement_method = SettlementMethod.query.get(settlement_method_uuid)
        if not settlement_method:
            raise ValueError('结算方式不存在')
        
        settlement_method_data = settlement_method.to_dict()
        
        # 获取创建人和修改人用户名
        if settlement_method.created_by:
            created_user = User.query.get(settlement_method.created_by)
            if created_user:
                settlement_method_data['created_by_name'] = created_user.get_full_name()
            else:
                settlement_method_data['created_by_name'] = '未知用户'
        
        if settlement_method.updated_by:
            updated_user = User.query.get(settlement_method.updated_by)
            if updated_user:
                settlement_method_data['updated_by_name'] = updated_user.get_full_name()
            else:
                settlement_method_data['updated_by_name'] = '未知用户'
        
        return settlement_method_data
    def create_settlement_method(self, data, created_by):
        """创建结算方式"""
        
        # 验证数据
        if not data.get('settlement_name'):
            raise ValueError('结算方式名称不能为空')
        
        from app.models.basic_data import SettlementMethod
        
        # 获取当前schema名称
        from flask import g, current_app
        schema_name = getattr(g, 'schema_name', current_app.config.get('DEFAULT_SCHEMA', 'public'))
        
        # 检查结算方式名称是否重复
        check_query = f"""
        SELECT COUNT(*) as count
        FROM {schema_name}.settlement_methods
        WHERE settlement_name = :settlement_name
        """
        result = self.get_session().execute(text(check_query), {'settlement_name': data['settlement_name']})
        if result.scalar() > 0:
            raise ValueError('结算方式名称已存在')
        
        try:
            created_by_uuid = uuid.UUID(created_by)
        except ValueError:
            raise ValueError('无效的创建用户ID')
        
        # 创建结算方式
        settlement_method = SettlementMethod(
            settlement_name=data['settlement_name'],
            description=data.get('description'),
            sort_order=data.get('sort_order', 0),
            is_enabled=data.get('is_enabled', True),
            created_by=created_by_uuid
        )
        
        try:
            self.get_session().add(settlement_method)
            self.get_session().commit()
            return settlement_method.to_dict()
        except Exception as e:
            self.get_session().rollback()
            raise ValueError(f'创建结算方式失败: {str(e)}')
    def update_settlement_method(self, settlement_method_id, data, updated_by):
        """更新结算方式"""
        
        try:
            settlement_method_uuid = uuid.UUID(settlement_method_id)
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的ID')
        
        from app.models.basic_data import SettlementMethod
        settlement_method = SettlementMethod.query.get(settlement_method_uuid)
        if not settlement_method:
            raise ValueError('结算方式不存在')
        
        # 检查结算方式名称是否重复（排除自己）
        if 'settlement_name' in data and data['settlement_name'] != settlement_method.settlement_name:
            existing = SettlementMethod.query.filter(
                and_(
                    SettlementMethod.settlement_name == data['settlement_name'],
                    SettlementMethod.id != settlement_method_uuid
                )
            ).first()
            if existing:
                raise ValueError('结算方式名称已存在')
        
        # 更新字段
        if 'settlement_name' in data:
            settlement_method.settlement_name = data['settlement_name']
        if 'description' in data:
            settlement_method.description = data['description']
        if 'sort_order' in data:
            settlement_method.sort_order = data['sort_order']
        if 'is_enabled' in data:
            settlement_method.is_enabled = data['is_enabled']
        
        settlement_method.updated_by = updated_by_uuid
        
        try:
            self.get_session().commit()
            return settlement_method.to_dict()
        except Exception as e:
            self.get_session().rollback()
            raise ValueError(f'更新结算方式失败: {str(e)}')
    def delete_settlement_method(self, settlement_method_id):
        """删除结算方式"""
        
        try:
            settlement_method_uuid = uuid.UUID(settlement_method_id)
        except ValueError:
            raise ValueError('无效的结算方式ID')
        
        from app.models.basic_data import SettlementMethod
        settlement_method = SettlementMethod.query.get(settlement_method_uuid)
        if not settlement_method:
            raise ValueError('结算方式不存在')
        
        try:
            self.get_session().delete(settlement_method)
            self.get_session().commit()
        except Exception as e:
            self.get_session().rollback()
            raise ValueError(f'删除结算方式失败: {str(e)}')
    def batch_update_settlement_methods(self, data_list, updated_by):
        """批量更新结算方式"""
        
        try:
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的更新用户ID')
        
        results = []
        
        for data in data_list:
            try:
                if data.get('id') and not data['id'].startswith('temp_'):
                    # 更新现有记录
                    result = SettlementMethodService().update_settlement_method(data['id'], data, updated_by)
                else:
                    # 创建新记录
                    result = SettlementMethodService().create_settlement_method(data, updated_by)
                results.append(result)
            except Exception as e:
                current_app.logger.error(f"Error processing settlement method {data.get('id', 'new')}: {str(e)}")
                continue
        
        return results
    def get_enabled_settlement_methods(self):
        """获取启用的结算方式列表"""
        
        from app.models.basic_data import SettlementMethod
        settlement_methods = SettlementMethod.query.filter_by(is_enabled=True).order_by(SettlementMethod.sort_order, SettlementMethod.created_at).all()
        return [sm.to_dict() for sm in settlement_methods]

