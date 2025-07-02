# -*- coding: utf-8 -*-
"""
材料分类服务
"""

from app.models.basic_data import MaterialCategory, Unit
from app.extensions import db
from app.services.base_service import TenantAwareService
from flask import g
from sqlalchemy import or_, and_
import uuid


class MaterialCategoryService(TenantAwareService):
    """材料分类服务类"""
    
    def get_material_categories(self, page=1, per_page=20, search=None, material_type=None, is_enabled=None):
        """
        获取材料分类列表
        
        Args:
            page: 页码
            per_page: 每页数量
            search: 搜索关键词
            material_type: 材料属性筛选
            is_enabled: 启用状态筛选
            
        Returns:
            dict: 包含材料分类列表和分页信息
        """
        self._set_schema()
        query = self.get_session().query(MaterialCategory)
        
        # 搜索条件
        if search:
            search_filter = or_(
                MaterialCategory.material_name.ilike(f'%{search}%'),
                MaterialCategory.account_subject.ilike(f'%{search}%')
            )
            query = query.filter(search_filter)
        
        # 材料属性筛选
        if material_type:
            query = query.filter(MaterialCategory.material_type == material_type)
        
        # 启用状态筛选
        if is_enabled is not None:
            query = query.filter(MaterialCategory.is_active == is_enabled)
        
        # 排序
        query = query.order_by(MaterialCategory.display_order, MaterialCategory.material_name)
        
        # 分页
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        # 获取单位信息
        units = {str(unit.id): unit.unit_name for unit in self.get_session().query(Unit).filter(Unit.is_enabled == True).all()}
        
        # 转换为字典并添加单位名称
        material_categories = []
        for category in pagination.items:
            category_dict = category.to_dict()
            
            # 添加单位名称
            category_dict['base_unit_name'] = units.get(str(category_dict['base_unit_id']), '')
            category_dict['auxiliary_unit_name'] = units.get(str(category_dict['auxiliary_unit_id']), '')
            category_dict['sales_unit_name'] = units.get(str(category_dict['sales_unit_id']), '')
            
            material_categories.append(category_dict)
        
        return {
            'material_categories': material_categories,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page,
            'per_page': pagination.per_page,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next
        }
    
    def get_material_category_by_id(self, category_id):
        """
        根据ID获取材料分类
        
        Args:
            category_id: 材料分类ID
            
        Returns:
            dict: 材料分类信息
        """
        self._set_schema()
        category = self.get_session().query(MaterialCategory).get(uuid.UUID(category_id))
        if not category:
            return None
        
        # 获取单位信息
        units = {str(unit.id): unit.unit_name for unit in self.get_session().query(Unit).filter(Unit.is_enabled == True).all()}
        
        category_dict = category.to_dict()
        
        # 添加单位名称
        category_dict['base_unit_name'] = units.get(str(category_dict['base_unit_id']), '')
        category_dict['auxiliary_unit_name'] = units.get(str(category_dict['auxiliary_unit_id']), '')
        category_dict['sales_unit_name'] = units.get(str(category_dict['sales_unit_id']), '')
        
        return category_dict
    
    def create_material_category(self, data, created_by=None):
        """
        创建材料分类
        
        Args:
            data: 材料分类数据
            created_by: 创建者ID
            
        Returns:
            dict: 创建的材料分类信息
        """
        self._set_schema()
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
                unit = self.get_session().query(Unit).get(uuid.UUID(unit_id))
                if not unit:
                    raise ValueError(f'{unit_field}对应的单位不存在')
        
        # 获取创建者ID
        user_id = created_by
        if not user_id and hasattr(g, 'current_user') and g.current_user:
            user_id = g.current_user.id
        
        # 创建材料分类
        category = MaterialCategory(
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
        
        self.get_session().add(category)
        self.get_session().commit()
        
        return self.get_material_category_by_id(category.id)
    
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
        self._set_schema()
        category = self.get_session().query(MaterialCategory).get(uuid.UUID(category_id))
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
                unit = self.get_session().query(Unit).get(uuid.UUID(data[unit_field]))
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
        self.get_session().commit()
        
        return self.get_material_category_by_id(category.id)
    
    def delete_material_category(self, category_id):
        """
        删除材料分类
        
        Args:
            category_id: 材料分类ID
            
        Returns:
            bool: 删除是否成功
        """
        self._set_schema()
        category = self.get_session().query(MaterialCategory).get(uuid.UUID(category_id))
        if not category:
            raise ValueError('材料分类不存在')
        
        # 这里可以添加删除前的业务检查
        # 例如检查是否有关联的材料等
        
        self.get_session().delete(category)
        self.get_session().commit()
        
        return True
    
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
        self._set_schema()
        units = self.get_session().query(Unit).filter(Unit.is_enabled == True).all()
        return [{'id': str(unit.id), 'name': unit.unit_name} for unit in units] 