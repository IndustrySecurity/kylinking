# -*- coding: utf-8 -*-
"""
LossType管理服务
"""
from typing import Dict, List, Optional, Any
from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError
import uuid

from app.services.base_service import TenantAwareService
from app.models.basic_data import LossType
from app.models.user import User


class LossTypeService(TenantAwareService):
    """报损类型管理服务"""

    def get_loss_types(self, page=1, per_page=20, search=None, enabled_only=False):
        """获取报损类型列表"""
        try:
            query = self.session.query(LossType)
            
            # 搜索条件
            if search:
                query = query.filter(LossType.loss_type_name.ilike(f'%{search}%'))
            
            # 启用状态过滤
            if enabled_only:
                query = query.filter(LossType.is_enabled == True)
            
            # 排序
            query = query.order_by(LossType.sort_order, LossType.created_at)
            
            # 分页
            total = query.count()
            loss_types = query.offset((page - 1) * per_page).limit(per_page).all()
            
            # 构建返回数据
            types_data = []
            for loss_type in loss_types:
                loss_type_data = loss_type.to_dict()
                
                # 简化用户名显示
                loss_type_data['created_by_name'] = '系统用户'
                loss_type_data['updated_by_name'] = '系统用户' if loss_type.updated_by else ''
                
                types_data.append(loss_type_data)
            
            # 计算分页信息
            pages = (total + per_page - 1) // per_page
                
            return {
                'items': types_data,
                'total': total,
                'pages': pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': page < pages,
                'has_prev': page > 1
            }
        except Exception as e:
            raise ValueError(f'查询报损类型失败: {str(e)}')

    def create_loss_type(self, data, created_by):
        """创建报损类型"""
        # 验证数据
        if not data.get('loss_type_name'):
            raise ValueError('报损类型名称不能为空')
        
        # 检查报损类型名称是否重复
        existing = self.session.query(LossType).filter_by(
            loss_type_name=data['loss_type_name']
        ).first()
        if existing:
            raise ValueError('报损类型名称已存在')
        
        try:
            created_by_uuid = uuid.UUID(created_by)
        except ValueError:
            raise ValueError('无效的创建用户ID')
        
        try:
            # 创建报损类型
            loss_type = self.create_with_tenant(LossType,
                loss_type_name=data['loss_type_name'],
                process_id=uuid.UUID(data['process_id']) if data.get('process_id') else None,
                loss_category_id=uuid.UUID(data['loss_category_id']) if data.get('loss_category_id') else None,
                is_assessment=data.get('is_assessment', False),
                description=data.get('description'),
                sort_order=data.get('sort_order', 0),
                is_enabled=data.get('is_enabled', True),
                created_by=created_by_uuid
            )
            
            self.commit()
            return loss_type.to_dict()
        except Exception as e:
            self.rollback()
            raise ValueError(f'创建报损类型失败: {str(e)}')

    def update_loss_type(self, loss_type_id, data, updated_by):
        """更新报损类型"""
        try:
            loss_type_uuid = uuid.UUID(loss_type_id)
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的ID')
        
        try:
            loss_type = self.session.query(LossType).get(loss_type_uuid)
            if not loss_type:
                raise ValueError('报损类型不存在')
            
            # 检查报损类型名称是否重复（排除自己）
            if 'loss_type_name' in data and data['loss_type_name'] != loss_type.loss_type_name:
                existing = self.session.query(LossType).filter(
                    and_(
                        LossType.loss_type_name == data['loss_type_name'],
                        LossType.id != loss_type_uuid
                    )
                ).first()
                if existing:
                    raise ValueError('报损类型名称已存在')
            
            # 更新字段
            for key, value in data.items():
                if key == 'process_id' and value:
                    setattr(loss_type, key, uuid.UUID(value))
                elif key == 'loss_category_id' and value:
                    setattr(loss_type, key, uuid.UUID(value))
                elif hasattr(loss_type, key) and key not in ['id', 'created_by', 'created_at']:
                    setattr(loss_type, key, value)
            
            loss_type.updated_by = updated_by_uuid
            self.commit()
            
            return loss_type.to_dict()
        except Exception as e:
            self.rollback()
            raise ValueError(f'更新报损类型失败: {str(e)}')

    def delete_loss_type(self, loss_type_id):
        """删除报损类型"""
        try:
            loss_type_uuid = uuid.UUID(loss_type_id)
        except ValueError:
            raise ValueError('无效的报损类型ID')
        
        try:
            loss_type = self.session.query(LossType).get(loss_type_uuid)
            if not loss_type:
                raise ValueError('报损类型不存在')
            
            self.session.delete(loss_type)
            self.commit()
            
            return True
        except Exception as e:
            self.rollback()
            raise ValueError(f'删除报损类型失败: {str(e)}')

    def get_enabled_loss_types(self):
        """获取所有启用的报损类型"""
        try:
            loss_types = self.session.query(LossType).filter(
                LossType.is_enabled == True
            ).order_by(LossType.sort_order, LossType.loss_type_name).all()
            
            return [lt.to_dict() for lt in loss_types]
        except Exception as e:
            raise ValueError(f'获取启用报损类型失败: {str(e)}')

