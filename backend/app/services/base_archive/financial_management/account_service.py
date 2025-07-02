# -*- coding: utf-8 -*-
"""
Account管理服务
"""
from typing import Dict, List, Optional, Any
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import uuid

from app.services.base_service import TenantAwareService
from app.models.basic_data import AccountManagement
from app.models.user import User


class AccountService(TenantAwareService):
    """账户管理服务类"""

    def __init__(self, tenant_id: Optional[str] = None, schema_name: Optional[str] = None):
        """初始化Account服务"""
        super().__init__(tenant_id, schema_name)

        if schema_name != 'public':
            pass

    def get_accounts(self, page=1, per_page=20, search=None, enabled_only=False):
        """获取账户列表"""
        
        # 获取当前schema名称
        from flask import g, current_app
        schema_name = getattr(g, 'schema_name', current_app.config.get('DEFAULT_SCHEMA', 'public'))
        
        # 构建基础查询
        base_query = f"""
        SELECT 
            a.id, a.account_name, a.account_type, a.currency_id, a.bank_name, 
            a.bank_account, a.opening_date, a.opening_address, a.description, 
            a.sort_order, a.is_enabled, a.created_by, a.updated_by, 
            a.created_at, a.updated_at,
            c.currency_name, c.currency_code
        FROM {schema_name}.account_management a
        LEFT JOIN {schema_name}.currencies c ON a.currency_id = c.id
        """
        
        # 构建查询条件
        where_conditions = []
        params = {}
        
        if search:
            where_conditions.append("""
                (a.account_name ILIKE :search OR 
                 a.account_type ILIKE :search OR
                 a.bank_name ILIKE :search OR
                 a.bank_account ILIKE :search OR
                 a.description ILIKE :search)
            """)
            params['search'] = f'%{search}%'
        
        if enabled_only:
            where_conditions.append("a.is_enabled = true")
        
        # 构建完整查询
        if where_conditions:
            base_query += " WHERE " + " AND ".join(where_conditions)
        
        base_query += " ORDER BY a.sort_order, a.created_at"
        
        # 计算总数
        count_query = f"""
        SELECT COUNT(*) as total
        FROM {schema_name}.account_management a
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
            
            accounts = []
            for row in rows:
                account_data = {
                    'id': str(row.id),
                    'account_name': row.account_name,
                    'account_type': row.account_type,
                    'currency_id': str(row.currency_id) if row.currency_id else None,
                    'currency_name': row.currency_name,
                    'currency_code': row.currency_code,
                    'bank_name': row.bank_name,
                    'bank_account': row.bank_account,
                    'opening_date': row.opening_date.isoformat() if row.opening_date else None,
                    'opening_address': row.opening_address,
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
                        account_data['created_by_name'] = created_user.get_full_name()
                    else:
                        account_data['created_by_name'] = '未知用户'
                else:
                    account_data['created_by_name'] = '系统'
                    
                if row.updated_by:
                    updated_user = User.query.get(row.updated_by)
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
            current_app.logger.error(f"Error querying accounts: {str(e)}")
            raise ValueError(f'查询账户失败: {str(e)}')
    def get_account(self, account_id):
        """获取账户详情"""
        
        try:
            account_uuid = uuid.UUID(account_id)
        except ValueError:
            raise ValueError('无效的账户ID')
        
        from app.models.basic_data import AccountManagement
        account = AccountManagement.query.get(account_uuid)
        if not account:
            raise ValueError('账户不存在')
        
        account_data = account.to_dict()
        
        # 获取创建人和修改人用户名
        if account.created_by:
            created_user = User.query.get(account.created_by)
            if created_user:
                account_data['created_by_name'] = created_user.get_full_name()
            else:
                account_data['created_by_name'] = '未知用户'
        
        if account.updated_by:
            updated_user = User.query.get(account.updated_by)
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
        
        from app.models.basic_data import AccountManagement
        
        # 获取当前schema名称
        from flask import g, current_app
        schema_name = getattr(g, 'schema_name', current_app.config.get('DEFAULT_SCHEMA', 'public'))
        
        # 检查账户名称是否重复
        check_query = f"""
        SELECT COUNT(*) as count
        FROM {schema_name}.account_management
        WHERE account_name = :account_name
        """
        result = self.get_session().execute(text(check_query), {'account_name': data['account_name']})
        if result.scalar() > 0:
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
            from datetime import datetime
            try:
                opening_date = datetime.fromisoformat(data['opening_date'].replace('Z', '+00:00')).date()
            except ValueError:
                raise ValueError('无效的开户日期格式')
        
        # 创建账户
        account = AccountManagement(
            account_name=data['account_name'],
            account_type=data['account_type'],
            currency_id=currency_id,
            bank_name=data.get('bank_name'),
            bank_account=data.get('bank_account'),
            opening_date=opening_date,
            opening_address=data.get('opening_address'),
            description=data.get('description'),
            sort_order=data.get('sort_order', 0),
            is_enabled=data.get('is_enabled', True),
            created_by=created_by_uuid
        )
        
        try:
            self.get_session().add(account)
            self.get_session().commit()
            return account.to_dict()
        except Exception as e:
            self.get_session().rollback()
            raise ValueError(f'创建账户失败: {str(e)}')
    def update_account(self, account_id, data, updated_by):
        """更新账户"""
        
        try:
            account_uuid = uuid.UUID(account_id)
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的ID')
        
        from app.models.basic_data import AccountManagement
        account = AccountManagement.query.get(account_uuid)
        if not account:
            raise ValueError('账户不存在')
        
        # 检查账户名称是否重复（排除自己）
        if 'account_name' in data and data['account_name'] != account.account_name:
            existing = AccountManagement.query.filter(
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
                from datetime import datetime
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
            self.get_session().commit()
            return account.to_dict()
        except Exception as e:
            self.get_session().rollback()
            raise ValueError(f'更新账户失败: {str(e)}')
    def delete_account(self, account_id):
        """删除账户"""
        
        try:
            account_uuid = uuid.UUID(account_id)
        except ValueError:
            raise ValueError('无效的账户ID')
        
        from app.models.basic_data import AccountManagement
        account = AccountManagement.query.get(account_uuid)
        if not account:
            raise ValueError('账户不存在')
        
        try:
            self.get_session().delete(account)
            self.get_session().commit()
        except Exception as e:
            self.get_session().rollback()
            raise ValueError(f'删除账户失败: {str(e)}')
    def batch_update_accounts(self, data_list, updated_by):
        """批量更新账户"""
        
        try:
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的更新用户ID')
        
        results = []
        
        for data in data_list:
            try:
                if data.get('id') and not data['id'].startswith('temp_'):
                    # 更新现有记录
                    result = AccountManagementService().update_account(data['id'], data, updated_by)
                else:
                    # 创建新记录
                    result = AccountManagementService().create_account(data, updated_by)
                results.append(result)
            except Exception as e:
                current_app.logger.error(f"Error processing account {data.get('id', 'new')}: {str(e)}")
                continue
        
        return results
    def get_enabled_accounts(self):
        """获取启用的账户列表"""
        
        from app.models.basic_data import AccountManagement
        accounts = AccountManagement.query.filter_by(is_enabled=True).order_by(AccountManagement.sort_order, AccountManagement.created_at).all()
        return [account.to_dict() for account in accounts]


def get_account_service(tenant_id: str = None, schema_name: str = None) -> AccountService:
    """获取账户服务实例"""
    return AccountService(tenant_id=tenant_id, schema_name=schema_name)

