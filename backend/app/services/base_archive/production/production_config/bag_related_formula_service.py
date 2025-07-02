# -*- coding: utf-8 -*-
"""
BagRelatedFormula 服务
"""

from app.services.base_service import TenantAwareService
from app.extensions import db
from sqlalchemy import func, text, and_, or_
from sqlalchemy.exc import IntegrityError
import uuid
from datetime import datetime
import re

class BagRelatedFormulaService(TenantAwareService):
    """袋型相关公式服务"""
    
    def _set_schema(self):
        """设置当前租户的schema搜索路径"""
        from flask import g, current_app
        from sqlalchemy import text
        schema_name = getattr(g, 'schema_name', current_app.config.get('DEFAULT_SCHEMA', 'public'))
        if schema_name != 'public':
            current_app.logger.info(f"Setting search_path to {schema_name} in BagRelatedFormulaService")
            self.get_session().execute(text(f'SET search_path TO {schema_name}, public'))
    
    def get_bag_related_formulas(self, page=1, per_page=20, search=None, bag_type_id=None, is_enabled=None):
        """获取袋型相关公式列表"""
        try:
            self._set_schema()
            from app.models.basic_data import BagRelatedFormula, BagType
            
            # 构建查询
            query = self.get_session().query(BagRelatedFormula).join(BagType)
            
            # 搜索条件
            if search:
                search_pattern = f"%{search}%"
                query = query.filter(or_(
                    BagType.bag_type_name.ilike(search_pattern),
                    BagRelatedFormula.dimension_description.ilike(search_pattern),
                    BagRelatedFormula.description.ilike(search_pattern)
                ))
            
            # 袋型筛选
            if bag_type_id:
                query = query.filter(BagRelatedFormula.bag_type_id == uuid.UUID(bag_type_id))
            
            # 启用状态筛选
            if is_enabled is not None:
                query = query.filter(BagRelatedFormula.is_enabled == is_enabled)
            
            # 排序
            query = query.order_by(BagRelatedFormula.sort_order, BagType.bag_type_name)
            
            # 分页
            total = query.count()
            formulas = query.offset((page - 1) * per_page).limit(per_page).all()
            
            return {
                'success': True,
                'data': {
                    'formulas': [formula.to_dict(include_user_info=True, include_formulas=True) for formula in formulas],
                    'total': total,
                    'current_page': page,
                    'per_page': per_page
                }
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'获取袋型相关公式列表失败: {str(e)}'
            }
    
    def get_bag_related_formula(self, formula_id):
        """获取单个袋型相关公式"""
        try:
            self._set_schema()
            from app.models.basic_data import BagRelatedFormula
            
            formula = self.get_session().query(BagRelatedFormula).get(uuid.UUID(formula_id))
            if not formula:
                raise ValueError("袋型相关公式不存在")
            
            return {
                'success': True,
                'data': formula.to_dict(include_user_info=True, include_formulas=True)
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'获取袋型相关公式失败: {str(e)}'
            }
    
    def create_bag_related_formula(self, data, created_by):
        """创建袋型相关公式"""
        try:
            self._set_schema()
            from app.models.basic_data import BagRelatedFormula
            
            # 处理UUID字段
            def to_uuid_or_none(value):
                if value:
                    return uuid.UUID(value) if isinstance(value, str) else value
                return None
            
            formula = BagRelatedFormula(
                bag_type_id=uuid.UUID(data['bag_type_id']),
                meter_formula_id=to_uuid_or_none(data.get('meter_formula_id')),
                square_formula_id=to_uuid_or_none(data.get('square_formula_id')),
                material_width_formula_id=to_uuid_or_none(data.get('material_width_formula_id')),
                per_piece_formula_id=to_uuid_or_none(data.get('per_piece_formula_id')),
                dimension_description=data.get('dimension_description', ''),
                sort_order=data.get('sort_order', 0),
                description=data.get('description', ''),
                is_enabled=data.get('is_enabled', True),
                created_by=uuid.UUID(created_by)
            )
            
            self.get_session().add(formula)
            self.get_session().commit()
            
            return {
                'success': True,
                'message': '袋型相关公式创建成功',
                'data': formula.to_dict(include_user_info=True, include_formulas=True)
            }
            
        except Exception as e:
            self.get_session().rollback()
            return {
                'success': False,
                'message': f'创建袋型相关公式失败: {str(e)}'
            }
    
    def update_bag_related_formula(self, formula_id, data, updated_by):
        """更新袋型相关公式"""
        try:
            self._set_schema()
            from app.models.basic_data import BagRelatedFormula
            
            formula = self.get_session().query(BagRelatedFormula).get(uuid.UUID(formula_id))
            if not formula:
                raise ValueError("袋型相关公式不存在")
            
            # 处理UUID字段
            def to_uuid_or_none(value):
                if value:
                    return uuid.UUID(value) if isinstance(value, str) else value
                return None
            
            # 更新字段
            if 'bag_type_id' in data:
                formula.bag_type_id = uuid.UUID(data['bag_type_id'])
            if 'meter_formula_id' in data:
                formula.meter_formula_id = to_uuid_or_none(data['meter_formula_id'])
            if 'square_formula_id' in data:
                formula.square_formula_id = to_uuid_or_none(data['square_formula_id'])
            if 'material_width_formula_id' in data:
                formula.material_width_formula_id = to_uuid_or_none(data['material_width_formula_id'])
            if 'per_piece_formula_id' in data:
                formula.per_piece_formula_id = to_uuid_or_none(data['per_piece_formula_id'])
            if 'dimension_description' in data:
                formula.dimension_description = data['dimension_description']
            if 'sort_order' in data:
                formula.sort_order = data['sort_order']
            if 'description' in data:
                formula.description = data['description']
            if 'is_enabled' in data:
                formula.is_enabled = data['is_enabled']
            
            formula.updated_by = uuid.UUID(updated_by)
            
            self.get_session().commit()
            
            return {
                'success': True,
                'message': '袋型相关公式更新成功',
                'data': formula.to_dict(include_user_info=True, include_formulas=True)
            }
            
        except Exception as e:
            self.get_session().rollback()
            return {
                'success': False,
                'message': f'更新袋型相关公式失败: {str(e)}'
            }
    
    def delete_bag_related_formula(self, formula_id):
        """删除袋型相关公式"""
        try:
            self._set_schema()
            from app.models.basic_data import BagRelatedFormula
            
            formula = self.get_session().query(BagRelatedFormula).get(uuid.UUID(formula_id))
            if not formula:
                raise ValueError("袋型相关公式不存在")
            
            self.get_session().delete(formula)
            self.get_session().commit()
            
            return {
                'success': True,
                'message': '袋型相关公式删除成功'
            }
            
        except Exception as e:
            self.get_session().rollback()
            return {
                'success': False,
                'message': f'删除袋型相关公式失败: {str(e)}'
            }
    
    def batch_update_bag_related_formulas(self, updates, updated_by):
        """批量更新袋型相关公式"""
        try:
            self._set_schema()
            from app.models.basic_data import BagRelatedFormula
            
            for update in updates:
                formula_id = update['id']
                formula_data = update['data']
                
                result = self.update_bag_related_formula(formula_id, formula_data, updated_by)
                if not result['success']:
                    raise Exception(result['message'])
            
            return {
                'success': True,
                'message': '批量更新袋型相关公式成功'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'批量更新袋型相关公式失败: {str(e)}'
            }
    
    def get_bag_related_formula_options(self):
        """获取袋型相关公式选项数据"""
        try:
            self._set_schema()
            from app.models.basic_data import BagType, CalculationScheme
            
            # 获取袋型选项
            bag_types = self.get_session().query(BagType).filter(
                BagType.is_enabled == True
            ).order_by(BagType.sort_order, BagType.bag_type_name).all()
            
            bag_type_options = [
                {
                    'id': str(bag_type.id),
                    'bag_type_name': bag_type.bag_type_name,
                    'sort_order': bag_type.sort_order
                }
                for bag_type in bag_types
            ]
            
            # 获取计算方案选项
            calculation_schemes = self.get_session().query(CalculationScheme).filter(
                CalculationScheme.is_enabled == True
            ).order_by(CalculationScheme.sort_order, CalculationScheme.scheme_name).all()
            
            formula_options = [
                {
                    'id': str(scheme.id),
                    'scheme_name': scheme.scheme_name,
                    'scheme_category': scheme.scheme_category,
                    'sort_order': scheme.sort_order
                }
                for scheme in calculation_schemes
            ]
            
            return {
                'success': True,
                'data': {
                    'bag_types': bag_type_options,
                    'formulas': formula_options
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'获取袋型相关公式选项数据失败: {str(e)}'
            }

# 创建服务实例的工厂函数
def get_bag_related_formula_service():
    """获取袋型相关公式服务实例"""
    return BagRelatedFormulaService()


