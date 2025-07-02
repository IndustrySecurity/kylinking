# -*- coding: utf-8 -*-
"""
LossType管理服务
"""
from typing import Dict, List, Optional, Any
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import uuid

from app.services.base_service import TenantAwareService
from app.models.basic_data import LossType
from app.models.user import User


class LossTypeService(TenantAwareService):
    """报损类型管理服务"""

    def __init__(self, tenant_id: Optional[str] = None, schema_name: Optional[str] = None):
        """初始化LossType服务"""
        super().__init__(tenant_id, schema_name)

        if schema_name != 'public':
            pass

    def get_loss_types(self, page=1, per_page=20, search=None, enabled_only=False):
        """获取报损类型列表"""
        
        from app.models.basic_data import LossType
        
        # 构建查询
        query = LossType.query
        
        # 搜索条件
        if search:
            query = query.filter(LossType.loss_type_name.ilike(f'%{search}%'))
        
        # 启用状态过滤
        if enabled_only:
            query = query.filter(LossType.is_enabled == True)
        
        # 排序
        query = query.order_by(LossType.sort_order, LossType.created_at)
        
        # 分页
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        loss_types = []
        for loss_type in pagination.items:
            loss_type_data = loss_type.to_dict()
            
            # 简化用户名显示
            loss_type_data['created_by_name'] = '系统用户'
            loss_type_data['updated_by_name'] = '系统用户' if loss_type.updated_by else ''
            
            loss_types.append(loss_type_data)
        
        return {
            'items': loss_types,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page,
            'per_page': pagination.per_page,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    def create_loss_type(self, data, created_by):
        """创建报损类型"""
        
        # 验证数据
        if not data.get('loss_type_name'):
            raise ValueError('报损类型名称不能为空')
        
        from app.models.basic_data import LossType
        
        # 检查报损类型名称是否重复
        existing = LossType.query.filter_by(
            loss_type_name=data['loss_type_name']
        ).first()
        if existing:
            raise ValueError('报损类型名称已存在')
        
        try:
            created_by_uuid = uuid.UUID(created_by)
        except ValueError:
            raise ValueError('无效的创建用户ID')
        
        # 创建报损类型
        loss_type = LossType(
            loss_type_name=data['loss_type_name'],
            process_id=uuid.UUID(data['process_id']) if data.get('process_id') else None,
            loss_category_id=uuid.UUID(data['loss_category_id']) if data.get('loss_category_id') else None,
            is_assessment=data.get('is_assessment', False),
            description=data.get('description'),
            sort_order=data.get('sort_order', 0),
            is_enabled=data.get('is_enabled', True),
            created_by=created_by_uuid
        )
        
        try:
            self.get_session().add(loss_type)
            self.get_session().commit()
            return loss_type.to_dict()
        except Exception as e:
            self.get_session().rollback()
            raise ValueError(f'创建报损类型失败: {str(e)}')
    def update_loss_type(self, loss_type_id, data, updated_by):
        """更新报损类型"""
        
        try:
            loss_type_uuid = uuid.UUID(loss_type_id)
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的ID')
        
        from app.models.basic_data import LossType
        loss_type = LossType.query.get(loss_type_uuid)
        if not loss_type:
            raise ValueError('报损类型不存在')
        
        # 检查报损类型名称是否重复（排除自己）
        if 'loss_type_name' in data and data['loss_type_name'] != loss_type.loss_type_name:
            existing = LossType.query.filter(
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
            elif hasattr(loss_type, key):
                setattr(loss_type, key, value)
        
        loss_type.updated_by = updated_by_uuid
        
        try:
            self.get_session().commit()
            return loss_type.to_dict()
        except Exception as e:
            self.get_session().rollback()
            raise ValueError(f'更新报损类型失败: {str(e)}')
    def delete_loss_type(self, loss_type_id):
        """删除报损类型"""
        
        try:
            loss_type_uuid = uuid.UUID(loss_type_id)
        except ValueError:
            raise ValueError('无效的报损类型ID')
        
        from app.models.basic_data import LossType
        loss_type = LossType.query.get(loss_type_uuid)
        if not loss_type:
            raise ValueError('报损类型不存在')
        
        try:
            self.get_session().delete(loss_type)
            self.get_session().commit()
        except Exception as e:
            self.get_session().rollback()
            raise ValueError(f'删除报损类型失败: {str(e)}')
    def batch_update_loss_types(self, data_list, updated_by):
        """批量更新报损类型（用于可编辑表格）"""
        
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
                    loss_type = LossTypeService().update_loss_type(
                        data['id'], data, updated_by
                    )
                    results.append(loss_type)
                else:
                    # 创建新记录
                    loss_type = LossTypeService().create_loss_type(
                        data, updated_by
                    )
                    results.append(loss_type)
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
    def get_enabled_loss_types(self):
        """获取启用的报损类型列表（用于下拉选择）"""
        
        from app.models.basic_data import LossType
        loss_types = LossType.query.filter_by(
            is_enabled=True
        ).order_by(LossType.sort_order, LossType.loss_type_name).all()
        
        return [lt.to_dict() for lt in loss_types]

