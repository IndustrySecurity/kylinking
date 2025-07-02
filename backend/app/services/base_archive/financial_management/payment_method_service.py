# -*- coding: utf-8 -*-
"""
PaymentMethod管理服务
"""
from typing import Dict, List, Optional, Any
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import uuid

from app.services.base_service import TenantAwareService
from app.models.basic_data import PaymentMethod
from app.models.user import User


class PaymentMethodService(TenantAwareService):
    """付款方式管理服务"""

    def __init__(self, tenant_id: Optional[str] = None, schema_name: Optional[str] = None):
        """初始化PaymentMethod服务"""
        super().__init__(tenant_id, schema_name)

        if schema_name != 'public':
            pass

    def get_payment_methods(self, page=1, per_page=20, search=None, enabled_only=False):
        """获取付款方式列表"""
        
        # 获取当前schema名称
        from flask import g, current_app
        schema_name = getattr(g, 'schema_name', current_app.config.get('DEFAULT_SCHEMA', 'public'))
        
        # 构建基础查询
        base_query = f"""
        SELECT 
            id, payment_name, cash_on_delivery, monthly_settlement, next_month_settlement,
            cash_on_delivery_days, monthly_settlement_days, monthly_reconciliation_day,
            next_month_settlement_count, monthly_payment_day, description, sort_order, 
            is_enabled, created_by, updated_by, created_at, updated_at
        FROM {schema_name}.payment_methods
        """
        
        # 添加搜索条件
        where_conditions = []
        params = {}
        
        if search:
            where_conditions.append("""
                (payment_name ILIKE :search OR 
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
        FROM {schema_name}.payment_methods
        """
        if where_conditions:
            count_query += " WHERE " + " AND ".join(where_conditions)
        
        # 执行查询
        try:
            # 获取总数
            count_result = self.get_session().execute(text(count_query), params)
            total = count_result.scalar()
            
            # 添加分页
            offset = (page - 1) * per_page
            base_query += f" LIMIT {per_page} OFFSET {offset}"
            
            # 获取数据
            result = self.get_session().execute(text(base_query), params)
            payment_methods = []
            
            for row in result:
                payment_method_dict = {
                    'id': str(row.id),
                    'payment_name': row.payment_name,
                    'cash_on_delivery': row.cash_on_delivery,
                    'monthly_settlement': row.monthly_settlement,
                    'next_month_settlement': row.next_month_settlement,
                    'cash_on_delivery_days': row.cash_on_delivery_days,
                    'monthly_settlement_days': row.monthly_settlement_days,
                    'monthly_reconciliation_day': row.monthly_reconciliation_day,
                    'next_month_settlement_count': row.next_month_settlement_count,
                    'monthly_payment_day': row.monthly_payment_day,
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
                        payment_method_dict['created_by_name'] = created_user.get_full_name()
                    else:
                        payment_method_dict['created_by_name'] = '未知用户'
                else:
                    payment_method_dict['created_by_name'] = '系统'
                    
                if row.updated_by:
                    updated_user = User.query.get(row.updated_by)
                    if updated_user:
                        payment_method_dict['updated_by_name'] = updated_user.get_full_name()
                    else:
                        payment_method_dict['updated_by_name'] = '未知用户'
                else:
                    payment_method_dict['updated_by_name'] = ''
                
                payment_methods.append(payment_method_dict)
            
            return {
                'payment_methods': payment_methods,
                'total': total,
                'current_page': page,
                'per_page': per_page,
                'total_pages': (total + per_page - 1) // per_page
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting payment methods: {str(e)}")
            raise ValueError(f'获取付款方式列表失败: {str(e)}')
    def get_payment_method(self, payment_method_id):
        """获取单个付款方式"""
        
        try:
            payment_method_uuid = uuid.UUID(payment_method_id)
        except ValueError:
            raise ValueError('无效的付款方式ID')
        
        from app.models.basic_data import PaymentMethod
        payment_method = PaymentMethod.query.get(payment_method_uuid)
        if not payment_method:
            raise ValueError('付款方式不存在')
        
        payment_method_data = payment_method.to_dict()
        
        # 获取创建人和修改人用户名
        if payment_method.created_by:
            created_user = User.query.get(payment_method.created_by)
            if created_user:
                payment_method_data['created_by_name'] = created_user.get_full_name()
            else:
                payment_method_data['created_by_name'] = '未知用户'
        else:
            payment_method_data['created_by_name'] = '系统'
        
        if payment_method.updated_by:
            updated_user = User.query.get(payment_method.updated_by)
            if updated_user:
                payment_method_data['updated_by_name'] = updated_user.get_full_name()
            else:
                payment_method_data['updated_by_name'] = '未知用户'
        else:
            payment_method_data['updated_by_name'] = ''
        
        return payment_method_data
    def create_payment_method(self, data, created_by):
        """创建付款方式"""
        
        # 验证数据
        if not data.get('payment_name'):
            raise ValueError('付款方式名称不能为空')
        
        # 验证付款方式类型：必须选择一个且只能选择一个
        payment_types = [
            data.get('cash_on_delivery', False),
            data.get('monthly_settlement', False),
            data.get('next_month_settlement', False)
        ]
        selected_count = sum(payment_types)
        
        if selected_count == 0:
            raise ValueError('请选择一种付款方式类型（货到付款、月结或次月结）')
        
        if selected_count > 1:
            raise ValueError('只能选择一种付款方式类型')
        
        from app.models.basic_data import PaymentMethod
        
        # 检查付款方式名称是否重复
        existing = PaymentMethod.query.filter_by(
            payment_name=data['payment_name']
        ).first()
        if existing:
            raise ValueError('付款方式名称已存在')
        
        try:
            created_by_uuid = uuid.UUID(created_by)
        except ValueError:
            raise ValueError('无效的创建用户ID')
        
        # 创建付款方式
        payment_method = PaymentMethod(
            payment_name=data['payment_name'],
            cash_on_delivery=data.get('cash_on_delivery', False),
            monthly_settlement=data.get('monthly_settlement', False),
            next_month_settlement=data.get('next_month_settlement', False),
            cash_on_delivery_days=data.get('cash_on_delivery_days', 0),
            monthly_settlement_days=data.get('monthly_settlement_days', 0),
            monthly_reconciliation_day=data.get('monthly_reconciliation_day', 0),
            next_month_settlement_count=data.get('next_month_settlement_count', 0),
            monthly_payment_day=data.get('monthly_payment_day', 0),
            description=data.get('description'),
            sort_order=data.get('sort_order', 0),
            is_enabled=data.get('is_enabled', True),
            created_by=created_by_uuid
        )
        
        try:
            self.get_session().add(payment_method)
            self.get_session().commit()
            return payment_method.to_dict()
        except Exception as e:
            self.get_session().rollback()
            raise ValueError(f'创建付款方式失败: {str(e)}')
    def update_payment_method(self, payment_method_id, data, updated_by):
        """更新付款方式"""
        
        try:
            payment_method_uuid = uuid.UUID(payment_method_id)
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的ID')
        
        from app.models.basic_data import PaymentMethod
        payment_method = PaymentMethod.query.get(payment_method_uuid)
        if not payment_method:
            raise ValueError('付款方式不存在')
        
        # 验证付款方式类型：必须选择一个且只能选择一个
        # 获取当前值或使用传入的新值
        cash_on_delivery = data.get('cash_on_delivery', payment_method.cash_on_delivery)
        monthly_settlement = data.get('monthly_settlement', payment_method.monthly_settlement)
        next_month_settlement = data.get('next_month_settlement', payment_method.next_month_settlement)
        
        payment_types = [cash_on_delivery, monthly_settlement, next_month_settlement]
        selected_count = sum(payment_types)
        
        if selected_count == 0:
            raise ValueError('请选择一种付款方式类型（货到付款、月结或次月结）')
        
        if selected_count > 1:
            raise ValueError('只能选择一种付款方式类型')
        
        # 检查付款方式名称是否重复（排除自己）
        if 'payment_name' in data and data['payment_name'] != payment_method.payment_name:
            existing = PaymentMethod.query.filter(
                PaymentMethod.payment_name == data['payment_name'],
                PaymentMethod.id != payment_method_uuid
            ).first()
            if existing:
                raise ValueError('付款方式名称已存在')
        
        # 更新字段
        for key, value in data.items():
            if hasattr(payment_method, key):
                setattr(payment_method, key, value)
        
        payment_method.updated_by = updated_by_uuid
        
        try:
            self.get_session().commit()
            return payment_method.to_dict()
        except Exception as e:
            self.get_session().rollback()
            raise ValueError(f'更新付款方式失败: {str(e)}')
    def delete_payment_method(self, payment_method_id):
        """删除付款方式"""
        
        try:
            payment_method_uuid = uuid.UUID(payment_method_id)
        except ValueError:
            raise ValueError('无效的付款方式ID')
        
        from app.models.basic_data import PaymentMethod
        payment_method = PaymentMethod.query.get(payment_method_uuid)
        if not payment_method:
            raise ValueError('付款方式不存在')
        
        try:
            self.get_session().delete(payment_method)
            self.get_session().commit()
        except Exception as e:
            self.get_session().rollback()
            raise ValueError(f'删除付款方式失败: {str(e)}')
    def batch_update_payment_methods(self, data_list, updated_by):
        """批量更新付款方式"""
        
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
                    payment_method = PaymentMethodService().update_payment_method(
                        data['id'], data, updated_by
                    )
                    results.append(payment_method)
                else:
                    # 创建新记录
                    payment_method = PaymentMethodService().create_payment_method(
                        data, updated_by
                    )
                    results.append(payment_method)
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
    def get_enabled_payment_methods(self):
        """获取启用的付款方式列表（用于下拉选择）"""
        
        from app.models.basic_data import PaymentMethod
        payment_methods = PaymentMethod.query.filter_by(
            is_enabled=True
        ).order_by(PaymentMethod.sort_order, PaymentMethod.payment_name).all()
        
        return [payment_method.to_dict() for payment_method in payment_methods]

