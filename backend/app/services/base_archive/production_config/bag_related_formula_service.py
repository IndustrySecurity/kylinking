# -*- coding: utf-8 -*-
"""
BagRelatedFormula服务
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
    
    def get_bag_related_formulas(self, page=1, per_page=20, search=None, bag_type_id=None):
        """获取袋型相关公式列表"""
        try:
            from app.models.basic_data import BagRelatedFormula, BagType
            
            query = self.session.query(BagRelatedFormula).join(BagType)
            
            # 搜索条件 - 移除不存在的formula_name字段，改为搜索dimension_description和bag_type_name
            if search:
                search_pattern = f"%{search}%"
                query = query.filter(or_(
                    BagRelatedFormula.dimension_description.ilike(search_pattern),
                    BagType.bag_type_name.ilike(search_pattern),
                    BagRelatedFormula.description.ilike(search_pattern)
                ))
            
            # 按袋型筛选
            if bag_type_id:
                query = query.filter(BagRelatedFormula.bag_type_id == uuid.UUID(bag_type_id))
            
            # 排序 - 移除不存在的formula_name字段
            query = query.order_by(
                BagType.bag_type_name,
                BagRelatedFormula.sort_order,
                BagRelatedFormula.dimension_description
            )
            
            # 分页
            total = query.count()
            formulas = query.offset((page - 1) * per_page).limit(per_page).all()
            
            # 构建返回数据
            result_data = []
            for formula in formulas:
                formula_dict = formula.to_dict(include_user_info=True, include_formulas=True)
                # 添加袋型信息
                if formula.bag_type:
                    formula_dict['bag_type_name'] = formula.bag_type.bag_type_name
                result_data.append(formula_dict)
            
            return {
                'formulas': result_data,
                'total': total,
                'page': page,
                'per_page': per_page,
                'pages': (total + per_page - 1) // per_page
            }
        except Exception as e:
            raise ValueError(f"获取袋型相关公式列表失败: {str(e)}")
    
    def get_bag_related_formula(self, formula_id):
        """获取袋型相关公式详情"""
        try:
            from app.models.basic_data import BagRelatedFormula
            
            formula = self.session.query(BagRelatedFormula).get(formula_id)
            if not formula:
                raise ValueError("袋型相关公式不存在")
            
            result = formula.to_dict(include_user_info=True, include_formulas=True)
            if formula.bag_type:
                result['bag_type_name'] = formula.bag_type.bag_type_name
            
            return result
        except Exception as e:
            raise ValueError(f"获取袋型相关公式详情失败: {str(e)}")
    
    def create_bag_related_formula(self, data, created_by):
        """创建袋型相关公式"""
        from app.models.basic_data import BagRelatedFormula, BagType
        
        try:
            # 验证必填字段
            if not data.get('bag_type_id'):
                raise ValueError("袋型不能为空")
            
            # 验证袋型是否存在
            bag_type = self.session.query(BagType).get(uuid.UUID(data['bag_type_id']))
            if not bag_type:
                raise ValueError("选择的袋型不存在")
            
            # 检查同一袋型下是否已存在记录（一个袋型只能有一条公式记录）
            existing = self.session.query(BagRelatedFormula).filter_by(
                bag_type_id=uuid.UUID(data['bag_type_id'])
            ).first()
            if existing:
                raise ValueError("该袋型已存在相关公式配置")

            # 创建袋型相关公式对象
            formula = self.create_with_tenant(BagRelatedFormula,
                bag_type_id=uuid.UUID(data['bag_type_id']),
                meter_formula_id=uuid.UUID(data['meter_formula_id']) if data.get('meter_formula_id') else None,
                square_formula_id=uuid.UUID(data['square_formula_id']) if data.get('square_formula_id') else None,
                material_width_formula_id=uuid.UUID(data['material_width_formula_id']) if data.get('material_width_formula_id') else None,
                per_piece_formula_id=uuid.UUID(data['per_piece_formula_id']) if data.get('per_piece_formula_id') else None,
                dimension_description=data.get('dimension_description', ''),
                description=data.get('description', ''),
                sort_order=data.get('sort_order', 0),
                is_enabled=data.get('is_enabled', True),
                created_by=uuid.UUID(created_by)
            )
            self.commit()
            return self.get_bag_related_formula(formula.id)
            
        except IntegrityError as e:
            self.rollback()
            raise ValueError("数据完整性错误")
        except Exception as e:
            self.rollback()
            raise ValueError(f"创建袋型相关公式失败: {str(e)}")
    
    def update_bag_related_formula(self, formula_id, data, updated_by):
        """更新袋型相关公式"""
        from app.models.basic_data import BagRelatedFormula, BagType
        
        try:
            formula = self.session.query(BagRelatedFormula).get(uuid.UUID(formula_id))
            if not formula:
                raise ValueError("袋型相关公式不存在")
            
            # 如果更新了袋型，验证袋型是否存在
            if 'bag_type_id' in data:
                if not data['bag_type_id']:
                    raise ValueError("袋型不能为空")
                
                bag_type = self.session.query(BagType).get(uuid.UUID(data['bag_type_id']))
                if not bag_type:
                    raise ValueError("选择的袋型不存在")
            
                # 检查新袋型是否已有其他记录（排除当前记录）
                existing = self.session.query(BagRelatedFormula).filter(
                    BagRelatedFormula.bag_type_id == uuid.UUID(data['bag_type_id']),
                    BagRelatedFormula.id != formula.id
                ).first()
                if existing:
                    raise ValueError("该袋型已存在相关公式配置")
            
            # 更新字段
            for key, value in data.items():
                if hasattr(formula, key):
                    if key in ['bag_type_id', 'meter_formula_id', 'square_formula_id', 
                             'material_width_formula_id', 'per_piece_formula_id'] and value:
                        setattr(formula, key, uuid.UUID(value))
                    else:
                        setattr(formula, key, value)
            
            formula.updated_by = uuid.UUID(updated_by)
            
            self.commit()
            
            return self.get_bag_related_formula(formula.id)
            
        except IntegrityError as e:
            self.rollback()
            raise ValueError("数据完整性错误")
        except Exception as e:
            self.rollback()
            raise ValueError(f"更新袋型相关公式失败: {str(e)}")
    
    def delete_bag_related_formula(self, formula_id):
        """删除袋型相关公式"""
        from app.models.basic_data import BagRelatedFormula
        
        try:
            formula = self.session.query(BagRelatedFormula).get(uuid.UUID(formula_id))
            if not formula:
                raise ValueError("袋型相关公式不存在")
            
            self.session.delete(formula)
            self.commit()
            
            return True
            
        except Exception as e:
            self.rollback()
            raise ValueError(f"删除袋型相关公式失败: {str(e)}")
    
    def get_bag_type_options(self):
        """获取袋型选项"""
        from app.models.basic_data import BagType
        
        try:
            bag_types = self.session.query(BagType).filter(
                BagType.is_enabled == True
            ).order_by(BagType.sort_order, BagType.bag_type_name).all()
            
            return [
                {
                    'value': str(bag_type.id),
                    'label': bag_type.bag_type_name,
                    'description': bag_type.description or ''
                }
                for bag_type in bag_types
            ]
            
        except Exception as e:
            raise ValueError(f"获取袋型选项失败: {str(e)}")
    
    def get_formulas_by_bag_type(self, bag_type_id):
        """根据袋型获取公式列表"""
        from app.models.basic_data import BagRelatedFormula
        
        try:
            formula = self.session.query(BagRelatedFormula).filter_by(
                bag_type_id=uuid.UUID(bag_type_id),
                is_enabled=True
            ).first()
            
            if formula:
                return formula.to_dict(include_user_info=True, include_formulas=True)
            else:
                return None
            
        except Exception as e:
            raise ValueError(f"获取袋型公式失败: {str(e)}")


# ==================== 工厂函数 ====================

def get_bag_related_formula_service(tenant_id: str = None, schema_name: str = None) -> BagRelatedFormulaService:
    """
    获取袋型相关公式服务实例
    
    Args:
        tenant_id: 租户ID（可选）
        schema_name: Schema名称（可选）
    
    Returns:
        BagRelatedFormulaService: 袋型相关公式服务实例
    """
    return BagRelatedFormulaService(tenant_id=tenant_id, schema_name=schema_name)


