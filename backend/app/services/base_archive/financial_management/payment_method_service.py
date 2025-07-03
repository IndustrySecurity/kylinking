# -*- coding: utf-8 -*-
"""
PaymentMethod管理服务
"""
from typing import Dict, List, Optional, Any
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

    def get_payment_methods(self, page=1, per_page=20, search=None, enabled_only=False):
        """获取付款方式列表"""
        try:
            # 构建基础查询
            query = self.session.query(PaymentMethod)
        
            # 添加搜索条件
            if search:
                search_pattern = f'%{search}%'
                query = query.filter(
                    PaymentMethod.payment_name.ilike(search_pattern) |
                    PaymentMethod.description.ilike(search_pattern)
                )
        
            if enabled_only:
                query = query.filter(PaymentMethod.is_enabled == True)
        
            # 排序
            query = query.order_by(PaymentMethod.sort_order, PaymentMethod.created_at)
        
            # 分页
            total = query.count()
            offset = (page - 1) * per_page
            payment_methods_list = query.offset(offset).limit(per_page).all()
            
            payment_methods = []
            for payment_method in payment_methods_list:
                payment_method_dict = payment_method.to_dict()
                
                # 获取创建人和修改人用户名
                if payment_method.created_by:
                    created_user = self.session.query(User).get(payment_method.created_by)
                    if created_user:
                        payment_method_dict['created_by_name'] = created_user.get_full_name()
                    else:
                        payment_method_dict['created_by_name'] = '未知用户'
                else:
                    payment_method_dict['created_by_name'] = '系统'
                    
                if payment_method.updated_by:
                    updated_user = self.session.query(User).get(payment_method.updated_by)
                    if updated_user:
                        payment_method_dict['updated_by_name'] = updated_user.get_full_name()
                    else:
                        payment_method_dict['updated_by_name'] = '未知用户'
                else:
                    payment_method_dict['updated_by_name'] = ''
                
                payment_methods.append(payment_method_dict)
            
            # 计算分页信息
            pages = (total + per_page - 1) // per_page
            has_next = page < pages
            has_prev = page > 1
            
            return {
                'payment_methods': payment_methods,
                'total': total,
                'pages': pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': has_next,
                'has_prev': has_prev
            }
            
        except Exception as e:
            raise ValueError(f'获取付款方式列表失败: {str(e)}')

    def get_payment_method(self, payment_method_id):
        """获取单个付款方式"""
        try:
            payment_method_uuid = uuid.UUID(payment_method_id)
        except ValueError:
            raise ValueError('无效的付款方式ID')
        
        payment_method = self.session.query(PaymentMethod).get(payment_method_uuid)
        if not payment_method:
            raise ValueError('付款方式不存在')
        
        payment_method_data = payment_method.to_dict()
        
        # 获取创建人和修改人用户名
        if payment_method.created_by:
            created_user = self.session.query(User).get(payment_method.created_by)
            if created_user:
                payment_method_data['created_by_name'] = created_user.get_full_name()
            else:
                payment_method_data['created_by_name'] = '未知用户'
        else:
            payment_method_data['created_by_name'] = '系统'
        
        if payment_method.updated_by:
            updated_user = self.session.query(User).get(payment_method.updated_by)
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
        
        # 检查付款方式名称是否重复
        existing = self.session.query(PaymentMethod).filter_by(
            payment_name=data['payment_name']
        ).first()
        if existing:
            raise ValueError('付款方式名称已存在')
        
        try:
            created_by_uuid = uuid.UUID(created_by)
        except ValueError:
            raise ValueError('无效的创建用户ID')
        
        # 准备数据
        payment_method_data = {
            'payment_name': data['payment_name'],
            'description': data.get('description'),
            'sort_order': data.get('sort_order', 0),
            'is_enabled': data.get('is_enabled', True),
        }
        
        try:
            payment_method = self.create_with_tenant(PaymentMethod, **payment_method_data)
            self.commit()
            return payment_method.to_dict()
        except Exception as e:
            self.rollback()
            raise ValueError(f'创建付款方式失败: {str(e)}')

    def update_payment_method(self, payment_method_id, data, updated_by):
        """更新付款方式"""
        try:
            payment_method_uuid = uuid.UUID(payment_method_id)
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的ID')
        
        payment_method = self.session.query(PaymentMethod).get(payment_method_uuid)
        if not payment_method:
            raise ValueError('付款方式不存在')
        
        # 检查付款方式名称是否重复（排除自己）
        if 'payment_name' in data and data['payment_name'] != payment_method.payment_name:
            existing = self.session.query(PaymentMethod).filter(
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
            self.commit()
            return payment_method.to_dict()
        except Exception as e:
            self.rollback()
            raise ValueError(f'更新付款方式失败: {str(e)}')

    def delete_payment_method(self, payment_method_id):
        """删除付款方式"""
        try:
            payment_method_uuid = uuid.UUID(payment_method_id)
        except ValueError:
            raise ValueError('无效的付款方式ID')
        
        payment_method = self.session.query(PaymentMethod).get(payment_method_uuid)
        if not payment_method:
            raise ValueError('付款方式不存在')
        
        try:
            self.session.delete(payment_method)
            self.commit()
        except Exception as e:
            self.rollback()
            raise ValueError(f'删除付款方式失败: {str(e)}')

    def get_enabled_payment_methods(self):
        """获取启用的付款方式列表（用于下拉选择）"""
        try:
            payment_methods = self.session.query(PaymentMethod).filter_by(
                is_enabled=True
            ).order_by(PaymentMethod.sort_order, PaymentMethod.payment_name).all()
            
            return [payment_method.to_dict() for payment_method in payment_methods]
        except Exception as e:
            raise ValueError(f'获取启用付款方式失败: {str(e)}')


def get_payment_method_service(tenant_id: Optional[str] = None, schema_name: Optional[str] = None) -> PaymentMethodService:
    """获取付款方式服务实例"""
    return PaymentMethodService(tenant_id=tenant_id, schema_name=schema_name)

