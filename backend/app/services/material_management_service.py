# -*- coding: utf-8 -*-
"""
材料管理服务层
"""

from typing import Dict, List, Optional, Any
from sqlalchemy import func, and_, or_
from sqlalchemy.orm import joinedload
from app.extensions import db
from app.models.basic_data import (
    Material, MaterialProperty, MaterialSupplier,
    MaterialCategory, Unit, CalculationScheme
)
from app.utils.database import get_current_user_id
import uuid


class MaterialService:
    """材料服务类"""
    
    @staticmethod
    def _set_schema():
        """设置当前租户的schema搜索路径"""
        from flask import g, current_app
        from sqlalchemy import text
        schema_name = getattr(g, 'schema_name', current_app.config.get('DEFAULT_SCHEMA', 'public'))
        if schema_name != 'public':
            db.session.execute(text(f'SET search_path TO {schema_name}, public'))
    
    @classmethod
    def get_materials(
        cls,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        material_category_id: Optional[str] = None,
        inspection_type: Optional[str] = None,
        is_enabled: Optional[bool] = None,
        sort_by: str = 'material_code',
        sort_order: str = 'asc'
    ) -> Dict[str, Any]:
        """获取材料列表"""
        cls._set_schema()
        query = Material.query
        
        # 搜索条件
        if search:
            search_conditions = or_(
                Material.material_name.ilike(f'%{search}%'),
                Material.material_code.ilike(f'%{search}%'),
                Material.specification_model.ilike(f'%{search}%'),
                Material.remarks.ilike(f'%{search}%')
            )
            query = query.filter(search_conditions)
        
        # 材料分类筛选
        if material_category_id:
            query = query.filter(Material.material_category_id == material_category_id)
        
        # 检验类型筛选
        if inspection_type:
            query = query.filter(Material.inspection_type == inspection_type)
        
        # 启用状态筛选
        if is_enabled is not None:
            query = query.filter(Material.is_enabled == is_enabled)
        
        # 排序
        query = query.order_by(Material.sort_order, Material.material_code)
        
        # 分页
        total = query.count()
        materials = query.offset((page - 1) * page_size).limit(page_size).all()
        
        # 构建材料数据，包含用户信息和单位信息
        material_items = []
        for material in materials:
            material_data = material.to_dict()
            
            # 获取单位信息
            if material.unit_id:
                from app.models.basic_data import Unit
                unit = Unit.query.get(material.unit_id)
                if unit:
                    material_data['unit'] = unit.unit_name
                    material_data['unit_name'] = unit.unit_name
                else:
                    material_data['unit'] = ''
                    material_data['unit_name'] = ''
            else:
                material_data['unit'] = ''
                material_data['unit_name'] = ''
            
            # 获取创建人和修改人用户名
            if material.created_by:
                from app.models.user import User
                created_user = User.query.get(material.created_by)
                if created_user:
                    material_data['created_by_name'] = created_user.get_full_name()
                else:
                    material_data['created_by_name'] = '未知用户'
            else:
                material_data['created_by_name'] = '系统'
                
            if material.updated_by:
                from app.models.user import User
                updated_user = User.query.get(material.updated_by)
                if updated_user:
                    material_data['updated_by_name'] = updated_user.get_full_name()
                else:
                    material_data['updated_by_name'] = '未知用户'
            else:
                material_data['updated_by_name'] = ''
            
            material_items.append(material_data)
        
        return {
            'items': material_items,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }
    
    @classmethod
    def get_material_by_id(cls, material_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取材料详情"""
        try:
            material = Material.query.get(uuid.UUID(material_id))
            if not material:
                return None
            
            # 获取材料详情及关联数据
            material_dict = material.to_dict(include_details=True)
            
            # 获取子表数据
            properties = [prop.to_dict() for prop in material.properties]
            suppliers = [supplier.to_dict() for supplier in material.suppliers]
            
            material_dict['properties'] = properties
            material_dict['suppliers'] = suppliers
            
            return material_dict
            
        except Exception as e:
            print(f"获取材料详情失败: {str(e)}")
            return None
    
    @classmethod
    def create_material(cls, data: Dict[str, Any], created_by: str = None) -> Dict[str, Any]:
        """创建材料"""
        try:
            # 设置schema路径
            cls._set_schema()
            
            # 自动生成材料编号
            data['material_code'] = Material.generate_material_code()
            
            # 设置审计字段
            if created_by:
                data['created_by'] = uuid.UUID(created_by)
                data['updated_by'] = uuid.UUID(created_by)
            
            # 提取子表数据
            properties_data = data.pop('properties', [])
            suppliers_data = data.pop('suppliers', [])
            
            # 数据类型转换
            if 'material_category_id' in data and data['material_category_id']:
                data['material_category_id'] = uuid.UUID(data['material_category_id'])
            if 'unit_id' in data and data['unit_id']:
                data['unit_id'] = uuid.UUID(data['unit_id'])
            if 'auxiliary_unit_id' in data and data['auxiliary_unit_id']:
                data['auxiliary_unit_id'] = uuid.UUID(data['auxiliary_unit_id'])
            if 'sales_unit_id' in data and data['sales_unit_id']:
                data['sales_unit_id'] = uuid.UUID(data['sales_unit_id'])
            if 'material_formula_id' in data and data['material_formula_id']:
                data['material_formula_id'] = uuid.UUID(data['material_formula_id'])
            if 'subject_id' in data and data['subject_id']:
                data['subject_id'] = uuid.UUID(data['subject_id'])
            if 'substitute_material_category_id' in data and data['substitute_material_category_id']:
                data['substitute_material_category_id'] = uuid.UUID(data['substitute_material_category_id'])
            
            # 创建主记录
            material = Material(
                **data
            )
            
            db.session.add(material)
            db.session.flush()  # 获取材料ID
            
            # 创建子表记录
            for prop_data in properties_data:
                prop = MaterialProperty(
                    material_id=material.id,
                    **prop_data
                )
                db.session.add(prop)
            
            for supplier_data in suppliers_data:
                if 'supplier_id' in supplier_data and supplier_data['supplier_id']:
                    supplier_data['supplier_id'] = uuid.UUID(supplier_data['supplier_id'])
                
                supplier = MaterialSupplier(
                    material_id=material.id,
                    **supplier_data
                )
                db.session.add(supplier)
            
            db.session.commit()
            
            return {
                'success': True,
                'message': '材料创建成功',
                'material_id': str(material.id)
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'材料创建失败: {str(e)}'
            }
    
    @classmethod
    def update_material(cls, material_id: str, data: Dict[str, Any], updated_by: str = None) -> Dict[str, Any]:
        """更新材料"""
        try:
            material = Material.query.get(uuid.UUID(material_id))
            if not material:
                return {
                    'success': False,
                    'message': '材料不存在'
                }
            
            # 设置审计字段
            if updated_by:
                data['updated_by'] = uuid.UUID(updated_by)
            
            # 提取子表数据
            properties_data = data.pop('properties', None)
            suppliers_data = data.pop('suppliers', None)
            
            # 数据类型转换
            if 'material_category_id' in data and data['material_category_id']:
                data['material_category_id'] = uuid.UUID(data['material_category_id'])
            if 'unit_id' in data and data['unit_id']:
                data['unit_id'] = uuid.UUID(data['unit_id'])
            if 'auxiliary_unit_id' in data and data['auxiliary_unit_id']:
                data['auxiliary_unit_id'] = uuid.UUID(data['auxiliary_unit_id'])
            if 'sales_unit_id' in data and data['sales_unit_id']:
                data['sales_unit_id'] = uuid.UUID(data['sales_unit_id'])
            if 'material_formula_id' in data and data['material_formula_id']:
                data['material_formula_id'] = uuid.UUID(data['material_formula_id'])
            if 'subject_id' in data and data['subject_id']:
                data['subject_id'] = uuid.UUID(data['subject_id'])
            if 'substitute_material_category_id' in data and data['substitute_material_category_id']:
                data['substitute_material_category_id'] = uuid.UUID(data['substitute_material_category_id'])
            
            # 更新主记录字段
            for field, value in data.items():
                if hasattr(material, field):
                    setattr(material, field, value)
            
            # 更新子表数据
            if properties_data is not None:
                # 删除现有属性
                MaterialProperty.query.filter_by(material_id=material.id).delete()
                
                # 添加新属性
                for prop_data in properties_data:
                    prop = MaterialProperty(
                        material_id=material.id,
                        **prop_data
                    )
                    db.session.add(prop)
            
            if suppliers_data is not None:
                # 删除现有供应商
                MaterialSupplier.query.filter_by(material_id=material.id).delete()
                
                # 添加新供应商
                for supplier_data in suppliers_data:
                    if 'supplier_id' in supplier_data and supplier_data['supplier_id']:
                        supplier_data['supplier_id'] = uuid.UUID(supplier_data['supplier_id'])
                    
                    supplier = MaterialSupplier(
                        material_id=material.id,
                        **supplier_data
                    )
                    db.session.add(supplier)
            
            db.session.commit()
            
            return {
                'success': True,
                'message': '材料更新成功'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'材料更新失败: {str(e)}'
            }
    
    @classmethod
    def delete_material(cls, material_id: str) -> Dict[str, Any]:
        """删除材料"""
        try:
            material = Material.query.get(uuid.UUID(material_id))
            if not material:
                return {
                    'success': False,
                    'message': '材料不存在'
                }
            
            # 删除子表数据(由于设置了cascade，会自动删除)
            db.session.delete(material)
            db.session.commit()
            
            return {
                'success': True,
                'message': '材料删除成功'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'材料删除失败: {str(e)}'
            }
    
    @classmethod
    def get_form_options(cls) -> Dict[str, Any]:
        """获取表单选项数据"""
        try:
            # 材料分类选项
            material_categories = []
            try:
                categories = MaterialCategory.get_enabled_list()
                material_categories = [{'id': str(cat.id), 'material_name': cat.material_name} for cat in categories]
            except Exception as e:
                print(f"获取材料分类失败: {str(e)}")
            
            # 单位选项
            units = []
            try:
                unit_list = Unit.get_enabled_list()
                units = [{'id': str(unit.id), 'unit_name': unit.unit_name} for unit in unit_list]
            except Exception as e:
                print(f"获取单位列表失败: {str(e)}")
            
            # 检验类型选项
            inspection_types = Material.get_inspection_type_options()
            
            # 计算方案选项（所有类型）
            calculation_schemes = []
            try:
                schemes = CalculationScheme.query.filter_by(is_enabled=True).all()
                calculation_schemes = [{'id': str(scheme.id), 'scheme_name': scheme.scheme_name, 'scheme_category': scheme.scheme_category} for scheme in schemes]
            except Exception as e:
                print(f"获取计算方案失败: {str(e)}")
            
            # 科目选项（示例）
            subjects = [
                {'id': 'raw_materials', 'name': '原材料'},
                {'id': 'auxiliary_materials', 'name': '辅助材料'},
                {'id': 'packaging_materials', 'name': '包装材料'},
            ]
            
            # 保密编码选项（示例）
            security_codes = [
                {'id': 'public', 'name': '公开'},
                {'id': 'internal', 'name': '内部'},
                {'id': 'confidential', 'name': '机密'},
            ]
            
            return {
                'material_categories': material_categories,
                'units': units,
                'inspection_types': inspection_types,
                'calculation_schemes': calculation_schemes,
                'subjects': subjects,
                'security_codes': security_codes
            }
            
        except Exception as e:
            print(f"获取表单选项失败: {str(e)}")
            return {
                'material_categories': [],
                'units': [],
                'inspection_types': [
                    {'value': 'exempt', 'label': '免检'},
                    {'value': 'spot_check', 'label': '抽检'},
                    {'value': 'full_check', 'label': '全检'}
                ],
                'calculation_schemes': [],
                'subjects': [],
                'security_codes': []
            }
    
    @classmethod
    def get_material_category_details(cls, category_id: str) -> Dict[str, Any]:
        """获取材料分类详情，用于自动填充"""
        try:
            category = MaterialCategory.query.get(uuid.UUID(category_id))
            if not category:
                return {}
            
            return {
                'material_attribute': category.material_type,
                'unit_id': str(category.base_unit_id) if category.base_unit_id else None,
                'auxiliary_unit_id': str(category.auxiliary_unit_id) if category.auxiliary_unit_id else None,
                'sales_unit_id': str(category.sales_unit_id) if category.sales_unit_id else None,
                'density': float(category.density) if category.density else None,
                'square_weight': float(category.square_weight) if category.square_weight else None,
                'shelf_life_days': category.shelf_life,
                'inspection_standard': category.inspection_standard,
                'quality_grade': category.quality_grade,
                'latest_purchase_price': float(category.latest_purchase_price) if category.latest_purchase_price else None,
                'sales_price': float(category.sales_price) if category.sales_price else None,
                'subject': category.account_subject,
                'warning_days': category.warning_days,
                # 各种布尔标识
                'is_paper': category.enable_batch,
                'is_surface_printing_ink': category.is_ink,
                'is_carton': category.is_accessory,
                'is_paper_core': category.is_consumable,
                'is_zipper': category.is_recyclable,
            }
            
        except Exception as e:
            print(f"获取材料分类详情失败: {str(e)}")
            return {}
    
    @classmethod
    def batch_update_materials(cls, data: Dict[str, Any], updated_by: str = None) -> Dict[str, Any]:
        """批量更新材料"""
        try:
            material_ids = data.get('material_ids', [])
            update_fields = data.get('update_fields', {})
            
            if not material_ids or not update_fields:
                return {
                    'success': False,
                    'message': '缺少必要参数'
                }
            
            # 设置审计字段
            if updated_by:
                update_fields['updated_by'] = uuid.UUID(updated_by)
            
            # 数据类型转换
            if 'material_category_id' in update_fields and update_fields['material_category_id']:
                update_fields['material_category_id'] = uuid.UUID(update_fields['material_category_id'])
            
            # 批量更新
            Material.query.filter(
                Material.id.in_([uuid.UUID(mid) for mid in material_ids])
            ).update(update_fields, synchronize_session=False)
            
            db.session.commit()
            
            return {
                'success': True,
                'message': f'成功更新 {len(material_ids)} 条材料记录'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'批量更新失败: {str(e)}'
            } 