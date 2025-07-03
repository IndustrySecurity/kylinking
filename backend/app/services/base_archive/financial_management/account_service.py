# -*- coding: utf-8 -*-
"""
Account管理服务
"""
from typing import Dict, List, Optional, Any
from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import uuid

from app.services.base_service import TenantAwareService
from app.models.basic_data import AccountManagement, Currency
from app.models.user import User


class AccountService(TenantAwareService):
    """账户管理服务类"""

    def __init__(self, tenant_id: Optional[str] = None, schema_name: Optional[str] = None):
        """初始化Account服务"""
        super().__init__(tenant_id, schema_name)

    def get_accounts(self, page=1, per_page=20, search=None, enabled_only=False):
        """获取账户列表"""
        try:
            # 构建基础查询，包含关联的币别信息
            query = self.session.query(AccountManagement, Currency).outerjoin(
                Currency, AccountManagement.currency_id == Currency.id
            )
            
            # 添加搜索条件
            if search:
                search_pattern = f'%{search}%'
                query = query.filter(
                    AccountManagement.account_name.ilike(search_pattern) |
                    AccountManagement.account_type.ilike(search_pattern) |
                    AccountManagement.bank_name.ilike(search_pattern) |
                    AccountManagement.bank_account.ilike(search_pattern) |
                    AccountManagement.description.ilike(search_pattern)
                )
        
            if enabled_only:
                query = query.filter(AccountManagement.is_enabled == True)
        
            # 排序
            query = query.order_by(AccountManagement.sort_order, AccountManagement.created_at)
        
            # 分页
            total = query.count()
            offset = (page - 1) * per_page
            results = query.offset(offset).limit(per_page).all()
            
            accounts = []
            for account, currency in results:
                account_data = account.to_dict()
                
                # 添加币别信息
                if currency:
                    account_data['currency_name'] = currency.currency_name
                    account_data['currency_code'] = currency.currency_code
                else:
                    account_data['currency_name'] = None
                    account_data['currency_code'] = None
                
                # 获取创建人和修改人用户名
                if account.created_by:
                    created_user = self.session.query(User).get(account.created_by)
                    if created_user:
                        account_data['created_by_name'] = created_user.get_full_name()
                    else:
                        account_data['created_by_name'] = '未知用户'
                else:
                    account_data['created_by_name'] = '系统'
                    
                if account.updated_by:
                    updated_user = self.session.query(User).get(account.updated_by)
                    if updated_user:
                        account_data['updated_by_name'] = updated_user.get_full_name()
                    else:
                        account_data['updated_by_name'] = '未知用户'
                else:
                    account_data['updated_by_name'] = ''
                
                accounts.append(account_data)
            
            # 计算分页信息
            pages = (total + per_page - 1) // per_page
            has_next = page < pages
            has_prev = page > 1
            
            return {
                'accounts': accounts,
                'total': total,
                'pages': pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': has_next,
                'has_prev': has_prev
            }
            
        except Exception as e:
            raise ValueError(f'查询账户失败: {str(e)}')

    def get_account(self, account_id):
        """获取账户详情"""
        try:
            account_uuid = uuid.UUID(account_id)
        except ValueError:
            raise ValueError('无效的账户ID')
        
        account = self.session.query(AccountManagement).get(account_uuid)
        if not account:
            raise ValueError('账户不存在')
        
        account_data = account.to_dict()
        
        # 获取创建人和修改人用户名
        if account.created_by:
            created_user = self.session.query(User).get(account.created_by)
            if created_user:
                account_data['created_by_name'] = created_user.get_full_name()
            else:
                account_data['created_by_name'] = '未知用户'
        
        if account.updated_by:
            updated_user = self.session.query(User).get(account.updated_by)
            if updated_user:
                account_data['updated_by_name'] = updated_user.get_full_name()
            else:
                account_data['updated_by_name'] = '未知用户'
        
        return account_data

    def create_account(self, data, created_by):
        """创建账户"""
        # 验证数据
        if not data.get('account_name'):
            raise ValueError('账户名称不能为空')
        
        if not data.get('account_type'):
            raise ValueError('账户类型不能为空')
        
        # 检查账户名称是否重复
        existing = self.session.query(AccountManagement).filter_by(
            account_name=data['account_name']
        ).first()
        if existing:
            raise ValueError('账户名称已存在')
        
        try:
            created_by_uuid = uuid.UUID(created_by)
        except ValueError:
            raise ValueError('无效的创建用户ID')
        
        # 处理币别ID
        currency_id = None
        if data.get('currency_id'):
            try:
                currency_id = uuid.UUID(data['currency_id'])
            except ValueError:
                raise ValueError('无效的币别ID')
        
        # 处理开户日期
        opening_date = None
        if data.get('opening_date'):
            try:
                opening_date = datetime.fromisoformat(data['opening_date'].replace('Z', '+00:00')).date()
            except ValueError:
                raise ValueError('无效的开户日期格式')
        
        # 准备账户数据
        account_data = {
            'account_name': data['account_name'],
            'account_type': data['account_type'],
            'currency_id': currency_id,
            'bank_name': data.get('bank_name'),
            'bank_account': data.get('bank_account'),
            'opening_date': opening_date,
            'opening_address': data.get('opening_address'),
            'description': data.get('description'),
            'sort_order': data.get('sort_order', 0),
            'is_enabled': data.get('is_enabled', True),
        }
        
        try:
            account = self.create_with_tenant(AccountManagement, **account_data)
            self.commit()
            return account.to_dict()
        except Exception as e:
            self.rollback()
            raise ValueError(f'创建账户失败: {str(e)}')

    def update_account(self, account_id, data, updated_by):
        """更新账户"""
        try:
            account_uuid = uuid.UUID(account_id)
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的ID')
        
        account = self.session.query(AccountManagement).get(account_uuid)
        if not account:
            raise ValueError('账户不存在')
        
        # 检查账户名称是否重复（排除自己）
        if 'account_name' in data and data['account_name'] != account.account_name:
            existing = self.session.query(AccountManagement).filter(
                and_(
                    AccountManagement.account_name == data['account_name'],
                    AccountManagement.id != account_uuid
                )
            ).first()
            if existing:
                raise ValueError('账户名称已存在')
        
        # 更新字段
        if 'account_name' in data:
            account.account_name = data['account_name']
        if 'account_type' in data:
            account.account_type = data['account_type']
        if 'currency_id' in data:
            if data['currency_id']:
                try:
                    account.currency_id = uuid.UUID(data['currency_id'])
                except ValueError:
                    raise ValueError('无效的币别ID')
            else:
                account.currency_id = None
        if 'bank_name' in data:
            account.bank_name = data['bank_name']
        if 'bank_account' in data:
            account.bank_account = data['bank_account']
        if 'opening_date' in data:
            if data['opening_date']:
                try:
                    account.opening_date = datetime.fromisoformat(data['opening_date'].replace('Z', '+00:00')).date()
                except ValueError:
                    raise ValueError('无效的开户日期格式')
            else:
                account.opening_date = None
        if 'opening_address' in data:
            account.opening_address = data['opening_address']
        if 'description' in data:
            account.description = data['description']
        if 'sort_order' in data:
            account.sort_order = data['sort_order']
        if 'is_enabled' in data:
            account.is_enabled = data['is_enabled']
        
        account.updated_by = updated_by_uuid
        
        try:
            self.commit()
            return account.to_dict()
        except Exception as e:
            self.rollback()
            raise ValueError(f'更新账户失败: {str(e)}')

    def delete_account(self, account_id):
        """删除账户"""
        try:
            account_uuid = uuid.UUID(account_id)
        except ValueError:
            raise ValueError('无效的账户ID')
        
        account = self.session.query(AccountManagement).get(account_uuid)
        if not account:
            raise ValueError('账户不存在')
        
        try:
            self.session.delete(account)
            self.commit()
        except Exception as e:
            self.rollback()
            raise ValueError(f'删除账户失败: {str(e)}')

    def batch_update_accounts(self, data_list, updated_by):
        """批量更新账户"""
        try:
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的更新用户ID')
        
        results = []
        errors = []
        
        for index, data in enumerate(data_list):
            try:
                if data.get('id') and not data['id'].startswith('temp_'):
                    # 更新现有记录
                    result = self.update_account(data['id'], data, updated_by)
                else:
                    # 创建新记录
                    result = self.create_account(data, updated_by)
                results.append(result)
            except Exception as e:
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

    def get_enabled_accounts(self):
        """获取启用的账户列表"""
        accounts = self.session.query(AccountManagement).filter_by(
            is_enabled=True
        ).order_by(AccountManagement.sort_order, AccountManagement.created_at).all()
        
        return [account.to_dict() for account in accounts]


def get_account_service(tenant_id: Optional[str] = None, schema_name: Optional[str] = None) -> AccountService:
    """获取账户服务实例"""
    return AccountService(tenant_id=tenant_id, schema_name=schema_name)

