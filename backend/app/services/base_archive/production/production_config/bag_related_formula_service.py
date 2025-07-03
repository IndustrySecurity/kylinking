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
            
            # 搜索条件
            if search:
                search_pattern = f"%{search}%"
                query = query.filter(or_(
                    BagRelatedFormula.formula_name.ilike(search_pattern),
                    BagType.bag_type_name.ilike(search_pattern),
                    BagRelatedFormula.description.ilike(search_pattern)
                ))
            
            # 按袋型筛选
            if bag_type_id:
                query = query.filter(BagRelatedFormula.bag_type_id == uuid.UUID(bag_type_id))
            
            # 排序
            query = query.order_by(
                BagType.bag_type_name,
                BagRelatedFormula.sort_order,
                BagRelatedFormula.formula_name
            )
            
            # 分页
            total = query.count()
            formulas = query.offset((page - 1) * per_page).limit(per_page).all()
            
            # 构建返回数据
            result_data = []
            for formula in formulas:
                formula_dict = formula.to_dict()
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
            
            formula = self.session.query(BagRelatedFormula).get(uuid.UUID(formula_id))
            if not formula:
                raise ValueError("袋型相关公式不存在")
            
            result = formula.to_dict()
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
            if not data.get('formula_name'):
                raise ValueError("公式名称不能为空")
            
            if not data.get('bag_type_id'):
                raise ValueError("袋型不能为空")
            
            # 验证袋型是否存在
            bag_type = self.session.query(BagType).get(uuid.UUID(data['bag_type_id']))
            if not bag_type:
                raise ValueError("选择的袋型不存在")
            
            # 检查同一袋型下公式名称是否重复
            existing = self.session.query(BagRelatedFormula).filter_by(
                bag_type_id=uuid.UUID(data['bag_type_id']),
                formula_name=data['formula_name']
            ).first()
            if existing:
                raise ValueError("该袋型下已存在同名公式")
            
            # 创建袋型相关公式对象
            formula = self.create_with_tenant(BagRelatedFormula,
                formula_name=data['formula_name'],
                bag_type_id=uuid.UUID(data['bag_type_id']),
                formula_content=data.get('formula_content', ''),
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
            
            # 验证必填字段
            if 'formula_name' in data and not data['formula_name']:
                raise ValueError("公式名称不能为空")
            
            # 如果更新了袋型，验证袋型是否存在
            if 'bag_type_id' in data:
                if not data['bag_type_id']:
                    raise ValueError("袋型不能为空")
                
                bag_type = self.session.query(BagType).get(uuid.UUID(data['bag_type_id']))
                if not bag_type:
                    raise ValueError("选择的袋型不存在")
            
            # 检查同一袋型下公式名称是否重复（排除自己）
            if 'formula_name' in data or 'bag_type_id' in data:
                new_name = data.get('formula_name', formula.formula_name)
                new_bag_type_id = data.get('bag_type_id', formula.bag_type_id)
                
                existing = self.session.query(BagRelatedFormula).filter(
                    BagRelatedFormula.bag_type_id == uuid.UUID(new_bag_type_id),
                    BagRelatedFormula.formula_name == new_name,
                    BagRelatedFormula.id != formula.id
                ).first()
                if existing:
                    raise ValueError("该袋型下已存在同名公式")
            
            # 更新字段
            for key, value in data.items():
                if hasattr(formula, key):
                    if key == 'bag_type_id' and value:
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
            formulas = self.session.query(BagRelatedFormula).filter_by(
                bag_type_id=uuid.UUID(bag_type_id),
                is_enabled=True
            ).order_by(BagRelatedFormula.sort_order, BagRelatedFormula.formula_name).all()
            
            return [
                {
                    'value': str(formula.id),
                    'label': formula.formula_name,
                    'content': formula.formula_content or '',
                    'description': formula.description or ''
                }
                for formula in formulas
            ]
            
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


