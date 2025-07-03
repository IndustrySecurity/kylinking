# -*- coding: utf-8 -*-
"""
Currency管理服务
"""
from typing import Dict, List, Optional, Any
from sqlalchemy.exc import SQLAlchemyError
import uuid

from app.services.base_service import TenantAwareService
from app.models.basic_data import Currency
from app.models.user import User


class CurrencyService(TenantAwareService):
    """币别管理服务"""

    def __init__(self, tenant_id: Optional[str] = None, schema_name: Optional[str] = None):
        """初始化Currency服务"""
        super().__init__(tenant_id, schema_name)

    def get_currencies(self, page=1, per_page=20, search=None, enabled_only=False):
        """获取币别列表"""
        try:
            # 构建基础查询
            query = self.session.query(Currency)
            
            # 添加搜索条件
            if search:
                search_pattern = f'%{search}%'
                query = query.filter(
                    Currency.currency_code.ilike(search_pattern) |
                    Currency.currency_name.ilike(search_pattern) |
                    Currency.description.ilike(search_pattern)
                )
            
            if enabled_only:
                query = query.filter(Currency.is_enabled == True)
            
            # 排序
            query = query.order_by(Currency.sort_order, Currency.created_at)
            
            # 分页
            total = query.count()
            offset = (page - 1) * per_page
            currencies_list = query.offset(offset).limit(per_page).all()
            
            currencies = []
            for currency in currencies_list:
                currency_data = currency.to_dict()
                
                # 获取创建人和修改人用户名
                if currency.created_by:
                    created_user = self.session.query(User).get(currency.created_by)
                    if created_user:
                        currency_data['created_by_name'] = created_user.get_full_name()
                    else:
                        currency_data['created_by_name'] = '未知用户'
                else:
                    currency_data['created_by_name'] = '系统'
                    
                if currency.updated_by:
                    updated_user = self.session.query(User).get(currency.updated_by)
                    if updated_user:
                        currency_data['updated_by_name'] = updated_user.get_full_name()
                    else:
                        currency_data['updated_by_name'] = '未知用户'
                else:
                    currency_data['updated_by_name'] = ''
                
                currencies.append(currency_data)
            
            # 计算分页信息
            pages = (total + per_page - 1) // per_page
            has_next = page < pages
            has_prev = page > 1
            
            return {
                'currencies': currencies,
                'total': total,
                'pages': pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': has_next,
                'has_prev': has_prev
            }
            
        except Exception as e:
            raise ValueError(f'查询币别失败: {str(e)}')

    def get_currency(self, currency_id):
        """获取币别详情"""
        try:
            currency_uuid = uuid.UUID(currency_id)
        except ValueError:
            raise ValueError('无效的币别ID')
        
        currency = self.session.query(Currency).get(currency_uuid)
        if not currency:
            raise ValueError('币别不存在')
        
        currency_data = currency.to_dict()
        
        # 获取创建人和修改人用户名
        if currency.created_by:
            created_user = self.session.query(User).get(currency.created_by)
            currency_data['created_by_name'] = created_user.get_full_name() if created_user else '未知用户'
        
        if currency.updated_by:
            updated_user = self.session.query(User).get(currency.updated_by)
            currency_data['updated_by_name'] = updated_user.get_full_name() if updated_user else '未知用户'
        
        return currency_data

    def create_currency(self, data, created_by):
        """创建币别"""
        # 验证数据
        if not data.get('currency_code'):
            raise ValueError('币别代码不能为空')
        
        if not data.get('currency_name'):
            raise ValueError('币别名称不能为空')
        
        if not data.get('exchange_rate'):
            raise ValueError('汇率不能为空')
        
        # 检查币别代码是否重复
        existing = self.session.query(Currency).filter_by(
            currency_code=data['currency_code']
        ).first()
        if existing:
            raise ValueError('币别代码已存在')
        
        try:
            created_by_uuid = uuid.UUID(created_by)
        except ValueError:
            raise ValueError('无效的创建用户ID')
        
        # 准备币别数据
        currency_data = {
            'currency_code': data['currency_code'],
            'currency_name': data['currency_name'],
            'exchange_rate': data['exchange_rate'],
            'is_base_currency': data.get('is_base_currency', False),
            'description': data.get('description'),
            'sort_order': data.get('sort_order', 0),
            'is_enabled': data.get('is_enabled', True),
        }
        
        # 如果设置为本位币，需要取消其他币别的本位币标记
        if currency_data['is_base_currency']:
            self.session.query(Currency).filter_by(is_base_currency=True).update({'is_base_currency': False})
        
        try:
            # 使用继承的create_with_tenant方法
            currency = self.create_with_tenant(Currency, **currency_data)
            self.commit()
            return currency.to_dict()
        except Exception as e:
            self.rollback()
            raise ValueError(f'创建币别失败: {str(e)}')

    def update_currency(self, currency_id, data, updated_by):
        """更新币别"""
        try:
            currency_uuid = uuid.UUID(currency_id)
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的ID')
        
        currency = self.session.query(Currency).get(currency_uuid)
        if not currency:
            raise ValueError('币别不存在')
        
        # 检查币别代码是否重复（排除自己）
        if 'currency_code' in data and data['currency_code'] != currency.currency_code:
            existing = self.session.query(Currency).filter(
                Currency.currency_code == data['currency_code'],
                Currency.id != currency_uuid
            ).first()
            if existing:
                raise ValueError('币别代码已存在')
        
        # 更新字段
        for key, value in data.items():
            if hasattr(currency, key):
                setattr(currency, key, value)
        
        currency.updated_by = updated_by_uuid
        
        # 如果设置为本位币，需要取消其他币别的本位币标记
        if currency.is_base_currency:
            self.session.query(Currency).filter(Currency.id != currency.id).update({'is_base_currency': False})
        
        try:
            self.commit()
            return currency.to_dict()
        except Exception as e:
            self.rollback()
            raise ValueError(f'更新币别失败: {str(e)}')

    def delete_currency(self, currency_id):
        """删除币别"""
        try:
            currency_uuid = uuid.UUID(currency_id)
        except ValueError:
            raise ValueError('无效的币别ID')
        
        currency = self.session.query(Currency).get(currency_uuid)
        if not currency:
            raise ValueError('币别不存在')
        
        # 检查是否为本位币（本位币不允许删除）
        if currency.is_base_currency:
            raise ValueError('本位币不允许删除')
        
        try:
            self.session.delete(currency)
            self.commit()
        except Exception as e:
            self.rollback()
            raise ValueError(f'删除币别失败: {str(e)}')

    def set_base_currency(self, currency_id, updated_by):
        """设置为本位币"""
        try:
            currency_uuid = uuid.UUID(currency_id)
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的币别ID')
        
        currency = self.session.query(Currency).get(currency_uuid)
        if not currency:
            raise ValueError('币别不存在')
        
        try:
            # 取消其他币别的本位币标记
            self.session.query(Currency).filter(Currency.id != currency.id).update({'is_base_currency': False})
            
            # 设置当前币别为本位币
            currency.is_base_currency = True
            currency.updated_by = updated_by_uuid
            
            self.commit()
            return currency.to_dict()
        except Exception as e:
            self.rollback()
            raise ValueError(f'设置本位币失败: {str(e)}')

    def batch_update_currencies(self, data_list, updated_by):
        """批量更新币别（用于可编辑表格）"""
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
                    currency = self.update_currency(
                        data['id'], data, updated_by
                    )
                    results.append(currency)
                else:
                    # 创建新记录
                    currency = self.create_currency(
                        data, updated_by
                    )
                    results.append(currency)
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

    def get_enabled_currencies(self):
        """获取启用的币别列表（用于下拉选择）"""
        try:
            currencies = self.session.query(Currency).filter_by(
                is_enabled=True
            ).order_by(Currency.sort_order, Currency.currency_name).all()
            
            return [currency.to_dict() for currency in currencies]
        except Exception as e:
            raise ValueError(f'获取启用币别失败: {str(e)}')


def get_currency_service(tenant_id: Optional[str] = None, schema_name: Optional[str] = None) -> CurrencyService:
    """获取币别服务实例"""
    return CurrencyService(tenant_id=tenant_id, schema_name=schema_name)

