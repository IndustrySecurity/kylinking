# -*- coding: utf-8 -*-
"""
材料分类服务
"""

from app.models.basic_data import MaterialCategory, Unit
from app.extensions import db
from app.services.base_service import TenantAwareService
from flask import g
from sqlalchemy import or_, and_, func, desc, asc
from sqlalchemy.orm import joinedload
import uuid


class MaterialCategoryService(TenantAwareService):
    """材料分类服务类"""
    
    def __init__(self):
        super().__init__()
    
    def get_material_categories(self, page=1, per_page=20, search=None, material_type=None, is_enabled=None):
        """
        获取材料分类列表
        
        Args:
            page: 页码
            per_page: 每页条数
            search: 搜索关键词
            material_type: 材料属性筛选
            is_enabled: 是否启用筛选
            
        Returns:
            dict: 包含材料分类列表和分页信息
        """
        try:
            query = self.session.query(MaterialCategory)
            
            # 搜索过滤
            if search:
                search_filter = or_(
                    MaterialCategory.material_name.ilike(f'%{search}%'),
                    MaterialCategory.material_type.ilike(f'%{search}%'),
                    MaterialCategory.code_prefix.ilike(f'%{search}%')
                )
                query = query.filter(search_filter)
            
            # 材料属性过滤
            if material_type:
                query = query.filter(MaterialCategory.material_type == material_type)
            
            # 是否启用过滤
            if is_enabled is not None:
                query = query.filter(MaterialCategory.is_active == is_enabled)
            
            # 按创建时间倒序
            query = query.order_by(desc(MaterialCategory.created_at))
            
            # 分页
            total = query.count()
            items = query.offset((page - 1) * per_page).limit(per_page).all()
            
            return {
                'items': [self._format_material_category(item) for item in items],
                'total': total,
                'page': page,
                'per_page': per_page,
                'pages': (total + per_page - 1) // per_page
            }
            
        except Exception as e:
            self.rollback()
            raise e
    
    def get_material_category_by_id(self, category_id):
        """
        根据ID获取材料分类详情
        
        Args:
            category_id: 材料分类ID
            
        Returns:
            dict: 材料分类详情
        """
        try:
            category = self.session.query(MaterialCategory).get(uuid.UUID(category_id))
            if not category:
                raise ValueError('材料分类不存在')
            
            return self._format_material_category(category)
            
        except Exception as e:
            raise e
    
    def _format_material_category(self, category):
        """格式化材料分类数据"""
        return {
            'id': str(category.id),
            'material_name': category.material_name,
            'material_type': category.material_type,
            'base_unit_id': str(category.base_unit_id) if category.base_unit_id else None,
            'auxiliary_unit_id': str(category.auxiliary_unit_id) if category.auxiliary_unit_id else None,
            'sales_unit_id': str(category.sales_unit_id) if category.sales_unit_id else None,
            'density': category.density,
            'square_weight': category.square_weight,
            'shelf_life': category.shelf_life,
            'inspection_standard': category.inspection_standard,
            'quality_grade': category.quality_grade,
            'latest_purchase_price': category.latest_purchase_price,
            'sales_price': category.sales_price,
            'product_quote_price': category.product_quote_price,
            'cost_price': category.cost_price,
            'show_on_kanban': category.show_on_kanban,
            'account_subject': category.account_subject,
            'code_prefix': category.code_prefix,
            'warning_days': category.warning_days,
            'carton_param1': category.carton_param1,
            'carton_param2': category.carton_param2,
            'carton_param3': category.carton_param3,
            'carton_param4': category.carton_param4,
            'enable_batch': category.enable_batch,
            'enable_barcode': category.enable_barcode,
            'is_ink': category.is_ink,
            'is_accessory': category.is_accessory,
            'is_consumable': category.is_consumable,
            'is_recyclable': category.is_recyclable,
            'is_hazardous': category.is_hazardous,
            'is_imported': category.is_imported,
            'is_customized': category.is_customized,
            'is_seasonal': category.is_seasonal,
            'is_fragile': category.is_fragile,
            'is_perishable': category.is_perishable,
            'is_temperature_sensitive': category.is_temperature_sensitive,
            'is_moisture_sensitive': category.is_moisture_sensitive,
            'is_light_sensitive': category.is_light_sensitive,
            'requires_special_storage': category.requires_special_storage,
            'requires_certification': category.requires_certification,
            'display_order': category.display_order,
            'is_active': category.is_active,
            'created_by': str(category.created_by) if category.created_by else None,
            'created_at': category.created_at.isoformat() if category.created_at else None,
            'updated_by': str(category.updated_by) if category.updated_by else None,
            'updated_at': category.updated_at.isoformat() if category.updated_at else None,
        }
    
    def create_material_category(self, data, created_by=None):
        """
        创建材料分类
        
        Args:
            data: 材料分类数据
            created_by: 创建者ID
            
        Returns:
            dict: 创建的材料分类信息
        """
        try:
            # 验证必填字段
            if not data.get('material_name'):
                raise ValueError('材料分类名称不能为空')
            
            if not data.get('material_type'):
                raise ValueError('材料属性不能为空')
            
            # 验证材料属性值
            if data['material_type'] not in ['主材', '辅材']:
                raise ValueError('材料属性必须是"主材"或"辅材"')
            
            # 验证单位ID是否存在
            for unit_field in ['base_unit_id', 'auxiliary_unit_id', 'sales_unit_id']:
                unit_id = data.get(unit_field)
                if unit_id:
                    unit = self.session.query(Unit).get(uuid.UUID(unit_id))
                    if not unit:
                        raise ValueError(f'{unit_field}对应的单位不存在')
            
            # 获取创建者ID
            user_id = created_by
            if not user_id and hasattr(g, 'current_user') and g.current_user:
                user_id = g.current_user.id
            
            # 创建材料分类
            category = self.create_with_tenant(MaterialCategory,
                material_name=data['material_name'],
                material_type=data['material_type'],
                base_unit_id=data.get('base_unit_id'),
                auxiliary_unit_id=data.get('auxiliary_unit_id'),
                sales_unit_id=data.get('sales_unit_id'),
                density=data.get('density'),
                square_weight=data.get('square_weight'),
                shelf_life=data.get('shelf_life'),
                inspection_standard=data.get('inspection_standard'),
                quality_grade=data.get('quality_grade'),
                latest_purchase_price=data.get('latest_purchase_price'),
                sales_price=data.get('sales_price'),
                product_quote_price=data.get('product_quote_price'),
                cost_price=data.get('cost_price'),
                show_on_kanban=data.get('show_on_kanban', False),
                account_subject=data.get('account_subject'),
                code_prefix=data.get('code_prefix'),
                warning_days=data.get('warning_days'),
                carton_param1=data.get('carton_param1'),
                carton_param2=data.get('carton_param2'),
                carton_param3=data.get('carton_param3'),
                carton_param4=data.get('carton_param4'),
                enable_batch=data.get('enable_batch', False),
                enable_barcode=data.get('enable_barcode', False),
                is_ink=data.get('is_ink', False),
                is_accessory=data.get('is_accessory', False),
                is_consumable=data.get('is_consumable', False),
                is_recyclable=data.get('is_recyclable', False),
                is_hazardous=data.get('is_hazardous', False),
                is_imported=data.get('is_imported', False),
                is_customized=data.get('is_customized', False),
                is_seasonal=data.get('is_seasonal', False),
                is_fragile=data.get('is_fragile', False),
                is_perishable=data.get('is_perishable', False),
                is_temperature_sensitive=data.get('is_temperature_sensitive', False),
                is_moisture_sensitive=data.get('is_moisture_sensitive', False),
                is_light_sensitive=data.get('is_light_sensitive', False),
                requires_special_storage=data.get('requires_special_storage', False),
                requires_certification=data.get('requires_certification', False),
                display_order=data.get('display_order', 0),
                is_active=data.get('is_active', True),
                created_by=user_id
            )
            
            self.commit()
            
            return self.get_material_category_by_id(category.id)
        except Exception as e:
            self.rollback()
            raise e
    
    def update_material_category(self, category_id, data, updated_by=None):
        """
        更新材料分类
        
        Args:
            category_id: 材料分类ID
            data: 更新数据
            updated_by: 更新者ID
            
        Returns:
            dict: 更新后的材料分类信息
        """
        try:
            category = self.session.query(MaterialCategory).get(uuid.UUID(category_id))
            if not category:
                raise ValueError('材料分类不存在')
            
            # 验证必填字段
            if 'material_name' in data and not data['material_name']:
                raise ValueError('材料分类名称不能为空')
            
            if 'material_type' in data and not data['material_type']:
                raise ValueError('材料属性不能为空')
            
            # 验证材料属性值
            if 'material_type' in data and data['material_type'] not in ['主材', '辅材']:
                raise ValueError('材料属性必须是"主材"或"辅材"')
            
            # 验证单位ID是否存在
            for unit_field in ['base_unit_id', 'auxiliary_unit_id', 'sales_unit_id']:
                if unit_field in data and data[unit_field]:
                    unit = self.session.query(Unit).get(uuid.UUID(data[unit_field]))
                    if not unit:
                        raise ValueError(f'{unit_field}对应的单位不存在')
            
            # 更新字段
            for field, value in data.items():
                if hasattr(category, field) and field not in ['id', 'created_by', 'created_at']:
                    setattr(category, field, value)
            
            # 设置更新者
            user_id = updated_by
            if not user_id and hasattr(g, 'current_user') and g.current_user:
                user_id = g.current_user.id
            
            category.updated_by = user_id
            self.commit()
            
            return self.get_material_category_by_id(category.id)
        except Exception as e:
            self.rollback()
            raise e
    
    def delete_material_category(self, category_id):
        """
        删除材料分类
        
        Args:
            category_id: 材料分类ID
            
        Returns:
            bool: 删除是否成功
        """
        try:
            category = self.session.query(MaterialCategory).get(uuid.UUID(category_id))
            if not category:
                raise ValueError('材料分类不存在')
            
            # 这里可以添加删除前的业务检查
            # 例如检查是否有关联的材料等
            
            self.session.delete(category)
            self.commit()
            
            return True
        except Exception as e:
            self.rollback()
            raise e
    
    def batch_update_material_categories(self, updates):
        """
        批量更新材料分类
        
        Args:
            updates: 更新数据列表
            
        Returns:
            list: 更新后的材料分类列表
        """
        results = []
        
        for update_data in updates:
            category_id = update_data.get('id')
            if not category_id:
                continue
            
            try:
                # 提取updated_by参数
                updated_by = update_data.pop('updated_by', None)
                result = self.update_material_category(category_id, update_data, updated_by)
                results.append(result)
            except Exception as e:
                # 记录错误但继续处理其他记录
                results.append({
                    'id': category_id,
                    'error': str(e)
                })
        
        return results
    
    def get_material_types(self):
        """获取材料属性选项"""
        return ['主材', '辅材']
    
    def get_units(self):
        """获取单位列表"""
        try:
            units = self.session.query(Unit).filter(Unit.is_enabled == True).all()
            return [{'id': str(unit.id), 'name': unit.unit_name} for unit in units]
        except Exception as e:
            raise e 