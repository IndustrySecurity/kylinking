# -*- coding: utf-8 -*-
"""
InkOption管理服务
"""
from typing import Dict, List, Optional, Any
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
import uuid

from app.services.base_service import TenantAwareService
from app.models.basic_data import InkOption
from app.models.user import User


class InkOptionService(TenantAwareService):
    """油墨选项管理服务"""

    def get_ink_options(self, page=1, per_page=20, search=None, enabled_only=False):
        """获取油墨选项列表"""
        try:
            query = self.session.query(InkOption)
            
            # 搜索条件
            if search:
                search_filter = or_(
                    InkOption.option_name.ilike(f'%{search}%'),
                    InkOption.description.ilike(f'%{search}%')
                )
                query = query.filter(search_filter)
            
            # 启用状态过滤
            if enabled_only:
                query = query.filter(InkOption.is_enabled == True)
        
            # 排序
            query = query.order_by(InkOption.sort_order, InkOption.created_at)
            
            # 分页
            total = query.count()
            ink_options = query.offset((page - 1) * per_page).limit(per_page).all()
            
            # 构建返回数据
            options_data = []
            for option in ink_options:
                option_data = option.to_dict()
                
                # 添加用户信息
                if option.created_by:
                    created_user = self.session.query(User).get(option.created_by)
                    option_data['created_by_name'] = created_user.get_full_name() if created_user else '未知用户'
                else:
                    option_data['created_by_name'] = '系统'
                    
                if option.updated_by:
                    updated_user = self.session.query(User).get(option.updated_by)
                    option_data['updated_by_name'] = updated_user.get_full_name() if updated_user else '未知用户'
                else:
                    option_data['updated_by_name'] = ''
                
                options_data.append(option_data)
            
            # 计算分页信息
            pages = (total + per_page - 1) // per_page
            
            return {
                'ink_options': options_data,
                'total': total,
                'pages': pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': page < pages,
                'has_prev': page > 1
            }
            
        except Exception as e:
            raise ValueError(f'查询油墨选项失败: {str(e)}')

    def get_ink_option(self, option_id):
        """获取油墨选项详情"""
        try:
            option_uuid = uuid.UUID(option_id)
        except ValueError:
            raise ValueError('无效的油墨选项ID')
        
        option = self.session.query(InkOption).get(option_uuid)
        if not option:
            raise ValueError('油墨选项不存在')
        
        option_data = option.to_dict()
        
        # 获取创建人和修改人用户名
        if option.created_by:
            created_user = self.session.query(User).get(option.created_by)
            option_data['created_by_name'] = created_user.get_full_name() if created_user else '未知用户'
        
        if option.updated_by:
            updated_user = self.session.query(User).get(option.updated_by)
            option_data['updated_by_name'] = updated_user.get_full_name() if updated_user else '未知用户'
        
        return option_data

    def create_ink_option(self, data, created_by):
        """创建油墨选项"""
        # 验证数据
        if not data.get('option_name'):
            raise ValueError('选项名称不能为空')
        
        # 检查选项名称是否重复
        existing = self.session.query(InkOption).filter_by(
            option_name=data['option_name']
        ).first()
        if existing:
            raise ValueError('选项名称已存在')
        
        try:
            created_by_uuid = uuid.UUID(created_by)
        except ValueError:
            raise ValueError('无效的创建用户ID')
        
        try:
            # 创建油墨选项
            option = self.create_with_tenant(InkOption,
                option_name=data['option_name'],
                sort_order=data.get('sort_order', 0),
                is_enabled=data.get('is_enabled', True),
                description=data.get('description'),
                created_by=created_by_uuid
            )
        
            self.commit()
            return self.get_ink_option(option.id)
        except Exception as e:
            self.rollback()
            raise ValueError(f'创建油墨选项失败: {str(e)}')

    def update_ink_option(self, option_id, data, updated_by):
        """更新油墨选项"""
        try:
            option_uuid = uuid.UUID(option_id)
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的ID')
        
        try:
            option = self.session.query(InkOption).get(option_uuid)
            if not option:
                raise ValueError('油墨选项不存在')
        
            # 验证数据
            if 'option_name' in data and not data['option_name']:
                raise ValueError('选项名称不能为空')
            
            # 检查选项名称是否重复（排除自己）
            if 'option_name' in data and data['option_name'] != option.option_name:
                existing = self.session.query(InkOption).filter(
                    InkOption.option_name == data['option_name'],
                    InkOption.id != option_uuid
                ).first()
                if existing:
                    raise ValueError('选项名称已存在')
        
            # 更新字段
            for field, value in data.items():
                if hasattr(option, field) and field not in ['id', 'created_by', 'created_at']:
                    setattr(option, field, value)
        
            option.updated_by = updated_by_uuid
            self.commit()
        
            return self.get_ink_option(option.id)
        except Exception as e:
            self.rollback()
            raise ValueError(f'更新油墨选项失败: {str(e)}')

    def delete_ink_option(self, option_id):
        """删除油墨选项"""
        try:
            option_uuid = uuid.UUID(option_id)
        except ValueError:
            raise ValueError('无效的油墨选项ID')
        
        try:
            option = self.session.query(InkOption).get(option_uuid)
            if not option:
                raise ValueError('油墨选项不存在')
        
            self.session.delete(option)
            self.commit()
            
            return True
        except Exception as e:
            self.rollback()
            raise ValueError(f'删除油墨选项失败: {str(e)}')

    def get_enabled_ink_options(self):
        """获取所有启用的油墨选项"""
        try:
            ink_options = self.session.query(InkOption).filter(
                InkOption.is_enabled == True
            ).order_by(InkOption.sort_order, InkOption.option_name).all()
            
            return [io.to_dict() for io in ink_options]
        except Exception as e:
            raise ValueError(f'获取启用油墨选项失败: {str(e)}')


def get_ink_option_service(tenant_id: str = None, schema_name: str = None) -> InkOptionService:
    """获取油墨选项服务实例"""
    return InkOptionService(tenant_id=tenant_id, schema_name=schema_name)

