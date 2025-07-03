# -*- coding: utf-8 -*-
"""
SettlementMethod管理服务
"""
from typing import Dict, List, Optional, Any
from sqlalchemy import and_
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

    def get_settlement_methods(self, page=1, per_page=20, search=None, enabled_only=False):
        """获取结算方式列表"""
        try:
            # 构建基础查询
            query = self.session.query(SettlementMethod)
        
            # 添加搜索条件
            if search:
                search_pattern = f'%{search}%'
                query = query.filter(
                    SettlementMethod.settlement_name.ilike(search_pattern) |
                    SettlementMethod.description.ilike(search_pattern)
                )
        
            if enabled_only:
                query = query.filter(SettlementMethod.is_enabled == True)
        
            # 排序
            query = query.order_by(SettlementMethod.sort_order, SettlementMethod.created_at)
            
            # 分页
            total = query.count()
            offset = (page - 1) * per_page
            settlement_methods_list = query.offset(offset).limit(per_page).all()
            
            settlement_methods = []
            for settlement_method in settlement_methods_list:
                settlement_method_data = settlement_method.to_dict()
                
                # 获取创建人和修改人用户名
                if settlement_method.created_by:
                    created_user = self.session.query(User).get(settlement_method.created_by)
                    if created_user:
                        settlement_method_data['created_by_name'] = created_user.get_full_name()
                    else:
                        settlement_method_data['created_by_name'] = '未知用户'
                else:
                    settlement_method_data['created_by_name'] = '系统'
                    
                if settlement_method.updated_by:
                    updated_user = self.session.query(User).get(settlement_method.updated_by)
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
            raise ValueError(f'查询结算方式失败: {str(e)}')

    def get_settlement_method(self, settlement_method_id):
        """获取结算方式详情"""
        try:
            settlement_method_uuid = uuid.UUID(settlement_method_id)
        except ValueError:
            raise ValueError('无效的结算方式ID')
        
        settlement_method = self.session.query(SettlementMethod).get(settlement_method_uuid)
        if not settlement_method:
            raise ValueError('结算方式不存在')
        
        settlement_method_data = settlement_method.to_dict()
        
        # 获取创建人和修改人用户名
        if settlement_method.created_by:
            created_user = self.session.query(User).get(settlement_method.created_by)
            if created_user:
                settlement_method_data['created_by_name'] = created_user.get_full_name()
            else:
                settlement_method_data['created_by_name'] = '未知用户'
        
        if settlement_method.updated_by:
            updated_user = self.session.query(User).get(settlement_method.updated_by)
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
        
        # 检查结算方式名称是否重复
        existing = self.session.query(SettlementMethod).filter_by(
            settlement_name=data['settlement_name']
        ).first()
        if existing:
            raise ValueError('结算方式名称已存在')
        
        try:
            created_by_uuid = uuid.UUID(created_by)
        except ValueError:
            raise ValueError('无效的创建用户ID')
        
        # 准备数据
        settlement_method_data = {
            'settlement_name': data['settlement_name'],
            'description': data.get('description'),
            'sort_order': data.get('sort_order', 0),
            'is_enabled': data.get('is_enabled', True),
        }
        
        try:
            settlement_method = self.create_with_tenant(SettlementMethod, **settlement_method_data)
            self.commit()
            return settlement_method.to_dict()
        except Exception as e:
            self.rollback()
            raise ValueError(f'创建结算方式失败: {str(e)}')

    def update_settlement_method(self, settlement_method_id, data, updated_by):
        """更新结算方式"""
        try:
            settlement_method_uuid = uuid.UUID(settlement_method_id)
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的ID')
        
        settlement_method = self.session.query(SettlementMethod).get(settlement_method_uuid)
        if not settlement_method:
            raise ValueError('结算方式不存在')
        
        # 检查结算方式名称是否重复（排除自己）
        if 'settlement_name' in data and data['settlement_name'] != settlement_method.settlement_name:
            existing = self.session.query(SettlementMethod).filter(
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
            self.commit()
            return settlement_method.to_dict()
        except Exception as e:
            self.rollback()
            raise ValueError(f'更新结算方式失败: {str(e)}')

    def delete_settlement_method(self, settlement_method_id):
        """删除结算方式"""
        try:
            settlement_method_uuid = uuid.UUID(settlement_method_id)
        except ValueError:
            raise ValueError('无效的结算方式ID')
        
        settlement_method = self.session.query(SettlementMethod).get(settlement_method_uuid)
        if not settlement_method:
            raise ValueError('结算方式不存在')
        
        try:
            self.session.delete(settlement_method)
            self.commit()
        except Exception as e:
            self.rollback()
            raise ValueError(f'删除结算方式失败: {str(e)}')

    def batch_update_settlement_methods(self, data_list, updated_by):
        """批量更新结算方式"""
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
                    result = self.update_settlement_method(data['id'], data, updated_by)
                else:
                    # 创建新记录
                    result = self.create_settlement_method(data, updated_by)
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

    def get_enabled_settlement_methods(self):
        """获取启用的结算方式列表"""
        try:
            settlement_methods = self.session.query(SettlementMethod).filter_by(
                is_enabled=True
            ).order_by(SettlementMethod.sort_order, SettlementMethod.created_at).all()
            
            return [sm.to_dict() for sm in settlement_methods]
        except Exception as e:
            raise ValueError(f'获取启用结算方式失败: {str(e)}')


def get_settlement_method_service(tenant_id: Optional[str] = None, schema_name: Optional[str] = None) -> SettlementMethodService:
    """获取结算方式服务实例"""
    return SettlementMethodService(tenant_id=tenant_id, schema_name=schema_name)

