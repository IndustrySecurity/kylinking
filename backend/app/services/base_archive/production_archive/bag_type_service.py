# -*- coding: utf-8 -*-
"""
BagType 服务
"""

from app.services.base_service import TenantAwareService
from app.extensions import db
from sqlalchemy import func, text, and_, or_
from sqlalchemy.exc import IntegrityError
import uuid
from datetime import datetime
import re

class BagTypeService(TenantAwareService):
    """袋型管理服务"""
    
    def get_bag_types(self, page=1, per_page=20, search=None, is_enabled=None):
        """获取袋型列表"""
        try:
            from app.models.basic_data import BagType, BagTypeStructure, CalculationScheme
            
            # 构建查询
            query = self.session.query(BagType)
            
            # 搜索条件
            if search:
                search_pattern = f"%{search}%"
                query = query.filter(or_(
                    BagType.bag_type_name.ilike(search_pattern),
                    BagType.spec_expression.ilike(search_pattern),
                    BagType.description.ilike(search_pattern)
                ))
            
            # 启用状态筛选
            if is_enabled is not None:
                query = query.filter(BagType.is_enabled == is_enabled)
            
            # 排序
            query = query.order_by(BagType.sort_order, BagType.bag_type_name)
            
            # 分页
            total = query.count()
            bag_types = query.offset((page - 1) * per_page).limit(per_page).all()
            
            # 为每个袋型获取结构信息
            bag_types_with_structures = []
            for bag_type in bag_types:
                bag_type_dict = bag_type.to_dict(include_user_info=True)
                
                # 获取该袋型的结构列表
                structures = self.session.query(BagTypeStructure).filter(
                    BagTypeStructure.bag_type_id == bag_type.id
                ).order_by(BagTypeStructure.sort_order, BagTypeStructure.created_at).all()
                
                # 获取计算方案信息的辅助函数
                def get_scheme_info(scheme_id):
                    if scheme_id:
                        scheme = self.session.query(CalculationScheme).get(scheme_id)
                        if scheme:
                            return {
                                'id': str(scheme.id),
                                'name': scheme.scheme_name,
                                'formula': scheme.scheme_formula
                            }
                    return None
                
                bag_type_dict['structures'] = []
                for structure in structures:
                    # 获取创建人信息
                    created_by_name = None
                    if structure.created_by:
                        from app.models.user import User
                        creator = self.session.query(User).get(structure.created_by)
                        created_by_name = creator.get_full_name() if creator else '未知用户'
                    
                    structure_info = {
                        'id': str(structure.id),
                        'structure_name': structure.structure_name,
                        'image_url': structure.image_url,
                        'sort_order': structure.sort_order,
                        'structure_expression': get_scheme_info(structure.structure_expression_id),
                        'expand_length_formula': get_scheme_info(structure.expand_length_formula_id),
                        'expand_width_formula': get_scheme_info(structure.expand_width_formula_id),
                        'material_length_formula': get_scheme_info(structure.material_length_formula_id),
                        'material_width_formula': get_scheme_info(structure.material_width_formula_id),
                        'single_piece_width_formula': get_scheme_info(structure.single_piece_width_formula_id),
                        'created_at': structure.created_at.isoformat() if structure.created_at else None,
                        'created_by_name': created_by_name
                    }
                    bag_type_dict['structures'].append(structure_info)
                
                bag_types_with_structures.append(bag_type_dict)
            
            return {
                'bag_types': bag_types_with_structures,
                'total': total,
                'current_page': page,
                'per_page': per_page,
                'pages': (total + per_page - 1) // per_page
            }
            
        except Exception as e:
            raise ValueError(f"获取袋型列表失败: {str(e)}")
    
    def get_bag_type(self, bag_type_id):
        """获取袋型详情"""
        try:
            from app.models.basic_data import BagType
            
            bag_type = self.session.query(BagType).get(uuid.UUID(bag_type_id))
            if not bag_type:
                raise ValueError("袋型不存在")
            
            return bag_type.to_dict(include_user_info=True)
            
        except Exception as e:
            raise ValueError(f"获取袋型详情失败: {str(e)}")
    
    def create_bag_type(self, data, created_by):
        """创建袋型"""
        try:
            from app.models.basic_data import BagType
            
            # 验证袋型名称唯一性
            existing = self.session.query(BagType).filter(
                BagType.bag_type_name == data['bag_type_name']
            ).first()
            if existing:
                raise ValueError("袋型名称已存在")
            
            # 验证单位是否存在
            production_unit_id = None
            sales_unit_id = None
            
            if data.get('production_unit_id'):
                from app.models.basic_data import Unit
                production_unit_id = uuid.UUID(data['production_unit_id'])
                production_unit = self.session.query(Unit).get(production_unit_id)
                if not production_unit:
                    raise ValueError("生产单位不存在")
                if not production_unit.is_enabled:
                    raise ValueError("生产单位未启用")
            
            if data.get('sales_unit_id'):
                from app.models.basic_data import Unit
                sales_unit_id = uuid.UUID(data['sales_unit_id'])
                sales_unit = self.session.query(Unit).get(sales_unit_id)
                if not sales_unit:
                    raise ValueError("销售单位不存在")
                if not sales_unit.is_enabled:
                    raise ValueError("销售单位未启用")
            
            # 创建袋型对象
            bag_type = self.create_with_tenant(BagType,
                bag_type_name=data['bag_type_name'],
                spec_expression=data.get('spec_expression'),
                production_unit_id=production_unit_id,
                sales_unit_id=sales_unit_id,
                difficulty_coefficient=data.get('difficulty_coefficient', 0),
                bag_making_unit_price=data.get('bag_making_unit_price', 0),
                sort_order=data.get('sort_order', 0),
                is_roll_film=data.get('is_roll_film', False),
                is_custom_spec=data.get('is_custom_spec', False),
                is_strict_bag_type=data.get('is_strict_bag_type', True),
                is_process_judgment=data.get('is_process_judgment', False),
                is_diaper=data.get('is_diaper', False),
                is_woven_bag=data.get('is_woven_bag', False),
                is_label=data.get('is_label', False),
                is_antenna=data.get('is_antenna', False),
                description=data.get('description', ''),
                is_enabled=data.get('is_enabled', True),
                created_by=uuid.UUID(created_by)
            )
            
            self.commit()
            
            return bag_type.to_dict(include_user_info=True)
                        
        except Exception as e:
            self.rollback()
            raise ValueError(f"创建袋型失败: {str(e)}")
    
    def update_bag_type(self, bag_type_id, data, updated_by):
        """更新袋型"""
        try:
            from app.models.basic_data import BagType
            
            bag_type = self.get_session().query(BagType).get(uuid.UUID(bag_type_id))
            if not bag_type:
                raise ValueError("袋型不存在")
            
            # 验证袋型名称唯一性（排除自己）
            if 'bag_type_name' in data and data['bag_type_name'] != bag_type.bag_type_name:
                existing = self.get_session().query(BagType).filter(
                    BagType.bag_type_name == data['bag_type_name'],
                    BagType.id != bag_type.id
                ).first()
                if existing:
                    raise ValueError("袋型名称已存在")
            
            # 验证单位
            if 'production_unit_id' in data and data['production_unit_id']:
                from app.models.basic_data import Unit
                production_unit = self.get_session().query(Unit).get(uuid.UUID(data['production_unit_id']))
                if not production_unit:
                    raise ValueError("生产单位不存在")
                if not production_unit.is_enabled:
                    raise ValueError("生产单位未启用")
            
            if 'sales_unit_id' in data and data['sales_unit_id']:
                from app.models.basic_data import Unit
                sales_unit = self.get_session().query(Unit).get(uuid.UUID(data['sales_unit_id']))
                if not sales_unit:
                    raise ValueError("销售单位不存在")
                if not sales_unit.is_enabled:
                    raise ValueError("销售单位未启用")
            
            # 更新字段
            for key, value in data.items():
                if hasattr(bag_type, key):
                    setattr(bag_type, key, value)
            
            bag_type.updated_by = uuid.UUID(updated_by)
            
            self.commit()
            return bag_type.to_dict(include_user_info=True)
            
        except Exception as e:
            self.rollback()
            raise ValueError(f'更新袋型失败: {str(e)}')
    
    def delete_bag_type(self, bag_type_id):
        """删除袋型"""
        try:
            from app.models.basic_data import BagType, BagTypeStructure
            
            bag_type = self.get_session().query(BagType).get(uuid.UUID(bag_type_id))
            if not bag_type:
                raise ValueError("袋型不存在")
            
            # 先删除相关的袋型结构记录
            self.get_session().query(BagTypeStructure).filter(
                BagTypeStructure.bag_type_id == bag_type.id
            ).delete()
            
            # 再删除袋型记录
            self.get_session().delete(bag_type)
            self.get_session().commit()
            
            return True
            
        except Exception as e:
            self.get_session().rollback()
            raise ValueError(f"删除袋型失败: {str(e)}")
    
    def batch_update_bag_types(self, updates, updated_by):
        """批量更新袋型"""
        try:
            from app.models.basic_data import BagType
            
            updated_bag_types = []
            
            for update_data in updates:
                bag_type_id = update_data.get('id')
                if not bag_type_id:
                    continue
                
                bag_type = self.get_session().query(BagType).get(uuid.UUID(bag_type_id))
                if not bag_type:
                    continue
                
                # 更新指定字段
                update_fields = ['sort_order', 'is_enabled']
                for field in update_fields:
                    if field in update_data:
                        setattr(bag_type, field, update_data[field])
                
                bag_type.updated_by = uuid.UUID(updated_by)
                updated_bag_types.append(bag_type)
            
            self.commit()
            
            return [bag_type.to_dict(include_user_info=True) for bag_type in updated_bag_types]
            
        except Exception as e:
            self.rollback()
            raise ValueError(f"批量更新袋型失败: {str(e)}")
    
    def get_bag_type_options(self):
        """获取袋型选项数据"""
        try:
            from app.models.basic_data import BagType
            
            bag_types = BagType.get_enabled_list()
            return [
                {
                    'value': str(bag_type.id),
                    'label': bag_type.bag_type_name,
                    'spec_expression': bag_type.spec_expression
                }
                for bag_type in bag_types
            ]
        except Exception as e:
            raise ValueError(f"获取袋型选项失败: {str(e)}")
    
    def get_form_options(self):
        """获取袋型表单选项数据"""
        try:
            from app.models.basic_data import Unit, CalculationScheme
            
            # 获取单位选项
            units = self.get_session().query(Unit).filter_by(is_enabled=True).order_by(Unit.sort_order, Unit.unit_name).all()
            unit_options = [
                {
                    'value': str(unit.id),
                    'label': unit.unit_name
                }
                for unit in units
            ]
            
            # 获取计算方案选项
            calculation_schemes = self.get_session().query(CalculationScheme).filter_by(is_enabled=True).order_by(CalculationScheme.sort_order, CalculationScheme.scheme_name).all()
            scheme_options = [
                {
                    'value': str(scheme.id),
                    'label': scheme.scheme_name
                }
                for scheme in calculation_schemes
            ]
            
            # 返回所有选项数据
            return {
                'units': unit_options,
                'spec_expressions': [
                    {'value': 'length_width', 'label': '长×宽', 'description': '标准矩形规格'},
                    {'value': 'length_width_gusset', 'label': '长×宽×底折', 'description': '带底折的矩形'},
                    {'value': 'diameter_height', 'label': '直径×高', 'description': '圆形规格'},
                    {'value': 'custom', 'label': '自定义', 'description': '自定义规格表达式'}
                ],
                'structure_expressions': [
                    {'value': 'single_layer', 'label': '单层结构', 'description': '简单单层薄膜'},
                    {'value': 'multi_layer', 'label': '多层结构', 'description': '复合多层薄膜'},
                    {'value': 'woven', 'label': '编织结构', 'description': '编织袋结构'},
                    {'value': 'laminated', 'label': '复合结构', 'description': '复合材料结构'}
                ],
                'formulas': scheme_options
            }
            
        except Exception as e:
            raise ValueError(f"获取表单选项失败: {str(e)}")
    
    def get_unit_options(self):
        """获取单位选项数据"""
        try:
            from app.models.basic_data import Unit
            
            units = Unit.get_enabled_list()
            return [
                {
                    'value': str(unit.id),
                    'label': unit.unit_name
                }
                for unit in units
            ]
        except Exception as e:
            raise ValueError(f"获取单位选项失败: {str(e)}")
    
    def get_calculation_scheme_options(self):
        """获取规格表达式选项（从计算方案获取）"""
        try:
            from app.models.basic_data import CalculationScheme
            
            schemes = self.get_session().query(CalculationScheme).filter(
                CalculationScheme.scheme_category == 'bag_spec',
                CalculationScheme.is_enabled == True
            ).order_by(CalculationScheme.sort_order, CalculationScheme.scheme_name).all()
            
            return [
                {
                    'value': scheme.scheme_formula,
                    'label': scheme.scheme_name,
                    'description': scheme.description
                }
                for scheme in schemes
            ]
        except Exception as e:
            raise ValueError(f"获取规格表达式选项失败: {str(e)}")
    
    def get_calculation_schemes_by_category(self, category):
        """根据分类获取计算方案选项"""
        try:
            from app.models.basic_data import CalculationScheme
            
            schemes = self.get_session().query(CalculationScheme).filter(
                CalculationScheme.scheme_category == category,
                CalculationScheme.is_enabled == True
            ).order_by(CalculationScheme.sort_order, CalculationScheme.scheme_name).all()
            
            return [
                {
                    'value': str(scheme.id),
                    'label': scheme.scheme_name,
                    'category': scheme.scheme_category,
                    'description': scheme.description or '',
                    'formula': scheme.scheme_formula or ''
                }
                for scheme in schemes
            ]
        except Exception as e:
            raise ValueError(f"获取{category}分类计算方案选项失败: {str(e)}")
    
    def get_all_formula_options(self):
        """获取袋型结构所需的所有公式选项"""
        try:
            return {
                # 结构表达式选项（袋型规格分类）
                'structure_expressions': self.get_calculation_schemes_by_category('bag_spec'),
                # 公式选项（袋型公式分类）- 用于展长、展宽、用料长、用料宽、单片宽公式
                'formulas': self.get_calculation_schemes_by_category('bag_formula')
            }
        except Exception as e:
            raise ValueError(f"获取袋型结构公式选项失败: {str(e)}")
    
    # ====================== 袋型结构管理 ======================
    
    def get_bag_type_structures(self, bag_type_id):
        """获取袋型结构列表"""
        try:
            from app.models.basic_data import BagTypeStructure
            
            structures = self.get_session().query(BagTypeStructure).filter(
                BagTypeStructure.bag_type_id == uuid.UUID(bag_type_id)
            ).order_by(BagTypeStructure.sort_order, BagTypeStructure.created_at).all()
            
            return {
                'success': True,
                'data': {
                    'structures': [structure.to_dict(include_user_info=True, include_formulas=True) for structure in structures]
                }
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'获取袋型结构列表失败: {str(e)}'
            }
    
    def update_bag_type_structure(self, structure_id, data, updated_by):
        """更新袋型结构"""
        try:
            from app.models.basic_data import BagTypeStructure
            
            structure = self.get_session().query(BagTypeStructure).get(uuid.UUID(structure_id))
            if not structure:
                raise ValueError("袋型结构不存在")
            
            # 更新字段
            update_fields = [
                'structure_name', 'structure_expression_id', 'expand_length_formula_id',
                'expand_width_formula_id', 'material_length_formula_id', 
                'material_width_formula_id', 'single_piece_width_formula_id',
                'sort_order', 'image_url'
            ]
            
            for field in update_fields:
                if field in data:
                    value = data[field]
                    if field.endswith('_id') and value:
                        # 处理UUID字段
                        value = uuid.UUID(value)
                    setattr(structure, field, value)
            
            structure.updated_by = uuid.UUID(updated_by)
            
            self.commit()
            
            return {
                'success': True,
                'message': '袋型结构更新成功',
                'data': structure.to_dict(include_user_info=True)
            }
            
        except Exception as e:
            self.rollback()
            return {
                'success': False,
                'message': f'更新袋型结构失败: {str(e)}'
            }
    
    def delete_bag_type_structure(self, structure_id):
        """删除袋型结构"""
        try:
            from app.models.basic_data import BagTypeStructure
            
            structure = self.get_session().query(BagTypeStructure).get(uuid.UUID(structure_id))
            if not structure:
                raise ValueError("袋型结构不存在")
            
            self.get_session().delete(structure)
            self.get_session().commit()
            
            return {
                'success': True,
                'message': '袋型结构删除成功'
            }
            
        except Exception as e:
            self.get_session().rollback()
            return {
                'success': False,
                'message': f'删除袋型结构失败: {str(e)}'
            }
    
    def batch_update_bag_type_structures(self, bag_type_id, structures_data, updated_by):
        """批量更新袋型结构"""
        try:
            from app.models.basic_data import BagTypeStructure, CalculationScheme
            
            # 删除现有结构
            self.get_session().query(BagTypeStructure).filter(
                BagTypeStructure.bag_type_id == uuid.UUID(bag_type_id)
            ).delete()
            
            # 获取所有有效的计算方案ID，用于验证
            valid_scheme_ids = set()
            schemes = self.get_session().query(CalculationScheme.id).filter(
                CalculationScheme.is_enabled == True
            ).all()
            valid_scheme_ids = {str(scheme[0]) for scheme in schemes}
            
            # 创建新结构
            for structure_data in structures_data:
                # 处理UUID字段，确保空值转为None，无效值也转为None
                def validate_scheme_id(scheme_id_str):
                    if not scheme_id_str:
                        return None
                    if str(scheme_id_str) not in valid_scheme_ids:
                        # 记录警告但不抛出错误，设为None
                        print(f"警告：计算方案ID {scheme_id_str} 无效，将设为None")
                        return None
                    return uuid.UUID(scheme_id_str)
                
                structure = BagTypeStructure(
                    bag_type_id=uuid.UUID(bag_type_id),
                    structure_name=structure_data.get('structure_name', ''),
                    structure_expression_id=validate_scheme_id(structure_data.get('structure_expression_id')),
                    expand_length_formula_id=validate_scheme_id(structure_data.get('expand_length_formula_id')),
                    expand_width_formula_id=validate_scheme_id(structure_data.get('expand_width_formula_id')),
                    material_length_formula_id=validate_scheme_id(structure_data.get('material_length_formula_id')),
                    material_width_formula_id=validate_scheme_id(structure_data.get('material_width_formula_id')),
                    single_piece_width_formula_id=validate_scheme_id(structure_data.get('single_piece_width_formula_id')),
                    sort_order=structure_data.get('sort_order', 0),
                    image_url=structure_data.get('image_url'),
                    created_by=uuid.UUID(updated_by)
                )
                
                self.get_session().add(structure)
            
            self.commit()
            
            return {
                'success': True,
                'message': '袋型结构批量更新成功'
            }
            
        except Exception as e:
            self.rollback()
            return {
                'success': False,
                'message': f'批量更新袋型结构失败: {str(e)}'
            }


