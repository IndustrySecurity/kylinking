# -*- coding: utf-8 -*-
"""
TaxRate管理服务
"""
from typing import Dict, List, Optional, Any
from sqlalchemy.exc import SQLAlchemyError
import uuid

from app.services.base_service import TenantAwareService
from app.models.basic_data import TaxRate
from app.models.user import User


class TaxRateService(TenantAwareService):
    """税率管理服务"""

    def get_tax_rates(self, page=1, per_page=20, search=None, enabled_only=False):
        """获取税率列表"""
        from flask import g, current_app
        from sqlalchemy import text
        
        schema_name = getattr(g, 'schema_name', current_app.config.get('DEFAULT_SCHEMA', 'public'))
        
        # 基础查询
        base_query = f"""
        SELECT 
            t.id, t.tax_name, t.tax_rate, t.is_default, t.description, 
            t.sort_order, t.is_enabled, t.created_by, t.updated_by, 
            t.created_at, t.updated_at
        FROM {schema_name}.tax_rates t
        """
        
        # 构建查询条件
        where_conditions = []
        params = {}
        
        if search:
            where_conditions.append("""
                (t.tax_name ILIKE :search OR 
                 t.description ILIKE :search)
            """)
            params['search'] = f'%{search}%'
        
        if enabled_only:
            where_conditions.append("t.is_enabled = true")
        
        # 构建完整查询
        if where_conditions:
            base_query += " WHERE " + " AND ".join(where_conditions)
        
        base_query += " ORDER BY t.sort_order, t.created_at"
        
        # 计算总数
        count_query = f"""
        SELECT COUNT(*) as total
        FROM {schema_name}.tax_rates t
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
            
            tax_rates = []
            for row in rows:
                tax_rate_data = {
                    'id': str(row.id),
                    'tax_name': row.tax_name,
                    'tax_rate': float(row.tax_rate) if row.tax_rate else 0,
                    'is_default': row.is_default,
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
                        tax_rate_data['created_by_name'] = created_user.get_full_name()
                    else:
                        tax_rate_data['created_by_name'] = '未知用户'
                else:
                    tax_rate_data['created_by_name'] = '系统'
                    
                if row.updated_by:
                    updated_user = User.query.get(row.updated_by)
                    if updated_user:
                        tax_rate_data['updated_by_name'] = updated_user.get_full_name()
                    else:
                        tax_rate_data['updated_by_name'] = '未知用户'
                else:
                    tax_rate_data['updated_by_name'] = ''
                
                tax_rates.append(tax_rate_data)
            
            # 计算分页信息
            pages = (total + per_page - 1) // per_page
            has_next = page < pages
            has_prev = page > 1
            
            return {
                'tax_rates': tax_rates,
                'total': total,
                'pages': pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': has_next,
                'has_prev': has_prev
            }
            
        except Exception as e:
            current_app.logger.error(f"Error querying tax rates: {str(e)}")
            raise ValueError(f'查询税率失败: {str(e)}')

    def get_tax_rate(self, tax_rate_id):
        """获取税率详情"""
        try:
            tax_rate_uuid = uuid.UUID(tax_rate_id)
        except ValueError:
            raise ValueError('无效的税率ID')
        
        tax_rate = self.session.query(TaxRate).get(tax_rate_uuid)
        if not tax_rate:
            raise ValueError('税率不存在')
        
        tax_rate_data = tax_rate.to_dict()
        
        # 获取创建人和修改人用户名
        if tax_rate.created_by:
            created_user = self.session.query(User).get(tax_rate.created_by)
            tax_rate_data['created_by_name'] = created_user.get_full_name() if created_user else '未知用户'
        
        if tax_rate.updated_by:
            updated_user = self.session.query(User).get(tax_rate.updated_by)
            tax_rate_data['updated_by_name'] = updated_user.get_full_name() if updated_user else '未知用户'
        
        return tax_rate_data

    def create_tax_rate(self, data, created_by):
        """创建税率"""
        # 验证数据
        if not data.get('tax_name'):
            raise ValueError('税收名称不能为空')
        
        if data.get('tax_rate') is None:
            raise ValueError('税率不能为空')
        
        # 检查税收名称是否重复
        existing = self.session.query(TaxRate).filter_by(
            tax_name=data['tax_name']
        ).first()
        if existing:
            raise ValueError('税收名称已存在')
        
        try:
            created_by_uuid = uuid.UUID(created_by)
        except ValueError:
            raise ValueError('无效的创建用户ID')
        
        # 准备税率数据
        tax_rate_data = {
            'tax_name': data['tax_name'],
            'tax_rate': data['tax_rate'],
            'is_default': data.get('is_default', False),
            'description': data.get('description'),
            'sort_order': data.get('sort_order', 0),
            'is_enabled': data.get('is_enabled', True),
        }
        
        # 如果设置为默认，需要取消其他税率的默认标记
        if tax_rate_data['is_default']:
            self.session.query(TaxRate).filter_by(is_default=True).update({'is_default': False})
        
        try:
            # 使用继承的create_with_tenant方法
            tax_rate = self.create_with_tenant(TaxRate, **tax_rate_data)
            self.commit()
            return tax_rate.to_dict()
        except Exception as e:
            self.rollback()
            raise ValueError(f'创建税率失败: {str(e)}')

    def update_tax_rate(self, tax_rate_id, data, updated_by):
        """更新税率"""
        try:
            tax_rate_uuid = uuid.UUID(tax_rate_id)
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的ID')
        
        tax_rate = self.session.query(TaxRate).get(tax_rate_uuid)
        if not tax_rate:
            raise ValueError('税率不存在')
        
        # 检查税收名称是否重复（排除自己）
        if 'tax_name' in data and data['tax_name'] != tax_rate.tax_name:
            existing = self.session.query(TaxRate).filter(
                TaxRate.tax_name == data['tax_name'],
                TaxRate.id != tax_rate_uuid
            ).first()
            if existing:
                raise ValueError('税收名称已存在')
        
        # 更新字段
        for key, value in data.items():
            if hasattr(tax_rate, key):
                setattr(tax_rate, key, value)
        
        tax_rate.updated_by = updated_by_uuid
        
        # 如果设置为默认，需要取消其他税率的默认标记
        if tax_rate.is_default:
            self.session.query(TaxRate).filter(TaxRate.id != tax_rate.id).update({'is_default': False})
        
        try:
            self.commit()
            return tax_rate.to_dict()
        except Exception as e:
            self.rollback()
            raise ValueError(f'更新税率失败: {str(e)}')

    def delete_tax_rate(self, tax_rate_id):
        """删除税率"""
        try:
            tax_rate_uuid = uuid.UUID(tax_rate_id)
        except ValueError:
            raise ValueError('无效的税率ID')
        
        tax_rate = self.session.query(TaxRate).get(tax_rate_uuid)
        if not tax_rate:
            raise ValueError('税率不存在')
        
        try:
            self.session.delete(tax_rate)
            self.commit()
        except Exception as e:
            self.rollback()
            raise ValueError(f'删除税率失败: {str(e)}')

    def set_default_tax_rate(self, tax_rate_id, updated_by):
        """设置为默认税率"""
        try:
            tax_rate_uuid = uuid.UUID(tax_rate_id)
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的税率ID')
        
        tax_rate = self.session.query(TaxRate).get(tax_rate_uuid)
        if not tax_rate:
            raise ValueError('税率不存在')
        
        try:
            # 取消其他税率的默认标记
            self.session.query(TaxRate).filter(TaxRate.id != tax_rate.id).update({'is_default': False})
            
            # 设置当前税率为默认
            tax_rate.is_default = True
            tax_rate.updated_by = updated_by_uuid
            
            self.commit()
            return tax_rate.to_dict()
        except Exception as e:
            self.rollback()
            raise ValueError(f'设置默认税率失败: {str(e)}')

    def batch_update_tax_rates(self, data_list, updated_by):
        """批量更新税率（用于可编辑表格）"""
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
                    tax_rate = self.update_tax_rate(
                        data['id'], data, updated_by
                    )
                    results.append(tax_rate)
                else:
                    # 创建新记录
                    tax_rate = self.create_tax_rate(
                        data, updated_by
                    )
                    results.append(tax_rate)
            except ValueError as e:
                errors.append({
                    'index': index,
                    'error': str(e),
                    'data': data
                })
        
        if errors:
            # 如果有错误，回滚事务
            self.rollback()
            raise ValueError(f'批量更新失败，错误详情: {errors}')
        
        return results

    def get_enabled_tax_rates(self):
        """获取启用的税率列表（用于下拉选择）"""
        tax_rates = self.session.query(TaxRate).filter_by(
            is_enabled=True
        ).order_by(TaxRate.sort_order, TaxRate.tax_name).all()
        
        return [tax_rate.to_dict() for tax_rate in tax_rates]


def get_tax_rate_service(tenant_id: str = None, schema_name: str = None) -> TaxRateService:
    """获取税率服务实例"""
    return TaxRateService(tenant_id=tenant_id, schema_name=schema_name)

