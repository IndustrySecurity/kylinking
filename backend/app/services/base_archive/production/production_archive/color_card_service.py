from sqlalchemy import and_, or_
from app.models.basic_data import ColorCard
from app.models.user import User
from app.services.base_service import BaseService
import uuid


class ColorCardService(BaseService):
    """色卡服务"""
    
    def get_color_cards(self, page=1, per_page=20, search=None, enabled_only=False):
        """获取色卡列表"""
        try:
            query = self.session.query(ColorCard)
            
            # 搜索过滤
            if search:
                search_filter = or_(
                    ColorCard.color_name.ilike(f'%{search}%'),
                    ColorCard.color_code.ilike(f'%{search}%'),
                    ColorCard.color_value.ilike(f'%{search}%')
                )
                query = query.filter(search_filter)
            
            # 启用状态过滤
            if enabled_only:
                query = query.filter(ColorCard.is_enabled == True)
            
            # 排序
            query = query.order_by(ColorCard.sort_order, ColorCard.color_name)
            
            # 分页
            total = query.count()
            color_cards = query.offset((page - 1) * per_page).limit(per_page).all()
            
            # 构建返回数据
            cards_data = []
            for color_card in color_cards:
                card_data = self._format_color_card(color_card)
                cards_data.append(card_data)
            
            # 计算分页信息
            pages = (total + per_page - 1) // per_page
            
            return {
                'color_cards': cards_data,
                'total': total,
                'pages': pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': page < pages,
                'has_prev': page > 1
            }
            
        except Exception as e:
            raise ValueError(f'查询色卡失败: {str(e)}')

    def get_color_card(self, color_card_id):
        """获取色卡详情"""
        try:
            color_card_uuid = uuid.UUID(color_card_id)
        except ValueError:
            raise ValueError('无效的色卡ID')
        
        color_card = self.session.query(ColorCard).get(color_card_uuid)
        if not color_card:
            raise ValueError('色卡不存在')
        
        return self._format_color_card(color_card)

    def _format_color_card(self, color_card):
        """格式化色卡数据"""
        card_data = color_card.to_dict()
        
        # 添加用户信息
        if color_card.created_by:
            created_user = self.session.query(User).get(color_card.created_by)
            card_data['created_by_name'] = created_user.get_full_name() if created_user else '未知用户'
        else:
            card_data['created_by_name'] = '系统'
            
        if color_card.updated_by:
            updated_user = self.session.query(User).get(color_card.updated_by)
            card_data['updated_by_name'] = updated_user.get_full_name() if updated_user else '未知用户'
        else:
            card_data['updated_by_name'] = ''
            
        return card_data

    def create_color_card(self, data, created_by):
        """创建色卡"""
        # 验证数据
        if not data.get('color_name'):
            raise ValueError('色卡名称不能为空')
        
        if not data.get('color_value'):
            raise ValueError('色值不能为空')
        
        # 检查色卡名称是否重复
        existing = self.session.query(ColorCard).filter_by(
            color_name=data['color_name']
        ).first()
        if existing:
            raise ValueError('色卡名称已存在')
        
        try:
            created_by_uuid = uuid.UUID(created_by)
        except ValueError:
            raise ValueError('无效的创建用户ID')
        
        try:
            # 自动生成色卡编号
            color_code = data.get('color_code') or f"CC{str(uuid.uuid4())[:8].upper()}"
            
            # 创建色卡
            color_card = self.create_with_tenant(ColorCard,
                color_code=color_code,
                color_name=data['color_name'],
                color_value=data['color_value'],
                remarks=data.get('remarks'),
                sort_order=data.get('sort_order', 0),
                is_enabled=data.get('is_enabled', True),
                created_by=created_by_uuid
            )
            
            self.commit()
            return self.get_color_card(color_card.id)
            
        except Exception as e:
            self.rollback()
            raise ValueError(f'创建色卡失败: {str(e)}')

    def update_color_card(self, color_card_id, data, updated_by):
        """更新色卡"""
        try:
            color_card_uuid = uuid.UUID(color_card_id)
            updated_by_uuid = uuid.UUID(updated_by)
        except ValueError:
            raise ValueError('无效的ID')
        
        try:
            color_card = self.session.query(ColorCard).get(color_card_uuid)
            if not color_card:
                raise ValueError('色卡不存在')
            
            # 验证数据
            if 'color_name' in data and not data['color_name']:
                raise ValueError('色卡名称不能为空')
            
            if 'color_value' in data and not data['color_value']:
                raise ValueError('色值不能为空')
            
            # 检查色卡名称是否重复（排除自己）
            if 'color_name' in data and data['color_name'] != color_card.color_name:
                existing = self.session.query(ColorCard).filter(
                    and_(
                        ColorCard.color_name == data['color_name'],
                        ColorCard.id != color_card_uuid
                    )
                ).first()
                if existing:
                    raise ValueError('色卡名称已存在')
            
            # 更新字段
            for field, value in data.items():
                if hasattr(color_card, field) and field not in ['id', 'created_by', 'created_at']:
                    setattr(color_card, field, value)
            
            color_card.updated_by = updated_by_uuid
            self.commit()
            
            return self.get_color_card(color_card.id)
            
        except Exception as e:
            self.rollback()
            raise ValueError(f'更新色卡失败: {str(e)}')

    def delete_color_card(self, color_card_id):
        """删除色卡"""
        try:
            color_card_uuid = uuid.UUID(color_card_id)
        except ValueError:
            raise ValueError('无效的色卡ID')
        
        try:
            color_card = self.session.query(ColorCard).get(color_card_uuid)
            if not color_card:
                raise ValueError('色卡不存在')
            
            self.session.delete(color_card)
            self.commit()
            
            return True
            
        except Exception as e:
            self.rollback()
            raise ValueError(f'删除色卡失败: {str(e)}')

    def get_enabled_color_cards(self):
        """获取所有启用的色卡"""
        try:
            color_cards = self.session.query(ColorCard).filter(
                ColorCard.is_enabled == True
            ).order_by(ColorCard.sort_order, ColorCard.color_name).all()
            
            return [self._format_color_card(cc) for cc in color_cards]
            
        except Exception as e:
            raise ValueError(f'获取启用色卡失败: {str(e)}') 