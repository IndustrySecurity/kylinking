# -*- coding: utf-8 -*-
"""
QuoteMaterial 服务
"""

from app.services.base_service import TenantAwareService
from app.extensions import db
from sqlalchemy import func, text, and_, or_
from sqlalchemy.exc import IntegrityError
import uuid
from datetime import datetime
import re

class QuoteMaterialService(TenantAwareService):
    """报价材料服务"""

    def get_quote_materials(self, page=1, per_page=20, search=None):
        """获取报价材料列表"""
        from app.models.basic_data import QuoteMaterial
        
        try:
            query = self.session.query(QuoteMaterial)
            
            # 搜索条件
            if search:
                search_pattern = f"%{search}%"
                query = query.filter(or_(
                    QuoteMaterial.material_name.ilike(search_pattern),
                    QuoteMaterial.description.ilike(search_pattern)
                ))
            
            # 计算总数
            total = query.count()
            
            # 排序和分页
            query = query.order_by(QuoteMaterial.sort_order, QuoteMaterial.material_name)
            materials = query.offset((page - 1) * per_page).limit(per_page).all()
            
            return {
                'materials': [material.to_dict() for material in materials],
                'total': total,
                'current_page': page,
                'per_page': per_page,
                'pages': (total + per_page - 1) // per_page
            }
            
        except Exception as e:
            raise ValueError(f"获取报价材料列表失败: {str(e)}")
    
    def get_quote_material(self, material_id):
        """获取报价材料详情"""
        from app.models.basic_data import QuoteMaterial
        
        try:
            material = self.session.query(QuoteMaterial).get(uuid.UUID(material_id))
            if not material:
                raise ValueError("报价材料不存在")
            return material.to_dict()
        except Exception as e:
            raise ValueError(f"获取报价材料详情失败: {str(e)}")
    
    def create_quote_material(self, data, created_by):
        """创建报价材料"""
        from app.models.basic_data import QuoteMaterial
        
        try:
            # 验证必填字段
            if not data.get('material_name'):
                raise ValueError("材料名称不能为空")
            
            # 检查名称是否重复
            existing = self.session.query(QuoteMaterial).filter_by(
                material_name=data['material_name']
            ).first()
            if existing:
                raise ValueError("材料名称已存在")
            
            # 创建报价材料对象
            material = self.create_with_tenant(QuoteMaterial,
                material_name=data['material_name'],
                unit_price=data.get('unit_price', 0.0),
                material_type=data.get('material_type', ''),
                specification=data.get('specification', ''),
                description=data.get('description', ''),
                sort_order=data.get('sort_order', 0),
                is_enabled=data.get('is_enabled', True),
                created_by=uuid.UUID(created_by)
            )
            
            self.commit()
            return material.to_dict()
            
        except IntegrityError as e:
            self.rollback()
            raise ValueError("数据完整性错误")
        except Exception as e:
            self.rollback()
            raise ValueError(f"创建报价材料失败: {str(e)}")
    
    def update_quote_material(self, material_id, data, updated_by):
        """更新报价材料"""
        from app.models.basic_data import QuoteMaterial
        
        try:
            material = self.session.query(QuoteMaterial).get(uuid.UUID(material_id))
            if not material:
                raise ValueError("报价材料不存在")
            
            # 验证必填字段
            if 'material_name' in data and not data['material_name']:
                raise ValueError("材料名称不能为空")
            
            # 检查名称是否重复（排除自己）
            if 'material_name' in data:
                existing = self.session.query(QuoteMaterial).filter(
                    QuoteMaterial.material_name == data['material_name'],
                    QuoteMaterial.id != material.id
                ).first()
                if existing:
                    raise ValueError("材料名称已存在")
            
            # 更新字段
            for key, value in data.items():
                if hasattr(material, key):
                    setattr(material, key, value)
            
            material.updated_by = uuid.UUID(updated_by)
            
            self.commit()
            return material.to_dict()
            
        except IntegrityError as e:
            self.rollback()
            raise ValueError("数据完整性错误")
        except Exception as e:
            self.rollback()
            raise ValueError(f"更新报价材料失败: {str(e)}")
    
    def delete_quote_material(self, material_id):
        """删除报价材料"""
        from app.models.basic_data import QuoteMaterial
        
        try:
            material = self.session.query(QuoteMaterial).get(uuid.UUID(material_id))
            if not material:
                raise ValueError("报价材料不存在")
            
            self.session.delete(material)
            self.commit()
            
            return True
            
        except Exception as e:
            self.rollback()
            raise ValueError(f"删除报价材料失败: {str(e)}")
    
    def get_quote_material_options(self):
        """获取报价材料选项数据"""
        from app.models.basic_data import QuoteMaterial
        
        try:
            # 获取启用的报价材料
            enabled_materials = self.session.query(QuoteMaterial).filter(
                QuoteMaterial.is_enabled == True
            ).order_by(QuoteMaterial.sort_order, QuoteMaterial.material_name).all()
            
            return {
                'materials': [
                    {
                        'id': str(material.id),
                        'material_name': material.material_name,
                        'unit_price': float(material.unit_price),
                        'material_type': material.material_type,
                        'specification': material.specification,
                        'sort_order': material.sort_order
                    }
                    for material in enabled_materials
                ]
            }
            
        except Exception as e:
            raise ValueError(f"获取报价材料选项失败: {str(e)}")


# ==================== 工厂函数 ====================

def get_quote_material_service(tenant_id: str = None, schema_name: str = None) -> QuoteMaterialService:
    """
    获取报价材料服务实例
    
    Args:
        tenant_id: 租户ID（可选）
        schema_name: Schema名称（可选）
    
    Returns:
        QuoteMaterialService: 报价材料服务实例
    """
    return QuoteMaterialService(tenant_id=tenant_id, schema_name=schema_name)

