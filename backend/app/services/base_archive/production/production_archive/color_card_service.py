# -*- coding: utf-8 -*-
"""
ColorCard管理服务
"""
from typing import Dict, List, Optional, Any
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import uuid

from app.services.base_service import TenantAwareService
from app.models.basic_data import ColorCard
from app.models.user import User


class ColorCardService(TenantAwareService):
    """色卡管理服务"""

    def __init__(self, tenant_id: Optional[str] = None, schema_name: Optional[str] = None):
        """初始化ColorCard服务"""
        super().__init__(tenant_id, schema_name)

        if schema_name != 'public':
            pass

    def get_color_cards(self, page=1, per_page=20, search=None, enabled_only=False):
        """获取色卡列表"""
        
        # 获取当前schema名称
        
        from flask import g, current_app
        schema_name = getattr(g, 'schema_name', current_app.config.get('DEFAULT_SCHEMA', 'public'))
        
        # 构建基础查询
        base_query = f"""
        SELECT 
            id, color_code, color_name, color_value, remarks, sort_order, 
            is_enabled, created_by, updated_by, created_at, updated_at
        FROM {schema_name}.color_cards
        """
        
        # 添加搜索条件
        where_conditions = []
        params = {}
        
        if search:
            where_conditions.append("""
                (color_name ILIKE :search OR 
                 color_code ILIKE :search OR 
                 remarks ILIKE :search)
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
        FROM {schema_name}.color_cards
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
            
            color_cards = []
            for row in rows:
                color_card_data = {
                    'id': str(row.id),
                    'color_code': row.color_code,
                    'color_name': row.color_name,
                    'color_value': row.color_value,
                    'remarks': row.remarks,
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
                        color_card_data['created_by_name'] = created_user.get_full_name()
                    else:
                        color_card_data['created_by_name'] = '未知用户'
                else:
                    color_card_data['created_by_name'] = '系统'
                    
                if row.updated_by:
                    updated_user = User.query.get(row.updated_by)
                    if updated_user:
                        color_card_data['updated_by_name'] = updated_user.get_full_name()
                    else:
                        color_card_data['updated_by_name'] = '未知用户'
                else:
                    color_card_data['updated_by_name'] = ''
                
                color_cards.append(color_card_data)
            
            # 计算分页信息
            pages = (total + per_page - 1) // per_page
            has_next = page < pages
            has_prev = page > 1
            
            return {
                'color_cards': color_cards,
                'total': total,
                'pages': pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': has_next,
                'has_prev': has_prev
            }
            
        except Exception as e:
            current_app.logger.error(f"Error querying color cards: {str(e)}")
            raise ValueError(f'查询色卡失败: {str(e)}')
    def get_color_card(self, color_card_id):
        """获取色卡详情"""
        
        try:
            color_card_uuid = uuid.UUID(color_card_id)
        except ValueError:
            raise ValueError('无效的色卡ID')
        
        from app.models.basic_data import ColorCard
        color_card = ColorCard.query.get(color_card_uuid)
        if not color_card:
            raise ValueError('色卡不存在')
        
        color_card_data = color_card.to_dict()
        
        # 获取创建人和修改人用户名
        if color_card.created_by:
            created_user = User.query.get(color_card.created_by)
            if created_user:
                color_card_data['created_by_name'] = created_user.get_full_name()
            else:
                color_card_data['created_by_name'] = '未知用户'
        
        if color_card.updated_by:
            updated_user = User.query.get(color_card.updated_by)
            if updated_user:
                color_card_data['updated_by_name'] = updated_user.get_full_name()
            else:
                color_card_data['updated_by_name'] = '未知用户'
        
        return color_card_data
    def create_color_card(self, data, created_by):
        """创建色卡"""
        
        # 验证数据
        if not data.get('color_name'):
            raise ValueError('色卡名称不能为空')
        
        if not data.get('color_value'):
            raise ValueError('色值不能为空')
        
        from app.models.basic_data import ColorCard
        
        # 检查色卡名称是否重复
        existing = ColorCard.query.filter_by(
            color_name=data['color_name']
        ).first()
        if existing:
            raise ValueError('色卡名称已存在')
        
        # 自动生成色卡编号（忽略用户输入的编号）
        color_code = ColorCard.generate_color_code()
        
        try:
            created_by_uuid = uuid.UUID(created_by)
        except ValueError:
            raise ValueError('无效的创建用户ID')
        
        # 创建色卡
        color_card = ColorCard(
            color_code=color_code,
            color_name=data['color_name'],
            color_value=data['color_value'],
            remarks=data.get('remarks'),
            sort_order=data.get('sort_order', 0),
            is_enabled=data.get('is_enabled', True),
            created_by=created_by_uuid
        )
        
        try:
            self.get_session().add(color_card)
            self.get_session().commit()
            return color_card.to_dict()
        except Exception as e:
            self.get_session().rollback()
            raise ValueError(f'创建色卡失败: {str(e)}')
    def update_color_card(self, color_card_id, data, updated_by):
        """更新色卡"""
        
        try:
            color_card_uuid = uuid.UUID(color_card_id)
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的ID')
        
        from app.models.basic_data import ColorCard
        color_card = ColorCard.query.get(color_card_uuid)
        if not color_card:
            raise ValueError('色卡不存在')
        
        # 检查色卡名称是否重复（排除自己）
        if 'color_name' in data and data['color_name'] != color_card.color_name:
            existing = ColorCard.query.filter(
                and_(
                    ColorCard.color_name == data['color_name'],
                    ColorCard.id != color_card_uuid
                )
            ).first()
            if existing:
                raise ValueError('色卡名称已存在')
        
        # 移除色卡编号字段，不允许修改
        if 'color_code' in data:
            del data['color_code']
        
        # 更新字段
        for key, value in data.items():
            if hasattr(color_card, key):
                setattr(color_card, key, value)
        
        color_card.updated_by = updated_by_uuid
        
        try:
            self.get_session().commit()
            return color_card.to_dict()
        except Exception as e:
            self.get_session().rollback()
            raise ValueError(f'更新色卡失败: {str(e)}')
    def delete_color_card(self, color_card_id):
        """删除色卡"""
        
        try:
            color_card_uuid = uuid.UUID(color_card_id)
        except ValueError:
            raise ValueError('无效的色卡ID')
        
        from app.models.basic_data import ColorCard
        color_card = ColorCard.query.get(color_card_uuid)
        if not color_card:
            raise ValueError('色卡不存在')
        
        try:
            self.get_session().delete(color_card)
            self.get_session().commit()
        except Exception as e:
            self.get_session().rollback()
            raise ValueError(f'删除色卡失败: {str(e)}')
    def batch_update_color_cards(self, data_list, updated_by):
        """批量更新色卡（用于可编辑表格）"""
        
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
                    color_card = ColorCardService().update_color_card(
                        data['id'], data, updated_by
                    )
                    results.append(color_card)
                else:
                    # 创建新记录
                    color_card = ColorCardService().create_color_card(
                        data, updated_by
                    )
                    results.append(color_card)
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
    def get_enabled_color_cards(self):
        """获取启用的色卡列表（用于下拉选择）"""
        
        from app.models.basic_data import ColorCard
        color_cards = ColorCard.query.filter_by(
            is_enabled=True
        ).order_by(ColorCard.sort_order, ColorCard.color_name).all()
        
        return [cc.to_dict() for cc in color_cards]

